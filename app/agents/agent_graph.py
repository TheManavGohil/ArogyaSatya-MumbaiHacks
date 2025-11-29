import json
from typing import List, Dict, TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from app.agents.prompts import EXPLAINER_PROMPT
from app.core.config import settings

# Import Agents
from app.agents.claim_extraction import claim_extraction_node
from app.agents.canonicalization import canonicalization_node
from app.agents.evidence_retrieval import evidence_retrieval_node
from app.agents.verification import verification_node
from app.agents.vlm_agent import vlm_node
from app.agents.video_processor import video_processor_node
from app.agents.pubmed_agent import pubmed_node
from app.agents.safety_agent import safety_monitor_node

# Initialize LLM (for Explainer)
llm = ChatGroq(
    temperature=0, 
    model_name="openai/gpt-oss-120b", 
    api_key=settings.GROQ_API_KEY
)

class AgentState(TypedDict):
    article_id: int
    text: str
    images: List[str] # List of image URLs
    claims: List[str] # From Extraction
    evidence: Dict[str, List[Dict]] # From Retrieval
    verification_results: List[Dict] # From Verification
    image_analysis: List[Dict] # From VLM
    final_report: str # From Explainer
    safety_status: Dict # From Safety Monitor

def explainer_node(state: AgentState):
    print("---EXPLAINER NODE---")
    
    # Check Safety First
    safety = state.get("safety_status", {})
    if safety and not safety.get("is_safe", True):
        return {"final_report": f"⚠️ **SAFETY WARNING**: Analysis halted.\n\n{safety.get('warning', 'Content flagged as unsafe.')}\n\nReason: {safety.get('reason')}"}

    results = state["verification_results"]
    image_results = state.get("image_analysis", [])
    
    # Filter for false or unverified claims to address
    to_address = [r for r in results if r.get("status") != "True"]
    
    # Add image findings to report context
    image_context = ""
    if image_results:
        image_context = "\n\nImage Analysis:\n" + json.dumps(image_results)
    
    if not to_address and not image_results:
        return {"final_report": "No misinformation detected."}
        
    response = llm.invoke([
        SystemMessage(content=EXPLAINER_PROMPT.format(verification_results=json.dumps(to_address) + image_context))
    ])
    
    return {"final_report": response.content}

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("video_processor", video_processor_node)
workflow.add_node("safety_monitor", safety_monitor_node)
workflow.add_node("claim_extraction", claim_extraction_node)
workflow.add_node("vlm_analysis", vlm_node)
workflow.add_node("canonicalization", canonicalization_node)
workflow.add_node("evidence_retrieval", evidence_retrieval_node)
workflow.add_node("pubmed_search", pubmed_node)
workflow.add_node("verification", verification_node)
workflow.add_node("explainer", explainer_node)

# Set Video Processor as entry point
workflow.set_entry_point("video_processor")

# Flow
workflow.add_edge("video_processor", "safety_monitor")

# Conditional Edge for Safety
def check_safety(state):
    safety = state.get("safety_status", {})
    if safety and not safety.get("is_safe", True):
        return "explainer" # Skip to explainer to show warning
    return "claim_extraction"

workflow.add_conditional_edges(
    "safety_monitor",
    check_safety,
    {
        "explainer": "explainer",
        "claim_extraction": "claim_extraction"
    }
)

workflow.add_edge("claim_extraction", "vlm_analysis")
workflow.add_edge("vlm_analysis", "canonicalization")
workflow.add_edge("canonicalization", "evidence_retrieval")
workflow.add_edge("evidence_retrieval", "pubmed_search") # Chain PubMed after general retrieval
workflow.add_edge("pubmed_search", "verification")
workflow.add_edge("verification", "explainer")
workflow.add_edge("explainer", END)

app_graph = workflow.compile()

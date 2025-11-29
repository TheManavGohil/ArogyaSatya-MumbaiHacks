import json
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from app.core.config import settings
from app.agents.prompts import VERIFIER_PROMPT

# Initialize LLM
llm = ChatGroq(
    temperature=0, 
    model_name="openai/gpt-oss-120b", 
    api_key=settings.GROQ_API_KEY
)

def verification_node(state):
    print("---VERIFICATION NODE (Sync)---")
    claims = state["claims"]
    evidence_map = state["evidence"]
    results = []
    
    for claim in claims:
        evidence_items = evidence_map.get(claim, [])
        
        # Format evidence for LLM
        if not evidence_items:
            evidence_text = "No evidence found."
        else:
            evidence_text = "\n".join([f"- [{item['source']}] {item['title']}: {item['snippet']}" for item in evidence_items])
            
        response = llm.invoke([
            SystemMessage(content=VERIFIER_PROMPT.format(claim=claim, evidence=evidence_text))
        ])
        
        try:
            verification = json.loads(response.content)
        except:
            verification = {"status": "Unverified", "explanation": "Could not parse verification result.", "correction": ""}
        
        verification["claim"] = claim
        verification["evidence"] = evidence_items # Pass structured evidence to UI
        results.append(verification)
        
    return {"verification_results": results}

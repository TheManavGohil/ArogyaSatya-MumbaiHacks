import json
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from app.core.config import settings

# Initialize LLM
llm = ChatGroq(
    temperature=0, 
    model_name="openai/gpt-oss-120b", 
    api_key=settings.GROQ_API_KEY
)

CLAIM_EXTRACTION_PROMPT = """
You are an expert fact-checker. Your task is to extract atomic, verifiable claims from the provided text.
Focus on healthcare and medical assertions.
Ignore opinions, questions, or vague statements.

Input Text:
{text}

Output format:
Return a JSON list of strings, where each string is a standalone claim.
Example: ["Vaccine X causes infertility", "Vitamin C cures COVID-19"]
"""

def claim_extraction_node(state):
    print("---CLAIM EXTRACTION NODE---")
    text = state["text"]
    
    response = llm.invoke([
        SystemMessage(content=CLAIM_EXTRACTION_PROMPT.format(text=text))
    ])
    
    try:
        claims = json.loads(response.content)
        if not isinstance(claims, list):
            claims = []
    except:
        claims = []
    
    print(f"Extracted claims: {claims}")
    return {"claims": claims}

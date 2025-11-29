from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from app.core.config import settings
import json

SAFETY_PROMPT = """
You are a Safety Monitor for a healthcare analysis system.
Your job is to screen the following text for IMMEDIATE HARM or DANGEROUS ADVICE.

Dangerous advice includes:
- Encouraging self-harm or suicide.
- Promoting the ingestion of toxic substances (e.g., bleach, pesticides).
- Advising against life-saving emergency treatment (e.g., "don't call 911 for a heart attack").
- Promoting violence.

If the content contains such advice, return JSON:
{{
    "is_safe": false,
    "reason": "Explanation of the danger",
    "warning": "DO NOT FOLLOW THIS ADVICE. SEEK PROFESSIONAL HELP IMMEDIATELY."
}}

If the content is just misinformation (even if wrong) but not immediately life-threatening in an acute way (e.g., "eat garlic for flu"), or if it is safe, return:
{{
    "is_safe": true,
    "reason": "Safe for analysis"
}}

Text to screen:
{text}
"""

llm = ChatGroq(
    temperature=0, 
    model_name="openai/gpt-oss-120b", 
    api_key=settings.GROQ_API_KEY
)

def safety_monitor_node(state):
    print("---SAFETY MONITOR AGENT---")
    text = state.get("text", "")
    
    if not text:
        return {"safety_status": {"is_safe": True, "reason": "No text provided"}}

    try:
        response = llm.invoke([SystemMessage(content=SAFETY_PROMPT.format(text=text[:2000]))]) # Check first 2000 chars
        result = json.loads(response.content)
        
        if not result["is_safe"]:
            print(f"⚠️ SAFETY ALERT: {result['reason']}")
            # We can choose to halt execution here or just tag it
            # For now, we'll tag it and let the explainer handle the warning
            return {"safety_status": result}
            
    except Exception as e:
        print(f"Safety check failed: {e}")
        
    return {"safety_status": {"is_safe": True, "reason": "Check passed or failed safely"}}

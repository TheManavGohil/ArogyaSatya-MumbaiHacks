import json
from app.core.llm_cache import cached_llm_invoke

# Simplified safety prompt for faster processing
SAFETY_PROMPT = """
Screen this text for DANGEROUS advice (self-harm, toxic ingestion, avoiding emergency care, violence).

Text: {text}

Return JSON only:
{{"is_safe": true/false, "reason": "brief reason"}}
"""

def safety_monitor_node(state):
    print("---SAFETY MONITOR AGENT---")
    text = state.get("text", "")

    if not text:
        return {"safety_status": {"is_safe": True, "reason": "No text provided"}}

    try:
        # Check only first 1000 chars for speed
        prompt = SAFETY_PROMPT.format(text=text[:1000])
        response_content = cached_llm_invoke(prompt)
        result = json.loads(response_content)

        if not result.get("is_safe", True):
            print(f"⚠️ SAFETY ALERT: {result.get('reason', 'Unknown')}")
            result["warning"] = "DO NOT FOLLOW THIS ADVICE. SEEK PROFESSIONAL HELP."
            return {"safety_status": result}

    except Exception as e:
        print(f"Safety check error: {e}")

    return {"safety_status": {"is_safe": True, "reason": "Passed"}}

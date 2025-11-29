import json
from app.core.llm_cache import cached_llm_invoke

CLAIM_EXTRACTION_PROMPT = """
You are an expert fact-checker. Extract up to 5 key verifiable healthcare claims from this text.
Focus on medical assertions. Ignore opinions or vague statements. Be concise.

Text:
{text}

Return ONLY a JSON list of claim strings. Example: ["Claim 1", "Claim 2"]
"""

def claim_extraction_node(state):
    print("---CLAIM EXTRACTION NODE---")
    text = state["text"]

    # Limit text length to improve speed
    truncated_text = text[:3000] if len(text) > 3000 else text

    prompt = CLAIM_EXTRACTION_PROMPT.format(text=truncated_text)
    response_content = cached_llm_invoke(prompt)

    try:
        claims = json.loads(response_content)
        if not isinstance(claims, list):
            claims = []
        # Limit to 5 claims for performance
        claims = claims[:5]
    except:
        claims = []

    print(f"Extracted {len(claims)} claims")
    return {"claims": claims}

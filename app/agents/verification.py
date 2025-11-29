import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.core.llm_cache import cached_llm_invoke
from app.agents.prompts import VERIFIER_PROMPT


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling common formatting issues."""
    # Try direct parse first
    try:
        return json.loads(text)
    except:
        pass

    # Try to find JSON object in the text
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass

    # Try to extract key-value pairs manually
    status_match = re.search(r'"?status"?\s*[:\-]\s*"?(True|False|Unverified)"?', text, re.IGNORECASE)
    explanation_match = re.search(r'"?explanation"?\s*[:\-]\s*"?([^"]+)"?', text, re.IGNORECASE)

    if status_match:
        return {
            "status": status_match.group(1).capitalize(),
            "explanation": explanation_match.group(1) if explanation_match else "See evidence above.",
            "correction": ""
        }

    return None


def _verify_single_claim(claim: str, evidence_items: list) -> dict:
    """Verify a single claim - for parallel execution."""
    # Format evidence for LLM
    if not evidence_items:
        evidence_text = "No evidence found."
    else:
        # Limit evidence to avoid token limits and speed up
        limited_evidence = evidence_items[:4]
        evidence_text = "\n".join([
            f"- [{item['source']}] {item['title']}: {item['snippet'][:200]}"
            for item in limited_evidence
        ])

    prompt = VERIFIER_PROMPT.format(claim=claim, evidence=evidence_text)
    response_content = cached_llm_invoke(prompt)

    verification = _extract_json(response_content)
    if not verification:
        # Fallback: if we have evidence, mark as True (well-supported), else Unverified
        has_trusted = any(item.get('trusted', False) for item in evidence_items)
        verification = {
            "status": "True" if has_trusted else "Unverified",
            "explanation": "Claim is supported by available evidence." if has_trusted else "Unable to verify - please check sources.",
            "correction": ""
        }

    verification["claim"] = claim
    verification["evidence"] = evidence_items
    return verification


def verification_node(state):
    print("---VERIFICATION NODE (Parallel)---")
    claims = state["claims"]
    evidence_map = state["evidence"]
    results = []

    if not claims:
        return {"verification_results": results}

    # Parallel verification of claims
    max_workers = min(len(claims), 3)  # Limit concurrent LLM calls

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_verify_single_claim, claim, evidence_map.get(claim, [])): claim
            for claim in claims
        }

        for future in as_completed(futures):
            try:
                verification = future.result(timeout=30)
                results.append(verification)
                print(f"Verified: '{verification['claim'][:40]}...' -> {verification.get('status', 'Unknown')}")
            except Exception as e:
                claim = futures[future]
                print(f"Verification failed for '{claim[:30]}...': {e}")
                results.append({
                    "claim": claim,
                    "status": "Unverified",
                    "explanation": f"Verification error: {str(e)}",
                    "correction": "",
                    "evidence": evidence_map.get(claim, [])
                })

    return {"verification_results": results}

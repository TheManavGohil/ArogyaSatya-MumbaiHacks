DETECTOR_PROMPT = """
You are an expert misinformation detector in the healthcare domain.
Analyze the following text and extract specific factual claims that sound suspicious, unverified, or potentially false.
Focus on medical advice, vaccine claims, cure claims, and statistical assertions.

Text:
{text}

Return the output as a JSON list of strings, where each string is a distinct claim.
If no suspicious claims are found, return an empty list.
Example format: ["Vaccines cause magnetism", "Drinking bleach cures COVID"]
"""

VERIFIER_PROMPT = """
Verify this healthcare claim using the evidence provided.

Claim: {claim}

Evidence:
{evidence}

Return ONLY valid JSON (no other text):
{{"status": "True" or "False" or "Unverified", "explanation": "brief explanation citing evidence", "correction": "correct info if False, else empty string"}}
"""

EXPLAINER_PROMPT = """
You are a helpful health communicator.
Based on the following verification results, generate a clear, accessible, and empathetic explanation for the general public.
Address the misinformation directly but politely, providing the correct information.

Verification Results:
{verification_results}

Write a short article or social media post correcting the misinformation.
"""

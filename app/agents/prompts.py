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
You are a professional fact-checker. Your task is to verify the following claim using the provided evidence.
Claim: {claim}

Evidence:
{evidence}

Determine if the claim is True, False, or Unverified based on the evidence.
Provide a brief explanation and cite the evidence if possible.
Return the output as a JSON object with keys: "status" (True/False/Unverified), "explanation", "correction" (if False).
"""

EXPLAINER_PROMPT = """
You are a helpful health communicator.
Based on the following verification results, generate a clear, accessible, and empathetic explanation for the general public.
Address the misinformation directly but politely, providing the correct information.

Verification Results:
{verification_results}

Write a short article or social media post correcting the misinformation.
"""

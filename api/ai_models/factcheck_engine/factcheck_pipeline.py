"""
FACT CHECKING MASTER PIPELINE
This file is imported by FastAPI.
DO NOT rename the main function: factcheck_text
"""

from typing import Dict, List
from .claim_extractor import extract_claims
from .evidence_retriever import get_urls
from .verifier import verify_claim


# -----------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------

def compute_fact_score(support: float, contradict: float) -> float:
    """
    Convert NLI scores into a normalized trust score.
    Range: 0 → 1
    """
    raw_score = support - contradict
    return max(0.0, raw_score)


def generate_verdict(support: float, contradict: float) -> str:
    """
    Human-readable verdict from NLI scores.
    """
    if support > contradict and support > 0.5:
        return "Likely True"
    elif contradict > support and contradict > 0.5:
        return "Likely False"
    else:
        return "Uncertain"


# -----------------------------------------------------------
# MAIN FACT CHECK FUNCTION (Imported by FastAPI)
# -----------------------------------------------------------

def factcheck_text(text: str) -> Dict:
    """
    Full Fact Checking Pipeline

    Steps:
    1. Extract factual claims
    2. Retrieve web evidence
    3. Verify using NLI
    4. Aggregate trust score
    """

    if not text or text.strip() == "":
        return {
            "claims": [],
            "fact_trust_score": 0.0
        }

    claims: List[str] = extract_claims(text)

    results = []
    cumulative_score = 0.0

    for claim in claims:
        # ---------------------------------------------------
        # Step 1: Retrieve evidence URLs
        # ---------------------------------------------------
        urls = get_urls(claim)

        # Convert URLs → text proxy (hackathon demo simplification)
        evidence_text = " ".join(urls)

        # ---------------------------------------------------
        # Step 2: Verify claim using NLI
        # ---------------------------------------------------
        scores = verify_claim(claim, evidence_text)

        support = float(scores.get("Supported", 0))
        contradict = float(scores.get("Contradicted", 0))

        # ---------------------------------------------------
        # Step 3: Compute trust score
        # ---------------------------------------------------
        fact_score = compute_fact_score(support, contradict)
        cumulative_score += fact_score

        verdict = generate_verdict(support, contradict)

        results.append({
            "claim": claim,
            "verdict": verdict,
            "support_score": round(support, 3),
            "contradiction_score": round(contradict, 3),
            "sources": urls[:3]
        })

    # ---------------------------------------------------
    # Step 4: Aggregate overall trust score
    # ---------------------------------------------------
    if len(results) > 0:
        overall_score = cumulative_score / len(results)
    else:
        overall_score = 0.0

    return {
        "claims": results,
        "fact_trust_score": round(overall_score, 3)
    }

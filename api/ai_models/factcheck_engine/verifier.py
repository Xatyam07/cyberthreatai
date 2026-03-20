from transformers import pipeline

# Load once globally
nli_model = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

LABELS = ["Supported","Contradicted","Uncertain"]

def verify_claim(claim: str, evidence_text: str):
    """
    Compare evidence vs claim using Natural Language Inference.
    """

    if evidence_text.strip() == "":
        return {"Supported":0, "Contradicted":0, "Uncertain":1}

    result = nli_model(
        evidence_text,
        LABELS,
        hypothesis_template="This text {} the claim: " + claim
    )

    scores = dict(zip(result["labels"], result["scores"]))
    return scores

def verify_claim(claim: str, evidence_text: str):
    """
    Compare evidence vs claim using Natural Language Inference.
    Safe version for deployment.
    """

    try:
        from transformers import pipeline

        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )

        LABELS = ["Supported", "Contradicted", "Uncertain"]

        if not evidence_text.strip():
            return {"Supported": 0, "Contradicted": 0, "Uncertain": 1}

        result = classifier(
            evidence_text,
            LABELS,
            hypothesis_template="This text {} the claim: " + claim
        )

        scores = dict(zip(result["labels"], result["scores"]))
        return scores

    except Exception as e:
        print("Transformer error:", e)

        # fallback (VERY IMPORTANT for Render stability)
        return {"Supported": 0, "Contradicted": 0, "Uncertain": 1}
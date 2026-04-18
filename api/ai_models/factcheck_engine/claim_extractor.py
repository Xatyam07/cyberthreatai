import spacy

# 🔥 Safe loading (prevents crash on Render)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = spacy.blank("en")  # fallback model


IMPORTANT_ENTITIES = [
    "ORG", "GPE", "PERSON", "MONEY", "DATE",
    "EVENT", "PRODUCT", "NORP", "FAC"
]

NUMERIC_KEYWORDS = [
    "crore", "lakh", "million", "billion",
    "percent", "%", "₹", "$"
]


def is_claim_sentence(sent):
    """Heuristic to detect factual claims"""
    
    # If model fallback used → no NER → avoid crash
    has_entity = False
    if hasattr(sent.doc, "ents"):
        has_entity = any(ent.label_ in IMPORTANT_ENTITIES for ent in sent.ents)

    has_number = any(token.like_num for token in sent)
    has_numeric_word = any(word in sent.text.lower() for word in NUMERIC_KEYWORDS)

    return has_entity or has_number or has_numeric_word


def extract_claims(text: str):
    """
    Extract sentences that look like factual claims.
    """
    
    # Handle empty input safely
    if not text or not text.strip():
        return []

    doc = nlp(text)
    claims = []

    for sent in doc.sents:
        if len(sent.text.split()) < 5:
            continue

        if is_claim_sentence(sent):
            claims.append(sent.text.strip())

    # fallback: if nothing detected, use full text
    if not claims:
        claims.append(text.strip())

    return claims
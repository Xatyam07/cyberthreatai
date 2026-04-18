import spacy

nlp = None  # not loaded initially


def get_nlp():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except:
            nlp = spacy.blank("en")
    return nlp


IMPORTANT_ENTITIES = [
    "ORG", "GPE", "PERSON", "MONEY", "DATE",
    "EVENT", "PRODUCT", "NORP", "FAC"
]

NUMERIC_KEYWORDS = [
    "crore", "lakh", "million", "billion",
    "percent", "%", "₹", "$"
]


def is_claim_sentence(sent):
    has_entity = any(ent.label_ in IMPORTANT_ENTITIES for ent in getattr(sent.doc, "ents", []))
    has_number = any(token.like_num for token in sent)
    has_numeric_word = any(word in sent.text.lower() for word in NUMERIC_KEYWORDS)

    return has_entity or has_number or has_numeric_word


def extract_claims(text: str):
    if not text or not text.strip():
        return []

    nlp = get_nlp()  # 🔥 safe loading here

    doc = nlp(text)
    claims = []

    for sent in doc.sents:
        if len(sent.text.split()) < 5:
            continue

        if is_claim_sentence(sent):
            claims.append(sent.text.strip())

    if not claims:
        claims.append(text.strip())

    return claims
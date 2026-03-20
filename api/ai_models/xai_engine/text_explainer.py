import re
from collections import Counter

# -----------------------------
# KEYWORD KNOWLEDGE BASE
# -----------------------------

SCAM_KEYWORDS = [
    "urgent","immediately","limited","act now","winner","congratulations",
    "free","guaranteed","risk free","lottery","jackpot","crypto",
    "investment","double your money","bank","otp","password","click",
    "verify","account suspended","loan","offer","reward","gift"
]

EMOTIONAL_WORDS = [
    "shocking","unbelievable","amazing","terrifying","panic",
    "breaking","exclusive","secret","alert","danger"
]

FINANCIAL_PATTERNS = [
    r"\₹\d+",
    r"\$\d+",
    r"\d+% return",
    r"double your money",
    r"earn money fast",
]

URGENCY_PATTERNS = [
    r"within \d+ hours",
    r"today only",
    r"limited time",
    r"last chance"
]

# -----------------------------
# TOKEN HIGHLIGHT ENGINE
# -----------------------------

def highlight_text_tokens(text: str):
    tokens = text.split()
    highlighted_tokens = []

    for token in tokens:
        clean = token.lower().strip(".,!?")

        risk = "normal"
        reason = None

        if clean in SCAM_KEYWORDS:
            risk = "high"
            reason = "Scam keyword"

        elif clean in EMOTIONAL_WORDS:
            risk = "medium"
            reason = "Emotional manipulation"

        highlighted_tokens.append({
            "token": token,
            "risk": risk,
            "reason": reason
        })

    return highlighted_tokens

# -----------------------------
# PATTERN DETECTORS
# -----------------------------

def detect_financial_patterns(text):
    matches = []
    for pattern in FINANCIAL_PATTERNS:
        if re.search(pattern, text.lower()):
            matches.append(pattern)
    return matches


def detect_urgency_patterns(text):
    matches = []
    for pattern in URGENCY_PATTERNS:
        if re.search(pattern, text.lower()):
            matches.append(pattern)
    return matches


def keyword_density(text):
    words = text.lower().split()
    count = sum(word in SCAM_KEYWORDS for word in words)
    return count / max(len(words),1)

# -----------------------------
# RISK BREAKDOWN GENERATOR
# -----------------------------

def generate_risk_breakdown(text_score, fact_score):
    breakdown = {
        "linguistic_risk": round(text_score,2),
        "factual_risk": round(1 - fact_score,2),
        "emotional_manipulation": 0,
        "financial_scam_signals": 0,
        "urgency_pressure": 0
    }
    return breakdown

# -----------------------------
# HUMAN EXPLANATION ENGINE
# -----------------------------

def generate_human_explanation(text, text_score, fact_score):
    explanations = []

    if text_score > 0.7:
        explanations.append("Language strongly matches known scam/fake patterns.")

    if fact_score < 0.4:
        explanations.append("Claims could not be verified from trusted sources.")

    financial_hits = detect_financial_patterns(text)
    if financial_hits:
        explanations.append("Financial scam patterns detected.")

    urgency_hits = detect_urgency_patterns(text)
    if urgency_hits:
        explanations.append("Urgency tactics detected to pressure users.")

    density = keyword_density(text)
    if density > 0.05:
        explanations.append("High density of scam-related keywords detected.")

    if not explanations:
        explanations.append("No strong red flags detected.")

    return explanations

# -----------------------------
# MAIN PIPELINE FUNCTION
# -----------------------------

def explain_text(text, text_score, fact_score):
    return {
        "highlighted_tokens": highlight_text_tokens(text),
        "financial_patterns": detect_financial_patterns(text),
        "urgency_patterns": detect_urgency_patterns(text),
        "risk_breakdown": generate_risk_breakdown(text_score, fact_score),
        "human_explanations": generate_human_explanation(text, text_score, fact_score)
    }

def calculate_trust_score(text, image, video, fact):
    weights = {
        "text":0.25,
        "image":0.20,
        "video":0.20,
        "fact":0.35
    }

    trust = (
        text * weights["text"] +
        image * weights["image"] +
        video * weights["video"] +
        fact * weights["fact"]
    )

    return round(trust,3)


def risk_level(score):
    if score > 0.75:
        return "HIGH RISK"
    elif score > 0.45:
        return "MEDIUM RISK"
    else:
        return "LOW RISK"


def model_agreement(text, image, video):
    scores = [text, image, video]
    variance = max(scores) - min(scores)

    if variance < 0.2:
        return "Models strongly agree"
    elif variance < 0.4:
        return "Moderate model agreement"
    else:
        return "Models show disagreement"


def final_trust_report(text, image, video, fact):
    score = calculate_trust_score(text,image,video,fact)

    return {
        "final_score": score,
        "risk_level": risk_level(score),
        "model_agreement": model_agreement(text,image,video),
        "confidence_percentage": round(score*100,2)
    }

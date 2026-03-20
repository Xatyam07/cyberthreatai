def interpret_deepfake_score(score):
    if score > 0.85:
        return "Video is highly likely a deepfake."
    elif score > 0.6:
        return "Strong deepfake artifacts detected."
    elif score > 0.4:
        return "Possible facial inconsistencies detected."
    else:
        return "Video appears authentic."


def generate_video_risks(score):
    risks = []

    if score > 0.7:
        risks.append("Facial landmark instability across frames")

    if score > 0.6:
        risks.append("Lighting inconsistency detected")

    if score > 0.5:
        risks.append("Lip-sync mismatch probability")

    if not risks:
        risks.append("No deepfake artifacts detected")

    return risks


def deepfake_confidence(score):
    return round(score * 100,2)


def explain_video(score):
    return {
        "summary": interpret_deepfake_score(score),
        "confidence_percentage": deepfake_confidence(score),
        "risk_factors": generate_video_risks(score)
    }

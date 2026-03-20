def interpret_manipulation_score(score):
    if score > 0.85:
        return "Image is highly likely manipulated."
    elif score > 0.6:
        return "Strong signs of editing detected."
    elif score > 0.4:
        return "Possible minor editing detected."
    else:
        return "Image appears authentic."


def generate_image_risk_factors(score, exif_found):
    risks = []

    if score > 0.7:
        risks.append("High Error Level Analysis anomalies")

    if not exif_found:
        risks.append("Missing EXIF metadata (common in edited images)")

    if score > 0.5:
        risks.append("Compression inconsistencies detected")

    if not risks:
        risks.append("No major tampering signals detected")

    return risks


def confidence_meter(score):
    return round(score * 100,2)


def explain_image(score, exif_found=True):
    return {
        "summary": interpret_manipulation_score(score),
        "confidence_percentage": confidence_meter(score),
        "risk_factors": generate_image_risk_factors(score, exif_found)
    }

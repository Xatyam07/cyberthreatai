"""
xai_pipeline.py — Explainable AI Pipeline
==========================================
Cyber Threat AI · Phase F (XAI) · MOST ADVANCED VERSION

Generates three levels of explanation:

  Level 1 — Signal Attribution
    SHAP-inspired permutation importance: how much does each signal
    individually change the final prediction when zeroed out?
    → "Image reuse signal contributed +31% to the FAKE verdict"

  Level 2 — Attention Visualisation
    Uses the attention weights from AttentionFusionNet to show which
    signals the model paid most attention to when making its decision.
    → Signal-to-signal attention matrix (7×7)

  Level 3 — Natural Language Explanation
    Synthesises all evidence into a journalist-quality summary that
    explains WHY the verdict was reached, with specific evidence citations.
    → "This image was originally published in 2011 during the Kerala
       floods. The caption claiming it shows J&K 2026 is contradicted
       by 3 independent sources. The AI system detected..."

All three levels are returned together in the /explain-result response.
"""

import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

# Signal metadata for human-readable output
SIGNAL_META = {
    "text_score":        {"label": "Text analysis",       "emoji": "📝", "direction": "fake"},
    "image_score":       {"label": "Image forensics",     "emoji": "🖼️", "direction": "fake"},
    "video_score":       {"label": "Video analysis",      "emoji": "🎥", "direction": "fake"},
    "fact_score":        {"label": "Fact check",          "emoji": "🔍", "direction": "fake"},
    "image_reused":      {"label": "Image reuse",         "emoji": "🔄", "direction": "fake"},
    "caption_mismatch":  {"label": "Caption mismatch",    "emoji": "⚠️", "direction": "fake"},
    "web_contradicts":   {"label": "Web contradiction",   "emoji": "🌐", "direction": "fake"},
}

SIGNAL_ORDER = list(SIGNAL_META.keys())


# ─────────────────────────────────────────────────────────────────────────
# Level 1: Signal Attribution (Permutation Importance)
# ─────────────────────────────────────────────────────────────────────────
def compute_signal_attribution(
    signals:       dict,
    fusion_engine,
    n_permutations: int = 10,
) -> dict:
    """
    SHAP-inspired permutation importance.

    For each signal s:
      1. Record baseline prediction with all signals
      2. Zero out signal s (set to 0.5 = neutral)
      3. Measure change in fake_probability
      4. Δ = baseline - zeroed_prediction = signal's contribution

    Positive Δ = signal pushed toward FAKE
    Negative Δ = signal pushed toward REAL

    Args:
        signals:       dict of signal name → float value
        fusion_engine: AttentionFusionEngine instance
        n_permutations: not used yet (single ablation for speed)

    Returns:
        {
            "attributions":    dict of signal → Δ contribution,
            "baseline_prob":   float,
            "top_signals":     list of (signal, contribution) sorted by |Δ|,
            "explanation_fragments": list of strings
        }
    """
    # Build full feature vector
    sig_vec = _signals_to_vector(signals)
    baseline = fusion_engine.predict(**signals, extract_attention=False)
    baseline_prob = baseline["fake_probability"]

    attributions = {}

    for i, signal_name in enumerate(SIGNAL_ORDER):
        # Zero out this signal (set to neutral 0.0)
        ablated = sig_vec.copy()
        ablated[i] = 0.0

        ablated_signals = _vector_to_signals(ablated)
        ablated_result  = fusion_engine.predict(**ablated_signals, extract_attention=False)
        ablated_prob    = ablated_result["fake_probability"]

        delta = baseline_prob - ablated_prob
        attributions[signal_name] = round(float(delta), 4)

    # Sort by absolute contribution
    top_signals = sorted(
        attributions.items(),
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    # Build explanation fragments
    fragments = []
    for sig, delta in top_signals[:4]:
        if abs(delta) < 0.02:
            continue
        meta  = SIGNAL_META[sig]
        label = meta["label"]
        emoji = meta["emoji"]
        val   = signals.get(sig, 0)

        if delta > 0.05:
            fragments.append(
                f"{emoji} {label} contributed **+{delta*100:.0f}%** toward FAKE "
                f"(signal value: {_format_signal(sig, val)})"
            )
        elif delta < -0.05:
            fragments.append(
                f"{emoji} {label} contributed **{delta*100:.0f}%** toward REAL "
                f"(signal value: {_format_signal(sig, val)})"
            )

    return {
        "attributions":          attributions,
        "baseline_prob":         round(baseline_prob, 4),
        "top_signals":           top_signals,
        "explanation_fragments": fragments,
    }


# ─────────────────────────────────────────────────────────────────────────
# Level 2: Attention Visualisation
# ─────────────────────────────────────────────────────────────────────────
def format_attention_for_display(attention_weights: dict) -> dict:
    """
    Convert raw attention weight matrices into display-ready format.

    Returns:
        {
            "signal_importance": dict,             # per-signal importance score
            "top_attending_pairs": list[dict],     # which signals attend to which
            "matrix_block2": list[list],           # 7×7 matrix for heatmap
        }
    """
    if not attention_weights or "block2" not in attention_weights:
        return {}

    matrix = np.array(attention_weights["block2"])   # (7, 7)

    # Column sums = "how much was this signal attended to"
    col_sums    = matrix.sum(axis=0)
    importance  = col_sums / (col_sums.sum() + 1e-8)

    signal_importance = {
        SIGNAL_ORDER[i]: round(float(importance[i]), 4)
        for i in range(len(SIGNAL_ORDER))
    }

    # Find top attending pairs (signal A attends strongly to signal B)
    pairs = []
    for i in range(7):
        for j in range(7):
            if i != j:
                pairs.append({
                    "from":   SIGNAL_ORDER[i],
                    "to":     SIGNAL_ORDER[j],
                    "weight": round(float(matrix[i, j]), 4),
                })
    top_pairs = sorted(pairs, key=lambda p: p["weight"], reverse=True)[:5]

    return {
        "signal_importance":   signal_importance,
        "top_attending_pairs": top_pairs,
        "matrix_block2":       matrix.tolist(),
        "signal_labels":       [SIGNAL_META[s]["label"] for s in SIGNAL_ORDER],
    }


# ─────────────────────────────────────────────────────────────────────────
# Level 3: Natural Language Explanation
# ─────────────────────────────────────────────────────────────────────────
def generate_explanation(
    verdict:              str,
    confidence:           float,
    uncertainty:          float,
    uncertainty_level:    str,
    signals:              dict,
    contradiction_result: dict,
    attribution:          dict,
    original_context:     Optional[str] = None,
    evidence_list:        list[str]     = None,
    evidence_score:       Optional[dict] = None,
) -> dict:
    """
    Generate a complete, journalist-quality natural language explanation.

    Returns:
        {
            "summary":          str,    # one-sentence verdict summary
            "headline":         str,    # bold headline for the UI
            "body":             str,    # full paragraph explanation
            "bullet_points":    list,   # key findings as bullets
            "confidence_note":  str,    # uncertainty interpretation
            "recommendation":   str,    # what the user should do next
        }
    """
    if evidence_list is None:
        evidence_list = []

    verdict_upper = verdict.upper()
    is_fake       = "FAKE" in verdict_upper
    is_suspicious = "SUSPICIOUS" in verdict_upper
    is_real       = not (is_fake or is_suspicious)

    # ── Headline ──────────────────────────────────────────────────────
    if is_fake:
        headline = f"🚨 VERDICT: {verdict} ({confidence:.1f}% confidence)"
    elif is_suspicious:
        headline = f"⚠️ VERDICT: {verdict} — Requires Verification ({confidence:.1f}%)"
    else:
        headline = f"✅ VERDICT: Content Appears Legitimate ({confidence:.1f}%)"

    # ── Summary sentence ──────────────────────────────────────────────
    summary = _build_summary(verdict, confidence, signals, original_context, contradiction_result)

    # ── Bullet points ─────────────────────────────────────────────────
    bullets = []

    if signals.get("image_reused"):
        ctx = original_context or "a different event/time period"
        bullets.append(f"🔄 Image was originally published in the context of: **{ctx}**")

    if signals.get("caption_mismatch"):
        bullets.append("⚠️ Image and caption are semantically misaligned (CLIP analysis)")

    if contradiction_result:
        for finding in contradiction_result.get("findings", [])[:3]:
            desc    = finding.get("description", "")
            claimed = finding.get("claimed")
            actual  = finding.get("actual")
            if desc:
                detail = f" (claimed: {claimed} | actual: {actual})" if claimed and actual else ""
                bullets.append(f"🔍 {desc}{detail}")

    if signals.get("web_contradicts") and evidence_list:
        n = len([e for e in evidence_list if any(
            kw in e.lower() for kw in ["false", "fake", "misleading", "debunked"]
        )])
        if n > 0:
            bullets.append(f"🌐 {n} web source(s) directly contradict the claim")

    if signals.get("image_score", 0) > 0.5:
        bullets.append(f"🖼️ Image forensics detected possible digital manipulation "
                       f"({signals['image_score']*100:.0f}% manipulation score)")

    top_signals = attribution.get("top_signals", [])[:2]
    for sig, delta in top_signals:
        if abs(delta) > 0.08:
            meta  = SIGNAL_META.get(sig, {})
            label = meta.get("label", sig)
            direction = "toward FAKE" if delta > 0 else "toward REAL"
            bullets.append(f"📊 {label} was the strongest driver ({abs(delta)*100:.0f}% {direction})")

    # ── Confidence note ───────────────────────────────────────────────
    conf_note = _confidence_note(confidence, uncertainty, uncertainty_level)

    # ── Recommendation ────────────────────────────────────────────────
    recommendation = _recommendation(verdict, confidence, uncertainty_level, signals)

    # ── Full body paragraph ───────────────────────────────────────────
    body_parts = [summary]
    if bullets:
        body_parts.append("Key findings: " + "; ".join(
            b.replace("**", "").replace("🔄 ", "").replace("⚠️ ", "")
             .replace("🔍 ", "").replace("🌐 ", "").replace("🖼️ ", "")
             .replace("📊 ", "")
            for b in bullets[:3]
        ) + ".")
    body_parts.append(conf_note)

    return {
        "headline":         headline,
        "summary":          summary,
        "body":             " ".join(body_parts),
        "bullet_points":    bullets,
        "confidence_note":  conf_note,
        "recommendation":   recommendation,
    }


# ─────────────────────────────────────────────────────────────────────────
# Full XAI pipeline
# ─────────────────────────────────────────────────────────────────────────
def run_xai_pipeline(
    fusion_result:        dict,
    signals:              dict,
    contradiction_result: dict         = None,
    original_context:     Optional[str] = None,
    evidence_list:        list[str]    = None,
    evidence_score:       Optional[dict] = None,
    fusion_engine=None,
) -> dict:
    """
    Run all three XAI levels and return combined explanation.

    Args:
        fusion_result:        output from AttentionFusionEngine.predict()
        signals:              raw input signals dict
        contradiction_result: from contradiction_scorer
        original_context:     from phash/reverse_search
        evidence_list:        from web_verify
        evidence_score:       from evidence_scorer
        fusion_engine:        AttentionFusionEngine instance (for attribution)
    """
    # Level 2: format attention
    attention_display = format_attention_for_display(
        fusion_result.get("attention_weights", {})
    )

    # Level 1: attribution (requires fusion engine)
    attribution = {"attributions": {}, "top_signals": [], "explanation_fragments": []}
    if fusion_engine and signals:
        try:
            attribution = compute_signal_attribution(signals, fusion_engine)
        except Exception as e:
            logger.warning("Attribution computation failed: %s", e)

    # Level 3: natural language
    explanation = generate_explanation(
        verdict=              fusion_result.get("verdict", "UNKNOWN"),
        confidence=           fusion_result.get("confidence", 0),
        uncertainty=          fusion_result.get("uncertainty", 0),
        uncertainty_level=    fusion_result.get("uncertainty_level", "MEDIUM"),
        signals=              signals or {},
        contradiction_result= contradiction_result or {},
        attribution=          attribution,
        original_context=     original_context,
        evidence_list=        evidence_list or [],
        evidence_score=       evidence_score,
    )

    return {
        "level1_attribution":  attribution,
        "level2_attention":    attention_display,
        "level3_explanation":  explanation,
        "signal_importance":   fusion_result.get("signal_importance", {}),
        "review_recommended":  fusion_result.get("review_recommended", False),
        "uncertainty_level":   fusion_result.get("uncertainty_level", "MEDIUM"),
    }


# ─────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────
def _signals_to_vector(signals: dict) -> np.ndarray:
    return np.array([
        float(signals.get("text_score",       0)),
        float(signals.get("image_score",      0)),
        float(signals.get("video_score",      0)),
        float(signals.get("fact_score",       0)),
        float(signals.get("image_reused",     False)),
        float(signals.get("caption_mismatch", False)),
        float(signals.get("web_contradicts",  False)),
    ], dtype=np.float32)


def _vector_to_signals(vec: np.ndarray) -> dict:
    return {
        "text_score":       float(vec[0]),
        "image_score":      float(vec[1]),
        "video_score":      float(vec[2]),
        "fact_score":       float(vec[3]),
        "image_reused":     bool(vec[4] > 0.5),
        "caption_mismatch": bool(vec[5] > 0.5),
        "web_contradicts":  bool(vec[6] > 0.5),
    }


def _format_signal(signal_name: str, value) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return f"{float(value)*100:.0f}%"


def _build_summary(verdict, confidence, signals, original_context, contradiction) -> str:
    parts = []
    if "FAKE" in verdict.upper():
        parts.append(f"This content has been assessed as FAKE with {confidence:.1f}% confidence.")
        if original_context:
            parts.append(f"The image originates from {original_context}.")
        if contradiction and contradiction.get("findings"):
            parts.append(f"The system detected {len(contradiction['findings'])} contradiction(s) "
                         f"between the image origin and the caption claims.")
    elif "SUSPICIOUS" in verdict.upper():
        parts.append(f"This content is SUSPICIOUS and could not be verified ({confidence:.1f}% confidence).")
        parts.append("Manual verification is recommended before sharing.")
    else:
        parts.append(f"No significant threat signals detected ({confidence:.1f}% confidence).")
        parts.append("Content appears to be legitimate.")
    return " ".join(parts)


def _confidence_note(confidence, uncertainty, uncertainty_level) -> str:
    notes = {
        "LOW":    f"The model is highly certain of this assessment (uncertainty: {uncertainty:.3f}). "
                  f"Signals are consistent across all modalities.",
        "MEDIUM": f"Moderate uncertainty detected (uncertainty: {uncertainty:.3f}). "
                  f"Some signals may be ambiguous. Consider additional verification.",
        "HIGH":   f"High uncertainty in this assessment (uncertainty: {uncertainty:.3f}). "
                  f"Modalities may be conflicting. Human review is strongly recommended.",
    }
    return notes.get(uncertainty_level, "")


def _recommendation(verdict, confidence, uncertainty_level, signals) -> str:
    if "FAKE" in verdict.upper() and confidence > 80:
        return ("Do not share this content. Report it to the platform. "
                "If you are a journalist, contact the original source for verification.")
    if "FAKE" in verdict.upper():
        return "Treat this content with high suspicion. Verify through independent sources before sharing."
    if "SUSPICIOUS" in verdict.upper() or uncertainty_level == "HIGH":
        return ("Verify this content through at least 2 independent credible sources "
                "before sharing or reporting on it.")
    return "Content appears legitimate, but always verify important claims through primary sources."
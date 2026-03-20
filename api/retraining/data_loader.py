# ============================================================
# ENTERPRISE RETRAINING DATA LOADER
# Extracts and prepares dataset for model retraining
# ============================================================

from sqlalchemy.orm import Session
from sqlalchemy import func
from api.database.models import Scan, Feedback
import logging
import random

logger = logging.getLogger("CyberThreatAI.Retraining")


MIN_CONFIDENCE_THRESHOLD = 0.60
MAX_SAMPLES = 5000


def get_misclassified_samples(db: Session):
    """
    Extract samples where prediction != user feedback.
    Applies filtering, balancing and confidence thresholding.
    """

    logger.info("🔍 Extracting misclassified samples from database...")

    query = (
        db.query(Scan, Feedback)
        .join(Feedback, Scan.id == Feedback.scan_id)
        .filter(Scan.verdict != Feedback.correct_label)
        .filter(Scan.confidence >= MIN_CONFIDENCE_THRESHOLD)
        .order_by(Scan.created_at.desc())
    )

    results = query.limit(MAX_SAMPLES).all()

    dataset = []

    for scan, feedback in results:

        # Skip if no stored input
        if not hasattr(scan, "input_length"):
            continue

        if scan.input_length is None:
            continue

        # You must store raw text in Scan model for true retraining
        if not hasattr(scan, "raw_text"):
            continue

        if scan.raw_text is None:
            continue

        dataset.append({
            "text": scan.raw_text,
            "original_prediction": scan.verdict,
            "correct_label": feedback.correct_label,
            "confidence": scan.confidence
        })

    logger.info(f"✅ Retrieved {len(dataset)} retraining samples")

    return balance_dataset(dataset)


def balance_dataset(dataset):
    """
    Balances dataset between classes to prevent bias.
    """

    fake_samples = [d for d in dataset if d["correct_label"] == "fake"]
    real_samples = [d for d in dataset if d["correct_label"] == "real"]

    if not fake_samples or not real_samples:
        logger.warning("⚠️ Imbalanced dataset detected.")
        return dataset

    min_count = min(len(fake_samples), len(real_samples))

    balanced = (
        random.sample(fake_samples, min_count) +
        random.sample(real_samples, min_count)
    )

    random.shuffle(balanced)

    logger.info(f"⚖️ Balanced dataset size: {len(balanced)}")

    return balanced


def compute_feedback_statistics(db: Session):
    """
    Useful for monitoring retraining need.
    """

    total_scans = db.query(func.count(Scan.id)).scalar()
    total_feedback = db.query(func.count(Feedback.id)).scalar()

    return {
        "total_scans": total_scans,
        "total_feedback": total_feedback,
        "feedback_ratio": round(total_feedback / total_scans, 3) if total_scans else 0
    }
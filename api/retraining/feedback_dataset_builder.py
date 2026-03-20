import pandas as pd
import os
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from api.database.db import SessionLocal
from api.database.models import Scan, Feedback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ContinualLearningBuilder")

# ==============================
# CYBER THREAT LABEL TAXONOMY
# ==============================

LABEL_MAP = {
    "fake": "fake_news",
    "fake_news": "fake_news",
    "scam": "scam",
    "phishing": "phishing",
    "propaganda": "propaganda",
    "real": "legitimate",
    "genuine": "legitimate"
}

# ==============================
# TEXT VALIDATION
# ==============================

def validate_text(text):
    if not text:
        return False
    if len(text) < 20:
        return False
    return True

# ==============================
# LOAD FEEDBACK + SCANS
# ==============================

def load_feedback_dataset(db: Session):

    query = (
        db.query(
            Feedback.correct_label,
            Feedback.feedback_weight,
            Scan.raw_input,
            Scan.verdict,
            Scan.created_at
        )
        .join(Scan, Scan.id == Feedback.scan_id)
        .filter(Scan.content_type == "text")
        .filter(Scan.raw_input != None)
    )

    df = pd.read_sql(query.statement, db.bind)

    logger.info(f"Loaded feedback samples: {len(df)}")

    return df

# ==============================
# NORMALIZE LABELS
# ==============================

def normalize_labels(df):

    df["label"] = df["correct_label"].str.lower().map(LABEL_MAP)
    df = df.dropna(subset=["label"])

    logger.info(f"After label normalization: {len(df)}")

    return df

# ==============================
# CLEAN DATASET
# ==============================

def clean_dataset(df):

    df["text"] = df["raw_input"]

    df = df[df["text"].apply(validate_text)]

    df = df.drop_duplicates(subset=["text"])

    logger.info(f"After cleaning dataset: {len(df)}")

    return df

# ==============================
# CLASS BALANCING
# ==============================

def balance_dataset(df, max_per_class=3000):

    balanced = []

    for label in df["label"].unique():
        subset = df[df["label"] == label]

        if len(subset) > max_per_class:
            subset = subset.sample(max_per_class)

        balanced.append(subset)

    df_balanced = pd.concat(balanced)

    logger.info(f"Balanced dataset size: {len(df_balanced)}")

    return df_balanced

# ==============================
# SAVE VERSIONED DATASET
# ==============================

def save_dataset(df):

    os.makedirs("data/continual_learning", exist_ok=True)

    version = datetime.now().strftime("%Y%m%d_%H%M")

    path = f"data/continual_learning/continual_dataset_{version}.csv"

    df[["text", "label", "feedback_weight"]].to_csv(path, index=False)

    logger.info(f"Saved dataset: {path}")

    return path

# ==============================
# MAIN PIPELINE
# ==============================

def build_continual_dataset():

    logger.info("Starting Continual Learning Dataset Builder...")

    db = SessionLocal()

    try:
        df = load_feedback_dataset(db)

        if len(df) == 0:
            logger.warning("No feedback data available.")
            return None

        df = normalize_labels(df)
        df = clean_dataset(df)
        df = balance_dataset(df)

        path = save_dataset(df)

        logger.info("Continual dataset builder completed.")

        return path

    finally:
        db.close()

# ==============================
# CLI ENTRY
# ==============================

if __name__ == "__main__":
    build_continual_dataset()
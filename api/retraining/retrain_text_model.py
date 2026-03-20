# ============================================================
# ENTERPRISE TEXT MODEL RETRAINING PIPELINE
# Includes evaluation, versioning, and safe deployment
# ============================================================

import os
import logging
import shutil
import torch
import numpy as np
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)

from api.database.db import SessionLocal
from api.retraining.data_loader import get_misclassified_samples

logger = logging.getLogger("CyberThreatAI.Retraining")

MODEL_BASE = "distilbert-base-uncased"
MODEL_REGISTRY_PATH = "./models/text_model_registry"
MIN_RETRAIN_SAMPLES = 50


# ============================================================
# METRIC FUNCTION
# ============================================================

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        predictions,
        average="weighted"
    )

    acc = accuracy_score(labels, predictions)

    return {
        "accuracy": acc,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }


# ============================================================
# VERSION MANAGEMENT
# ============================================================

def get_next_model_version():
    if not os.path.exists(MODEL_REGISTRY_PATH):
        os.makedirs(MODEL_REGISTRY_PATH)

    existing = [
        d for d in os.listdir(MODEL_REGISTRY_PATH)
        if d.startswith("v")
    ]

    if not existing:
        return "v1"

    versions = [int(v.replace("v", "")) for v in existing]
    return f"v{max(versions)+1}"


# ============================================================
# RETRAINING PIPELINE
# ============================================================

def retrain_text_model():

    logger.info("🚀 Starting advanced retraining pipeline...")

    db = SessionLocal()

    samples = get_misclassified_samples(db)

    if len(samples) < MIN_RETRAIN_SAMPLES:
        logger.warning("❌ Not enough samples for retraining.")
        return "Not enough samples"

    texts = [s["text"] for s in samples]
    labels = [1 if s["correct_label"] == "fake" else 0 for s in samples]

    dataset = Dataset.from_dict({
        "text": texts,
        "label": labels
    })

    # Train/Validation split
    dataset = dataset.train_test_split(test_size=0.2)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_BASE)

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            padding="max_length",
            truncation=True,
            max_length=256
        )

    tokenized_dataset = dataset.map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_BASE,
        num_labels=2
    )

    version = get_next_model_version()
    save_path = os.path.join(MODEL_REGISTRY_PATH, version)

    training_args = TrainingArguments(
        output_dir=save_path,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        logging_dir="./logs",
        load_best_model_at_end=True,
        metric_for_best_model="f1"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
        compute_metrics=compute_metrics
    )

    trainer.train()

    metrics = trainer.evaluate()

    logger.info(f"📊 Evaluation Metrics: {metrics}")

    trainer.save_model(save_path)
    tokenizer.save_pretrained(save_path)

    logger.info(f"✅ Model saved as {version}")

    # Optional: Promote to active model
    promote_model(save_path)

    return {
        "status": "success",
        "version": version,
        "metrics": metrics
    }


# ============================================================
# SAFE DEPLOYMENT
# ============================================================

def promote_model(new_model_path):
    """
    Safely replace active model with retrained model.
    """

    active_path = "./models/active_text_model"

    if os.path.exists(active_path):
        shutil.rmtree(active_path)

    shutil.copytree(new_model_path, active_path)

    logger.info("🔥 New model promoted to active deployment.")
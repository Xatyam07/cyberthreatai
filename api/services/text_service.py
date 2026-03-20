# api/services/text_service.py

import time
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from ai_models.text_model import TextModel
from database.models import Scan
from xai_engine.text_explainer import generate_text_explanation
from monitoring.drift_detector import DriftDetector

logger = logging.getLogger(__name__)


class TextService:
    def __init__(self):
        self.model = TextModel()
        self.drift_detector = DriftDetector(model_type="text")

    def analyze(
        self,
        text: str,
        user_id: str,
        db: Session,
        run_xai: bool = True
    ) -> Dict[str, Any]:

        start_time = time.time()

        if not text or len(text.strip()) < 5:
            raise ValueError("Text input too short")

        # -------------------
        # Model Inference
        # -------------------
        prediction, confidence, raw_scores = self.model.predict(text)

        risk_score = float(raw_scores.get("risk_score", confidence))

        # -------------------
        # Drift Detection
        # -------------------
        self.drift_detector.update_distribution(risk_score)

        # -------------------
        # Store in Database
        # -------------------
        scan = Scan(
            user_id=user_id,
            content_type="text",
            risk_score=risk_score,
            verdict=prediction,
            confidence=confidence,
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        # -------------------
        # Explainability
        # -------------------
        explanation = None
        if run_xai:
            explanation = generate_text_explanation(
                model=self.model,
                text=text
            )

        latency = round(time.time() - start_time, 3)

        result = {
            "scan_id": scan.id,
            "type": "text",
            "prediction": prediction,
            "confidence": confidence,
            "risk_score": risk_score,
            "latency_seconds": latency,
            "explanation": explanation
        }

        logger.info(f"[TEXT] ScanID={scan.id} Risk={risk_score}")

        return result
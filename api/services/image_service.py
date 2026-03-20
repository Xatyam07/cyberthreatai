# api/services/image_service.py

import time
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from ai_models.image_model import ImageModel
from database.models import Scan
from xai_engine.image_explainer import generate_image_heatmap
from monitoring.drift_detector import DriftDetector

logger = logging.getLogger(__name__)


class ImageService:
    def __init__(self):
        self.model = ImageModel()
        self.drift_detector = DriftDetector(model_type="image")

    def analyze(
        self,
        image_bytes: bytes,
        user_id: str,
        db: Session,
        run_xai: bool = True
    ) -> Dict[str, Any]:

        start_time = time.time()

        if not image_bytes:
            raise ValueError("No image provided")

        # -------------------
        # Model Inference
        # -------------------
        prediction, confidence, risk_score = self.model.predict(image_bytes)

        self.drift_detector.update_distribution(risk_score)

        # -------------------
        # Store in Database
        # -------------------
        scan = Scan(
            user_id=user_id,
            content_type="image",
            risk_score=risk_score,
            verdict=prediction,
            confidence=confidence,
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        # -------------------
        # Explainability (Grad-CAM)
        # -------------------
        heatmap = None
        if run_xai:
            heatmap = generate_image_heatmap(
                model=self.model,
                image_bytes=image_bytes
            )

        latency = round(time.time() - start_time, 3)

        result = {
            "scan_id": scan.id,
            "type": "image",
            "prediction": prediction,
            "confidence": confidence,
            "risk_score": risk_score,
            "latency_seconds": latency,
            "heatmap": heatmap
        }

        logger.info(f"[IMAGE] ScanID={scan.id} Risk={risk_score}")

        return result
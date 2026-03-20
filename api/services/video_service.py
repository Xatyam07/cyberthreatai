# api/services/video_service.py

import time
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from ai_models.video_model import VideoModel
from database.models import Scan
from monitoring.drift_detector import DriftDetector

logger = logging.getLogger(__name__)


class VideoService:
    def __init__(self):
        self.model = VideoModel()
        self.drift_detector = DriftDetector(model_type="video")

    def analyze(
        self,
        video_bytes: bytes,
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:

        start_time = time.time()

        if not video_bytes:
            raise ValueError("No video provided")

        # -------------------
        # Deepfake Detection
        # -------------------
        prediction, confidence, risk_score, frame_analysis = \
            self.model.predict(video_bytes)

        self.drift_detector.update_distribution(risk_score)

        # -------------------
        # Store in Database
        # -------------------
        scan = Scan(
            user_id=user_id,
            content_type="video",
            risk_score=risk_score,
            verdict=prediction,
            confidence=confidence,
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        latency = round(time.time() - start_time, 3)

        result = {
            "scan_id": scan.id,
            "type": "video",
            "prediction": prediction,
            "confidence": confidence,
            "risk_score": risk_score,
            "frame_level_analysis": frame_analysis,
            "latency_seconds": latency
        }

        logger.info(f"[VIDEO] ScanID={scan.id} Risk={risk_score}")

        return result
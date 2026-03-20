# api/services/fusion_service.py

import time
import logging
import torch
from typing import Dict, Any
from sqlalchemy.orm import Session

from ai_models.fusion_model import FusionNet
from database.models import Scan

logger = logging.getLogger(__name__)


class FusionService:
    def __init__(self):
        self.model = FusionNet()
        self.model.eval()

    def analyze(
        self,
        text_score: float,
        image_score: float,
        video_score: float,
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:

        start_time = time.time()

        inputs = torch.tensor(
            [[text_score, image_score, video_score]],
            dtype=torch.float32
        )

        with torch.no_grad():
            fusion_score = float(self.model(inputs).item())

        # Decision threshold
        verdict = "High Risk" if fusion_score > 0.7 else "Safe"

        # Store fusion as separate scan entry
        scan = Scan(
            user_id=user_id,
            content_type="multimodal",
            risk_score=fusion_score,
            verdict=verdict,
            confidence=fusion_score
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        latency = round(time.time() - start_time, 3)

        result = {
            "scan_id": scan.id,
            "type": "multimodal",
            "fusion_score": fusion_score,
            "verdict": verdict,
            "latency_seconds": latency
        }

        logger.info(f"[FUSION] ScanID={scan.id} Risk={fusion_score}")

        return result
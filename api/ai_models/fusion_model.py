"""
fusion_model.py — FusionNet Neural Fusion Model
================================================
Cyber Threat AI · Phase F (Critical Fix)

This file was MISSING, causing fusion_service.py to crash on import.
FusionNet takes clean float inputs from all modalities and produces
a calibrated final threat score.

Input vector (7 features):
  [text_score, image_score, video_score, fact_score,
   image_reused, caption_mismatch, web_contradicts]

Output: single float in [0, 1] — probability of being FAKE/THREAT
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model constants
# ---------------------------------------------------------------------------
INPUT_DIM      = 7      # number of input signals
HIDDEN_DIM_1   = 64
HIDDEN_DIM_2   = 32
OUTPUT_DIM     = 1
THRESHOLD      = 0.70   # confidence threshold to call FAKE
MODEL_PATH     = os.path.join(os.path.dirname(__file__), "fusion_net.pt")


# ---------------------------------------------------------------------------
# FusionNet architecture
# ---------------------------------------------------------------------------
class FusionNet(nn.Module):
    """
    Lightweight MLP that fuses multimodal threat signals.

    Architecture:
        Linear(7 → 64) → BatchNorm → ReLU → Dropout(0.3)
        Linear(64 → 32) → BatchNorm → ReLU → Dropout(0.2)
        Linear(32 → 1) → Sigmoid

    Uses BatchNorm for training stability and Dropout to prevent
    over-fitting on small feedback datasets.
    """

    def __init__(self, input_dim: int = INPUT_DIM):
        super(FusionNet, self).__init__()

        self.net = nn.Sequential(
            # Layer 1
            nn.Linear(input_dim, HIDDEN_DIM_1),
            nn.BatchNorm1d(HIDDEN_DIM_1),
            nn.ReLU(),
            nn.Dropout(0.3),

            # Layer 2
            nn.Linear(HIDDEN_DIM_1, HIDDEN_DIM_2),
            nn.BatchNorm1d(HIDDEN_DIM_2),
            nn.ReLU(),
            nn.Dropout(0.2),

            # Output
            nn.Linear(HIDDEN_DIM_2, OUTPUT_DIM),
            nn.Sigmoid(),
        )

        # Initialise weights with Xavier uniform for better gradient flow
        self._init_weights()

    def _init_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: FloatTensor of shape (batch_size, INPUT_DIM)
        Returns:
            FloatTensor of shape (batch_size, 1) — fake probability
        """
        return self.net(x)


# ---------------------------------------------------------------------------
# FusionEngine — wraps FusionNet with load/save + inference helpers
# ---------------------------------------------------------------------------
class FusionEngine:
    """
    High-level wrapper around FusionNet for inference.

    Usage:
        engine = FusionEngine()
        result = engine.predict(
            text_score=0.82,
            image_score=0.10,
            video_score=0.00,
            fact_score=0.15,
            image_reused=True,
            caption_mismatch=True,
            web_contradicts=True,
        )
        # → {"verdict": "FAKE", "confidence": 91.4, "fake_probability": 0.914}
    """

    def __init__(self):
        self.model = FusionNet()
        self.model.eval()
        self._load_weights_if_available()

    # ------------------------------------------------------------------
    # Weight persistence
    # ------------------------------------------------------------------
    def _load_weights_if_available(self):
        """Load saved weights if fusion_net.pt exists, else use random init."""
        if os.path.exists(MODEL_PATH):
            try:
                state = torch.load(MODEL_PATH, map_location="cpu")
                self.model.load_state_dict(state)
                logger.info("FusionNet weights loaded from %s", MODEL_PATH)
            except Exception as e:
                logger.warning("Could not load FusionNet weights: %s — using init", e)
        else:
            logger.info("No saved FusionNet weights found — using random init (will improve with feedback)")

    def save_weights(self):
        """Persist model weights after retraining."""
        torch.save(self.model.state_dict(), MODEL_PATH)
        logger.info("FusionNet weights saved to %s", MODEL_PATH)

    # ------------------------------------------------------------------
    # Feature construction
    # ------------------------------------------------------------------
    @staticmethod
    def build_feature_vector(
        text_score:        float,
        image_score:       float,
        video_score:       float,
        fact_score:        float,
        image_reused:      bool,
        caption_mismatch:  bool,
        web_contradicts:   bool,
    ) -> torch.Tensor:
        """
        Construct a normalised float tensor from raw signals.

        All boolean flags are cast to float (0.0 or 1.0).
        Scores are expected in [0, 1]; clamped for safety.
        """
        features = [
            float(np.clip(text_score,       0.0, 1.0)),
            float(np.clip(image_score,      0.0, 1.0)),
            float(np.clip(video_score,      0.0, 1.0)),
            float(np.clip(fact_score,       0.0, 1.0)),
            float(image_reused),
            float(caption_mismatch),
            float(web_contradicts),
        ]
        return torch.FloatTensor(features).unsqueeze(0)   # shape: (1, 7)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------
    def predict(
        self,
        text_score:        float = 0.0,
        image_score:       float = 0.0,
        video_score:       float = 0.0,
        fact_score:        float = 0.0,
        image_reused:      bool  = False,
        caption_mismatch:  bool  = False,
        web_contradicts:   bool  = False,
    ) -> dict:
        """
        Run inference and return structured verdict dict.

        Returns:
            {
                "verdict":          "FAKE" | "SUSPICIOUS" | "REAL",
                "confidence":       float,   # 0–100
                "fake_probability": float,   # 0–1
                "signals_used": {
                    "text_score":       float,
                    "image_score":      float,
                    "video_score":      float,
                    "fact_score":       float,
                    "image_reused":     bool,
                    "caption_mismatch": bool,
                    "web_contradicts":  bool,
                }
            }
        """
        x = self.build_feature_vector(
            text_score, image_score, video_score, fact_score,
            image_reused, caption_mismatch, web_contradicts,
        )

        with torch.no_grad():
            prob = self.model(x).item()   # scalar float in [0, 1]

        # Verdict thresholds
        if prob >= THRESHOLD:
            verdict = "FAKE"
        elif prob >= 0.45:
            verdict = "SUSPICIOUS"
        else:
            verdict = "REAL"

        return {
            "verdict":          verdict,
            "confidence":       round(prob * 100, 2),
            "fake_probability": round(prob, 4),
            "signals_used": {
                "text_score":       text_score,
                "image_score":      image_score,
                "video_score":      video_score,
                "fact_score":       fact_score,
                "image_reused":     image_reused,
                "caption_mismatch": caption_mismatch,
                "web_contradicts":  web_contradicts,
            },
        }

    # ------------------------------------------------------------------
    # Batch inference (used by retraining pipeline)
    # ------------------------------------------------------------------
    def predict_batch(self, feature_matrix: np.ndarray) -> np.ndarray:
        """
        Args:
            feature_matrix: np.ndarray of shape (N, 7)
        Returns:
            np.ndarray of shape (N,) — fake probabilities
        """
        x = torch.FloatTensor(feature_matrix)
        with torch.no_grad():
            probs = self.model(x).squeeze(1).numpy()
        return probs


# ---------------------------------------------------------------------------
# Module-level singleton — import this in fusion_service.py
# ---------------------------------------------------------------------------
_engine_instance: FusionEngine | None = None


def get_fusion_engine() -> FusionEngine:
    """Return the module-level singleton FusionEngine (lazy init)."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = FusionEngine()
    return _engine_instance
# ─────────────────────────────────────────────────────────────────────────
# fusion_engine.py — Attention-Based Neural Fusion Engine (SAFE VERSION)
# ─────────────────────────────────────────────────────────────────────────

import os
import math
import logging
import threading
from typing import Optional

import numpy as np

# SAFE TORCH IMPORT
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except Exception as e:
    print("⚠️ Torch not available:", e)
    torch = None
    nn = None
    F = None
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constants
INPUT_DIM      = 7
D_MODEL        = 32
N_HEADS        = 4
FFN_DIM        = 128
DROPOUT        = 0.20
MC_SAMPLES     = 20
FAKE_THRESHOLD = 0.68
SUSP_THRESHOLD = 0.42

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attention_fusion.pt")

SIGNAL_NAMES = [
    "text_score","image_score","video_score","fact_score",
    "image_reused","caption_mismatch","web_contradicts",
]

# ─────────────────────────────────────────────────────────────────────────
# MODEL (SAFE WRAPPED)
# ─────────────────────────────────────────────────────────────────────────
if TORCH_AVAILABLE:

    class _SinusoidalPE(nn.Module):
        def __init__(self, n: int, d: int):
            super().__init__()
            pe  = torch.zeros(n, d)
            pos = torch.arange(n).unsqueeze(1).float()
            div = torch.exp(torch.arange(0, d, 2).float() * (-math.log(10000.0) / d))
            pe[:, 0::2] = torch.sin(pos * div)
            pe[:, 1::2] = torch.cos(pos * div)
            self.register_buffer("pe", pe.unsqueeze(0))

        def forward(self, x):
            return x + self.pe[:, :x.size(1)]

    class _Block(nn.Module):
        def __init__(self, d, heads, ffn, drop):
            super().__init__()
            self.attn  = nn.MultiheadAttention(d, heads, dropout=drop, batch_first=True)
            self.norm1 = nn.LayerNorm(d)
            self.norm2 = nn.LayerNorm(d)
            self.ffn   = nn.Sequential(
                nn.Linear(d, ffn), nn.GELU(), nn.Dropout(drop),
                nn.Linear(ffn, d), nn.Dropout(drop),
            )

        def forward(self, x):
            a, w = self.attn(x, x, x)
            x    = self.norm1(x + a)
            x    = self.norm2(x + self.ffn(x))
            return x, w

    class AttentionFusionNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.embed   = nn.Linear(1, D_MODEL)
            self.pe      = _SinusoidalPE(INPUT_DIM, D_MODEL)
            self.block1  = _Block(D_MODEL, N_HEADS, FFN_DIM, DROPOUT)
            self.block2  = _Block(D_MODEL, N_HEADS, FFN_DIM, DROPOUT)
            self.head    = nn.Sequential(
                nn.Linear(D_MODEL, 16), nn.GELU(),
                nn.Dropout(DROPOUT),
                nn.Linear(16, 1),
            )
            self.temperature = nn.Parameter(torch.ones(1))

        def forward(self, x, return_attn=False):
            x = x.unsqueeze(-1)
            x = self.embed(x)
            x = self.pe(x)
            x, a1 = self.block1(x)
            x, a2 = self.block2(x)
            x     = x.mean(dim=1)
            logit = self.head(x) / self.temperature.clamp(min=0.1)

            if return_attn:
                return logit, {"block1": a1, "block2": a2}
            return logit


# ─────────────────────────────────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────────────────────────────────
class AttentionFusionEngine:

    def __init__(self):
        if not TORCH_AVAILABLE:
            print("⚠️ Fusion Engine fallback mode (no torch)")
            self.model = None
            return

        self._lock  = threading.Lock()
        self.model  = AttentionFusionNet()
        self.model.eval()
        self._load_weights()

    def _load_weights(self):
        if not TORCH_AVAILABLE:
            return
        if os.path.exists(MODEL_PATH):
            try:
                state = torch.load(MODEL_PATH, map_location="cpu")
                self.model.load_state_dict(state)
            except Exception as e:
                logger.warning("Weight load failed (%s)", e)

    @staticmethod
    def build_features(**kwargs):
        v = [
            float(kwargs.get("text_score",0)),
            float(kwargs.get("image_score",0)),
            float(kwargs.get("video_score",0)),
            float(kwargs.get("fact_score",0)),
            float(kwargs.get("image_reused",0)),
            float(kwargs.get("caption_mismatch",0)),
            float(kwargs.get("web_contradicts",0)),
        ]
        if not TORCH_AVAILABLE:
            return v
        return torch.FloatTensor(v).unsqueeze(0)

    def _mc_predict(self, x):
        if not TORCH_AVAILABLE:
            return 0.5, 0.5

        self.model.train()
        samples = []
        with torch.no_grad():
            for _ in range(MC_SAMPLES):
                samples.append(torch.sigmoid(self.model(x)).item())
        self.model.eval()
        return float(np.mean(samples)), float(np.std(samples))

    def _get_attention(self, x):
        if not TORCH_AVAILABLE:
            return {}
        with torch.no_grad():
            _, attn = self.model(x, return_attn=True)
        return {k: v.squeeze(0).cpu().numpy().tolist() for k,v in attn.items()}

    def predict(self, **kwargs):

        # 🔥 SAFE FALLBACK
        if not TORCH_AVAILABLE or self.model is None:
            avg = float(np.mean([
                kwargs.get("text_score",0),
                kwargs.get("image_score",0),
                kwargs.get("video_score",0),
                kwargs.get("fact_score",0),
            ]))
            return {
                "verdict":"SUSPICIOUS",
                "confidence":round(avg*100,2),
                "fake_probability":round(avg,4),
                "uncertainty":0.5,
                "uncertainty_level":"HIGH",
                "verdict_detail":"Fallback mode",
                "disagreement":{},
                "attention_weights":{},
                "signal_importance":{},
                "signals_used":kwargs,
                "review_recommended":True
            }

        x = self.build_features(**kwargs)
        prob, unc = self._mc_predict(x)

        verdict = "FAKE" if prob >= FAKE_THRESHOLD else "SUSPICIOUS" if prob >= SUSP_THRESHOLD else "REAL"

        return {
            "verdict":verdict,
            "confidence":round(prob*100,2),
            "fake_probability":round(prob,4),
            "uncertainty":round(unc,4),
            "uncertainty_level":"LOW" if unc < 0.1 else "HIGH",
            "signals_used":kwargs,
            "review_recommended":unc > 0.2
        }


_engine: Optional[AttentionFusionEngine] = None

def get_fusion_engine():
    global _engine
    if _engine is None:
        _engine = AttentionFusionEngine()
    return _engine
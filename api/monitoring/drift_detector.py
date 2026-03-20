"""
drift_detector.py — Concept Drift Detection & Monitoring
==========================================================
Cyber Threat AI · Monitoring · MOST ADVANCED VERSION

Detects when the model's prediction distribution shifts significantly —
indicating the threat landscape has changed and retraining is needed.

Methods:
  1. Page-Hinkley Test — sequential drift detection on confidence scores
     Triggers when cumulative deviation exceeds a threshold δ.
     Gold standard for non-stationary data streams.

  2. Population Stability Index (PSI) — compares current vs reference
     distribution of predictions. PSI > 0.2 = significant drift.
     Used in financial risk models (credit scoring) for decades.

  3. Label Drift — tracks rolling fake/real ratio.
     Sudden spike in fake rate = new campaign or model degradation.

Outputs:
  • Drift severity: NONE / MINOR / SIGNIFICANT / CRITICAL
  • Recommendation: MONITOR / RETRAIN_SOON / RETRAIN_NOW
  • Detailed statistics for the analytics dashboard
"""

import os
import json
import logging
import threading
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DRIFT_LOG  = os.path.join(BASE_DIR, "data", "drift_log.json")

PH_DELTA   = 0.005    # Page-Hinkley sensitivity (lower = more sensitive)
PH_LAMBDA  = 50       # Page-Hinkley threshold for alarm
PSI_MINOR  = 0.10     # PSI threshold for minor drift
PSI_MAJOR  = 0.20     # PSI threshold for major drift
WINDOW_SIZE = 500     # rolling window for statistics


# ─────────────────────────────────────────────────────────────────────────
# Dataclasses
# ─────────────────────────────────────────────────────────────────────────
@dataclass
class DriftEvent:
    method:      str
    severity:    str          # MINOR / SIGNIFICANT / CRITICAL
    statistic:   float
    threshold:   float
    timestamp:   str
    details:     dict = field(default_factory=dict)


@dataclass
class DriftReport:
    overall_severity:  str
    recommendation:    str
    ph_alarm:          bool
    psi_value:         float
    fake_rate_current: float
    fake_rate_baseline:float
    events:            list[DriftEvent]
    window_size:       int
    generated_at:      str


# ─────────────────────────────────────────────────────────────────────────
# Drift Detector
# ─────────────────────────────────────────────────────────────────────────
class DriftDetector:
    """
    Monitors model predictions for concept drift using three methods.
    Thread-safe — safe to call from FastAPI request handlers.
    """

    def __init__(self):
        self._lock           = threading.Lock()
        self._window         = deque(maxlen=WINDOW_SIZE)   # recent confidence scores
        self._labels         = deque(maxlen=WINDOW_SIZE)   # recent labels (fake=1, real=0)
        self._reference_dist = None   # set after first WINDOW_SIZE observations
        self._ph_cumsum      = 0.0    # Page-Hinkley cumulative sum
        self._ph_min         = float("inf")
        self._ph_alarm       = False
        self._events:        list[DriftEvent] = []
        self._load_state()

    # ── Persistence ───────────────────────────────────────────────────
    def _load_state(self):
        if os.path.exists(DRIFT_LOG):
            try:
                with open(DRIFT_LOG) as f:
                    state = json.load(f)
                scores = state.get("recent_scores", [])
                labels = state.get("recent_labels", [])
                self._window.extend(scores[-WINDOW_SIZE:])
                self._labels.extend(labels[-WINDOW_SIZE:])
                self._reference_dist = state.get("reference_dist")
                logger.info("Drift detector state loaded (%d observations)", len(self._window))
            except Exception as e:
                logger.warning("Drift state load failed: %s", e)

    def _save_state(self):
        os.makedirs(os.path.dirname(DRIFT_LOG), exist_ok=True)
        state = {
            "recent_scores":   list(self._window),
            "recent_labels":   list(self._labels),
            "reference_dist":  self._reference_dist,
            "updated_at":      datetime.now(timezone.utc).isoformat(),
        }
        try:
            with open(DRIFT_LOG, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error("Drift state save failed: %s", e)

    # ── Observation ingestion ─────────────────────────────────────────
    def record(self, fake_probability: float, verdict: str):
        """
        Record a new model output. Call this after every /verify prediction.

        Args:
            fake_probability: float in [0, 1]
            verdict:          "FAKE" | "SUSPICIOUS" | "REAL"
        """
        label = 1 if "FAKE" in verdict.upper() else 0

        with self._lock:
            self._window.append(fake_probability)
            self._labels.append(label)
            self._page_hinkley_update(fake_probability)

            # Set reference distribution after first full window
            if self._reference_dist is None and len(self._window) >= WINDOW_SIZE:
                self._reference_dist = list(self._window)
                logger.info("Drift reference distribution set (%d observations)", WINDOW_SIZE)

            # Periodic save (every 50 observations)
            if len(self._window) % 50 == 0:
                self._save_state()

    # ── Page-Hinkley Test ─────────────────────────────────────────────
    def _page_hinkley_update(self, x: float):
        """
        Page-Hinkley sequential change detection.

        Detects a persistent shift in the mean of the confidence distribution.
        Alarm when: PH_t = cumsum - min_cumsum > PH_LAMBDA
        """
        if len(self._window) < 10:
            return

        mean = np.mean(list(self._window))
        self._ph_cumsum += (x - mean - PH_DELTA)
        self._ph_min     = min(self._ph_min, self._ph_cumsum)

        ph_t = self._ph_cumsum - self._ph_min

        if ph_t > PH_LAMBDA:
            if not self._ph_alarm:
                logger.warning("Page-Hinkley ALARM: drift detected (PH=%.2f > %.0f)", ph_t, PH_LAMBDA)
                self._events.append(DriftEvent(
                    method="page_hinkley",
                    severity="SIGNIFICANT",
                    statistic=round(ph_t, 3),
                    threshold=PH_LAMBDA,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    details={"cumsum": round(self._ph_cumsum, 3), "min": round(self._ph_min, 3)},
                ))
            self._ph_alarm = True
        else:
            self._ph_alarm = False

    # ── Population Stability Index ────────────────────────────────────
    def _compute_psi(self) -> float:
        """
        PSI compares current distribution vs reference distribution.

        PSI = Σ (actual% - expected%) × ln(actual% / expected%)

        PSI < 0.10: no shift
        PSI 0.10–0.20: minor shift (monitor)
        PSI > 0.20: major shift (retrain)
        """
        if self._reference_dist is None or len(self._window) < 50:
            return 0.0

        bins = np.linspace(0, 1, 11)   # 10 equal-width bins

        ref_counts, _ = np.histogram(self._reference_dist, bins=bins)
        cur_counts, _ = np.histogram(list(self._window),   bins=bins)

        # Avoid division by zero — add small epsilon
        ref_pct = (ref_counts + 0.0001) / (len(self._reference_dist) + 0.001)
        cur_pct = (cur_counts + 0.0001) / (len(self._window) + 0.001)

        psi = float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))
        return round(psi, 4)

    # ── Label drift ───────────────────────────────────────────────────
    def _fake_rate(self) -> float:
        if not self._labels:
            return 0.0
        return float(np.mean(list(self._labels)))

    def _baseline_fake_rate(self) -> float:
        if not self._reference_dist or len(self._reference_dist) < 10:
            return 0.5
        # Estimate from reference distribution using 0.68 threshold
        return float(np.mean([1 if s >= 0.68 else 0 for s in self._reference_dist]))

    # ── Report generation ─────────────────────────────────────────────
    def get_report(self) -> DriftReport:
        """Generate a full drift report."""
        with self._lock:
            psi          = self._compute_psi()
            fake_rate    = self._fake_rate()
            base_rate    = self._baseline_fake_rate()
            rate_delta   = abs(fake_rate - base_rate)

        # Determine overall severity
        if self._ph_alarm or psi > PSI_MAJOR or rate_delta > 0.25:
            severity       = "CRITICAL"
            recommendation = "RETRAIN_NOW"
        elif psi > PSI_MINOR or rate_delta > 0.15:
            severity       = "SIGNIFICANT"
            recommendation = "RETRAIN_SOON"
        elif psi > 0.05 or rate_delta > 0.08:
            severity       = "MINOR"
            recommendation = "MONITOR"
        else:
            severity       = "NONE"
            recommendation = "MONITOR"

        return DriftReport(
            overall_severity=  severity,
            recommendation=    recommendation,
            ph_alarm=          self._ph_alarm,
            psi_value=         psi,
            fake_rate_current= round(fake_rate, 4),
            fake_rate_baseline=round(base_rate, 4),
            events=            list(self._events[-10:]),
            window_size=       len(self._window),
            generated_at=      datetime.now(timezone.utc).isoformat(),
        )

    def reset_reference(self):
        """Reset reference distribution (call after successful retraining)."""
        with self._lock:
            self._reference_dist = list(self._window)
            self._ph_cumsum      = 0.0
            self._ph_min         = float("inf")
            self._ph_alarm       = False
            self._events         = []
            self._save_state()
        logger.info("Drift reference distribution reset after retraining")


# ─────────────────────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────────────────────
_detector: Optional[DriftDetector] = None


def get_drift_detector() -> DriftDetector:
    global _detector
    if _detector is None:
        _detector = DriftDetector()
    return _detector


def record_prediction(fake_probability: float, verdict: str):
    """Convenience function — call after every model prediction."""
    get_drift_detector().record(fake_probability, verdict)


def get_drift_report() -> dict:
    """Get current drift report as a dict (for API endpoint)."""
    report = get_drift_detector().get_report()
    return {
        **asdict(report),
        "events": [asdict(e) for e in report.events],
    }
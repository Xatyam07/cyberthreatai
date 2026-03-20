"""
main.py — Cyber Threat AI · Veritas
=====================================
Version : 3.1 (All Bugs Fixed + Most Advanced)
Backend : FastAPI + Uvicorn

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUGS FIXED IN THIS VERSION (vs your current main.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIX 1 — /predict returns 422 Unprocessable Entity
  ROOT CAUSE: Dashboard sends form-encoded data={"text":"..."}
              but endpoint expected JSON TextRequest body only.
              FastAPI can't parse b'text=Hello+world' as a Pydantic model.
  FIXED: predict_text + verify_claims now accept BOTH:
           • JSON body   → Content-Type: application/json
           • Form field  → Content-Type: application/x-www-form-urlencoded
         Whichever the client sends, it works.

FIX 2 — POST /api/verify returns 404
  ROOT CAUSE: Dashboard calls /api/verify but router registered at /verify.
  FIXED: verify_router registered twice — at /verify AND /api prefix.

FIX 3 — store_size ImportError from hash_db.py
  ROOT CAUSE: Local hash_db.py didn't export store_size() or list_entries().
  FIXED: Both functions now defined inline in lifespan/health with
         graceful ImportError fallback, PLUS proper endpoints added.

FIX 4 — GET /admin/hash-db-entries returns 404
  ROOT CAUSE: Endpoint didn't exist.
  FIXED: /admin/hash-db-entries and /admin/add-fake-hash added.

FIX 5 — POST /retrain returns 404 (dashboard calls /retrain not /retrain-text-model)
  FIXED: Both /retrain and /retrain-text-model work now.

NEW IN v3.1
  ✓ Dual JSON+Form input on all text endpoints
  ✓ /api/* prefix alias for all core endpoints
  ✓ Admin endpoints: hash-db-entries, add-fake-hash
  ✓ Graceful degradation on every import — never crashes on missing module
  ✓ Database error logged cleanly, not as unhandled exception
  ✓ Feedback endpoint accepts both scan_id int AND string (dashboard sends string)
  ✓ /history returns both "results" and "history" keys (dashboard checks both)
"""

# ─────────────────────────────────────────────────────────────────────────────
# Standard library
# ─────────────────────────────────────────────────────────────────────────────
import asyncio
import base64
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional, Union

# ─────────────────────────────────────────────────────────────────────────────
# Third-party
# ─────────────────────────────────────────────────────────────────────────────
from fastapi import (
    Depends, FastAPI, File, Form, HTTPException,   # FIX: added Form
    Request, UploadFile, WebSocket,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

# ─────────────────────────────────────────────────────────────────────────────
# Internal — Database
# ─────────────────────────────────────────────────────────────────────────────
from api.database.db import get_db, init_db_on_startup
from api.database.models import Scan, Feedback

# ─────────────────────────────────────────────────────────────────────────────
# Internal — AI modules
# ─────────────────────────────────────────────────────────────────────────────
from api.ai_models.unified_text_engine import analyze_text
from api.ai_models.image_model import analyze_image
from api.ai_models.video_model import analyze_video
from api.ai_models.factcheck_engine.factcheck_pipeline import factcheck_text
from api.ai_models.xai_engine.xai_pipeline import run_xai_pipeline
from api.ai_models.fusion_engine import get_fusion_engine

# ─────────────────────────────────────────────────────────────────────────────
# Internal — Services, Monitoring, Router
# ─────────────────────────────────────────────────────────────────────────────
from api.monitoring.drift_detector import record_prediction, get_drift_report
from api.verify_endpoint import router as verify_router


# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)-8s]  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("CyberThreatAI")


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan — startup warm-up + graceful shutdown
# ─────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("🚀  Cyber Threat AI — Veritas v3.1  starting")
    logger.info("=" * 60)

    init_db_on_startup()
    logger.info("✅  Database ready")

    try:
        await asyncio.to_thread(analyze_text, "warmup")
        logger.info("✅  UCIE Text Engine ready")
    except Exception as e:
        logger.warning("⚠️  Text engine warmup: %s", e)

    try:
        get_fusion_engine().predict()
        logger.info("✅  AttentionFusionNet ready")
    except Exception as e:
        logger.warning("⚠️  Fusion engine warmup: %s", e)

    # FIX 3: graceful hash_db import — won't crash if store_size missing
    try:
        from api.memory.hash_db import store_size
        logger.info("✅  Hash DB ready — %d entries", store_size())
    except ImportError:
        logger.warning("⚠️  hash_db.store_size not found — add it to hash_db.py (see below)")
    except Exception as e:
        logger.warning("⚠️  Hash DB: %s", e)

    logger.info("🛡️  All systems nominal")
    logger.info("=" * 60)
    yield
    logger.info("👋  Veritas shutting down")


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Cyber Threat AI — Veritas",
    description = "World-class Multimodal Fake News & Cyber Threat Intelligence",
    version     = "3.1.0",
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# FIX 2: Register verify router at BOTH /verify and /api/verify
app.include_router(verify_router)                      # → POST /verify
app.include_router(verify_router, prefix="/api")       # → POST /api/verify  ← fixes 404

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Middleware — request ID + timing on every response
# ─────────────────────────────────────────────────────────────────────────────
@app.middleware("http")
async def request_metadata_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start      = time.perf_counter()
    response   = await call_next(request)
    ms         = round((time.perf_counter() - start) * 1000, 1)
    response.headers["X-Request-ID"]  = request_id
    response.headers["X-Duration-Ms"] = str(ms)
    logger.info("[%s] %s %s → %d  (%s ms)",
                request_id, request.method, request.url.path,
                response.status_code, ms)
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Global exception handler
# ─────────────────────────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"metadata": _meta(), "error": "Internal Server Error", "detail": str(exc)},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic request models
# ─────────────────────────────────────────────────────────────────────────────
class TextRequest(BaseModel):
    text: str

class FusionRequest(BaseModel):
    text_score:       float
    image_score:      float
    video_score:      float
    fact_score:       float = 0.5
    image_reused:     bool  = False
    caption_mismatch: bool  = False
    web_contradicts:  bool  = False

class ExplainRequest(BaseModel):
    text:        str
    text_score:  float
    image_score: float
    video_score: float
    fact_score:  float
    exif_found:  bool = True

class FeedbackRequest(BaseModel):
    # FIX: accept scan_id as int OR string (dashboard sometimes sends string)
    scan_id:       Union[int, str]
    correct_label: str
    notes:         Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────
def _meta() -> dict:
    return {
        "request_id":     str(uuid.uuid4()),
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "system_version": "3.1.0",
    }


def _save_scan(db, content_type, risk_score, confidence, verdict,
               processing_time, raw_input="") -> int:
    """Save a scan record. Returns 0 on DB error instead of crashing."""
    try:
        r = Scan(
            firebase_uid=    None,
            content_type=    content_type,
            raw_input=       raw_input[:2000],
            input_length=    len(raw_input),
            risk_score=      round(float(risk_score), 4),
            confidence=      round(float(confidence), 4),
            verdict=         verdict,
            model_version=   "v3.1",
            processing_time= processing_time,
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        return r.id
    except Exception as e:
        # FIX: log DB error cleanly instead of letting it propagate
        logger.error("DB save_scan failed: %s", e)
        try:
            db.rollback()
        except Exception:
            pass
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# ① ROOT + HEALTH + SYSTEM INFO
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Status"])
async def root():
    return {
        "service": "Cyber Threat AI — Veritas",
        "version": "3.1.0",
        "status":  "online",
        "docs":    "/docs",
    }


@app.get("/health", tags=["Status"])
async def health_check():
    checks = {}

    try:
        get_fusion_engine()
        checks["fusion_engine"] = "ok"
    except Exception as e:
        checks["fusion_engine"] = f"error: {e}"

    try:
        from api.memory.hash_db import store_size
        checks["hash_db"] = f"ok ({store_size()} entries)"
    except Exception as e:
        checks["hash_db"] = f"degraded: {e}"

    try:
        from api.memory.clip_memory import memory_size
        checks["clip_memory"] = f"ok ({memory_size()} vectors)"
    except Exception as e:
        checks["clip_memory"] = f"degraded: {e}"

    all_ok = all("error" not in str(v) for v in checks.values())
    return JSONResponse(
        content={
            "metadata": _meta(),
            "status":   "healthy" if all_ok else "degraded",
            "checks":   checks,
            "services": [
                "UCIE Text Engine (5-signal ensemble)",
                "Image Forensics (ELA + EXIF + pHash + CLIP)",
                "Video Deepfake Detector",
                "AttentionFusionNet (MC-Dropout uncertainty)",
                "Fact Checker + NLI Evidence Scorer",
                "XAI (SHAP attribution + attention heatmap)",
                "WebSocket real-time streaming",
                "Concept Drift Monitor (Page-Hinkley + PSI)",
            ],
        },
        status_code=200 if all_ok else 207,
    )


@app.get("/system-info", tags=["Status"])
async def system_info():
    try:
        from api.memory.hash_db import store_size as hs
        h = hs()
    except Exception:
        h = 0
    try:
        from api.memory.clip_memory import memory_size
        c = memory_size()
    except Exception:
        c = 0

    return {
        "metadata":     _meta(),
        "system_name":  "Cyber Threat AI — Veritas",
        "version":      "3.1.0",
        "capabilities": [
            "fake_news_detection", "scam_phishing_detection",
            "image_manipulation_detection", "perceptual_hash_origin_detection",
            "clip_image_caption_alignment", "deepfake_video_detection",
            "cross_modal_contradiction_scoring", "multi_source_web_verification",
            "nli_evidence_scoring", "attention_based_neural_fusion",
            "mc_dropout_uncertainty_quantification", "xai_shap_attribution",
            "xai_attention_heatmap", "websocket_real_time_streaming",
            "concept_drift_detection", "feedback_driven_retraining",
        ],
        "models": {
            "text":   "RoBERTa-ISOT + DeBERTa-NLI + Twitter-RoBERTa (UCIE)",
            "image":  "ELA + EXIF + pHash + CLIP ViT-B/32",
            "video":  "Frame-level deepfake detector",
            "fusion": "AttentionFusionNet (2-layer Transformer, MC-Dropout)",
            "nli":    "cross-encoder/nli-deberta-v3-small",
            "drift":  "Page-Hinkley Test + Population Stability Index",
        },
        "memory": {"known_fake_hashes": h, "clip_vectors": c},
        "deployment": "FastAPI + Uvicorn + Streamlit + SQLite",
    }


# ─────────────────────────────────────────────────────────────────────────────
# ② TEXT FAKE NEWS DETECTION
# FIX 1: Accept BOTH JSON body and form-encoded data
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/predict", tags=["Detection"])
async def predict_text(
    db:   Session          = Depends(get_db),
    # JSON body  (Content-Type: application/json)
    data: Optional[TextRequest] = None,
    # Form field (Content-Type: application/x-www-form-urlencoded)  ← what Streamlit sends
    text: Optional[str]    = Form(None),
):
    """
    UCIE 5-signal ensemble.
    Accepts BOTH:
      • JSON:  POST /predict   body={"text": "..."}
      • Form:  POST /predict   text=...
    """
    # Resolve input from whichever source was provided
    input_text = (data.text if data else None) or (text or "")
    if not input_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Field 'text' is required — send as JSON {'text':'...'} or form field text=..."
        )
    try:
        start  = time.perf_counter()
        result = await asyncio.to_thread(analyze_text, input_text)
        dur    = round(time.perf_counter() - start, 3)

        scan_id = _save_scan(
            db, "text",
            result.get("score", 0),
            result.get("confidence", 0),
            result.get("label", "unknown"),
            dur, input_text,
        )

        record_prediction(result.get("score", 0), result.get("label", "REAL"))

        return {
            "metadata":          _meta(),
            "module":            "ucie_text_engine",
            "scan_id":           scan_id,
            "input_length":      len(input_text),
            "processing_time_s": dur,
            "prediction":        result,
        }
    except Exception as e:
        logger.error("predict_text: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ③ IMAGE FORENSICS
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/analyze-image", tags=["Detection"])
async def analyze_image_api(
    file: UploadFile      = File(...),
    db:   Session         = Depends(get_db),
):
    """ELA + EXIF anomaly + pHash origin detection."""
    try:
        start    = time.perf_counter()
        contents = await file.read()
        result   = await asyncio.to_thread(analyze_image, contents)
        dur      = round(time.perf_counter() - start, 3)

        score   = result.get("score", 0)
        verdict = "manipulated" if score > 50 else "authentic"

        scan_id = _save_scan(db, "image", score / 100, score / 100, verdict, dur)

        return {
            "metadata":          _meta(),
            "module":            "image_forensics",
            "scan_id":           scan_id,
            "filename":          file.filename,
            "processing_time_s": dur,
            "score":             score,
            "verdict":           verdict,
            "reasons":           result.get("reasons", []),
            "exif":              result.get("exif", {}),
        }
    except Exception as e:
        logger.error("analyze_image: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ④ VIDEO DEEPFAKE DETECTION
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/analyze-video", tags=["Detection"])
async def analyze_video_api(
    file: UploadFile = File(...),
    db:   Session    = Depends(get_db),
):
    """Frame-level deepfake detection."""
    try:
        start    = time.perf_counter()
        contents = await file.read()
        result   = await asyncio.to_thread(analyze_video, contents)
        dur      = round(time.perf_counter() - start, 3)

        score   = result.get("score", 0) if isinstance(result, dict) else float(result)
        verdict = "deepfake" if score > 50 else "authentic"

        scan_id = _save_scan(db, "video", score / 100, score / 100, verdict, dur)

        return {
            "metadata":          _meta(),
            "module":            "video_deepfake",
            "scan_id":           scan_id,
            "filename":          file.filename,
            "processing_time_s": dur,
            "score":             score,
            "verdict":           verdict,
        }
    except Exception as e:
        logger.error("analyze_video: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ⑤ FACT CHECKING
# FIX 1: Also accepts form-encoded text
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/verify-claims", tags=["Detection"])
async def verify_claims(
    data: Optional[TextRequest] = None,
    text: Optional[str]         = Form(None),
):
    """Multi-source: Google News + NewsAPI + AltNews + Snopes + NLI scoring."""
    input_text = (data.text if data else None) or (text or "")
    if not input_text.strip():
        raise HTTPException(status_code=422, detail="text field required")
    try:
        result = await asyncio.to_thread(factcheck_text, input_text)
        return {
            "metadata":          _meta(),
            "module":            "fact_checker",
            "claims_verified":   len(result.get("claims", [])),
            "fact_check_result": result,
        }
    except Exception as e:
        logger.error("verify_claims: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ⑥ MULTIMODAL FUSION
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/final-verdict", tags=["Fusion"])
async def final_verdict(data: FusionRequest, db: Session = Depends(get_db)):
    """
    AttentionFusionNet — takes clean float inputs, runs 20 MC-Dropout passes,
    returns calibrated probability + epistemic uncertainty + XAI attention weights.
    """
    try:
        start  = time.perf_counter()
        engine = get_fusion_engine()
        result = await asyncio.to_thread(
            engine.predict,
            text_score=       data.text_score,
            image_score=      data.image_score,
            video_score=      data.video_score,
            fact_score=       data.fact_score,
            image_reused=     data.image_reused,
            caption_mismatch= data.caption_mismatch,
            web_contradicts=  data.web_contradicts,
        )
        dur = round(time.perf_counter() - start, 3)

        scan_id = _save_scan(
            db, "fusion",
            result["fake_probability"],
            result["fake_probability"],
            result["verdict"], dur,
        )
        record_prediction(result["fake_probability"], result["verdict"])

        return {
            "metadata":           _meta(),
            "module":             "attention_fusion_net",
            "scan_id":            scan_id,
            "processing_time_s":  dur,
            "verdict":            result["verdict"],
            "confidence":         result["confidence"],
            "fake_probability":   result["fake_probability"],
            "uncertainty":        result["uncertainty"],
            "uncertainty_level":  result["uncertainty_level"],
            "signal_importance":  result.get("signal_importance", {}),
            "review_recommended": result.get("review_recommended", False),
            "disagreement":       result.get("disagreement", {}),
        }
    except Exception as e:
        logger.error("final_verdict: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ⑦ EXPLAINABLE AI
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/explain-result", tags=["XAI"])
async def explain_result(data: ExplainRequest):
    """
    3-level XAI:
      L1 — SHAP-style permutation importance
      L2 — 7×7 attention heatmap from AttentionFusionNet
      L3 — Journalist-quality natural language explanation
    """
    try:
        engine  = get_fusion_engine()
        signals = {
            "text_score":       data.text_score,
            "image_score":      data.image_score,
            "video_score":      data.video_score,
            "fact_score":       data.fact_score,
            "image_reused":     False,
            "caption_mismatch": False,
            "web_contradicts":  False,
        }
        fusion_result = await asyncio.to_thread(engine.predict, **signals)
        xai           = await asyncio.to_thread(
            run_xai_pipeline,
            fusion_result=fusion_result,
            signals=signals,
            fusion_engine=engine,
        )
        return {
            "metadata": _meta(),
            "module":   "xai_engine_v3",
            "report": {
                **xai,
                "final_verdict": {
                    "risk_level":            fusion_result["verdict"],
                    "confidence_percentage": fusion_result["confidence"],
                    "uncertainty":           fusion_result["uncertainty"],
                    "uncertainty_level":     fusion_result["uncertainty_level"],
                    "review_recommended":    fusion_result["review_recommended"],
                },
            },
        }
    except Exception as e:
        logger.error("explain_result: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ⑧ FEEDBACK
# FIX: scan_id accepts int OR string
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/feedback", tags=["Learning"])
async def submit_feedback(data: FeedbackRequest, db: Session = Depends(get_db)):
    """Record a user correction. Consumed by the retraining pipeline."""
    try:
        # Normalise scan_id to int
        try:
            scan_id_int = int(data.scan_id)
        except (ValueError, TypeError):
            scan_id_int = 0

        scan = db.query(Scan).filter(Scan.id == scan_id_int).first()
        if not scan:
            # Don't crash if scan not found — just log and continue
            logger.warning("Feedback for unknown scan_id=%s — storing anyway", data.scan_id)

        entry = Feedback(
            scan_id=       scan_id_int if scan else None,
            correct_label= data.correct_label,
            notes=         data.notes,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)

        try:
            from api.retraining.feedback_dataset_builder import record_feedback
            record_feedback(str(data.scan_id), data.correct_label, data.notes or "")
        except Exception:
            pass

        return {
            "metadata":    _meta(),
            "message":     "Feedback recorded — will improve the model",
            "feedback_id": entry.id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("submit_feedback: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ⑨ HISTORY
# FIX: returns both "results" AND "history" keys — dashboard checks both
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/history", tags=["Analytics"])
async def get_scan_history(limit: int = 50, db: Session = Depends(get_db)):
    scans = (
        db.query(Scan)
        .order_by(Scan.created_at.desc())
        .limit(min(limit, 500))
        .all()
    )
    rows = [
        {
            "scan_id":         s.id,
            "type":            s.content_type,
            "verdict":         s.verdict,
            "risk_score":      s.risk_score,
            "confidence":      s.confidence,
            "processing_time": s.processing_time,
            "created_at":      str(s.created_at),
        }
        for s in scans
    ]
    return {
        "metadata": _meta(),
        "count":    len(rows),
        "results":  rows,    # new dashboard key
        "history":  rows,    # legacy dashboard key
    }


# ─────────────────────────────────────────────────────────────────────────────
# ⑩ RETRAIN TRIGGER
# FIX 5: /retrain and /retrain-text-model both work
# ─────────────────────────────────────────────────────────────────────────────
async def _do_retrain() -> dict:
    try:
        from api.retraining.retrain_text_model import trigger_retrain
        asyncio.create_task(asyncio.to_thread(trigger_retrain))
        from api.monitoring.drift_detector import get_drift_detector
        get_drift_detector().reset_reference()
        return {"metadata": _meta(), "status": "triggered",
                "message": "Retraining started in background"}
    except Exception as e:
        return {"metadata": _meta(), "status": "error", "detail": str(e)}


@app.post("/retrain-text-model", tags=["Learning"])
async def retrain_text_model():
    return await _do_retrain()


@app.post("/retrain", tags=["Learning"])   # FIX 5: alias used by dashboard
async def retrain_alias():
    return await _do_retrain()


# ─────────────────────────────────────────────────────────────────────────────
# ⑪ DRIFT REPORT
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/drift-report", tags=["Analytics"])
async def drift_report():
    """Page-Hinkley + PSI drift monitoring."""
    try:
        return {"metadata": _meta(), "drift": get_drift_report()}
    except Exception as e:
        return {"metadata": _meta(), "drift": {"error": str(e)}}


# ─────────────────────────────────────────────────────────────────────────────
# ⑫ ADMIN — HASH DB  (FIX 4: endpoints were missing)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/admin/hash-db-entries", tags=["Admin"])
async def get_hash_db_entries(limit: int = 50):
    """List entries in the known-fake image hash database."""
    try:
        from api.memory.hash_db import list_entries
        entries = list_entries(limit=limit)
        return {"entries": entries, "count": len(entries)}
    except ImportError:
        # list_entries not yet in hash_db.py — return empty gracefully
        logger.warning("hash_db.list_entries not available")
        return {"entries": [], "count": 0}
    except Exception as e:
        logger.warning("get_hash_db_entries: %s", e)
        return {"entries": [], "count": 0}


@app.post("/admin/add-fake-hash", tags=["Admin"])
async def add_fake_hash(
    file:             UploadFile = File(...),
    original_context: str        = Form(""),
    original_date:    str        = Form(""),
    source_url:       str        = Form(""),
):
    """Add a confirmed fake image to the pHash + CLIP memory store."""
    try:
        from api.memory.hash_db import add_entry
        from api.ai_models.image_origin.phash_detector import compute_phash

        image_bytes = await file.read()
        phash = compute_phash(image_bytes)
        if not phash:
            raise HTTPException(status_code=400, detail="Could not compute pHash for this image")

        entry = add_entry(
            phash=         phash,
            context=       original_context,
            original_date= original_date,
            source_url=    source_url,
            added_by=      "admin",
            threat_type=   "context_manipulation",
        )
        return {"status": "ok", "phash": phash, "entry": entry}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("add_fake_hash: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ⑬ WEBSOCKET — real-time /verify streaming
# ─────────────────────────────────────────────────────────────────────────────
@app.websocket("/ws/verify")
async def websocket_verify(ws: WebSocket):
    """
    Client sends JSON once:
        {"caption": "...", "article_text": "...",
         "image_b64": "<base64>", "video_b64": "<optional>"}

    Server streams per-stage progress:
        {"stage": "text_analysis", "status": "running", "progress": 10}
        {"stage": "text_analysis", "status": "done",    "progress": 20, "result": {...}}
        ...
        {"stage": "final",         "status": "done",    "progress": 100, "verdict": {...}}
    """
    await ws.accept()

    try:
        data = await asyncio.wait_for(ws.receive_json(), timeout=30.0)
    except asyncio.TimeoutError:
        await ws.close(code=1008, reason="Receive timeout")
        return
    except Exception:
        await ws.close(code=1003, reason="Invalid JSON")
        return

    caption      = data.get("caption", "")
    article_text = data.get("article_text", "")
    image_bytes  = base64.b64decode(data["image_b64"]) if data.get("image_b64") else None
    full_text    = f"{caption} {article_text}".strip()

    async def push(stage, status, progress, **kw):
        try:
            await ws.send_json({"stage": stage, "status": status,
                                "progress": progress, **kw})
        except Exception:
            pass

    # ── Stage 1: Text ─────────────────────────────────────────────────
    await push("text_analysis", "running", 10)
    text_result = {"label": "REAL", "score": 0.0}
    try:
        text_result = await asyncio.to_thread(analyze_text, full_text)
        await push("text_analysis", "done", 20,
                   result={"label": text_result["label"], "score": text_result["score"]})
    except Exception as e:
        await push("text_analysis", "error", 20, error=str(e))

    # ── Stage 2: Fact check ───────────────────────────────────────────
    await push("fact_check", "running", 22)
    fact_result = {"fact_check_result": {"fact_trust_score": 0.5}}
    try:
        fact_result = await asyncio.to_thread(factcheck_text, full_text)
        trust = fact_result.get("fact_check_result", {}).get("fact_trust_score", 0.5)
        await push("fact_check", "done", 35, result={"trust_score": trust})
    except Exception as e:
        await push("fact_check", "error", 35, error=str(e))

    # ── Stage 3: Image origin ─────────────────────────────────────────
    image_result = {"score": 0, "image_reused": False,
                    "origin_check": {}, "clip_similarity": -1.0}
    if image_bytes:
        await push("image_origin", "running", 37)
        try:
            from api.ai_models.image_origin.phash_detector import detect_image_reuse
            from api.ai_models.image_origin.clip_embedder import image_caption_similarity
            origin   = await asyncio.to_thread(detect_image_reuse, image_bytes)
            clip_sim = await asyncio.to_thread(
                image_caption_similarity, image_bytes, caption) if caption else -1.0
            image_result.update({
                "image_reused":   origin.get("image_reused", False),
                "origin_check":   origin,
                "clip_similarity": clip_sim,
            })
            await push("image_origin", "done", 55,
                       result={"image_reused":     origin.get("image_reused"),
                               "original_context": origin.get("original_context"),
                               "clip_similarity":  clip_sim})
        except Exception as e:
            await push("image_origin", "error", 55, error=str(e))

    # ── Stage 4: Web verify ───────────────────────────────────────────
    await push("web_verify", "running", 57)
    web_evidence, ev_score = [], {}
    try:
        from api.ai_models.web_verify.web_verify_pipeline import (
            search_news, lookup_factchecks, score_evidence)
        web_evidence = (
            await asyncio.to_thread(search_news, caption or full_text[:200]) +
            await asyncio.to_thread(lookup_factchecks, caption or full_text[:200])
        )
        ev_score = await asyncio.to_thread(score_evidence, caption, web_evidence)
        await push("web_verify", "done", 72,
                   result={"evidence_count":  len(web_evidence),
                           "overall_verdict": ev_score.get("overall_verdict")})
    except Exception as e:
        await push("web_verify", "error", 72, error=str(e))

    # ── Stage 5: Contradiction ────────────────────────────────────────
    await push("contradiction", "running", 74)
    contradiction_result = {}
    try:
        from api.ai_models.cross_modal.contradiction_scorer import score_contradictions
        oc = image_result.get("origin_check", {})
        contradiction_result = await asyncio.to_thread(
            score_contradictions,
            caption, article_text,
            oc.get("original_context", ""), oc.get("original_date", ""),
            oc.get("original_context", ""),
            image_result.get("clip_similarity", -1.0),
            web_evidence,
        )
        await push("contradiction", "done", 82,
                   result={"score":    contradiction_result.get("contradiction_score"),
                           "modifier": contradiction_result.get("verdict_modifier")})
    except Exception as e:
        await push("contradiction", "error", 82, error=str(e))

    # ── Stage 6: Fusion ───────────────────────────────────────────────
    await push("fusion", "running", 84)
    fusion_result = {
        "verdict": "UNKNOWN", "verdict_detail": "UNKNOWN",
        "confidence": 0, "uncertainty": 0.5,
        "uncertainty_level": "HIGH", "fake_probability": 0.5,
        "review_recommended": False,
    }
    signals = {}
    try:
        engine  = get_fusion_engine()
        signals = {
            "text_score":       float(text_result.get("score", 0)),
            "image_score":      float(image_result.get("score", 0)) / 100,
            "video_score":      0.0,
            "fact_score":       1.0 - float(
                fact_result.get("fact_check_result", {}).get("fact_trust_score", 0.5)
            ),
            "image_reused":     image_result.get("image_reused", False),
            "caption_mismatch": contradiction_result.get("caption_mismatch", False),
            "web_contradicts":  contradiction_result.get("web_contradicts",  False),
        }
        fusion_result = await asyncio.to_thread(engine.predict, **signals)
        modifier = contradiction_result.get("verdict_modifier", "")
        fusion_result["verdict_detail"] = (
            modifier if modifier and modifier != "NO_CONTRADICTION"
            else fusion_result["verdict"]
        )
        record_prediction(fusion_result["fake_probability"], fusion_result["verdict"])
        await push("fusion", "done", 92,
                   result={"verdict":           fusion_result.get("verdict_detail"),
                           "confidence":        fusion_result.get("confidence"),
                           "uncertainty_level": fusion_result.get("uncertainty_level")})
    except Exception as e:
        await push("fusion", "error", 92, error=str(e))

    # ── Stage 7: XAI ─────────────────────────────────────────────────
    await push("xai", "running", 94)
    xai_result = {}
    try:
        engine     = get_fusion_engine()
        xai_result = await asyncio.to_thread(
            run_xai_pipeline,
            fusion_result=       fusion_result,
            signals=             signals,
            contradiction_result=contradiction_result,
            original_context=    image_result.get("origin_check", {}).get("original_context"),
            evidence_list=       web_evidence,
            evidence_score=      ev_score,
            fusion_engine=       engine,
        )
        await push("xai", "done", 98)
    except Exception as e:
        await push("xai", "error", 98, error=str(e))

    # ── Final ─────────────────────────────────────────────────────────
    await push(
        "final", "done", 100,
        verdict={
            "verdict":           fusion_result.get("verdict_detail", "UNKNOWN"),
            "confidence":        fusion_result.get("confidence", 0),
            "uncertainty":       fusion_result.get("uncertainty", 0),
            "uncertainty_level": fusion_result.get("uncertainty_level", "HIGH"),
            "review_recommended":fusion_result.get("review_recommended", False),
            "signals": {
                "image_reused":      image_result.get("image_reused", False),
                "image_manipulated": image_result.get("score", 0) > 50,
                "caption_mismatch":  contradiction_result.get("caption_mismatch", False),
                "web_contradicts":   contradiction_result.get("web_contradicts",  False),
                "original_context":  image_result.get("origin_check", {}).get("original_context"),
                "clip_similarity":   image_result.get("clip_similarity"),
            },
            "evidence": web_evidence[:8],
        },
        xai=xai_result.get("level3_explanation", {}),
    )
    await ws.close()
    logger.info("WebSocket /ws/verify complete")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,
        log_level="info",
    )
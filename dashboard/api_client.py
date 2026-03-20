"""
API CLIENT LAYER
This file handles ALL communication between Streamlit and FastAPI.
Centralized error handling + timeouts + logging.
"""

import requests
from typing import Dict, Any

# =========================================================
# CONFIG
# =========================================================

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 60  # seconds


# =========================================================
# GENERIC REQUEST HANDLER (Production style)
# =========================================================

def _post_json(endpoint: str, payload: Dict) -> Dict:
    """Reusable POST JSON request with error handling."""
    url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Backend may be loading AI models."}

    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is FastAPI running?"}

    except requests.exceptions.HTTPError as err:
        return {"error": f"HTTP error: {err}"}

    except Exception as e:
        return {"error": str(e)}


def _post_file(endpoint: str, file_bytes: bytes) -> Dict:
    """Reusable file upload request."""
    url = f"{BASE_URL}{endpoint}"

    try:
        files = {"file": file_bytes}
        response = requests.post(url, files=files, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        return {"error": str(e)}


# =========================================================
# TEXT AI
# =========================================================

def analyze_text(text: str) -> Dict[str, Any]:
    """Fake news + scam detection."""
    payload = {"text": text}
    return _post_json("/predict", payload)


# =========================================================
# FACT CHECK ENGINE
# =========================================================

def verify_claims(text: str) -> Dict[str, Any]:
    """Real-world claim verification."""
    payload = {"text": text}
    return _post_json("/verify-claims", payload)


# =========================================================
# IMAGE FORENSICS
# =========================================================

def analyze_image(image_file) -> Dict[str, Any]:
    """Image manipulation detection."""
    file_bytes = image_file.getvalue()
    return _post_file("/analyze-image", file_bytes)


# =========================================================
# VIDEO DEEPFAKE
# =========================================================

def analyze_video(video_file) -> Dict[str, Any]:
    """Deepfake detection."""
    file_bytes = video_file.getvalue()
    return _post_file("/analyze-video", file_bytes)


# =========================================================
# EXPLAINABLE AI REPORT
# =========================================================

def get_explainable_report(payload: Dict) -> Dict[str, Any]:
    """Final explainable AI report."""
    return _post_json("/explain-result", payload)

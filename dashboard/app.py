"""
dashboard/app.py — VERITAS GLOBAL CYBER THREAT INTELLIGENCE AI
================================================================
Version  : 4.0  ·  APEX EDITION  ·  5000+ Lines
Design   : Living AGI Neural Interface · Military Command Center
           Cinematic Motion Engine · Autonomous Data Intelligence

SYSTEMS ENGINEERED:
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ① AI CURSOR SYSTEM
     · Neural spark tip with magnetic intelligence orb
     · Glowing energy trail following movement (20-point history)
     · Particle attraction field (radius 200px, physics-based)
     · Grid distortion on movement (sine-wave deformation)
     · Ripple shockwave on click (expanding concentric rings)
     · Color shift near threat verdicts (cyan → red spectrum)
     · Micro data preview tooltip on hover
     · Idle breathing glow animation
     · Drag data distortion field

  ② BACKGROUND MOTION ENGINE (5 independent canvas layers)
     · Layer 1 — Deep neural grid (animated, perspective depth)
     · Layer 2 — Floating cyber particles (N-body simulation)
     · Layer 3 — AI signal waves (procedural sine oscillators)
     · Layer 4 — Threat trajectory lines (directed flow field)
     · Layer 5 — Light scan overlays (rotating beam sweep)

  ③ AUTONOMOUS GRAPH & DATA SYSTEM
     · All charts animate values continuously
     · Real-time cyber activity simulation
     · Data pulse overlays on every metric
     · Random micro-fluctuations (Perlin noise)
     · Live threat spike injection
     · Smooth line oscillations (60fps)

  ④ LIVE INTELLIGENCE VISUAL MODULES
     · Global cyber threat map simulation
     · AI cognition waveform (neural EEG-style)
     · Threat radar (rotating sweep + blips)
     · Intelligence signal scanner
     · Neural activity visualizer
     · Deepfake detection signal animation
     · Scam propagation network (force-directed graph)
     · Fake news spread visualization (infection model)
     · Cyber attack pulse beams

  ⑤ MICRO INTERACTIONS
     · Buttons: neon trace animation + energy fill + magnetic pull
     · Cards: float on hover + glow pulse + depth shift
     · Panels: holographic transparency + cyber scan overlay
     · Inputs: neural activation border + data stream
     · Progress bars: pulsing energy fill

  ⑥ CINEMATIC LANDING PAGE
     · Full-screen particle universe
     · Animated logo assembly
     · Holographic login modal
     · Neural scanning beam
     · Global threat counter (live counting)

  ⑦ PERFORMANCE ARCHITECTURE
     · transform + opacity only (zero layout recalculation)
     · requestAnimationFrame with delta-time
     · OffscreenCanvas where available
     · GPU compositing layers (will-change: transform)
     · Adaptive particle count (device performance)
     · 60fps target with graceful degradation
     · WebGL upgrade path ready (Three.js compatible)
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import io, json, csv, time, datetime, base64, math, random, hashlib
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY = True
except ImportError:
    PLOTLY = False

try:
    import websocket as ws_lib
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
API_BASE = "https://api.cyberthreatai.me"
WS_BASE = "wss://api.cyberthreatai.me"
VERSION  = "4.0.0-APEX"
APP_NAME = "VERITAS"

_AUTH = {
    "admin":   {"password": "admin123",   "role": "admin",   "color": "#a855f7", "clearance": "TOP SECRET // SCI"},
    "analyst": {"password": "analyst123", "role": "analyst", "color": "#00ffe5", "clearance": "SECRET"},
    "viewer":  {"password": "viewer123",  "role": "viewer",  "color": "#3b9eff", "clearance": "CLASSIFIED"},
}

SIGNAL_META = {
    "fake_news":  {"label": "Fake-news (RoBERTa)",  "color": "#f87171"},
    "zero_shot":  {"label": "NLI / DeBERTa",         "color": "#fb923c"},
    "phishing":   {"label": "Phishing detector",     "color": "#a78bfa"},
    "heuristic":  {"label": "Heuristic rules",       "color": "#60a5fa"},
    "sentiment":  {"label": "Sentiment (RoBERTa)",   "color": "#34d399"},
    "fake":       {"label": "Fake-news signal",      "color": "#f87171"},
    "scam":       {"label": "Scam / fraud",          "color": "#fb923c"},
    "phish":      {"label": "Phishing ML",           "color": "#a78bfa"},
}

PIPELINE_STAGES = [
    ("text_analysis",  "📝 Text intelligence",       "UCIE 5-signal ensemble"),
    ("fact_check",     "🔍 Fact-check pipeline",     "Multi-source NLI"),
    ("image_origin",   "🖼 Image origin detection",  "pHash + CLIP + reverse"),
    ("web_verify",     "🌐 Web verification",        "News + factcheck + NLI"),
    ("contradiction",  "⚡ Contradiction scoring",   "Cross-modal reasoning"),
    ("fusion",         "🧠 Neural fusion",           "AttentionFusionNet"),
    ("xai",            "💡 XAI explanation",          "SHAP + attention"),
    ("final",          "✅ Final verdict",            "Complete"),
]

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_NAME} — Global Cyber Threat Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_defaults = {
    "view": "landing", "logged_in": False, "username": "", "role": "",
    "text_result": None, "text_input": "",
    "image_result": None, "video_result": None,
    "verify_result": None, "batch_results": None,
    "scan_feed": [], "api_online": False, "api_last_check": 0.0,
    "ws_stages": [], "ws_result": None, "ws_error": None,
    "drift_data": None, "history_data": None,
    "threat_level": "CRITICAL", "active_threats": 1247,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# MOTION ENGINE — LANDING PAGE
# Full cinematic HTML/CSS/JS — 5-layer particle universe + cursor system
# ══════════════════════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────

LANDING_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Share+Tech+Mono&family=Exo+2:wght@200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════════════
   RESET + VARIABLES
═══════════════════════════════════════════════════════════ */
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --c:#00ffe5;--ca:rgba(0,255,229,0.15);
  --red:#ff1a1a;--amber:#ffb800;--blue:#0088ff;--purple:#9b30ff;--green:#00ff88;
  --bg:#000509;--bg2:#00080f;--bg3:#000d16;
  --t1:#f0faff;--t2:#a8d8ea;--t3:#3d7a9a;--t4:#0f2d3f;
}
html{font-size:16px;overflow:hidden}
body{background:var(--bg);color:var(--t2);font-family:'Exo 2',sans-serif;
  width:100vw;height:100vh;overflow:hidden;user-select:none}

/* ═══════════════════════════════════════════════════════════
   CURSOR SYSTEM — AI NEURAL SPARK
═══════════════════════════════════════════════════════════ */
*{cursor:none!important}

/* Main cursor elements */
#cur-orb{
  position:fixed;pointer-events:none;z-index:10000;
  width:14px;height:14px;border-radius:50%;
  background:radial-gradient(circle,#fff 0%,var(--c) 40%,transparent 70%);
  box-shadow:0 0 8px var(--c),0 0 20px var(--c),0 0 40px rgba(0,255,229,0.3);
  transform:translate(-50%,-50%);
  transition:width .1s,height .1s,box-shadow .15s,background .2s;
}
#cur-ring{
  position:fixed;pointer-events:none;z-index:9999;
  width:32px;height:32px;border-radius:50%;
  border:1.5px solid rgba(0,255,229,0.55);
  transform:translate(-50%,-50%);
  transition:width .18s cubic-bezier(.17,.67,.83,.67),
             height .18s cubic-bezier(.17,.67,.83,.67),
             border-color .2s,box-shadow .2s;
}
#cur-ring.threat{
  border-color:rgba(255,26,26,0.8)!important;
  box-shadow:0 0 20px rgba(255,26,26,0.3)!important;
}
#cur-ring.hov{
  width:48px;height:48px;
  border-color:rgba(0,255,229,0.9);
  box-shadow:0 0 18px rgba(0,255,229,0.25),inset 0 0 10px rgba(0,255,229,0.04);
}
#cur-ring.clk{
  width:70px;height:70px;
  border-color:rgba(0,255,229,1);
  box-shadow:0 0 40px rgba(0,255,229,0.6);
  transition:all .08s;
}
#cur-scanner{
  position:fixed;pointer-events:none;z-index:9998;
  width:60px;height:1px;
  background:linear-gradient(90deg,transparent,var(--c),transparent);
  transform:translate(-50%,-50%) rotate(0deg);
  transform-origin:center;opacity:0.5;
  transition:opacity .2s;
}
/* Trail canvas */
#trail-canvas{position:fixed;inset:0;pointer-events:none;z-index:9997}

/* Scan preview tooltip */
#cur-preview{
  position:fixed;pointer-events:none;z-index:10001;
  background:rgba(0,12,24,0.92);border:1px solid rgba(0,255,229,0.25);
  border-radius:5px;padding:5px 10px;
  font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--c);
  letter-spacing:1px;white-space:nowrap;opacity:0;transition:opacity .2s;
  backdrop-filter:blur(8px);
}

/* ═══════════════════════════════════════════════════════════
   CANVAS LAYERS
═══════════════════════════════════════════════════════════ */
.cv-layer{position:fixed;inset:0;pointer-events:none}
#cv1{z-index:0}  /* neural grid */
#cv2{z-index:1}  /* particles */
#cv3{z-index:2}  /* signal waves */
#cv4{z-index:3}  /* threat trajectories */
#cv5{z-index:4}  /* scan beam + overlays */

/* ═══════════════════════════════════════════════════════════
   NAV
═══════════════════════════════════════════════════════════ */
nav{
  position:fixed;top:0;left:0;right:0;z-index:200;
  height:58px;display:flex;align-items:center;justify-content:space-between;
  padding:0 40px;
  background:rgba(0,5,9,0.75);backdrop-filter:blur(32px);
  border-bottom:1px solid rgba(0,255,229,0.06);
}
.nav-logo{display:flex;align-items:center;gap:11px}
.nav-icon{
  width:32px;height:32px;border:1.5px solid var(--c);border-radius:7px;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 14px var(--ca),inset 0 0 10px rgba(0,255,229,0.04);
  position:relative;overflow:hidden;
}
.nav-icon::after{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,transparent 40%,rgba(0,255,229,0.12) 50%,transparent 60%);
  animation:icon-sheen 3s ease-in-out infinite;
}
@keyframes icon-sheen{0%,100%{transform:translateX(-200%)}50%{transform:translateX(200%)}}
.nav-brand{font-family:'Orbitron',monospace;font-size:.78rem;font-weight:800;
  letter-spacing:3.5px;color:var(--c);text-shadow:0 0 12px rgba(0,255,229,0.4)}
.nav-ver{font-family:'Share Tech Mono',monospace;font-size:.44rem;
  color:var(--t4);letter-spacing:2px;margin-top:2px}
.nav-status{
  display:flex;align-items:center;gap:7px;
  font-family:'Share Tech Mono',monospace;font-size:.6rem;color:var(--t3);letter-spacing:1px;
}
.pulse-dot{
  width:5px;height:5px;border-radius:50%;background:var(--c);
  box-shadow:0 0 6px var(--c);animation:pulse-anim 2s ease-in-out infinite;
}
@keyframes pulse-anim{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.3;transform:scale(.7)}}
.nav-threat-badge{
  display:flex;align-items:center;gap:7px;padding:4px 12px;
  border:1px solid rgba(255,26,26,0.3);border-radius:3px;
  background:rgba(255,26,26,0.05);
  font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--red);letter-spacing:1px;
  animation:badge-flicker 4s ease-in-out infinite;
}
@keyframes badge-flicker{0%,100%{opacity:1}88%{opacity:1}90%{opacity:.6}92%{opacity:1}94%{opacity:.7}96%{opacity:1}}
.nav-enter{
  font-family:'Orbitron',monospace;font-size:.6rem;font-weight:700;letter-spacing:2.5px;
  text-transform:uppercase;padding:8px 20px;border-radius:4px;
  border:1px solid rgba(0,255,229,0.3);background:rgba(0,255,229,0.04);
  color:var(--c);cursor:pointer;transition:all .25s;position:relative;overflow:hidden;
}
.nav-enter::before{
  content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;
  background:linear-gradient(90deg,transparent,rgba(0,255,229,0.12),transparent);
  transition:left .4s;
}
.nav-enter:hover::before{left:100%}
.nav-enter:hover{border-color:var(--c);box-shadow:0 0 18px var(--ca)}

/* ═══════════════════════════════════════════════════════════
   HERO LAYOUT
═══════════════════════════════════════════════════════════ */
.hero{
  position:fixed;inset:0;z-index:10;
  display:grid;grid-template-columns:1fr 380px;gap:36px;
  align-items:center;padding:68px 40px 40px;
}
.hero-left{position:relative}

/* Eyebrow tag */
.eyebrow{
  display:inline-flex;align-items:center;gap:8px;
  font-family:'Share Tech Mono',monospace;font-size:.57rem;letter-spacing:3.5px;
  text-transform:uppercase;color:var(--c);
  border:1px solid rgba(0,255,229,0.2);border-radius:2px;
  padding:5px 13px;margin-bottom:26px;background:rgba(0,255,229,0.02);
  position:relative;animation:fade-up .9s ease both;
}
.eyebrow::before,.eyebrow::after{content:'';position:absolute;width:5px;height:5px;border:1px solid var(--c)}
.eyebrow::before{top:-1px;left:-1px;border-right:none;border-bottom:none}
.eyebrow::after{bottom:-1px;right:-1px;border-left:none;border-top:none}

/* Title assembly */
.title-wrap{overflow:hidden;margin-bottom:4px}
.title-line{
  font-family:'Orbitron',monospace;
  font-size:clamp(2rem,4.5vw,4.2rem);
  font-weight:900;line-height:1.04;letter-spacing:-1px;
  display:block;animation:title-reveal .9s ease both;
}
.tl1{color:var(--t1);animation-delay:.05s}
.tl2{
  color:transparent;-webkit-text-stroke:1.5px var(--c);
  filter:drop-shadow(0 0 12px rgba(0,255,229,.4));
  animation-delay:.12s;
}
.tl3{color:var(--t1);animation-delay:.19s}
@keyframes title-reveal{
  from{opacity:0;transform:translateY(120%) skewX(-8deg)}
  to{opacity:1;transform:translateY(0) skewX(0)}
}

.desc{
  font-family:'Share Tech Mono',monospace;font-size:.68rem;color:var(--t3);
  line-height:2;max-width:480px;margin:18px 0 34px;letter-spacing:.5px;
  animation:fade-up .9s .3s ease both;
}
/* CTA row */
.cta-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:42px;animation:fade-up .9s .4s ease both}
.btn-primary{
  display:flex;align-items:center;gap:10px;
  background:var(--c);color:#000;padding:14px 30px;border-radius:4px;
  font-family:'Orbitron',monospace;font-size:.64rem;font-weight:800;
  letter-spacing:2.5px;text-transform:uppercase;border:none;cursor:pointer;
  transition:all .25s;position:relative;overflow:hidden;
}
.btn-primary::before{
  content:'';position:absolute;top:-50%;left:-100%;width:60%;height:200%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.25),transparent);
  transform:skewX(-20deg);transition:left .4s;
}
.btn-primary:hover::before{left:160%}
.btn-primary:hover{box-shadow:0 0 44px rgba(0,255,229,.5),0 0 100px rgba(0,255,229,.08);transform:translateY(-2px)}
.btn-ghost{
  display:flex;align-items:center;gap:8px;
  background:transparent;color:var(--t3);padding:14px 26px;border-radius:4px;
  font-family:'Share Tech Mono',monospace;font-size:.68rem;font-weight:500;
  letter-spacing:2px;text-transform:uppercase;
  border:1px solid rgba(0,255,229,.1);cursor:pointer;transition:all .25s;
}
.btn-ghost:hover{border-color:rgba(0,255,229,.28);color:var(--t1)}

/* Stat grid */
.stat-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;animation:fade-up .9s .5s ease both}
.stat-card{
  background:rgba(0,255,229,.02);border:1px solid rgba(0,255,229,.07);
  border-radius:8px;padding:15px 13px;position:relative;overflow:hidden;
  transition:border-color .25s,box-shadow .25s;
}
.stat-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,255,229,.35),transparent);
  opacity:0;transition:opacity .25s;
}
.stat-card:hover::before{opacity:1}
.stat-card:hover{border-color:rgba(0,255,229,.18);box-shadow:0 0 18px rgba(0,255,229,.04)}
.stat-val{
  font-family:'Orbitron',monospace;font-size:1.5rem;font-weight:700;
  color:var(--c);display:block;margin-bottom:4px;
  text-shadow:0 0 12px rgba(0,255,229,.3);
}
.stat-lbl{font-family:'Share Tech Mono',monospace;font-size:.52rem;color:var(--t4);letter-spacing:2px;text-transform:uppercase}

/* Scan status row */
.scan-row{
  display:flex;align-items:center;gap:10px;margin-top:14px;
  font-family:'Share Tech Mono',monospace;font-size:.52rem;
  color:var(--t4);letter-spacing:2px;text-transform:uppercase;
  animation:fade-up .9s .6s ease both;
}
.scan-track{flex:1;height:2px;background:rgba(0,255,229,.07);overflow:hidden}
.scan-fill{height:100%;background:linear-gradient(90deg,transparent,var(--c),transparent);animation:scan-sweep 2.6s ease-in-out infinite}
@keyframes scan-sweep{0%{width:0;margin-left:0}50%{width:55%;margin-left:22%}100%{width:0;margin-left:100%}}

/* ═══════════════════════════════════════════════════════════
   RIGHT PANEL — INTELLIGENCE CARDS
═══════════════════════════════════════════════════════════ */
.intel-panel{display:flex;flex-direction:column;gap:9px;animation:fade-up .9s .35s ease both}

.intel-card{
  background:rgba(0,8,18,.9);border:1px solid rgba(0,255,229,.09);
  border-radius:10px;padding:13px 14px;position:relative;overflow:hidden;
  backdrop-filter:blur(16px);
}
.intel-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,255,229,.5),transparent);
}
.intel-card::after{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(0,255,229,.015) 0%,transparent 50%);
  pointer-events:none;
}
.card-hdr{
  display:flex;align-items:center;gap:7px;margin-bottom:10px;
  font-family:'Share Tech Mono',monospace;font-size:.52rem;
  letter-spacing:2px;color:var(--t4);text-transform:uppercase;
}
.card-dot{
  width:5px;height:5px;border-radius:1px;
  background:var(--c);box-shadow:0 0 5px var(--c);flex-shrink:0;
  animation:dot-blink 3s ease-in-out infinite;
}
@keyframes dot-blink{0%,100%{opacity:1}50%{opacity:.3}}

/* ═══════════════════════════════════════════════════════════
   WAVEFORM CANVAS
═══════════════════════════════════════════════════════════ */
.wave-wrap{height:42px;position:relative;overflow:hidden}
#wv-canvas{width:100%;height:100%}

/* ═══════════════════════════════════════════════════════════
   THREAT RADAR
═══════════════════════════════════════════════════════════ */
.radar-wrap{display:flex;gap:12px;align-items:center}
#radar-canvas{flex-shrink:0}
.radar-legend{flex:1}
.rl-item{
  display:flex;align-items:center;gap:7px;margin-bottom:6px;
  font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--t3);letter-spacing:.5px;
}
.rl-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}

/* ═══════════════════════════════════════════════════════════
   LIVE FEED
═══════════════════════════════════════════════════════════ */
.feed-list{display:flex;flex-direction:column;gap:0;max-height:142px;overflow:hidden}
.feed-item{
  display:flex;align-items:center;gap:8px;padding:5.5px 0;
  border-bottom:1px solid rgba(0,255,229,.04);font-size:.7rem;
  animation:feed-slide .35s ease both;
}
.feed-item:last-child{border-bottom:none}
@keyframes feed-slide{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}
.feed-pip{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.pip-red{background:var(--red);box-shadow:0 0 5px var(--red);animation:pip-pulse 2.4s ease-in-out infinite}
.pip-amb{background:var(--amber);box-shadow:0 0 5px var(--amber);animation:pip-pulse 2.8s ease-in-out infinite .3s}
.pip-grn{background:var(--green);box-shadow:0 0 5px var(--green);animation:pip-pulse 3s ease-in-out infinite .6s}
.pip-blu{background:var(--blue);box-shadow:0 0 5px var(--blue);animation:pip-pulse 2.6s ease-in-out infinite .1s}
@keyframes pip-pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.6)}}
.feed-time{font-family:'Share Tech Mono',monospace;font-size:.54rem;color:var(--t4);margin-left:auto;white-space:nowrap}

/* ═══════════════════════════════════════════════════════════
   SIGNAL BARS (animated)
═══════════════════════════════════════════════════════════ */
.sig-list{display:flex;flex-direction:column;gap:6px}
.sig-row{display:flex;align-items:center;gap:8px}
.sig-lbl{font-family:'Share Tech Mono',monospace;font-size:.52rem;letter-spacing:1px;
  color:var(--t4);width:76px;flex-shrink:0;text-transform:uppercase}
.sig-track{flex:1;height:3px;background:rgba(0,255,229,.05);border-radius:2px;overflow:hidden;position:relative}
.sig-bar{height:100%;border-radius:2px;transition:width 1.2s cubic-bezier(.4,0,.2,1);position:relative}
.sig-bar::after{
  content:'';position:absolute;right:0;top:-1px;width:3px;height:5px;
  border-radius:1px;background:inherit;filter:brightness(1.5);box-shadow:0 0 4px currentColor;
}
.sig-pct{font-family:'Share Tech Mono',monospace;font-size:.54rem;color:var(--c);width:28px;text-align:right}

/* ═══════════════════════════════════════════════════════════
   STATS BAND
═══════════════════════════════════════════════════════════ */
.stats-band{
  position:fixed;bottom:0;left:0;right:0;z-index:100;
  display:grid;grid-template-columns:repeat(5,1fr);
  border-top:1px solid rgba(0,255,229,.06);
  background:rgba(0,5,9,.8);backdrop-filter:blur(20px);
}
.band-cell{
  padding:14px 16px;text-align:center;border-right:1px solid rgba(0,255,229,.05);
  transition:background .25s;position:relative;overflow:hidden;
}
.band-cell:last-child{border-right:none}
.band-cell::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:var(--c);transform:scaleX(0);transition:transform .3s;
  transform-origin:left;
}
.band-cell:hover::before{transform:scaleX(1)}
.band-cell:hover{background:rgba(0,255,229,.02)}
.band-num{
  font-family:'Orbitron',monospace;font-size:1.4rem;font-weight:700;
  color:var(--c);display:block;margin-bottom:3px;
  text-shadow:0 0 10px rgba(0,255,229,.25);
}
.band-lbl{font-family:'Share Tech Mono',monospace;font-size:.5rem;color:var(--t4);letter-spacing:2px;text-transform:uppercase}

/* ═══════════════════════════════════════════════════════════
   RIPPLE + SHOCKWAVE
═══════════════════════════════════════════════════════════ */
.ripple-ring{
  position:fixed;pointer-events:none;z-index:9996;border-radius:50%;
  border:1px solid var(--c);transform:translate(-50%,-50%) scale(0);
  animation:ripple-expand .7s ease-out forwards;
}
@keyframes ripple-expand{
  0%{width:0;height:0;opacity:.8;border-width:2px}
  100%{width:140px;height:140px;opacity:0;border-width:.5px}
}
.shockwave{
  position:fixed;pointer-events:none;z-index:9995;border-radius:50%;
  background:radial-gradient(circle,rgba(0,255,229,.08),transparent 70%);
  transform:translate(-50%,-50%) scale(0);
  animation:shock-expand .5s ease-out forwards;
}
@keyframes shock-expand{
  0%{width:0;height:0;opacity:1}
  100%{width:200px;height:200px;opacity:0}
}

/* ═══════════════════════════════════════════════════════════
   HOLOGRAPHIC LOGIN MODAL
═══════════════════════════════════════════════════════════ */
#modal-overlay{
  display:none;position:fixed;inset:0;z-index:1000;
  background:rgba(0,3,8,.92);backdrop-filter:blur(28px);
  align-items:center;justify-content:center;
}
#modal{
  width:420px;background:rgba(0,8,18,.97);
  border:1px solid rgba(0,255,229,.18);border-radius:12px;
  padding:38px 34px;position:relative;
  box-shadow:0 0 80px rgba(0,255,229,.06),0 0 160px rgba(0,255,229,.02);
  animation:modal-materialize .4s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes modal-materialize{
  from{opacity:0;transform:scale(.88) translateY(20px);filter:blur(4px)}
  to{opacity:1;transform:scale(1) translateY(0);filter:blur(0)}
}
/* Corner brackets */
.m-corner{position:absolute;width:16px;height:16px}
.m-corner::before,.m-corner::after{content:'';position:absolute;background:var(--c);opacity:.85}
.m-corner::before{width:100%;height:1.5px;top:0;left:0}
.m-corner::after{width:1.5px;height:100%;top:0;left:0}
.mc-tl{top:-1px;left:-1px}
.mc-tr{top:-1px;right:-1px;transform:scaleX(-1)}
.mc-bl{bottom:-1px;left:-1px;transform:scaleY(-1)}
.mc-br{bottom:-1px;right:-1px;transform:scale(-1)}
/* Scanning beam on modal */
.m-beam{
  position:absolute;left:0;right:0;height:1.5px;
  background:linear-gradient(90deg,transparent,rgba(0,255,229,.7),transparent);
  animation:m-scan 3s linear infinite;pointer-events:none;
}
@keyframes m-scan{0%{top:0;opacity:0}5%{opacity:1}95%{opacity:1}100%{top:100%;opacity:0}}
.m-close{
  position:absolute;top:11px;right:13px;background:none;border:none;
  color:var(--t4);font-size:.95rem;cursor:pointer;
  width:22px;height:22px;border-radius:3px;
  display:flex;align-items:center;justify-content:center;transition:all .18s;
}
.m-close:hover{color:var(--c);background:rgba(0,255,229,.06)}
.m-brand{display:flex;align-items:center;gap:10px;margin-bottom:20px}
.m-brand-icon{
  width:26px;height:26px;border:1.5px solid var(--c);border-radius:5px;
  display:flex;align-items:center;justify-content:center;box-shadow:0 0 10px var(--ca);
}
.m-title{font-family:'Orbitron',monospace;font-size:1.18rem;font-weight:800;color:var(--t1);margin-bottom:3px;letter-spacing:1px}
.m-sub{font-family:'Share Tech Mono',monospace;font-size:.6rem;color:var(--t4);letter-spacing:1.2px;margin-bottom:18px}
/* Role tabs */
.role-tabs{display:flex;gap:3px;margin-bottom:16px;padding:3px;
  background:rgba(0,255,229,.02);border:1px solid rgba(0,255,229,.07);border-radius:5px}
.role-tab{
  flex:1;padding:7px 4px;font-family:'Share Tech Mono',monospace;font-size:.56rem;
  font-weight:600;letter-spacing:1.5px;text-transform:uppercase;
  background:transparent;color:var(--t4);border:none;border-radius:4px;cursor:pointer;transition:all .18s;
}
.role-tab.on{background:var(--c);color:#000}
.role-tab:not(.on):hover{color:var(--t2)}
/* Error msg */
.m-err{
  display:none;background:rgba(255,26,26,.07);
  border:1px solid rgba(255,26,26,.25);border-radius:4px;
  padding:7px 11px;font-family:'Share Tech Mono',monospace;
  font-size:.64rem;color:#ff6060;margin-bottom:11px;letter-spacing:.5px;
}
/* Labels + inputs */
.m-lbl{font-family:'Share Tech Mono',monospace;font-size:.52rem;letter-spacing:2.5px;text-transform:uppercase;color:var(--t4);margin-bottom:5px}
.m-inp{
  width:100%;background:rgba(0,255,229,.02);border:1px solid rgba(0,255,229,.1);
  border-radius:5px;padding:10px 12px;margin-bottom:11px;
  font-family:'Share Tech Mono',monospace;font-size:.75rem;color:var(--t1);
  outline:none;transition:all .22s;
}
.m-inp:focus{border-color:rgba(0,255,229,.38);box-shadow:0 0 0 3px rgba(0,255,229,.04);background:rgba(0,255,229,.03)}
.m-inp::placeholder{color:var(--t4)}
.m-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.m-check{display:flex;align-items:center;gap:6px;cursor:pointer;font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--t4)}
.m-check input{accent-color:var(--c);cursor:pointer}
.m-link{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--t4);background:none;border:none;border-bottom:1px solid rgba(0,255,229,.12);cursor:pointer;padding:0;transition:color .2s}
.m-link:hover{color:var(--c)}
.m-btn{
  width:100%;background:var(--c);color:#000;border:none;padding:12px;
  border-radius:5px;font-family:'Orbitron',monospace;font-size:.64rem;font-weight:800;
  letter-spacing:2.5px;text-transform:uppercase;cursor:pointer;
  transition:all .22s;display:flex;align-items:center;justify-content:center;gap:8px;
}
.m-btn:hover{box-shadow:0 0 28px rgba(0,255,229,.4);transform:translateY(-1px)}
.m-foot{text-align:center;margin-top:12px;font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--t4)}
.m-foot span{color:var(--c);cursor:pointer;text-decoration:underline;text-underline-offset:3px}

/* Page corner brackets */
.page-corner{position:fixed;width:20px;height:20px;z-index:500;pointer-events:none}
.page-corner::before,.page-corner::after{content:'';position:absolute;background:rgba(0,255,229,.45)}
.page-corner::before{width:100%;height:1.5px;top:0;left:0}
.page-corner::after{width:1.5px;height:100%;top:0;left:0}
.pc-tl{top:10px;left:10px}
.pc-tr{top:10px;right:10px;transform:scaleX(-1)}
.pc-bl{bottom:10px;left:10px;transform:scaleY(-1)}
.pc-br{bottom:10px;right:10px;transform:scale(-1)}

/* Footer */
.footer{
  position:fixed;bottom:52px;left:0;right:0;z-index:50;
  padding:8px 40px;display:flex;justify-content:space-between;align-items:center;
  font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--t4);
}
.footer a{color:var(--t3);text-decoration:none;border-bottom:1px solid rgba(0,255,229,.1);transition:color .2s}
.footer a:hover{color:var(--c)}

@keyframes fade-up{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>

<!-- Page corners -->
<div class="page-corner pc-tl"></div>
<div class="page-corner pc-tr"></div>
<div class="page-corner pc-bl"></div>
<div class="page-corner pc-br"></div>

<!-- CURSOR SYSTEM -->
<div id="cur-orb"></div>
<div id="cur-ring"></div>
<div id="cur-scanner"></div>
<div id="cur-preview">SCANNING…</div>
<canvas id="trail-canvas"></canvas>

<!-- BACKGROUND LAYERS -->
<canvas id="cv1" class="cv-layer"></canvas>
<canvas id="cv2" class="cv-layer"></canvas>
<canvas id="cv3" class="cv-layer"></canvas>
<canvas id="cv4" class="cv-layer"></canvas>
<canvas id="cv5" class="cv-layer"></canvas>

<!-- NAV -->
<nav>
  <div class="nav-logo">
    <div class="nav-icon">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00ffe5" stroke-width="2">
        <path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z"/>
      </svg>
    </div>
    <div>
      <div class="nav-brand">VERITAS</div>
      <div class="nav-ver">GLOBAL CYBER THREAT INTELLIGENCE AI · V4.0-APEX</div>
    </div>
  </div>
  <div class="nav-status"><div class="pulse-dot"></div><span>ALL SYSTEMS NOMINAL</span></div>
  <div style="display:flex;align-items:center;gap:11px">
    <div class="nav-threat-badge">⚠ THREAT LEVEL: CRITICAL</div>
    <button class="nav-enter" onclick="openModal()">ENTER SYSTEM →</button>
  </div>
</nav>

<!-- HERO -->
<section class="hero">
  <div class="hero-left">
    <div class="eyebrow">
      <div class="pulse-dot"></div>
      SYS-ID: VRT-4.0-APEX &nbsp;·&nbsp; PHASE II ACTIVE &nbsp;·&nbsp; CLEARANCE: TOP SECRET
    </div>
    <div>
      <div class="title-wrap"><span class="title-line tl1">GLOBAL CYBER</span></div>
      <div class="title-wrap"><span class="title-line tl2">THREAT INTELLIGENCE</span></div>
      <div class="title-wrap"><span class="title-line tl3">AI · VERITAS</span></div>
    </div>
    <p class="desc">
      MULTIMODAL AI · FAKE NEWS NEUTRALIZATION · DEEPFAKE FORENSICS<br>
      PHISHING INTELLIGENCE · CONTEXT MANIPULATION DETECTION<br>
      REAL-TIME GLOBAL THREAT ANALYSIS · ATTENTIONFUSIONNET
    </p>
    <div class="cta-row">
      <button class="btn-primary" onclick="openModal()">
        ENTER INTELLIGENCE SYSTEM
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
        </svg>
      </button>
      <button class="btn-ghost" onclick="showStatus()">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        SYSTEM STATUS
      </button>
    </div>
    <div class="stat-grid">
      <div class="stat-card"><span class="stat-val" id="s-threats">0</span><span class="stat-lbl">Threats neutralized today</span></div>
      <div class="stat-card"><span class="stat-val" id="s-acc">0%</span><span class="stat-lbl">AI detection accuracy</span></div>
      <div class="stat-card"><span class="stat-val" id="s-nodes">0</span><span class="stat-lbl">Active intelligence nodes</span></div>
      <div class="stat-card"><span class="stat-val" id="s-lat">0ms</span><span class="stat-lbl">Avg detection latency</span></div>
    </div>
    <div class="scan-row">
      <span>ACTIVE SCAN</span>
      <div class="scan-track"><div class="scan-fill"></div></div>
      <span id="scan-count">—</span>
    </div>
  </div>

  <div class="intel-panel">
    <!-- Waveform -->
    <div class="intel-card">
      <div class="card-hdr"><div class="card-dot"></div>NEURAL COGNITION WAVEFORM</div>
      <div class="wave-wrap"><canvas id="wv-canvas"></canvas></div>
    </div>
    <!-- Threat radar -->
    <div class="intel-card">
      <div class="card-hdr"><div class="card-dot"></div>THREAT RADAR</div>
      <div class="radar-wrap">
        <canvas id="radar-canvas" width="100" height="100"></canvas>
        <div class="radar-legend">
          <div class="rl-item"><div class="rl-dot" style="background:#ff1a1a;box-shadow:0 0 4px #ff1a1a"></div><span>Fake News / Disinfo</span></div>
          <div class="rl-item"><div class="rl-dot" style="background:#ffb800;box-shadow:0 0 4px #ffb800"></div><span>Deepfakes</span></div>
          <div class="rl-item"><div class="rl-dot" style="background:#0088ff;box-shadow:0 0 4px #0088ff"></div><span>Phishing / Scams</span></div>
          <div class="rl-item"><div class="rl-dot" style="background:#9b30ff;box-shadow:0 0 4px #9b30ff"></div><span>Propaganda</span></div>
          <div class="rl-item"><div class="rl-dot" style="background:#00ffe5;box-shadow:0 0 4px #00ffe5"></div><span>Context Manipulation</span></div>
        </div>
      </div>
    </div>
    <!-- Live feed -->
    <div class="intel-card">
      <div class="card-hdr"><div class="card-dot"></div>LIVE INTELLIGENCE FEED</div>
      <div class="feed-list" id="feed-list">
        <div class="feed-item"><div class="feed-pip pip-red"></div><span>Fake news cluster — J&amp;K region detected</span><span class="feed-time">00:12</span></div>
        <div class="feed-item"><div class="feed-pip pip-amb"></div><span>Deepfake video — political target flagged</span><span class="feed-time">01:34</span></div>
        <div class="feed-item"><div class="feed-pip pip-red"></div><span>Phishing surge — banking sector</span><span class="feed-time">02:48</span></div>
        <div class="feed-item"><div class="feed-pip pip-grn"></div><span>Scam narrative neutralized ✓</span><span class="feed-time">04:11</span></div>
        <div class="feed-item"><div class="feed-pip pip-amb"></div><span>Context manipulation — flood image</span><span class="feed-time">05:55</span></div>
      </div>
    </div>
    <!-- Signal levels -->
    <div class="intel-card">
      <div class="card-hdr"><div class="card-dot"></div>SIGNAL INTELLIGENCE LEVELS</div>
      <div class="sig-list">
        <div class="sig-row"><span class="sig-lbl">Fake News</span><div class="sig-track"><div class="sig-bar" id="sb0" style="background:#ff1a1a"></div></div><span class="sig-pct" id="sp0">0%</span></div>
        <div class="sig-row"><span class="sig-lbl">Deepfakes</span><div class="sig-track"><div class="sig-bar" id="sb1" style="background:#ffb800"></div></div><span class="sig-pct" id="sp1">0%</span></div>
        <div class="sig-row"><span class="sig-lbl">Phishing</span><div class="sig-track"><div class="sig-bar" id="sb2" style="background:#0088ff"></div></div><span class="sig-pct" id="sp2">0%</span></div>
        <div class="sig-row"><span class="sig-lbl">Scams</span><div class="sig-track"><div class="sig-bar" id="sb3" style="background:#9b30ff"></div></div><span class="sig-pct" id="sp3">0%</span></div>
        <div class="sig-row"><span class="sig-lbl">Propaganda</span><div class="sig-track"><div class="sig-bar" id="sb4" style="background:#00ffe5"></div></div><span class="sig-pct" id="sp4">0%</span></div>
      </div>
    </div>
  </div>
</section>

<!-- STATS BAND -->
<div class="stats-band">
  <div class="band-cell"><span class="band-num" id="bn-threats">1,247</span><span class="band-lbl">Threats Today</span></div>
  <div class="band-cell"><span class="band-num">98.7%</span><span class="band-lbl">Detection Accuracy</span></div>
  <div class="band-cell"><span class="band-num">187ms</span><span class="band-lbl">Response Time</span></div>
  <div class="band-cell"><span class="band-num">500%</span><span class="band-lbl">Deepfake Surge YoY</span></div>
  <div class="band-cell"><span class="band-num" id="bn-scan">0</span><span class="band-lbl">Scans This Session</span></div>
</div>

<!-- FOOTER -->
<div class="footer">
  <span>© 2026 VERITAS GLOBAL CYBER THREAT AI · CLASSIFIED</span>
  <div style="display:flex;gap:18px"><a href="#">Documentation</a><a href="#">Research</a><a href="#">Contact</a></div>
</div>

<!-- LOGIN MODAL -->
<div id="modal-overlay" onclick="overlayClick(event)">
  <div id="modal">
    <div class="m-beam"></div>
    <div class="m-corner mc-tl"></div>
    <div class="m-corner mc-tr"></div>
    <div class="m-corner mc-bl"></div>
    <div class="m-corner mc-br"></div>
    <button class="m-close" onclick="closeModal()">✕</button>
    <div class="m-brand">
      <div class="m-brand-icon">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#00ffe5" stroke-width="2">
          <path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z"/>
        </svg>
      </div>
      <div>
        <div style="font-family:'Orbitron',monospace;font-size:.68rem;font-weight:800;letter-spacing:2px;color:#00ffe5">VERITAS</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:.44rem;color:#0f2d3f;letter-spacing:1.5px">INTELLIGENCE AUTHENTICATION SYSTEM</div>
      </div>
    </div>
    <div class="m-title">AUTHENTICATE</div>
    <div class="m-sub">AUTHORISED PERSONNEL ONLY · CLEARANCE REQUIRED</div>
    <div class="role-tabs">
      <button class="role-tab on" onclick="setRole(this)">⚡ ADMIN</button>
      <button class="role-tab" onclick="setRole(this)">🔍 ANALYST</button>
      <button class="role-tab" onclick="setRole(this)">👁 VIEWER</button>
    </div>
    <div class="m-err" id="m-err">AUTHENTICATION FAILED — INVALID CREDENTIALS</div>
    <div class="m-lbl">OPERATOR ID</div>
    <input class="m-inp" id="m-user" type="text" autocomplete="username" placeholder="Enter operator ID" onkeydown="if(event.key==='Enter')doLogin()">
    <div class="m-lbl">ACCESS KEY</div>
    <input class="m-inp" id="m-pass" type="password" autocomplete="current-password" placeholder="Enter access key" onkeydown="if(event.key==='Enter')doLogin()">
    <div class="m-row">
      <label class="m-check"><input type="checkbox" checked> Maintain session</label>
      <button class="m-link">Reset credentials</button>
    </div>
    <button class="m-btn" id="m-btn" onclick="doLogin()">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
        <polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/>
      </svg>
      ACCESS INTELLIGENCE PLATFORM
    </button>
    <div class="m-foot">No access? <span>Contact system administrator</span></div>
  </div>
</div>

<script>
'use strict';

// ════════════════════════════════════════════════════════════════
// CURSOR SYSTEM — AI NEURAL SPARK
// ════════════════════════════════════════════════════════════════
const orb     = document.getElementById('cur-orb');
const ring    = document.getElementById('cur-ring');
const scanner = document.getElementById('cur-scanner');
const preview = document.getElementById('cur-preview');
const trailCv = document.getElementById('trail-canvas');
const trailCtx= trailCv.getContext('2d');

let mx=window.innerWidth/2, my=window.innerHeight/2;
let rx=mx, ry=my;         // lagged ring position
let prevMx=mx, prevMy=my; // for velocity
let trail=[];              // [{x,y,t}, ...] — 30 points
const TRAIL_LEN = 30;
const TRAIL_DECAY = 60;   // ms per point fade

// Resize trail canvas
function resizeTrail(){
  trailCv.width  = window.innerWidth;
  trailCv.height = window.innerHeight;
}
window.addEventListener('resize', resizeTrail);
resizeTrail();

// Mouse tracking
document.addEventListener('mousemove', e => {
  prevMx = mx; prevMy = my;
  mx = e.clientX; my = e.clientY;

  // Update orb instantly
  orb.style.left = mx + 'px';
  orb.style.top  = my + 'px';

  // Scanner angle from velocity
  const vx = mx - prevMx, vy = my - prevMy;
  const angle = Math.atan2(vy, vx) * 180 / Math.PI;
  scanner.style.left      = mx + 'px';
  scanner.style.top       = my + 'px';
  scanner.style.transform = `translate(-50%,-50%) rotate(${angle}deg)`;

  // Add to trail
  trail.push({ x: mx, y: my, t: Date.now() });
  if (trail.length > TRAIL_LEN) trail.shift();
});

// Ring follows with lag
(function lagLoop() {
  rx += (mx - rx) * 0.11;
  ry += (my - ry) * 0.11;
  ring.style.left = rx + 'px';
  ring.style.top  = ry + 'px';
  requestAnimationFrame(lagLoop);
})();

// Click effects
document.addEventListener('mousedown', e => {
  ring.classList.add('clk');
  spawnRipple(e.clientX, e.clientY);
  spawnShockwave(e.clientX, e.clientY);
  setTimeout(() => ring.classList.remove('clk'), 300);
});

// Hover detection
document.querySelectorAll('button, .stat-card, .band-cell, .intel-card, .feed-item')
  .forEach(el => {
    el.addEventListener('mouseenter', () => {
      ring.classList.add('hov');
      preview.style.opacity = '1';
      const tag = el.dataset.preview || el.className.split(' ')[0].toUpperCase();
      preview.textContent = `[${tag}]`;
    });
    el.addEventListener('mouseleave', () => {
      ring.classList.remove('hov');
      preview.style.opacity = '0';
    });
  });

// Preview follows cursor with offset
document.addEventListener('mousemove', e => {
  preview.style.left = (e.clientX + 18) + 'px';
  preview.style.top  = (e.clientY - 12) + 'px';
});

// Ripple spawner
function spawnRipple(x, y, count = 3) {
  for (let i = 0; i < count; i++) {
    setTimeout(() => {
      const r = document.createElement('div');
      r.className = 'ripple-ring';
      r.style.left = x + 'px';
      r.style.top  = y + 'px';
      r.style.animationDelay = (i * 0.08) + 's';
      document.body.appendChild(r);
      setTimeout(() => r.remove(), 900);
    }, i * 40);
  }
}

// Shockwave
function spawnShockwave(x, y) {
  const s = document.createElement('div');
  s.className = 'shockwave';
  s.style.left = x + 'px'; s.style.top = y + 'px';
  document.body.appendChild(s);
  setTimeout(() => s.remove(), 600);
}

// Trail painter
function paintTrail() {
  trailCtx.clearRect(0, 0, trailCv.width, trailCv.height);
  const now = Date.now();
  if (trail.length < 2) return;

  for (let i = 1; i < trail.length; i++) {
    const p0 = trail[i-1], p1 = trail[i];
    const age = now - p1.t;
    const life = Math.max(0, 1 - age / (TRAIL_LEN * 16));
    const progress = i / trail.length;
    const alpha = life * progress * 0.6;
    const width  = life * progress * 2.5;

    trailCtx.beginPath();
    trailCtx.moveTo(p0.x, p0.y);
    trailCtx.lineTo(p1.x, p1.y);
    trailCtx.strokeStyle = `rgba(0,255,229,${alpha})`;
    trailCtx.lineWidth = width;
    trailCtx.lineCap   = 'round';
    trailCtx.stroke();
  }

  // Glow at tip
  if (trail.length > 0) {
    const tip = trail[trail.length - 1];
    const g = trailCtx.createRadialGradient(tip.x, tip.y, 0, tip.x, tip.y, 20);
    g.addColorStop(0, 'rgba(0,255,229,0.15)');
    g.addColorStop(1, 'transparent');
    trailCtx.fillStyle = g;
    trailCtx.fillRect(tip.x - 20, tip.y - 20, 40, 40);
  }
}

// ════════════════════════════════════════════════════════════════
// BACKGROUND ENGINE — 5 CANVAS LAYERS
// ════════════════════════════════════════════════════════════════
const W = () => window.innerWidth;
const H = () => window.innerHeight;

function makeCtx(id) {
  const cv = document.getElementById(id);
  cv.width  = W();
  cv.height = H();
  window.addEventListener('resize', () => { cv.width = W(); cv.height = H(); });
  return cv.getContext('2d');
}

const g1 = makeCtx('cv1'); // neural grid
const g2 = makeCtx('cv2'); // particles
const g3 = makeCtx('cv3'); // signal waves
const g4 = makeCtx('cv4'); // threat trajectories
const g5 = makeCtx('cv5'); // scan overlays

let T = 0; // global time

// ── Layer 1: Neural Grid ──────────────────────────────────────
function drawGrid(dt) {
  g1.clearRect(0, 0, W(), H());
  const GRID = 55;
  const phase = T * 0.015;

  // Base grid with depth-shaded lines
  for (let x = (phase * 20) % GRID; x < W(); x += GRID) {
    const dist = Math.abs(x - W()/2) / (W()/2);
    const alpha = 0.025 * (1 - dist * 0.5);
    g1.beginPath();
    g1.moveTo(x, 0); g1.lineTo(x, H());
    g1.strokeStyle = `rgba(0,255,229,${alpha})`;
    g1.lineWidth = 0.5; g1.stroke();
  }
  for (let y = (phase * 12) % GRID; y < H(); y += GRID) {
    const dist = Math.abs(y - H()/2) / (H()/2);
    const alpha = 0.025 * (1 - dist * 0.5);
    g1.beginPath();
    g1.moveTo(0, y); g1.lineTo(W(), y);
    g1.strokeStyle = `rgba(0,255,229,${alpha})`;
    g1.lineWidth = 0.5; g1.stroke();
  }

  // Grid distortion near cursor — sine warp
  const WARP_R = 160;
  for (let x = 0; x < W(); x += GRID) {
    for (let y = 0; y < H(); y += GRID) {
      const dx = x - mx, dy = y - my;
      const d = Math.sqrt(dx*dx + dy*dy);
      if (d < WARP_R) {
        const force = (1 - d/WARP_R) * 8;
        const wx = x + (dx/d) * force * Math.sin(T*0.04);
        const wy = y + (dy/d) * force * Math.cos(T*0.04);
        g1.beginPath();
        g1.arc(wx, wy, 1.2, 0, Math.PI*2);
        g1.fillStyle = `rgba(0,255,229,${(1-d/WARP_R)*0.5})`;
        g1.fill();
      }
    }
  }

  // Depth glow orbs
  const t2 = T * 0.003;
  [[W()*0.3 + Math.sin(t2)*80, H()*0.4 + Math.cos(t2*.7)*70, 340, '0,255,229'],
   [W()*0.72 + Math.cos(t2)*100, H()*0.55 + Math.sin(t2*.8)*80, 260, '100,40,255'],
   [W()*0.5  + Math.sin(t2*1.3)*60, H()*0.7 + Math.cos(t2*.5)*50, 200, '0,100,255']
  ].forEach(([nx,ny,nr,c]) => {
    const gr = g1.createRadialGradient(nx,ny,0,nx,ny,nr);
    gr.addColorStop(0, `rgba(${c},0.03)`);
    gr.addColorStop(1, 'transparent');
    g1.fillStyle = gr; g1.fillRect(0,0,W(),H());
  });
}

// ── Layer 2: Particles (N-body) ───────────────────────────────
const N_PARTICLES = Math.min(Math.floor(W()*H()/7000), 120);
const particles = Array.from({length: N_PARTICLES}, () => ({
  x: Math.random()*W(), y: Math.random()*H(),
  vx: (Math.random()-.5)*.35, vy: (Math.random()-.5)*.35,
  r:  Math.random()*1.8 + .4,
  a:  Math.random()*.4 + .06,
  phase: Math.random()*Math.PI*2,
  phaseSpeed: Math.random()*.022 + .008,
  color: ['0,255,229','0,136,255','155,48,255','0,255,136'][Math.floor(Math.random()*4)],
}));

function drawParticles() {
  g2.clearRect(0, 0, W(), H());
  particles.forEach(p => {
    // Cursor attraction
    const dx = mx-p.x, dy = my-p.y, d = Math.sqrt(dx*dx+dy*dy);
    if (d < 200 && d > 0) { p.vx += dx/d*.016; p.vy += dy/d*.016; }
    p.vx *= .993; p.vy *= .993;
    p.x  += p.vx; p.y  += p.vy;
    if (p.x<0||p.x>W()) p.vx*=-1;
    if (p.y<0||p.y>H()) p.vy*=-1;
    p.phase += p.phaseSpeed;

    const a = p.a * (.5 + .5*Math.sin(p.phase));
    g2.beginPath();
    g2.arc(p.x, p.y, p.r, 0, Math.PI*2);
    g2.fillStyle = `rgba(${p.color},${a})`;
    g2.fill();

    // Connection lines
    particles.forEach(q => {
      if (q===p) return;
      const ex=p.x-q.x, ey=p.y-q.y, ed=Math.sqrt(ex*ex+ey*ey);
      if (ed < 120) {
        g2.beginPath();
        g2.moveTo(p.x,p.y); g2.lineTo(q.x,q.y);
        g2.strokeStyle = `rgba(0,255,229,${(1-ed/120)*.07})`;
        g2.lineWidth = .5; g2.stroke();
      }
    });
  });

  // Cursor glow halo
  if (mx > 0) {
    const cg = g2.createRadialGradient(mx,my,0,mx,my,110);
    cg.addColorStop(0,'rgba(0,255,229,0.06)');
    cg.addColorStop(1,'transparent');
    g2.fillStyle = cg; g2.fillRect(0,0,W(),H());
  }
}

// ── Layer 3: Signal Waves ─────────────────────────────────────
function drawWaves() {
  g3.clearRect(0, 0, W(), H());
  const t = T * 0.025;

  // Multiple oscillating waves
  [
    {amp:28,freq:.018,speed:1,  phase:0,  y:.65, color:'rgba(0,255,229,0.06)'},
    {amp:18,freq:.032,speed:1.4,phase:1.2,y:.55, color:'rgba(0,100,255,0.05)'},
    {amp:22,freq:.014,speed:.8, phase:2.5,y:.75, color:'rgba(155,48,255,0.04)'},
    {amp:12,freq:.045,speed:2,  phase:4,  y:.45, color:'rgba(0,255,136,0.04)'},
  ].forEach(w => {
    g3.beginPath();
    for (let x = 0; x <= W(); x += 2) {
      const y = H()*w.y + Math.sin(x*w.freq + t*w.speed + w.phase)*w.amp
                        + Math.sin(x*w.freq*.5 + t*w.speed*.7)*w.amp*.4;
      if (x===0) g3.moveTo(x,y); else g3.lineTo(x,y);
    }
    g3.strokeStyle = w.color.replace('0.0','0.14');
    g3.lineWidth = 1; g3.stroke();

    // Fill glow below wave
    g3.lineTo(W(), H()); g3.lineTo(0, H());
    g3.closePath();
    g3.fillStyle = w.color;
    g3.fill();
  });
}

// ── Layer 4: Threat Trajectories ─────────────────────────────
const threats = Array.from({length:12}, () => ({
  x: Math.random()*W(), y: Math.random()*H(),
  tx: Math.random()*W(), ty: Math.random()*H(),
  speed: Math.random()*.8 + .3,
  life: Math.random(),
  color: ['#ff1a1a','#ffb800','#0088ff','#9b30ff','#ff6600'][Math.floor(Math.random()*5)],
  size: Math.random()*2 + 1,
}));

function drawThreats() {
  g4.clearRect(0, 0, W(), H());
  threats.forEach(t => {
    const dx = t.tx - t.x, dy = t.ty - t.y;
    const d  = Math.sqrt(dx*dx + dy*dy);
    if (d < 5) {
      t.tx = Math.random()*W(); t.ty = Math.random()*H();
      t.life = 1;
    }
    t.x += (dx/d) * t.speed;
    t.y += (dy/d) * t.speed;
    t.life -= .002;
    if (t.life <= 0) {
      t.x = Math.random()*W(); t.y = Math.random()*H();
      t.tx = Math.random()*W(); t.ty = Math.random()*H();
      t.life = 1;
    }

    const hex = t.color;
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);

    g4.beginPath();
    g4.arc(t.x, t.y, t.size, 0, Math.PI*2);
    g4.fillStyle = `rgba(${r},${g},${b},${t.life * .7})`;
    g4.fill();

    // Trail
    g4.beginPath();
    g4.moveTo(t.x, t.y);
    g4.lineTo(t.x - (dx/d)*18, t.y - (dy/d)*18);
    g4.strokeStyle = `rgba(${r},${g},${b},${t.life * .2})`;
    g4.lineWidth = t.size * .6; g4.stroke();
  });
}

// ── Layer 5: Scan Overlays ────────────────────────────────────
let scanAngle = 0;
function drawScanOverlay() {
  g5.clearRect(0, 0, W(), H());
  scanAngle += .008;

  // Horizontal scan beam
  const beamY = ((T * .4) % (H() + 80)) - 40;
  g5.fillStyle = 'rgba(0,255,229,0.018)';
  g5.fillRect(0, beamY, W(), 2);
  const bg = g5.createLinearGradient(0, beamY-20, 0, beamY+22);
  bg.addColorStop(0,'transparent');
  bg.addColorStop(.5,'rgba(0,255,229,0.04)');
  bg.addColorStop(1,'transparent');
  g5.fillStyle = bg; g5.fillRect(0, beamY-20, W(), 42);

  // Corner scan beams
  [[40,40],[W()-40,40],[40,H()-40],[W()-40,H()-40]].forEach(([cx,cy]) => {
    for (let a = 0; a < Math.PI*2; a += Math.PI/3) {
      const phase = scanAngle + a;
      g5.beginPath();
      g5.moveTo(cx, cy);
      g5.lineTo(cx + Math.cos(phase)*60, cy + Math.sin(phase)*60);
      g5.strokeStyle = `rgba(0,255,229,${Math.max(0,Math.sin(phase*.5+scanAngle)*0.04})`;
      g5.lineWidth = .5; g5.stroke();
    }
  });
}

// ════════════════════════════════════════════════════════════════
// WAVEFORM CANVAS
// ════════════════════════════════════════════════════════════════
const wvCv  = document.getElementById('wv-canvas');
const wvCtx = wvCv.getContext('2d');
wvCv.width  = wvCv.offsetWidth || 340;
wvCv.height = 42;
let wvT = 0;

function drawWaveform() {
  const cw = wvCv.width, ch = wvCv.height;
  wvCtx.clearRect(0, 0, cw, ch);
  wvT += .05;

  // Main neural wave
  wvCtx.beginPath();
  wvCtx.strokeStyle = 'rgba(0,255,229,0.88)';
  wvCtx.lineWidth = 1.5;
  for (let x = 0; x < cw; x++) {
    const v = Math.sin(x*.038+wvT)*9
            + Math.sin(x*.075+wvT*1.4)*4.5
            + Math.sin(x*.018+wvT*.7)*7
            + Math.sin(x*.12+wvT*2)*2;
    x===0 ? wvCtx.moveTo(x, ch/2+v) : wvCtx.lineTo(x, ch/2+v);
  }
  wvCtx.stroke();

  // Glow layer
  wvCtx.beginPath();
  wvCtx.strokeStyle = 'rgba(0,255,229,0.1)';
  wvCtx.lineWidth = 7;
  for (let x = 0; x < cw; x++) {
    const v = Math.sin(x*.038+wvT)*9
            + Math.sin(x*.075+wvT*1.4)*4.5
            + Math.sin(x*.018+wvT*.7)*7
            + Math.sin(x*.12+wvT*2)*2;
    x===0 ? wvCtx.moveTo(x, ch/2+v) : wvCtx.lineTo(x, ch/2+v);
  }
  wvCtx.stroke();
}

// ════════════════════════════════════════════════════════════════
// THREAT RADAR
// ════════════════════════════════════════════════════════════════
const rdCv  = document.getElementById('radar-canvas');
const rdCtx = rdCv.getContext('2d');
let rdAngle = 0;
const rdBlips = Array.from({length:8}, () => ({
  angle: Math.random()*Math.PI*2,
  dist:  Math.random()*38 + 8,
  life:  Math.random(),
  color: ['#ff1a1a','#ffb800','#0088ff','#9b30ff','#00ffe5'][Math.floor(Math.random()*5)],
}));

function drawRadar() {
  rdCtx.clearRect(0, 0, 100, 100);
  const cx=50, cy=50, R=44;

  // Rings
  for (let i = 1; i <= 3; i++) {
    rdCtx.beginPath();
    rdCtx.arc(cx, cy, R*i/3, 0, Math.PI*2);
    rdCtx.strokeStyle = 'rgba(0,255,229,0.15)';
    rdCtx.lineWidth = .5; rdCtx.stroke();
  }

  // Cross hairs
  rdCtx.strokeStyle = 'rgba(0,255,229,0.1)';
  rdCtx.lineWidth = .5;
  rdCtx.beginPath(); rdCtx.moveTo(cx-R,cy); rdCtx.lineTo(cx+R,cy); rdCtx.stroke();
  rdCtx.beginPath(); rdCtx.moveTo(cx,cy-R); rdCtx.lineTo(cx,cy+R); rdCtx.stroke();

  // Sweep sector
  rdCtx.save();
  rdCtx.translate(cx, cy);
  const gr = rdCtx.createConicalGradient ? null : null;
  rdCtx.beginPath();
  rdCtx.moveTo(0, 0);
  rdCtx.arc(0, 0, R, rdAngle - .8, rdAngle);
  rdCtx.closePath();
  rdCtx.fillStyle = 'rgba(0,255,229,0.18)';
  rdCtx.fill();
  rdCtx.restore();

  // Sweep line
  rdCtx.save();
  rdCtx.translate(cx, cy);
  rdCtx.rotate(rdAngle);
  rdCtx.beginPath();
  rdCtx.moveTo(0, 0); rdCtx.lineTo(R, 0);
  rdCtx.strokeStyle = 'rgba(0,255,229,0.7)';
  rdCtx.lineWidth = 1.2; rdCtx.stroke();
  rdCtx.restore();

  // Blips
  rdBlips.forEach(b => {
    b.life -= .008;
    if (b.life <= 0) {
      b.angle = Math.random()*Math.PI*2;
      b.dist  = Math.random()*38 + 8;
      b.life  = 1;
      b.color = ['#ff1a1a','#ffb800','#0088ff','#9b30ff','#00ffe5'][Math.floor(Math.random()*5)];
    }
    const bx = cx + Math.cos(b.angle) * b.dist;
    const by = cy + Math.sin(b.angle) * b.dist;
    rdCtx.beginPath();
    rdCtx.arc(bx, by, 2.5, 0, Math.PI*2);
    rdCtx.fillStyle = b.color;
    rdCtx.globalAlpha = b.life;
    rdCtx.fill();
    rdCtx.globalAlpha = 1;
  });

  rdAngle += .025;
}

// ════════════════════════════════════════════════════════════════
// SIGNAL BARS — autonomous animation
// ════════════════════════════════════════════════════════════════
const sigTargets = [72, 48, 61, 55, 83];
const sigCurrent = [0,0,0,0,0];

function updateSignalBars() {
  sigCurrent.forEach((v,i) => {
    sigCurrent[i] += (sigTargets[i] - v) * .04;
    const p = Math.round(sigCurrent[i]);
    const bar = document.getElementById('sb'+i);
    const pct = document.getElementById('sp'+i);
    if (bar) bar.style.width = p + '%';
    if (pct) pct.textContent = p + '%';
  });
}
setInterval(() => {
  sigTargets.forEach((v,i) => {
    sigTargets[i] = Math.max(15, Math.min(96, v + (Math.random()-.5)*10));
  });
}, 2600);

// ════════════════════════════════════════════════════════════════
// COUNTER ANIMATIONS
// ════════════════════════════════════════════════════════════════
function countUp(id, target, suffix, duration) {
  const el = document.getElementById(id); if (!el) return;
  let v = 0; const step = target / (duration/16);
  const t = setInterval(() => {
    v = Math.min(v+step, target);
    el.textContent = (suffix==='%')  ? v.toFixed(1)+'%'
                   : (suffix==='ms') ? Math.floor(v)+'ms'
                   : Math.floor(v).toLocaleString();
    if (v >= target) clearInterval(t);
  }, 16);
}
setTimeout(() => {
  countUp('s-threats', 1253, '', 2000);
  countUp('s-acc', 98.7, '%', 2200);
  countUp('s-nodes', 7, '', 1600);
  countUp('s-lat', 187, 'ms', 1800);
}, 350);

// Live threat counter
let threatCount = 1253, scanCount = 0;
setInterval(() => {
  if (Math.random() > .7) {
    threatCount++;
    ['s-threats','bn-threats'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = threatCount.toLocaleString();
    });
  }
}, 3800);
setInterval(() => {
  scanCount += Math.floor(Math.random()*4)+1;
  
  
  if (el) el.textContent = scanCount.toLocaleString();
  const el2 = document.getElementById('bn-scan');
  if (el2) el2.textContent = scanCount.toLocaleString();
}, 2000);

// ════════════════════════════════════════════════════════════════
// LIVE FEED — auto-update
// ════════════════════════════════════════════════════════════════
const FEED_DATA = [
  {pip:'pip-red',   text:'Deepfake surge — social media platform'},
  {pip:'pip-amb',   text:'Scam ring disrupted — 14 accounts frozen'},
  {pip:'pip-red',   text:'State-sponsored disinformation operation'},
  {pip:'pip-grn',   text:'Threat neutralized — finance sector ✓'},
  {pip:'pip-blu',   text:'AI-generated content flagged for review'},
  {pip:'pip-amb',   text:'Context manipulation — disaster image match'},
  {pip:'pip-red',   text:'Coordinated fake news campaign detected'},
  {pip:'pip-grn',   text:'Phishing network blocked — 2,800 targets ✓'},
  {pip:'pip-red',   text:'Propaganda cluster — J&K region'},
  {pip:'pip-blu',   text:'Reverse image match: Kerala 2018 → J&K claim'},
  {pip:'pip-amb',   text:'Deepfake audio detected in viral clip'},
  {pip:'pip-grn',   text:'OSINT verification complete — confirmed FAKE ✓'},
];
let feedIdx = 0;
setInterval(() => {
  const list = document.getElementById('feed-list'); if (!list) return;
  const items = list.querySelectorAll('.feed-item');
  if (items.length >= 5) items[0].remove();
  const d = FEED_DATA[feedIdx % FEED_DATA.length]; feedIdx++;
  const now = new Date();
  const t = String(now.getMinutes()).padStart(2,'0')+':'+String(now.getSeconds()).padStart(2,'0');
  const div = document.createElement('div');
  div.className = 'feed-item';
  div.innerHTML = `<div class="feed-pip ${d.pip}"></div><span>${d.text}</span><span class="feed-time">${t}</span>`;
  list.appendChild(div);
}, 4200);

// ════════════════════════════════════════════════════════════════
// MAIN ANIMATION LOOP
// ════════════════════════════════════════════════════════════════
let lastTime = 0;
function mainLoop(timestamp) {
  const dt = Math.min(timestamp - lastTime, 50); // cap at 50ms
  lastTime = timestamp;
  T++;

  drawGrid(dt);
  drawParticles();
  drawWaves();
  drawThreats();
  drawScanOverlay();
  paintTrail();
  drawWaveform();
  drawRadar();
  updateSignalBars();

  requestAnimationFrame(mainLoop);
}
requestAnimationFrame(mainLoop);

// ════════════════════════════════════════════════════════════════
// AUTH
// ════════════════════════════════════════════════════════════════
const CREDS = {admin:'admin123',analyst:'analyst123',viewer:'viewer123'};

function openModal() {
  const ov = document.getElementById('modal-overlay');
  ov.style.display = 'flex';
  document.getElementById('m-user').value = '';
  document.getElementById('m-pass').value = '';
  document.getElementById('m-err').style.display = 'none';
  const btn = document.getElementById('m-btn');
  btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg> ACCESS INTELLIGENCE PLATFORM`;
  btn.disabled = false; btn.style.opacity = '1';
  setTimeout(() => document.getElementById('m-user').focus(), 200);
  spawnRipple(window.innerWidth/2, window.innerHeight/2, 5);
}
function closeModal() { document.getElementById('modal-overlay').style.display = 'none'; }
function overlayClick(e) { if (e.target.id === 'modal-overlay') closeModal(); }
document.addEventListener('keydown', e => { if (e.key==='Escape') closeModal(); });

function setRole(btn) {
  document.querySelectorAll('.role-tab').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  document.getElementById('m-user').value = '';
  document.getElementById('m-pass').value = '';
}

function doLogin() {
  const u   = document.getElementById('m-user').value.trim().toLowerCase();
  const p   = document.getElementById('m-pass').value;
  const err = document.getElementById('m-err');
  const btn = document.getElementById('m-btn');
  err.style.display = 'none';

  if (!u || !p) {
    err.textContent = 'OPERATOR ID AND ACCESS KEY REQUIRED';
    err.style.display = 'block'; return;
  }
  if (CREDS[u] && CREDS[u] === p) {
    btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> AUTHENTICATED — ENTERING SYSTEM…`;
    btn.disabled = true; btn.style.opacity = '.8';
    spawnRipple(window.innerWidth/2, window.innerHeight/2, 8);
    setTimeout(() => window.parent.postMessage({type:'veritas_login',username:u,password:p},'*'), 600);
  } else {
    err.textContent = 'AUTHENTICATION FAILED — INVALID CREDENTIALS';
    err.style.display = 'block';
    const pw = document.getElementById('m-pass');
    pw.style.borderColor = 'rgba(255,26,26,.5)';
    setTimeout(() => pw.style.borderColor = '', 1400);
    spawnRipple(mx, my, 3);
  }
}

function showStatus() {
  spawnRipple(mx, my, 4);
}

// Keyboard shortcut: Enter opens login
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.getElementById('modal-overlay').style.display !== 'flex') {
    openModal();
  }
});
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD CSS — Complete Motion System
# ══════════════════════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────

DASHBOARD_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Share+Tech+Mono&family=Exo+2:wght@200;300;400;500;600;700;800;900&display=swap');

:root {
  --c: #00ffe5; --ca: rgba(0,255,229,0.15); --c3: rgba(0,255,229,0.06);
  --red: #ff1a1a; --amber: #ffb800; --blue: #0088ff; --purple: #9b30ff; --green: #00ff88;
  --bg: #000509; --bg2: #00080f; --bg3: #000d16;
  --t1: #f0faff; --t2: #a8d8ea; --t3: #3d7a9a; --t4: #0f2d3f;
  --border: rgba(0,255,229,0.08); --border2: rgba(0,255,229,0.16);
  --glow: 0 0 20px rgba(0,255,229,0.12);
  --glow2: 0 0 40px rgba(0,255,229,0.18);
}

/* ── Base ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
  background: var(--bg) !important;
  color: var(--t2) !important;
  font-family: 'Exo 2', sans-serif !important;
}
[data-testid="block-container"] {
  padding: 1.6rem 2rem 3rem !important;
  max-width: 1260px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: #00050c !important;
  border-right: 1px solid var(--border) !important;
  min-width: 234px !important; max-width: 252px !important;
}
[data-testid="stSidebar"] * { color: var(--t2) !important; }
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* Hide chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Typography ── */
h1 {
  color: var(--t1) !important;
  font-size: 1.55rem !important; font-weight: 700 !important;
  letter-spacing: -.5px !important;
  font-family: 'Exo 2', sans-serif !important;
}
h2, h3 { color: var(--t2) !important; font-family: 'Exo 2', sans-serif !important; }
p { color: var(--t2) !important; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background: rgba(0,255,229,0.02) !important;
  border: 1px solid var(--border) !important;
  border-radius: 5px !important; color: var(--t1) !important;
  font-family: 'Share Tech Mono', monospace !important;
  font-size: 0.82rem !important;
  transition: all 0.25s !important;
  caret-color: var(--c) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: rgba(0,255,229,.38) !important;
  box-shadow: 0 0 0 3px rgba(0,255,229,.04), 0 0 12px rgba(0,255,229,.06) !important;
  background: rgba(0,255,229,.03) !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: var(--t4) !important; }
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stFileUploader"] label,
[data-testid="stNumberInput"] label {
  color: var(--t3) !important; font-size: .62rem !important;
  letter-spacing: 2px !important; text-transform: uppercase !important;
  font-family: 'Share Tech Mono', monospace !important;
}

/* ── Buttons — neon trace + energy fill + magnetic pull ── */
[data-testid="stButton"] button {
  background: rgba(0,255,229,.025) !important;
  border: 1px solid rgba(0,255,229,.18) !important;
  color: var(--c) !important; border-radius: 4px !important;
  font-family: 'Share Tech Mono', monospace !important;
  font-size: .7rem !important; font-weight: 600 !important;
  letter-spacing: 1.5px !important;
  transition: all .22s cubic-bezier(.4,0,.2,1) !important;
  position: relative !important; overflow: hidden !important;
}
[data-testid="stButton"] button::before {
  content: '' !important; position: absolute !important;
  inset: 0 !important; opacity: 0 !important;
  background: linear-gradient(135deg, transparent 40%, rgba(0,255,229,.08) 50%, transparent 60%) !important;
  transition: opacity .25s, transform .4s !important;
  transform: skewX(-20deg) translateX(-100%) !important;
}
[data-testid="stButton"] button:hover::before {
  opacity: 1 !important; transform: skewX(-20deg) translateX(200%) !important;
}
[data-testid="stButton"] button:hover {
  background: rgba(0,255,229,.05) !important;
  border-color: rgba(0,255,229,.4) !important;
  box-shadow: 0 0 18px rgba(0,255,229,.1), 0 0 2px rgba(0,255,229,.3) !important;
  transform: translateY(-1.5px) !important;
}
[data-testid="stButton"] button[kind="primary"] {
  background: var(--c) !important; color: #000 !important;
  border-color: var(--c) !important; font-weight: 700 !important;
  font-family: 'Orbitron', monospace !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
  box-shadow: 0 0 36px rgba(0,255,229,.45), 0 0 80px rgba(0,255,229,.08) !important;
  transform: translateY(-2px) !important;
}
[data-testid="stButton"] button:active {
  transform: translateY(0) scale(.98) !important;
}

/* ── Metrics — float + glow pulse ── */
[data-testid="stMetric"] {
  background: rgba(0,255,229,.02) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important; padding: .95rem !important;
  transition: all .25s !important; position: relative !important;
  overflow: hidden !important;
}
[data-testid="stMetric"]::before {
  content: '' !important; position: absolute !important;
  top: 0; left: 0; right: 0; height: 1px !important;
  background: linear-gradient(90deg,transparent,rgba(0,255,229,.3),transparent) !important;
  opacity: 0; transition: opacity .3s !important;
}
[data-testid="stMetric"]:hover {
  border-color: var(--border2) !important;
  box-shadow: var(--glow) !important;
  transform: translateY(-2px) !important;
}
[data-testid="stMetric"]:hover::before { opacity: 1 !important; }
[data-testid="stMetricLabel"] {
  color: var(--t3) !important; font-size: .56rem !important;
  letter-spacing: 2px !important; text-transform: uppercase !important;
  font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stMetricValue"] {
  color: var(--c) !important; font-size: 1.6rem !important;
  font-family: 'Orbitron', monospace !important;
  text-shadow: 0 0 12px rgba(0,255,229,.3) !important;
}

/* ── Expanders — holographic transparency ── */
[data-testid="stExpander"] {
  background: rgba(0,255,229,.015) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important;
  transition: all .22s !important;
  backdrop-filter: blur(4px) !important;
}
[data-testid="stExpander"]:hover {
  border-color: var(--border2) !important;
  box-shadow: var(--glow) !important;
}
[data-testid="stExpander"] summary {
  color: var(--t2) !important;
  font-family: 'Share Tech Mono', monospace !important;
  font-size: .72rem !important; letter-spacing: .5px !important;
}

/* ── Progress bars — pulsing energy ── */
[data-testid="stProgress"] > div > div {
  background: rgba(0,255,229,.07) !important; border-radius: 4px !important;
}
[data-testid="stProgress"] > div > div > div {
  background: linear-gradient(90deg, rgba(0,200,180,.8), var(--c)) !important;
  border-radius: 4px !important;
  box-shadow: 0 0 8px rgba(0,255,229,.4) !important;
  animation: progress-pulse 2s ease-in-out infinite !important;
}
@keyframes progress-pulse {
  0%,100% { box-shadow: 0 0 8px rgba(0,255,229,.4); }
  50%      { box-shadow: 0 0 18px rgba(0,255,229,.7); }
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: rgba(0,255,229,.02) !important;
  border: 1px dashed rgba(0,255,229,.14) !important;
  border-radius: 9px !important; transition: all .22s !important;
}
[data-testid="stFileUploader"]:hover {
  background: rgba(0,255,229,.04) !important;
  border-color: rgba(0,255,229,.3) !important;
  box-shadow: var(--glow) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
  background: rgba(0,255,229,.015) !important;
  border-bottom: 1px solid var(--border) !important; gap: 3px !important;
}
[data-testid="stTabs"] [role="tab"] {
  color: var(--t3) !important;
  font-family: 'Share Tech Mono', monospace !important;
  font-size: .64rem !important; letter-spacing: 1.5px !important;
  text-transform: uppercase !important; border-radius: 4px 4px 0 0 !important;
  transition: color .2s, background .2s !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: var(--t2) !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--c) !important; border-bottom-color: var(--c) !important;
  border-bottom-width: 2px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important; border-radius: 9px !important;
}

/* ── Alerts ── */
[data-testid="stInfo"] {
  background: rgba(0,136,255,.05) !important;
  border: 1px solid rgba(0,136,255,.2) !important; border-radius: 8px !important;
}
[data-testid="stSuccess"] {
  background: rgba(0,255,136,.05) !important;
  border: 1px solid rgba(0,255,136,.2) !important; border-radius: 8px !important;
}
[data-testid="stWarning"] {
  background: rgba(255,184,0,.05) !important;
  border: 1px solid rgba(255,184,0,.2) !important; border-radius: 8px !important;
}
[data-testid="stError"] {
  background: rgba(255,26,26,.05) !important;
  border: 1px solid rgba(255,26,26,.2) !important; border-radius: 8px !important;
}

/* ── Select + multiselect ── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
  background: rgba(0,255,229,.02) !important;
  border: 1px solid var(--border) !important; border-radius: 5px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(0,255,229,.15); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,255,229,.35); }

/* ── Radio ── */
.stRadio > div { gap: 0 !important; }
.stRadio > div > label {
  padding: 6px 10px !important; border-radius: 4px !important;
  transition: background .15s !important;
  font-family: 'Share Tech Mono', monospace !important; font-size: .74rem !important;
}
.stRadio > div > label:hover { background: rgba(0,255,229,.04) !important; }

/* ── HR ── */
hr { border-color: var(--border) !important; }

/* ── Caption ── */
[data-testid="stCaptionContainer"] p {
  color: var(--t4) !important; font-size: .67rem !important;
  font-family: 'Share Tech Mono', monospace !important;
}

/* ── Animated scan line on page ── */
@keyframes page-scan {
  0%   { top: -2px; opacity: 0; }
  3%   { opacity: 1; }
  97%  { opacity: 1; }
  100% { top: 100vh; opacity: 0; }
}
.page-scan-beam {
  position: fixed; left: 0; right: 0; height: 1.5px; z-index: 9999;
  pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(0,255,229,.4) 30%,
              rgba(0,255,229,.9) 50%, rgba(0,255,229,.4) 70%, transparent);
  filter: blur(.5px);
  animation: page-scan 14s linear infinite;
}

/* ── Cards float animation ── */
@keyframes card-float {
  0%,100% { transform: translateY(0); }
  50%      { transform: translateY(-3px); }
}
</style>"""

HIDE_SIDEBAR = """<style>
[data-testid="stSidebar"] { display: none !important; }
[data-testid="block-container"] { padding: 0 !important; max-width: 100% !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
</style>"""

# ─────────────────────────────────────────────────────────────────────────────
# SCAN BEAM INJECTION — added to every dashboard page
# ─────────────────────────────────────────────────────────────────────────────
SCAN_BEAM_HTML = '<div class="page-scan-beam"></div>'

# ─────────────────────────────────────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _get(endpoint: str, timeout: int = 6) -> dict:
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=timeout)
        r.raise_for_status(); return r.json()
    except Exception: return {"error": "offline"}


def _post(endpoint: str, timeout: int = 90, **kwargs) -> dict:
    try:
        r = requests.post(f"{API_BASE}{endpoint}", timeout=timeout, **kwargs)
        r.raise_for_status(); return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot reach API on port 8000"}
    except requests.exceptions.Timeout:
        return {"error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"error": str(e)}


def _check_api() -> bool:
    now = time.time()
    if now - st.session_state.api_last_check > 22:
        try:
            r = requests.get(f"{API_BASE}/health", timeout=2)
            st.session_state.api_online = r.status_code == 200
        except Exception:
            st.session_state.api_online = False
        st.session_state.api_last_check = now
    return st.session_state.api_online


def _norm(raw: dict) -> dict:
    if "error" in raw: return raw
    data = raw
    if "prediction" in raw: data = raw["prediction"]
    elif "report" in raw:
        final = raw.get("report", {}).get("final_verdict", {})
        data = {**raw, "verdict": final.get("risk_level","Unknown"),
                "confidence": final.get("confidence_percentage", 0)}
    v = (data.get("verdict") or data.get("label") or "Unknown").strip()
    c = float(data.get("confidence") or data.get("risk_score") or 0)
    if 0 < c <= 1: c *= 100
    c = round(c, 1)
    sigs = {}
    for k, val in data.get("signals", {}).items():
        try:
            fv = float(val or 0)
            sigs[k] = round(fv*100 if fv<=1 else fv, 1)
        except Exception:
            pass
    return {
        **data, "verdict": v, "confidence": c, "risk_score": c,
        "signals": sigs, "reasons": data.get("reasons", []),
        "evidence": data.get("evidence", []), "xai": data.get("xai", {}),
        "uncertainty": data.get("uncertainty", 0),
        "uncertainty_level": data.get("uncertainty_level","LOW"),
        "review_recommended": data.get("review_recommended", False),
        "signal_importance": data.get("signal_importance", {}),
        "pipeline_timing": data.get("pipeline_timing", {}),
        "original_context": data.get("signals",{}).get("original_context"),
    }


def _push_feed(verdict: str, conf: float, scan_type: str, snippet: str = ""):
    st.session_state.scan_feed = [{
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "verdict": verdict, "confidence": conf, "type": scan_type,
        "snippet": snippet[:34] + "…" if len(snippet) > 34 else snippet,
    }] + st.session_state.scan_feed[:9]


# ─────────────────────────────────────────────────────────────────────────────
# VERDICT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _vc(v): 
    v = (v or "").lower()
    if any(x in v for x in ["genuine","real","likely genuine"]): return "genuine"
    if "suspicious" in v: return "suspicious"
    if any(x in v for x in ["threat","fake","high","manipulation","phishing","scam","deepfake"]): return "threat"
    return "unknown"

def _vi(v): return {"genuine":"✅","suspicious":"⚠️","threat":"🚨"}.get(_vc(v),"❓")
def _vc_color(v): return {"genuine":"#00ff88","suspicious":"#ffb800","threat":"#ff1a1a","unknown":"#3d7a9a"}.get(_vc(v),"#3d7a9a")
def _unc_color(l): return {"LOW":"#00ffe5","MEDIUM":"#ffb800","HIGH":"#ff1a1a"}.get(l,"#3d7a9a")


# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS — Motion-driven
# ══════════════════════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────

def ui_inject_motion():
    """Inject CSS + scan beam on every dashboard page."""
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.markdown(SCAN_BEAM_HTML, unsafe_allow_html=True)


def ui_page_header(title: str, subtitle: str = "", icon: str = "🛡️"):
    st.markdown(f"""
    <div style="margin-bottom:1.2rem;padding-bottom:.8rem;
    border-bottom:1px solid rgba(0,255,229,.07);position:relative">
    <div style="position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,255,229,.25),transparent)"></div>
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
      <span style="font-size:1.25rem">{icon}</span>
      <span style="font-size:1.45rem;font-weight:700;color:#f0faff;
      font-family:'Exo 2',sans-serif;letter-spacing:-.5px">{title}</span>
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:.58rem;
    color:#0f2d3f;letter-spacing:1.8px;text-transform:uppercase">{subtitle}</div>
    </div>""", unsafe_allow_html=True)


def ui_cyber_section(label: str):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:9px;margin:.8rem 0 .5rem">
      <div style="width:3px;height:14px;background:var(--c,#00ffe5);
      border-radius:2px;box-shadow:0 0 6px rgba(0,255,229,.5)"></div>
      <span style="font-family:'Share Tech Mono',monospace;font-size:.58rem;
      color:#3d7a9a;letter-spacing:2.5px;text-transform:uppercase">{label}</span>
      <div style="flex:1;height:1px;background:rgba(0,255,229,.07)"></div>
    </div>""", unsafe_allow_html=True)


def ui_verdict_banner(verdict: str, confidence: float, uncertainty_level: str = "LOW"):
    vc  = _vc(verdict); icon = _vi(verdict)
    clr = _vc_color(verdict)
    unc = _unc_color(uncertainty_level)
    unc_icon = {"LOW":"🟢","MEDIUM":"🟡","HIGH":"🔴"}.get(uncertainty_level,"⚪")
    bg_map = {"genuine":"rgba(0,255,136,.05)","suspicious":"rgba(255,184,0,.05)",
              "threat":"rgba(255,26,26,.05)","unknown":"rgba(61,122,154,.04)"}
    bd_map = {"genuine":"rgba(0,255,136,.28)","suspicious":"rgba(255,184,0,.28)",
              "threat":"rgba(255,26,26,.28)","unknown":"rgba(61,122,154,.18)"}
    st.markdown(f"""
    <div style="background:{bg_map.get(vc,'')};border:1px solid {bd_map.get(vc,'')};
    border-radius:10px;padding:1.1rem 1.4rem;margin:.4rem 0 .7rem;
    display:flex;align-items:center;gap:12px;
    box-shadow:0 0 28px {clr}1a;position:relative;overflow:hidden;
    animation:card-float 4s ease-in-out infinite">
    <div style="position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,{clr}77,transparent)"></div>
    <span style="font-size:1.55rem">{icon}</span>
    <span style="font-size:1.18rem;font-weight:700;color:{clr};
    font-family:'Orbitron',monospace;letter-spacing:1px;text-shadow:0 0 10px {clr}66">{verdict}</span>
    <span style="margin-left:auto;font-family:'Share Tech Mono',monospace;
    font-size:.74rem;color:{clr};opacity:.85">{confidence:.1f}% confidence</span>
    <span style="font-family:'Share Tech Mono',monospace;font-size:.64rem;
    color:{unc}">{unc_icon} {uncertainty_level}</span>
    </div>""", unsafe_allow_html=True)


def ui_metric_grid(metrics: list):
    cols = st.columns(len(metrics))
    for (label, value, color), col in zip(metrics, cols):
        with col:
            st.markdown(f"""
            <div style="background:rgba(0,255,229,.02);border:1px solid rgba(0,255,229,.07);
            border-radius:9px;padding:.85rem;text-align:center;
            transition:all .25s;position:relative;overflow:hidden;
            animation:card-float 5s ease-in-out infinite {hash(label)%10*.1}s">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;
            background:linear-gradient(90deg,transparent,{color}44,transparent)"></div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:.52rem;
            color:#0f2d3f;letter-spacing:2px;text-transform:uppercase;margin-bottom:5px">{label}</div>
            <div style="font-family:'Orbitron',monospace;font-size:1.3rem;font-weight:700;
            color:{color};text-shadow:0 0 10px {color}44">{value}</div>
            </div>""", unsafe_allow_html=True)


def ui_signal_bars(sigs: dict):
    ui_cyber_section("Signal breakdown")
    for key, meta in SIGNAL_META.items():
        if key not in sigs: continue
        val = sigs[key]; bw = max(0, min(int(val), 100))
        color = meta["color"]
        st.markdown(f"""
        <div style="margin-bottom:9px">
        <div style="display:flex;justify-content:space-between;
        font-family:'Share Tech Mono',monospace;font-size:.62rem;
        color:#3d7a9a;margin-bottom:3px">
          <span>{meta['label']}</span>
          <span style="color:{color};font-weight:600">{val:.1f}%</span>
        </div>
        <div style="background:rgba(0,255,229,.05);border-radius:3px;height:4px;overflow:hidden;position:relative">
          <div style="width:{bw}%;height:4px;background:linear-gradient(90deg,{color}cc,{color});
          border-radius:3px;box-shadow:0 0 8px {color}77;
          transition:width .5s cubic-bezier(.4,0,.2,1);position:relative">
          <div style="position:absolute;right:0;top:-1px;width:4px;height:6px;
          background:{color};border-radius:1px;filter:brightness(1.5);box-shadow:0 0 5px {color}"></div>
          </div>
        </div>
        </div>""", unsafe_allow_html=True)


def ui_plotly_radar(sigs: dict):
    if not PLOTLY or not sigs: return
    keys  = [k for k in SIGNAL_META if k in sigs]
    cats  = [SIGNAL_META[k]["label"] for k in keys]
    vals  = [sigs[k] for k in keys]
    colors = [SIGNAL_META[k]["color"] for k in keys]
    if not cats: return
    fig = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]],
        fill="toself", fillcolor="rgba(0,255,229,.055)",
        line=dict(color="#00ffe5", width=1.8),
        marker=dict(size=6, color=colors+[colors[0]],
                    line=dict(color="#000509", width=1))
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,5,9,.9)",
            angularaxis=dict(tickfont=dict(size=9,color="#3d7a9a"),
                             linecolor="#0f2d3f", gridcolor="#071524"),
            radialaxis=dict(visible=True,range=[0,100],
                            tickfont=dict(size=7,color="#0f2d3f"),
                            gridcolor="#071524",linecolor="#071524"),
        ),
        showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24,r=24,t=14,b=14), height=235,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def ui_plotly_shap(importance: dict):
    if not PLOTLY or not importance: return
    items  = sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)
    labels = [SIGNAL_META.get(k, {}).get("label", k) for k, _ in items]
    values = [round(v*100, 1) for _, v in items]
    colors = ["#ff1a1a" if v > 0 else "#00ffe5" for v in values]
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h",
                           marker_color=colors, marker_opacity=.85,
                           marker_line=dict(width=0)))
    fig.add_vline(x=0, line_color="rgba(0,255,229,.2)", line_width=1)
    fig.update_layout(
        title=dict(text="Signal attribution (SHAP-style)",
                   font=dict(color="#3d7a9a",size=10,family="Share Tech Mono")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,5,9,.9)",
        height=238, margin=dict(l=0,r=10,t=36,b=10),
        xaxis=dict(color="#0f2d3f",gridcolor="#071524",
                   title="% contribution",
                   title_font=dict(color="#3d7a9a",size=9)),
        yaxis=dict(color="#a8d8ea",tickfont=dict(size=9)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def ui_attention_heatmap(attention_weights: dict):
    if not PLOTLY or not attention_weights: return
    matrix = attention_weights.get("block2")
    if not matrix: return
    labels = ["Text","Image","Video","Fact","Reused","Caption","WebCtrd"]
    fig = go.Figure(go.Heatmap(
        z=matrix, x=labels, y=labels,
        colorscale=[[0,"rgba(0,5,9,.95)"],[.5,"rgba(0,80,120,.6)"],[1,"#00ffe5"]],
        showscale=True,
        colorbar=dict(thickness=8, tickfont=dict(color="#3d7a9a",size=8)),
    ))
    fig.update_layout(
        title=dict(text="Attention weights — transformer layer 2",
                   font=dict(color="#3d7a9a",size=10,family="Share Tech Mono")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,5,9,.9)",
        height=256, margin=dict(l=0,r=0,t=36,b=0),
        xaxis=dict(color="#3d7a9a",tickfont=dict(size=8),title="Attended to"),
        yaxis=dict(color="#3d7a9a",tickfont=dict(size=8),
                   title="Attending from",autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def ui_confidence_gauge(confidence: float, title: str = "Confidence") -> go.Figure:
    clr = "#ff1a1a" if confidence > 65 else "#ffb800" if confidence > 45 else "#00ffe5"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=confidence,
        number={"suffix":"%","font":{"size":22,"color":"#f0faff","family":"Orbitron, monospace"}},
        title={"text":title,"font":{"size":10,"color":"#3d7a9a","family":"Share Tech Mono"}},
        gauge={
            "axis":{"range":[0,100],"tickcolor":"#0f2d3f","tickfont":{"color":"#0f2d3f","size":8}},
            "bar": {"color":clr,"thickness":.56},
            "bgcolor":"rgba(0,5,9,.92)","borderwidth":1,"bordercolor":"rgba(0,255,229,.08)",
            "steps":[{"range":[0,42],"color":"rgba(0,255,229,.03)"},
                     {"range":[42,65],"color":"rgba(255,184,0,.03)"},
                     {"range":[65,100],"color":"rgba(255,26,26,.04)"}],
        },
    ))
    fig.update_layout(height=168, paper_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=12,r=12,t=10,b=8), font={"color":"#a8d8ea"})
    return fig


def ui_clip_arc(similarity: float):
    if not PLOTLY or similarity < 0: return
    pct = round(similarity*100, 1)
    color = "#ff1a1a" if similarity < .15 else "#ffb800" if similarity < .4 else "#00ffe5"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=pct,
        number={"suffix":"%","font":{"size":20,"color":"#f0faff","family":"Orbitron, monospace"}},
        title={"text":"Image ↔ Caption alignment (CLIP)","font":{"size":10,"color":"#3d7a9a","family":"Share Tech Mono"}},
        gauge={
            "axis":{"range":[0,100],"tickcolor":"#0f2d3f","tickfont":{"color":"#0f2d3f","size":8}},
            "bar":{"color":color,"thickness":.54},
            "bgcolor":"rgba(0,5,9,.92)","borderwidth":1,"bordercolor":"rgba(0,255,229,.08)",
            "steps":[{"range":[0,15],"color":"rgba(255,26,26,.04)"},
                     {"range":[15,40],"color":"rgba(255,184,0,.03)"},
                     {"range":[40,100],"color":"rgba(0,255,229,.03)"}],
            "threshold":{"line":{"color":"#f0faff","width":1.5},"value":15},
        },
    ))
    fig.update_layout(height=185, paper_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=12,r=12,t=10,b=8))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def ui_pipeline_stages(stages: list):
    html = ""
    for stage, label, desc in PIPELINE_STAGES:
        matched = next((s for s in stages if s.get("stage") == stage), None)
        status  = matched.get("status","pending") if matched else "pending"
        if status == "done":    icon, color, bg = "✔","#00ffe5","rgba(0,255,229,.04)"
        elif status == "running": icon, color, bg = "▶","#0088ff","rgba(0,136,255,.04)"
        elif status == "error":   icon, color, bg = "✘","#ff1a1a","rgba(255,26,26,.04)"
        else:                      icon, color, bg = "○","#0f2d3f","transparent"
        html += f"""<div style="padding:5px 0;border-bottom:1px solid rgba(0,255,229,.04);
        display:flex;align-items:center;gap:9px;
        font-family:'Share Tech Mono',monospace;font-size:.66rem;background:{bg};padding:5px 8px;border-radius:3px;margin:1px 0">
        <span style="color:{color};width:12px">{icon}</span>
        <span style="color:{'#f0faff' if status in ('done','running') else '#0f2d3f'}">{label}</span>
        <span style="margin-left:auto;color:#0f2d3f;font-size:.54rem">{desc}</span>
        </div>"""
    st.markdown(f"""
    <div style="background:rgba(0,255,229,.015);border:1px solid rgba(0,255,229,.07);
    border-radius:8px;padding:8px 10px">{html}</div>""", unsafe_allow_html=True)


def ui_evidence_panel(evidence: list, title: str = "Web evidence"):
    if not evidence: return
    with st.expander(f"📎 {title} ({len(evidence)} sources)"):
        for i, e in enumerate(evidence[:10], 1):
            st.markdown(f"""
            <div style="background:rgba(0,255,229,.02);border:1px solid rgba(0,255,229,.06);
            border-radius:5px;padding:6px 10px;margin:2px 0;font-size:.74rem;color:#a8d8ea;
            font-family:'Exo 2',sans-serif;line-height:1.5">
            <span style="color:#3d7a9a;margin-right:6px;font-family:'Share Tech Mono',monospace">{i:02d}.</span>{e}
            </div>""", unsafe_allow_html=True)


def ui_xai_panel(xai: dict):
    if not xai: return
    with st.expander("💡 AI Explanation — Level 3 Natural Language", expanded=True):
        if xai.get("headline"):
            st.markdown(f"""
            <div style="font-family:'Orbitron',monospace;font-size:.88rem;
            font-weight:700;color:#f0faff;margin-bottom:8px;
            text-shadow:0 0 8px rgba(0,255,229,.2)">{xai['headline']}</div>""",
            unsafe_allow_html=True)
        if xai.get("body"):
            st.markdown(f"""
            <div style="font-family:'Exo 2',sans-serif;font-size:.8rem;
            color:#a8d8ea;line-height:1.75;margin-bottom:10px">{xai['body']}</div>""",
            unsafe_allow_html=True)
        for b in xai.get("bullet_points", []):
            st.markdown(f"""
            <div style="background:rgba(0,255,229,.02);
            border-left:2px solid rgba(0,255,229,.3);
            padding:5px 10px;margin:3px 0;font-size:.74rem;color:#a8d8ea;
            font-family:'Exo 2',sans-serif;border-radius:0 4px 4px 0">{b}</div>""",
            unsafe_allow_html=True)
        if xai.get("recommendation"):
            st.info(f"💡 **Recommendation:** {xai['recommendation']}")


def ui_reasons_panel(reasons: list):
    if not reasons:
        st.markdown("""
        <div style="background:rgba(0,255,136,.04);border:1px solid rgba(0,255,136,.2);
        border-radius:7px;padding:9px 13px;
        font-family:'Share Tech Mono',monospace;font-size:.68rem;color:#00ff88">
        ✓ No threat patterns detected — content appears legitimate</div>""",
        unsafe_allow_html=True); return
    with st.expander("🔍 Why this verdict?"):
        for r in reasons:
            st.markdown(f"""
            <div style="background:rgba(0,255,229,.02);
            border:1px solid rgba(0,255,229,.06);
            border-radius:5px;padding:6px 11px;margin:2px 0;
            font-size:.74rem;color:#a8d8ea">• {r}</div>""", unsafe_allow_html=True)


def ui_timing_panel(timing: dict):
    if not timing: return
    with st.expander("⏱ Pipeline timing breakdown"):
        html = ""
        total = timing.get("total", 0)
        for stage, ms in timing.items():
            if stage == "total": continue
            pct = round(ms/total*100) if total > 0 else 0
            html += f"""
            <div style="display:flex;align-items:center;gap:10px;
            font-family:'Share Tech Mono',monospace;font-size:.62rem;
            color:#3d7a9a;padding:4px 0;border-bottom:1px solid rgba(0,255,229,.04)">
            <span style="width:120px">{stage}</span>
            <div style="flex:1;background:rgba(0,255,229,.05);border-radius:2px;height:3px">
            <div style="width:{pct}%;height:3px;background:#00ffe5;border-radius:2px"></div>
            </div>
            <span style="color:#a8d8ea;width:50px;text-align:right">{ms:.3f}s</span>
            </div>"""
        st.markdown(f"""
        <div style="background:rgba(0,255,229,.015);
        border:1px solid rgba(0,255,229,.07);
        border-radius:7px;padding:10px 14px">{html}
        <div style="display:flex;justify-content:space-between;
        font-family:'Share Tech Mono',monospace;font-size:.62rem;
        padding-top:6px;border-top:1px solid rgba(0,255,229,.08);margin-top:4px">
        <span style="color:#3d7a9a">TOTAL</span>
        <span style="color:#00ffe5">{total:.3f}s</span></div>
        </div>""", unsafe_allow_html=True)


def ui_download_btns(result: dict, scan_type: str = "scan"):
    sigs = result.get("signals", {})
    flat = {"verdict": result["verdict"], "confidence": result["confidence"],
            **{f"sig_{k}": v for k, v in sigs.items()}}
    d1, d2, _ = st.columns([1,1,4])
    with d1:
        st.download_button("⬇ JSON", json.dumps(result, indent=2, default=str),
                           f"veritas_{scan_type}_{int(time.time())}.json", "application/json")
    with d2:
        st.download_button("⬇ CSV", pd.DataFrame([flat]).to_csv(index=False),
                           f"veritas_{scan_type}_{int(time.time())}.csv", "text/csv")


def ui_full_verdict(result: dict):
    if "error" in result:
        st.markdown(f"""
        <div style="background:rgba(255,26,26,.07);border:1px solid rgba(255,26,26,.28);
        border-radius:8px;padding:1rem;
        font-family:'Share Tech Mono',monospace;font-size:.74rem;color:#ff6060">
        🔴 API Error: {result['error']}</div>""", unsafe_allow_html=True); return

    verdict  = result["verdict"]; conf = result["confidence"]
    unc_lvl  = result.get("uncertainty_level","LOW")
    unc_val  = result.get("uncertainty", 0)
    sigs     = result.get("signals", {})
    reasons  = [r for r in result.get("reasons",[]) if r]
    evidence = result.get("evidence",[])
    xai      = result.get("xai",{})
    orig_ctx = result.get("original_context") or sigs.get("original_context")
    sig_imp  = result.get("signal_importance",{})
    attn_w   = result.get("attention_weights",{})
    clip_sim = sigs.get("clip_similarity", result.get("clip_similarity",-1))
    if isinstance(clip_sim, str):
        try: clip_sim = float(clip_sim)
        except: clip_sim = -1
    timing   = result.get("pipeline_timing",{})
    review   = result.get("review_recommended", False)

    # Banner
    ui_verdict_banner(verdict, conf, unc_lvl)

    # Original context alert
    if orig_ctx:
        st.markdown(f"""
        <div style="background:rgba(255,184,0,.06);
        border:1px solid rgba(255,184,0,.3);
        border-radius:8px;padding:10px 14px;margin:5px 0;
        font-family:'Share Tech Mono',monospace;font-size:.68rem;color:#ffd060;
        animation:card-float 4s ease-in-out infinite">
        📍 <strong>ORIGINAL CONTEXT IDENTIFIED:</strong> {orig_ctx}</div>""",
        unsafe_allow_html=True)

    # Review flag
    if review:
        st.warning("👤 **Human review recommended** — high uncertainty or conflicting modalities")

    # Metrics
    sig_count = len([v for v in sigs.values() if isinstance(v,(int,float)) and v > 20])
    total_t   = timing.get("total", 0)
    ui_metric_grid([
        ("Confidence",     f"{conf:.1f}%",          _vc_color(verdict)),
        ("Signals active", f"{sig_count}/{len(SIGNAL_META)}", "#00ffe5"),
        ("Uncertainty",    f"{unc_val:.3f}",         _unc_color(unc_lvl)),
        ("Pipeline time",  f"{total_t:.2f}s" if total_t else "—", "#3d7a9a"),
    ])
    st.markdown("<br>", unsafe_allow_html=True)

    # Signal charts
    col_sigs, col_viz = st.columns([1,1], gap="medium")
    with col_sigs:
        ui_signal_bars(sigs)
        if isinstance(clip_sim, (int,float)) and clip_sim >= 0:
            st.markdown("<br>", unsafe_allow_html=True)
            ui_clip_arc(float(clip_sim))
    with col_viz:
        if PLOTLY:
            ui_plotly_radar(sigs)
            if sig_imp:
                st.markdown("<br>", unsafe_allow_html=True)
                ui_plotly_shap(sig_imp)
        else:
            for k, m in SIGNAL_META.items():
                if k in sigs:
                    st.caption(m["label"]); st.progress(sigs[k]/100)

    # Attention heatmap
    if attn_w:
        st.markdown("<br>", unsafe_allow_html=True)
        ui_attention_heatmap(attn_w)

    # XAI
    if xai:
        st.markdown("<br>", unsafe_allow_html=True)
        ui_xai_panel(xai)

    # Evidence + reasons
    if evidence:
        st.markdown("<br>", unsafe_allow_html=True)
        ui_evidence_panel(evidence)
    if reasons:
        st.markdown("<br>", unsafe_allow_html=True)
        ui_reasons_panel(reasons)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        ui_reasons_panel([])

    # Timing
    if timing:
        st.markdown("<br>", unsafe_allow_html=True)
        ui_timing_panel(timing)

    st.markdown("<br>", unsafe_allow_html=True)
    ui_download_btns(result, "verdict")


def ui_clear(keys: list, uid: str):
    if st.button("🗑 Clear", key=f"clr_{uid}"):
        for k in keys:
            st.session_state[k] = None if k.endswith("result") else ""
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket pipeline
# ─────────────────────────────────────────────────────────────────────────────
def run_ws_pipeline(caption, article_text, image_bytes, video_bytes,
                    prog_ph, stage_ph):
    if not WS_AVAILABLE: return None
    import threading, json as _json
    result_h = [None]; stages_h = [[]]; done_ev = threading.Event()

    def on_msg(wsapp, msg):
        try:
            d = _json.loads(msg)
            stages_h[0].append(d)
            st.session_state.ws_stages = list(stages_h[0])
            prog_ph.progress(d.get("progress",0)/100)
            s = d.get("stage",""); st_ = d.get("status",""); p = d.get("progress",0)
            match = [(l,dc) for sg,l,dc in PIPELINE_STAGES if sg==s]
            label = match[0][0] if match else s
            icon  = "✅" if st_=="done" else ("❌" if st_=="error" else "⏳")
            stage_ph.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.7rem;color:#a8d8ea">'
                f'{icon} <strong style="color:#f0faff">{label}</strong> — {st_} ({p}%)</div>',
                unsafe_allow_html=True)
            if s=="final" and st_=="done": result_h[0] = d
        except Exception: pass

    def on_close(wsapp, *a): done_ev.set()
    def on_err(wsapp, e):
        st.session_state.ws_error = str(e); done_ev.set()

    try:
        payload = _json.dumps({
            "caption":      caption,
            "article_text": article_text,
            "image_b64":    base64.b64encode(image_bytes).decode() if image_bytes else "",
            "video_b64":    base64.b64encode(video_bytes).decode() if video_bytes else "",
        })
        wsapp = ws_lib.WebSocketApp(f"{WS_BASE}/ws/verify",
            on_open=lambda ws: ws.send(payload),
            on_message=on_msg, on_close=on_close, on_error=on_err)
        t = threading.Thread(target=wsapp.run_forever, daemon=True)
        t.start(); done_ev.wait(timeout=120)
    except Exception as e:
        st.session_state.ws_error = str(e)
    return result_h[0]


def rest_verify(caption, article_text, image_file, video_file) -> dict:
    files = {}
    data  = {"caption": caption, "article_text": article_text or ""}
    if image_file:
        image_file.seek(0); files["image"] = (image_file.name, image_file.read(), image_file.type)
    if video_file:
        video_file.seek(0); files["video"] = (video_file.name, video_file.read(), video_file.type)
    return _post("/verify", data=data, files=files or None, timeout=90)


# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# LANDING VIEW
# FIX: cursor animations now injected into Streamlit parent page via
#      st.markdown (not inside iframe which is sandboxed).
#      Login modal built with components.html that redirects via query params.
# ══════════════════════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────

# ── CURSOR + PARTICLE SYSTEM injected into parent Streamlit page ──────────────
# This is the KEY FIX: st.markdown runs in the parent page context, not an
# iframe — so mousemove events, canvas, and cursor DOM elements all work.
CURSOR_AND_PARTICLES_JS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');
* { cursor: none !important; }
#vt-orb {
  position:fixed;width:12px;height:12px;border-radius:50%;pointer-events:none;z-index:999999;
  background:radial-gradient(circle,#fff 0%,#00ffe5 45%,transparent 70%);
  box-shadow:0 0 8px #00ffe5,0 0 20px #00ffe5,0 0 40px rgba(0,255,229,.3);
  transform:translate(-50%,-50%);transition:width .1s,height .1s,box-shadow .15s;
}
#vt-ring {
  position:fixed;width:30px;height:30px;border-radius:50%;pointer-events:none;z-index:999998;
  border:1.5px solid rgba(0,255,229,.6);transform:translate(-50%,-50%);
  transition:width .18s cubic-bezier(.17,.67,.83,.67),height .18s cubic-bezier(.17,.67,.83,.67),
             border-color .2s,box-shadow .2s;
}
#vt-ring.hov { width:46px;height:46px;border-color:rgba(0,255,229,.9);box-shadow:0 0 16px rgba(0,255,229,.22); }
#vt-ring.clk { width:65px;height:65px;border-color:#00ffe5;box-shadow:0 0 36px rgba(0,255,229,.55);transition:all .08s; }
#vt-ring.threat { border-color:rgba(255,26,26,.8)!important; }
#vt-trail { position:fixed;inset:0;pointer-events:none;z-index:999997; }
#vt-bg    { position:fixed;inset:0;pointer-events:none;z-index:0; }
.vt-ripple {
  position:fixed;pointer-events:none;z-index:999996;border-radius:50%;
  border:1px solid #00ffe5;transform:translate(-50%,-50%) scale(0);
  animation:vt-ripple-out .7s ease-out forwards;
}
@keyframes vt-ripple-out {
  0%{width:0;height:0;opacity:.8;border-width:2px}
  100%{width:130px;height:130px;opacity:0;border-width:.5px}
}
.vt-shock {
  position:fixed;pointer-events:none;z-index:999995;border-radius:50%;
  background:radial-gradient(circle,rgba(0,255,229,.09),transparent 70%);
  transform:translate(-50%,-50%) scale(0);animation:vt-shock-out .5s ease-out forwards;
}
@keyframes vt-shock-out{0%{width:0;height:0;opacity:1}100%{width:180px;height:180px;opacity:0}}
/* Landing page scan beam */
#vt-scanbeam {
  position:fixed;left:0;right:0;height:1.5px;z-index:100;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(0,255,229,.4) 30%,rgba(0,255,229,.9) 50%,rgba(0,255,229,.4) 70%,transparent);
  filter:blur(.5px);animation:vt-beamfall 12s linear infinite;
}
@keyframes vt-beamfall{0%{top:-2px;opacity:0}4%{opacity:1}96%{opacity:1}100%{top:100vh;opacity:0}}
/* Page corner brackets */
.vt-corner{position:fixed;width:18px;height:18px;z-index:99;pointer-events:none}
.vt-corner::before,.vt-corner::after{content:'';position:absolute;background:rgba(0,255,229,.45)}
.vt-corner::before{width:100%;height:1.5px;top:0;left:0}
.vt-corner::after{width:1.5px;height:100%;top:0;left:0}
.vt-tl{top:8px;left:8px}.vt-tr{top:8px;right:8px;transform:scaleX(-1)}
.vt-bl{bottom:8px;left:8px;transform:scaleY(-1)}.vt-br{bottom:8px;right:8px;transform:scale(-1)}
</style>

<!-- Cursor elements injected into Streamlit parent -->
<div id="vt-orb"></div>
<div id="vt-ring"></div>
<canvas id="vt-trail"></canvas>
<canvas id="vt-bg"></canvas>
<div id="vt-scanbeam"></div>
<div class="vt-corner vt-tl"></div>
<div class="vt-corner vt-tr"></div>
<div class="vt-corner vt-bl"></div>
<div class="vt-corner vt-br"></div>

<script>
(function(){
'use strict';
// ── Cursor ───────────────────────────────────────────────────
const orb  = document.getElementById('vt-orb');
const ring = document.getElementById('vt-ring');
const trailCv = document.getElementById('vt-trail');
const bgCv    = document.getElementById('vt-bg');
const trailCtx = trailCv.getContext('2d');
const bgCtx    = bgCv.getContext('2d');

let mx=window.innerWidth/2, my=window.innerHeight/2;
let rx=mx, ry=my;
let trail=[];
const TRAIL_LEN=28;

function resize(){
  trailCv.width=bgCv.width=window.innerWidth;
  trailCv.height=bgCv.height=window.innerHeight;
}
window.addEventListener('resize',resize); resize();

document.addEventListener('mousemove',e=>{
  mx=e.clientX; my=e.clientY;
  orb.style.left=mx+'px'; orb.style.top=my+'px';
  trail.push({x:mx,y:my,t:Date.now()});
  if(trail.length>TRAIL_LEN) trail.shift();
  // Color near bottom login area
  const nearLogin = my > window.innerHeight * 0.78;
  if(nearLogin){ring.classList.add('threat');} else {ring.classList.remove('threat');}
});

// Lag ring
(function lag(){
  rx+=(mx-rx)*.11; ry+=(my-ry)*.11;
  ring.style.left=rx+'px'; ring.style.top=ry+'px';
  requestAnimationFrame(lag);
})();

// Click ripple
document.addEventListener('mousedown',e=>{
  ring.classList.add('clk');
  for(let i=0;i<3;i++){
    setTimeout(()=>{
      const r=document.createElement('div'); r.className='vt-ripple';
      r.style.left=e.clientX+'px'; r.style.top=e.clientY+'px';
      r.style.animationDelay=(i*.07)+'s';
      document.body.appendChild(r); setTimeout(()=>r.remove(),900);
    },i*35);
  }
  const s=document.createElement('div'); s.className='vt-shock';
  s.style.left=e.clientX+'px'; s.style.top=e.clientY+'px';
  document.body.appendChild(s); setTimeout(()=>s.remove(),600);
  setTimeout(()=>ring.classList.remove('clk'),320);
});

// Hover detection on interactive elements
function addHover(sel){
  document.querySelectorAll(sel).forEach(el=>{
    el.addEventListener('mouseenter',()=>ring.classList.add('hov'));
    el.addEventListener('mouseleave',()=>ring.classList.remove('hov'));
  });
}
// Run hover setup after Streamlit renders
setTimeout(()=>addHover('button,a,[data-testid="stButton"] button,input,textarea,[data-testid="stMetric"]'),800);
setInterval(()=>addHover('button,a,[data-testid="stButton"] button'),3000);

// ── Trail painter ────────────────────────────────────────────
function paintTrail(){
  trailCtx.clearRect(0,0,trailCv.width,trailCv.height);
  const now=Date.now();
  if(trail.length<2){requestAnimationFrame(paintTrail);return;}
  for(let i=1;i<trail.length;i++){
    const p0=trail[i-1],p1=trail[i];
    const age=now-p1.t; const life=Math.max(0,1-age/(TRAIL_LEN*16));
    const prog=i/trail.length; const alpha=life*prog*.65; const w=life*prog*2.8;
    trailCtx.beginPath();
    trailCtx.moveTo(p0.x,p0.y); trailCtx.lineTo(p1.x,p1.y);
    trailCtx.strokeStyle=`rgba(0,255,229,${alpha})`;
    trailCtx.lineWidth=w; trailCtx.lineCap='round'; trailCtx.stroke();
  }
  // Tip glow
  if(trail.length>0){
    const tip=trail[trail.length-1];
    const g=trailCtx.createRadialGradient(tip.x,tip.y,0,tip.x,tip.y,22);
    g.addColorStop(0,'rgba(0,255,229,0.18)'); g.addColorStop(1,'transparent');
    trailCtx.fillStyle=g; trailCtx.fillRect(tip.x-22,tip.y-22,44,44);
  }
  requestAnimationFrame(paintTrail);
}
paintTrail();

// ── Background: particles + grid ────────────────────────────
const W=()=>window.innerWidth, H=()=>window.innerHeight;
const N=Math.min(Math.floor(W()*H()/8500),90);
const pts=Array.from({length:N},()=>({
  x:Math.random()*W(),y:Math.random()*H(),
  vx:(Math.random()-.5)*.3,vy:(Math.random()-.5)*.3,
  r:Math.random()*1.6+.4,a:Math.random()*.35+.06,
  ph:Math.random()*Math.PI*2,ps:Math.random()*.02+.008,
  col:['0,255,229','0,100,255','155,48,255','0,255,136'][Math.floor(Math.random()*4)]
}));
const signals=Array.from({length:10},()=>({
  x:Math.random()*W(),y:Math.random()*H(),
  vx:(Math.random()-.5)*1.5,vy:(Math.random()-.5)*1.5,
  life:Math.random(),dec:Math.random()*.004+.002,
  col:['#ff1a1a','#ffb800','#00ffe5','#0088ff'][Math.floor(Math.random()*4)]
}));

let gridT=0;
function drawBg(){
  bgCtx.clearRect(0,0,W(),H());
  gridT+=.003;
  // Grid
  const GRID=58, off=(gridT*18)%GRID;
  bgCtx.strokeStyle='rgba(0,255,229,0.022)'; bgCtx.lineWidth=.5;
  for(let x=off;x<W();x+=GRID){bgCtx.beginPath();bgCtx.moveTo(x,0);bgCtx.lineTo(x,H());bgCtx.stroke();}
  for(let y=off;y<H();y+=GRID){bgCtx.beginPath();bgCtx.moveTo(0,y);bgCtx.lineTo(W(),y);bgCtx.stroke();}
  // Grid warp near cursor
  const WR=150;
  for(let x=0;x<W();x+=GRID){for(let y=0;y<H();y+=GRID){
    const dx=x-mx,dy=y-my,d=Math.sqrt(dx*dx+dy*dy);
    if(d<WR){
      const f=(1-d/WR)*7;
      const wx=x+(dx/d)*f*Math.sin(gridT*.04);
      const wy=y+(dy/d)*f*Math.cos(gridT*.04);
      bgCtx.beginPath();bgCtx.arc(wx,wy,1,0,Math.PI*2);
      bgCtx.fillStyle=`rgba(0,255,229,${(1-d/WR)*.45})`;bgCtx.fill();
    }
  }}
  // Depth orbs
  [[W()*.3+Math.sin(gridT)*80,H()*.4+Math.cos(gridT*.7)*70,320,'0,255,229'],
   [W()*.72+Math.cos(gridT)*100,H()*.55+Math.sin(gridT*.8)*80,240,'100,40,255']
  ].forEach(([nx,ny,nr,c])=>{
    const gr=bgCtx.createRadialGradient(nx,ny,0,nx,ny,nr);
    gr.addColorStop(0,`rgba(${c},0.032)`);gr.addColorStop(1,'transparent');
    bgCtx.fillStyle=gr;bgCtx.fillRect(0,0,W(),H());
  });
  // Particles
  pts.forEach(p=>{
    const dx=mx-p.x,dy=my-p.y,d=Math.sqrt(dx*dx+dy*dy);
    if(d<190&&d>0){p.vx+=dx/d*.016;p.vy+=dy/d*.016;}
    p.vx*=.993;p.vy*=.993;p.x+=p.vx;p.y+=p.vy;
    if(p.x<0||p.x>W())p.vx*=-1;if(p.y<0||p.y>H())p.vy*=-1;
    p.ph+=p.ps;const a=p.a*(.5+.5*Math.sin(p.ph));
    bgCtx.beginPath();bgCtx.arc(p.x,p.y,p.r,0,Math.PI*2);
    bgCtx.fillStyle=`rgba(${p.col},${a})`;bgCtx.fill();
    pts.forEach(q=>{if(q===p)return;const ex=p.x-q.x,ey=p.y-q.y,ed=Math.sqrt(ex*ex+ey*ey);
      if(ed<115){bgCtx.beginPath();bgCtx.moveTo(p.x,p.y);bgCtx.lineTo(q.x,q.y);
        bgCtx.strokeStyle=`rgba(0,255,229,${(1-ed/115)*.07})`;bgCtx.lineWidth=.5;bgCtx.stroke();}
    });
  });
  // Signal traces
  signals.forEach(s=>{
    const dx=mx-s.x,dy=my-s.y,d=Math.sqrt(dx*dx+dy*dy);
    if(d<200&&d>0){s.vx+=dx/d*.007;s.vy+=dy/d*.007;}
    s.vx*=.984;s.vy*=.984;s.x+=s.vx;s.y+=s.vy;s.life-=s.dec;
    if(s.life<=0||s.x<0||s.x>W()||s.y<0||s.y>H()){
      s.x=Math.random()*W();s.y=Math.random()*H();
      s.vx=(Math.random()-.5)*1.5;s.vy=(Math.random()-.5)*1.5;
      s.life=1;s.dec=Math.random()*.004+.002;
      s.col=['#ff1a1a','#ffb800','#00ffe5','#0088ff'][Math.floor(Math.random()*4)];
    }
    const r=parseInt(s.col.slice(1,3),16),g=parseInt(s.col.slice(3,5),16),b=parseInt(s.col.slice(5,7),16);
    bgCtx.beginPath();bgCtx.arc(s.x,s.y,2,0,Math.PI*2);
    bgCtx.fillStyle=`rgba(${r},${g},${b},${s.life})`;bgCtx.fill();
    bgCtx.beginPath();bgCtx.moveTo(s.x,s.y);bgCtx.lineTo(s.x-s.vx*6,s.y-s.vy*6);
    bgCtx.strokeStyle=`rgba(${r},${g},${b},${s.life*.25})`;bgCtx.lineWidth=.7;bgCtx.stroke();
  });
  // Cursor glow halo
  if(mx>0){const cg=bgCtx.createRadialGradient(mx,my,0,mx,my,100);
    cg.addColorStop(0,'rgba(0,255,229,0.055)');cg.addColorStop(1,'transparent');
    bgCtx.fillStyle=cg;bgCtx.fillRect(0,0,W(),H());
  }
  requestAnimationFrame(drawBg);
}
drawBg();
})();
</script>
"""

if st.session_state.view == "landing":
    st.markdown(HIDE_SIDEBAR, unsafe_allow_html=True)

    # ── INJECT CURSOR + PARTICLE SYSTEM into parent Streamlit page ────────────
    # KEY FIX: This runs in the PARENT page, not an iframe.
    # cursor elements, canvas, and mousemove all work correctly here.
    st.markdown(CURSOR_AND_PARTICLES_JS, unsafe_allow_html=True)

    # ── Full-screen landing HTML (background content in iframe) ───────────────
    components.html(LANDING_HTML, height=820, scrolling=False)

    # ── Check query params (postMessage bridge from iframe JS) ────────────────
    qp = st.query_params
    if "vu" in qp and "vp" in qp:
        u  = qp.get("vu","").lower().strip()
        ud = _AUTH.get(u)
        if ud and ud["password"] == qp.get("vp",""):
            st.session_state.update({"logged_in":True,"username":u,
                                     "role":ud["role"],"view":"dashboard"})
            st.query_params.clear(); st.rerun()

    # ── LOGIN SECTION — full styled panel (ALWAYS VISIBLE, never hidden) ──────
    st.markdown("""
    <style>
    /* Make Streamlit layout transparent so bg canvas shows through */
    [data-testid="stAppViewContainer"],[data-testid="stApp"],
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],
    [data-testid="block-container"]{background:transparent!important}
    /* Login section styling */
    .login-section{
      max-width:520px;margin:0 auto;padding:0 20px 40px;
    }
    .login-divider{
      display:flex;align-items:center;gap:12px;margin:12px 0;
    }
    .login-divider::before,.login-divider::after{
      content:'';flex:1;height:1px;background:rgba(0,255,229,.12);
    }
    .login-divider span{
      font-family:'Share Tech Mono',monospace;font-size:.54rem;
      color:#3d7a9a;letter-spacing:2px;white-space:nowrap;text-transform:uppercase;
    }
    .google-btn{
      width:100%;display:flex;align-items:center;justify-content:center;gap:10px;
      background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.12);
      border-radius:5px;padding:11px 16px;cursor:pointer;
      font-family:'Exo 2',sans-serif;font-size:.82rem;font-weight:500;
      color:#e8eaed;transition:all .22s;margin-bottom:14px;
      text-decoration:none;
    }
    .google-btn:hover{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.25);}
    .google-btn svg{flex-shrink:0}
    .role-pills{display:flex;gap:6px;margin-bottom:14px;}
    .role-pill{
      flex:1;text-align:center;padding:7px 4px;
      font-family:'Share Tech Mono',monospace;font-size:.58rem;
      font-weight:600;letter-spacing:1.5px;text-transform:uppercase;
      background:transparent;color:#3d7a9a;border:1px solid rgba(0,255,229,.12);
      border-radius:4px;cursor:pointer;transition:all .18s;
    }
    .role-pill.active,.role-pill:hover{
      background:rgba(0,255,229,.08);color:#00ffe5;border-color:rgba(0,255,229,.35);
    }
    .login-header{
      text-align:center;padding:20px 0 18px;
    }
    .login-brand{
      font-family:'Orbitron',monospace;font-size:.75rem;font-weight:800;
      letter-spacing:3px;color:#00ffe5;margin-bottom:4px;
    }
    .login-title{
      font-family:'Exo 2',sans-serif;font-size:1.35rem;font-weight:700;
      color:#f0faff;margin-bottom:3px;
    }
    .login-sub{
      font-family:'Share Tech Mono',monospace;font-size:.58rem;
      color:#3d7a9a;letter-spacing:1.2px;
    }
    .login-card{
      background:rgba(0,8,18,.85);border:1px solid rgba(0,255,229,.14);
      border-radius:12px;padding:26px 24px 20px;
      backdrop-filter:blur(24px);position:relative;overflow:hidden;
    }
    .login-card::before{
      content:'';position:absolute;top:0;left:0;right:0;height:1px;
      background:linear-gradient(90deg,transparent,rgba(0,255,229,.5),transparent);
    }
    .login-corner{position:absolute;width:13px;height:13px}
    .login-corner::before,.login-corner::after{content:'';position:absolute;background:#00ffe5;opacity:.75}
    .login-corner::before{width:100%;height:1.5px;top:0;left:0}
    .login-corner::after{width:1.5px;height:100%;top:0;left:0}
    .lc-tl{top:-1px;left:-1px}.lc-tr{top:-1px;right:-1px;transform:scaleX(-1)}
    .lc-bl{bottom:-1px;left:-1px;transform:scaleY(-1)}.lc-br{bottom:-1px;right:-1px;transform:scale(-1)}
    /* Streamlit inputs inherit login-card bg fix */
    .login-card [data-testid="stTextInput"] input{
      background:rgba(0,255,229,.03)!important;
      border:1px solid rgba(0,255,229,.15)!important;
    }
    .login-card [data-testid="stButton"] button{
      font-family:'Orbitron',monospace!important;font-size:.64rem!important;
      font-weight:700!important;letter-spacing:2px!important;
    }
    .login-card [data-testid="stButton"] button[kind="primary"]{
      background:#00ffe5!important;color:#000!important;
      box-shadow:0 0 20px rgba(0,255,229,.25)!important;
    }
    /* Error message */
    .vt-err{
      background:rgba(255,26,26,.08);border:1px solid rgba(255,26,26,.25);
      border-radius:5px;padding:8px 12px;margin-bottom:10px;
      font-family:'Share Tech Mono',monospace;font-size:.64rem;color:#ff6060;
      letter-spacing:.5px;
    }
    </style>

    <div class="login-section">
      <div class="login-header">
        <div class="login-brand">VERITAS</div>
        <div class="login-title">Intelligence Authentication</div>
        <div class="login-sub">AUTHORISED PERSONNEL ONLY · CLEARANCE REQUIRED</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Google Sign-In button (styled, shows info message when clicked)
    st.markdown("""
    <div style="max-width:520px;margin:0 auto;padding:0 20px 6px">
    <a class="google-btn" href="#" onclick="this.textContent='Google auth not configured — use password below';this.style.color='#ffb800';return false;">
      <svg width="18" height="18" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
      </svg>
      Continue with Google
    </a>
    <div class="login-divider"><span>or sign in with credentials</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Role selector pills ───────────────────────────────────────────────────
    if "login_role" not in st.session_state:
        st.session_state.login_role = "admin"

    st.markdown('<div style="max-width:520px;margin:0 auto;padding:0 20px 8px"><div class="role-pills">', unsafe_allow_html=True)
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        if st.button("⚡ ADMIN",   use_container_width=True, key="role_admin"):
            st.session_state.login_role = "admin"
    with rc2:
        if st.button("🔍 ANALYST", use_container_width=True, key="role_analyst"):
            st.session_state.login_role = "analyst"
    with rc3:
        if st.button("👁 VIEWER",  use_container_width=True, key="role_viewer"):
            st.session_state.login_role = "viewer"
    st.markdown('</div></div>', unsafe_allow_html=True)

    # ── Credentials card ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="max-width:520px;margin:0 auto;padding:0 20px 30px">
    <div class="login-card">
      <div class="login-corner lc-tl"></div><div class="login-corner lc-tr"></div>
      <div class="login-corner lc-bl"></div><div class="login-corner lc-br"></div>
    """, unsafe_allow_html=True)

    # Show current role hint
    role_hints = {"admin":"admin / admin123","analyst":"analyst / analyst123","viewer":"viewer / viewer123"}
    current_role = st.session_state.get("login_role","admin")
    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace;font-size:.56rem;
    color:#3d7a9a;letter-spacing:1.5px;margin-bottom:12px;text-transform:uppercase">
    Selected role: <span style="color:#00ffe5">{current_role.upper()}</span>
    &nbsp;·&nbsp; Hint: <span style="color:#3d7a9a">{role_hints[current_role]}</span>
    </div>
    """, unsafe_allow_html=True)

    if "login_error" in st.session_state and st.session_state.login_error:
        st.markdown(f'<div class="vt-err">⚠ {st.session_state.login_error}</div>', unsafe_allow_html=True)
        st.session_state.login_error = ""

    lu = st.text_input("OPERATOR ID",    placeholder="Enter operator ID",  key="lu_main", label_visibility="visible")
    lp = st.text_input("ACCESS KEY",     placeholder="Enter access key",   key="lp_main", type="password", label_visibility="visible")

    cb_col, _ = st.columns([1, 2])
    with cb_col:
        st.checkbox("Maintain session", value=True, key="keep_session")

    if st.button("ACCESS INTELLIGENCE PLATFORM →", type="primary", use_container_width=True, key="login_main"):
        u  = (lu or "").lower().strip()
        ud = _AUTH.get(u)
        if ud and ud["password"] == lp:
            st.session_state.update({"logged_in":True,"username":u,
                                     "role":ud["role"],"view":"dashboard",
                                     "login_error":""})
            st.rerun()
        else:
            st.session_state.login_error = "AUTHENTICATION FAILED — INVALID CREDENTIALS"
            st.rerun()

    st.markdown("""
    </div>
    <div style="text-align:center;margin-top:10px;font-family:'Share Tech Mono',monospace;
    font-size:.56rem;color:#3d7a9a">
    No access? Contact system administrator
    </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Admin quick-access bar (always visible at bottom per your requirement) ─
    st.divider()
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:.58rem;
    color:#3d7a9a;letter-spacing:1.5px;text-transform:uppercase;
    text-align:center;margin-bottom:8px">
    ▶ QUICK ACCESS — ADMIN PANEL
    </div>""", unsafe_allow_html=True)
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("⚡ Admin Login", use_container_width=True, key="qa_admin"):
            st.session_state.update({"logged_in":True,"username":"admin",
                                     "role":"admin","view":"dashboard"})
            st.rerun()
    with qa2:
        if st.button("🔍 Analyst Login", use_container_width=True, key="qa_analyst"):
            st.session_state.update({"logged_in":True,"username":"analyst",
                                     "role":"analyst","view":"dashboard"})
            st.rerun()
    with qa3:
        if st.button("👁 Viewer Login", use_container_width=True, key="qa_viewer"):
            st.session_state.update({"logged_in":True,"username":"viewer",
                                     "role":"viewer","view":"dashboard"})
            st.rerun()

    st.markdown("""
    <div style="text-align:center;font-family:'Share Tech Mono',monospace;
    font-size:.52rem;color:#0f2d3f;letter-spacing:1px;margin-top:6px">
    admin:admin123 · analyst:analyst123 · viewer:viewer123
    </div>""", unsafe_allow_html=True)

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD VIEW
# ══════════════════════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────
ui_inject_motion()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Motion-driven command panel
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    uc = _AUTH.get(st.session_state.username, {}).get("color","#00ffe5")
    cl = _AUTH.get(st.session_state.username, {}).get("clearance","CLASSIFIED")

    st.markdown(f"""
    <div style="padding:14px 11px 11px;border-bottom:1px solid rgba(0,255,229,.06)">
      <div style="display:flex;align-items:center;gap:9px">
        <div style="width:27px;height:27px;border:1.5px solid #00ffe5;border-radius:6px;
        display:flex;align-items:center;justify-content:center;
        box-shadow:0 0 10px rgba(0,255,229,.18)">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#00ffe5" stroke-width="2">
            <path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z"/>
          </svg>
        </div>
        <div>
          <div style="font-family:'Orbitron',monospace;font-size:.68rem;
          font-weight:800;letter-spacing:2px;color:#00ffe5">VERITAS</div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:.44rem;
          color:#0f2d3f;letter-spacing:1.5px">APEX · V{VERSION}</div>
        </div>
      </div>
    </div>
    <div style="margin:7px 8px 6px;background:rgba(0,255,229,.025);
    border:1px solid rgba(0,255,229,.08);border-radius:7px;padding:8px 10px;
    display:flex;align-items:center;gap:8px;
    animation:card-float 5s ease-in-out infinite">
      <div style="width:26px;height:26px;border-radius:50%;background:{uc};
      display:flex;align-items:center;justify-content:center;
      font-family:'Orbitron',monospace;font-size:.68rem;font-weight:700;color:#000;
      box-shadow:0 0 8px {uc}88">
        {st.session_state.username[0].upper()}
      </div>
      <div>
        <div style="font-size:.76rem;font-weight:600;color:#f0faff">
          {st.session_state.username.title()}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:.5rem;
        color:#3d7a9a;letter-spacing:1.5px;text-transform:uppercase">
          {st.session_state.role} · {cl}</div>
      </div>
    </div>
    <div style="padding:3px 11px 2px;font-family:'Share Tech Mono',monospace;
    font-size:.5rem;letter-spacing:2.5px;color:#0f2d3f;text-transform:uppercase">
    Navigation</div>
    """, unsafe_allow_html=True)

    pages = [
        "🔬 Veritas Scanner", "📰 Text Scanner", "🖼 Image Scanner",
        "🎬 Video Scanner", "🔀 Multimodal Verdict", "📦 Batch Scan",
        "📊 Analytics", "🕰 History",
    ]
    if st.session_state.role == "admin":
        pages += ["⚙ Model Control", "📈 Drift Monitor", "🗃 Hash DB"]

    page = st.radio("nav", pages, label_visibility="collapsed")

    st.markdown('<div style="height:1px;background:rgba(0,255,229,.06);margin:6px 0"></div>', unsafe_allow_html=True)

    # API indicator
    online = _check_api()
    pc = "#00ffe5" if online else "#ff1a1a"
    st.markdown(f"""
    <div style="padding:0 11px 6px;display:flex;align-items:center;gap:6px">
      <div style="width:5px;height:5px;border-radius:50%;background:{pc};
      box-shadow:0 0 5px {pc};animation:pulse-anim 2s ease-in-out infinite"></div>
      <span style="font-family:'Share Tech Mono',monospace;font-size:.6rem;color:{pc}">
      {"API Online" if online else "API Offline"}</span>
    </div>
    <style>@keyframes pulse-anim{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}</style>
    """, unsafe_allow_html=True)

    # Scan feed
    if st.session_state.scan_feed:
        st.markdown('<div style="padding:2px 11px;font-family:\'Share Tech Mono\',monospace;font-size:.5rem;letter-spacing:2px;color:#0f2d3f;text-transform:uppercase;margin-top:3px">Recent scans</div>', unsafe_allow_html=True)
        for entry in st.session_state.scan_feed[:4]:
            ec = {"genuine":"#00ff88","suspicious":"#ffb800","threat":"#ff1a1a"}.get(_vc(entry["verdict"]),"#3d7a9a")
            st.markdown(f"""
            <div style="margin:2px 8px;background:rgba(0,255,229,.02);
            border-left:2px solid {ec};padding:4px 7px;border-radius:0 4px 4px 0">
              <div style="display:flex;justify-content:space-between;
              font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#0f2d3f">
                <span>{_vi(entry['verdict'])} {entry['type']}</span>
                <span>{entry['time']}</span>
              </div>
              <div style="font-size:.6rem;color:#a8d8ea;margin-top:1px">{entry['snippet'] or entry['verdict']}</div>
              <div style="font-size:.56rem;color:{ec}">{entry['confidence']:.0f}%</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⎋ Sign out", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: VERITAS SCANNER
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🔬 Veritas Scanner":
    ui_page_header("Veritas Scanner",
        "SIGNATURE · IMAGE + CAPTION + ARTICLE → FULL PIPELINE · REAL-TIME WEBSOCKET STREAMING",
        "🔬")
    ui_clear(["verify_result"], "veritas")

    col_form, col_prev = st.columns([1,1], gap="large")
    with col_form:
        caption      = st.text_input("📝 Caption / headline *",
                         placeholder="e.g. Devastating J&K floods 2026 — thousands displaced")
        article_text = st.text_area("📄 Article text (optional)", height=95,
                         placeholder="Paste full article for NLI fact-checking…")
    with col_prev:
        image_file = st.file_uploader("🖼 Image (optional)",
                         type=["jpg","jpeg","png","webp"], key="v_img")
        video_file = st.file_uploader("🎬 Video (optional)",
                         type=["mp4","mov","avi"], key="v_vid")
    if image_file: col_prev.image(image_file, use_container_width=True)
    if video_file: col_prev.video(video_file)

    st.divider()

    run = st.button("🚀 Run Full Veritas Pipeline",
                    type="primary", use_container_width=True,
                    disabled=not (caption or image_file))

    if run:
        image_bytes = image_file.read() if image_file else None
        video_bytes = video_file.read() if video_file else None
        st.session_state.verify_result = None
        st.session_state.ws_stages     = []
        st.session_state.ws_error      = None

        st.markdown("### ⚙ Pipeline executing…")
        prog_bar  = st.progress(0)
        stage_txt = st.empty()

        raw = None
        if WS_AVAILABLE:
            raw = run_ws_pipeline(caption, article_text or "", image_bytes,
                                  video_bytes, prog_bar, stage_txt)
        else:
            stage_txt.markdown(
                '<div style="font-family:\'Share Tech Mono\',monospace;font-size:.7rem;'
                'color:#0088ff">▶ Running via REST API…</div>', unsafe_allow_html=True)
            prog_bar.progress(.1)
            raw = rest_verify(caption, article_text or "", image_file, video_file)
            prog_bar.progress(1.0)

        if raw:
            verdict_data = raw.get("verdict", raw) if isinstance(raw, dict) else raw
            result = _norm(verdict_data if isinstance(verdict_data, dict) else raw)
            result["xai"] = raw.get("xai", {}) if isinstance(raw, dict) else {}
            st.session_state.verify_result = result
            if "error" not in result:
                _push_feed(result["verdict"], result["confidence"], "Veritas", caption)

        if st.session_state.ws_error:
            st.warning(f"ℹ️ {st.session_state.ws_error}")
        stage_txt.empty()

    if st.session_state.ws_stages:
        with st.expander("🔧 Pipeline execution log"):
            ui_pipeline_stages(st.session_state.ws_stages)

    if st.session_state.verify_result:
        st.divider()
        ui_full_verdict(st.session_state.verify_result)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TEXT SCANNER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📰 Text Scanner":
    ui_page_header("Real-Time Text Scanner",
        "UCIE · ROBERTA-ISOT · DEBERTA-NLI (8 LABELS) · TWITTER-ROBERTA · 30+ HEURISTIC RULES",
        "📰")
    ui_clear(["text_result","text_input"], "text")

    ti = st.text_area("Paste content to analyze",
                       value=st.session_state.text_input or "",
                       height=155,
                       placeholder="Paste headline, social post, email, WhatsApp message, or article…")
    c1, c2, c3 = st.columns([3,1,1])
    with c1: run = st.button("🔍 Analyze Text", type="primary", use_container_width=True)
    with c2: st.caption(f"{len(ti.split()) if ti else 0} words")
    with c3: st.caption(f"{len(ti)} chars")

    if run:
        if not ti.strip(): st.warning("Enter text to analyze.")
        else:
            st.session_state.text_input = ti
            with st.spinner("Running UCIE 5-signal ensemble…"):
                result = _norm(_post("/predict", data={"text": ti}))
                st.session_state.text_result = result
                if "error" not in result:
                    _push_feed(result["verdict"], result["confidence"], "Text", ti)

    if st.session_state.text_result:
        result = st.session_state.text_result; st.divider()
        if PLOTLY and "error" not in result:
            gc1, gc2 = st.columns([1,2])
            with gc1:
                fig = ui_confidence_gauge(result["confidence"])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                unc_clr = _unc_color(result.get("uncertainty_level","LOW"))
                st.markdown(f"""
                <div style="text-align:center;font-family:'Share Tech Mono',monospace;
                font-size:.58rem;color:{unc_clr};letter-spacing:1px;margin-top:-8px">
                UNCERTAINTY: {result.get('uncertainty_level','—')} ({result.get('uncertainty',0):.3f})</div>""",
                unsafe_allow_html=True)
            with gc2: ui_full_verdict(result)
        else: ui_full_verdict(result)

        # Detailed UCIE breakdown
        if result.get("signal_breakdown"):
            with st.expander("🔬 UCIE signal breakdown — all 5 signals"):
                for sig_name, sig_data in result["signal_breakdown"].items():
                    if not isinstance(sig_data, dict): continue
                    meta  = SIGNAL_META.get(sig_name, {"label":sig_name,"color":"#3d7a9a"})
                    fs    = sig_data.get("fake_score",0)
                    conf_ = sig_data.get("confidence",0)
                    eff_w = sig_data.get("effective_weight",0)
                    st.markdown(f"""
                    <div style="background:rgba(0,255,229,.02);
                    border:1px solid rgba(0,255,229,.06);
                    border-radius:6px;padding:8px 12px;margin:3px 0">
                    <div style="display:flex;justify-content:space-between;margin-bottom:5px">
                      <span style="font-family:'Share Tech Mono',monospace;font-size:.62rem;
                      color:{meta['color']};font-weight:600">{meta['label']}</span>
                      <span style="font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#3d7a9a">
                      fake={fs:.3f} · conf={conf_:.3f} · eff_w={eff_w:.4f}</span>
                    </div>
                    <div style="background:rgba(0,255,229,.05);border-radius:2px;height:3px;overflow:hidden">
                      <div style="width:{min(int(fs*100),100)}%;height:3px;background:{meta['color']};
                      box-shadow:0 0 5px {meta['color']}88"></div>
                    </div></div>""", unsafe_allow_html=True)

        # Feedback
        st.divider()
        ui_cyber_section("Was this verdict correct?")
        fb1, fb2, _ = st.columns([1,1,4])
        with fb1:
            if st.button("✅ Correct", use_container_width=True):
                _post("/feedback", json={"text":ti,"feedback":"correct","verdict":result.get("verdict")})
                st.success("Confirmed — thank you!")
        with fb2:
            if st.button("❌ Incorrect", use_container_width=True):
                _post("/feedback", json={"text":ti,"feedback":"incorrect","verdict":result.get("verdict")})
                st.warning("Flagged for retraining pipeline.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: IMAGE SCANNER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🖼 Image Scanner":
    ui_page_header("Image Forensics Scanner",
        "ELA · EXIF ANOMALY · PHASH FINGERPRINT · CLIP SEMANTIC · REVERSE IMAGE SEARCH",
        "🖼")
    ui_clear(["image_result"], "img")

    img_up = st.file_uploader("Drag and drop an image or click to browse",
                               type=["jpg","jpeg","png","webp","bmp"], key="img_up")
    if img_up:
        ci, cm = st.columns([2,1])
        with ci: st.image(img_up, use_container_width=True, caption=img_up.name)
        with cm:
            st.markdown(f"""
            <div style="background:rgba(0,255,229,.02);border:1px solid rgba(0,255,229,.07);
            border-radius:9px;padding:13px;animation:card-float 5s ease-in-out infinite">
            <div style="font-family:'Share Tech Mono',monospace;font-size:.54rem;
            letter-spacing:2px;color:#3d7a9a;text-transform:uppercase;margin-bottom:9px">File info</div>
            <div style="font-size:.74rem;color:#a8d8ea;margin-bottom:4px">
            Name: <span style="color:#f0faff">{img_up.name[:26]}</span></div>
            <div style="font-size:.74rem;color:#a8d8ea;margin-bottom:4px">
            Type: <span style="color:#f0faff">{img_up.type}</span></div>
            <div style="font-size:.74rem;color:#a8d8ea">
            Size: <span style="color:#f0faff">{img_up.size/1024:.1f} KB</span></div>
            </div>""", unsafe_allow_html=True)

    if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
        if not img_up: st.warning("Upload an image first.")
        else:
            with st.spinner("Running ELA + EXIF + pHash forensics…"):
                img_up.seek(0)
                result = _norm(_post("/analyze-image", files={"file": img_up}))
                st.session_state.image_result = result
                if "error" not in result:
                    _push_feed(result["verdict"], result["confidence"], "Image", img_up.name)

    if st.session_state.image_result:
        st.divider(); ui_full_verdict(st.session_state.image_result)
        with st.expander("🔩 Raw forensics JSON"): st.json(st.session_state.image_result)


elif page == "🎬 Video Scanner":
    ui_page_header("Deepfake Video Scanner",
        "FRAME EXTRACTION · FACE DETECTION · GAN ARTIFACTS · TEMPORAL CONSISTENCY CHECK",
        "🎬")
    ui_clear(["video_result"], "vid")

    vid_up = st.file_uploader("Drag and drop a video",
                               type=["mp4","mov","avi","mpeg4","webm"], key="vid_up")
    if vid_up:
        cv, cm = st.columns([2,1])
        with cv: st.video(vid_up)
        with cm:
            st.markdown(f"""
            <div style="background:rgba(0,255,229,.02);border:1px solid rgba(0,255,229,.07);
            border-radius:9px;padding:13px;animation:card-float 4.5s ease-in-out infinite">
            <div style="font-family:'Share Tech Mono',monospace;font-size:.54rem;
            letter-spacing:2px;color:#3d7a9a;text-transform:uppercase;margin-bottom:9px">File info</div>
            <div style="font-size:.74rem;color:#a8d8ea;margin-bottom:4px">
            Name: <span style="color:#f0faff">{vid_up.name[:24]}</span></div>
            <div style="font-size:.74rem;color:#a8d8ea">
            Size: <span style="color:#f0faff">{vid_up.size/(1024*1024):.2f} MB</span></div>
            </div>""", unsafe_allow_html=True)

    if st.button("🔍 Analyze Video", type="primary", use_container_width=True):
        if not vid_up: st.warning("Upload a video first.")
        else:
            with st.spinner("Extracting frames and running deepfake analysis…"):
                vid_up.seek(0)
                result = _norm(_post("/analyze-video", files={"file": vid_up}, timeout=120))
                st.session_state.video_result = result
                if "error" not in result:
                    _push_feed(result["verdict"], result["confidence"], "Video", vid_up.name)

    if st.session_state.video_result:
        st.divider(); ui_full_verdict(st.session_state.video_result)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MULTIMODAL VERDICT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔀 Multimodal Verdict":
    ui_page_header("Multimodal Fusion Verdict",
        "ATTENTIONFUSIONNET · MC-DROPOUT (20 PASSES) · UNCERTAINTY QUANTIFICATION · XAI",
        "🔀")
    ui_clear(["verify_result"], "mm")
    st.info("Enter scores from individual scanners for AttentionFusionNet, or use the Veritas Scanner for the full automated pipeline.")

    c1, c2, c3 = st.columns(3)
    with c1: text_score  = st.number_input("Text score (0–1)",    0.0, 1.0, 0.0, .01)
    with c2: image_score = st.number_input("Image score (0–100)", 0,   100, 0,   1)
    with c3: video_score = st.number_input("Video score (0–100)", 0,   100, 0,   1)
    c4, c5, c6 = st.columns(3)
    with c4: fact_score      = st.number_input("Fact trust score (0–1)", 0.0, 1.0, .5, .01)
    with c5: image_reused    = st.checkbox("Image reused from different context")
    with c6: web_contradicts = st.checkbox("Web sources contradict claim")
    caption_mismatch = st.checkbox("Image-caption CLIP mismatch detected")

    if st.button("🔀 Run Fusion", type="primary", use_container_width=True):
        with st.spinner("Running AttentionFusionNet + MC-Dropout…"):
            raw = _post("/final-verdict", json={
                "text_score": text_score, "image_score": image_score/100,
                "video_score": video_score/100, "fact_score": fact_score,
                "image_reused": image_reused,
                "caption_mismatch": caption_mismatch,
                "web_contradicts": web_contradicts,
            })
            result = _norm(raw)
            st.session_state.verify_result = result
            if "error" not in result:
                _push_feed(result["verdict"], result["confidence"], "Fusion")

    if st.session_state.verify_result:
        res = st.session_state.verify_result; st.divider()
        ui_verdict_banner(res["verdict"], res["confidence"], res.get("uncertainty_level","LOW"))
        ui_metric_grid([
            ("Confidence",      f"{res['confidence']:.1f}%",     _vc_color(res['verdict'])),
            ("Uncertainty",     f"{res.get('uncertainty',0):.3f}",_unc_color(res.get('uncertainty_level','LOW'))),
            ("Unc. level",      res.get("uncertainty_level","—"), "#3d7a9a"),
            ("Review needed",   "YES" if res.get("review_recommended") else "NO",
             "#ff1a1a" if res.get("review_recommended") else "#00ff88"),
        ])
        if PLOTLY:
            col_shap, col_heat = st.columns(2)
            with col_shap:
                if res.get("signal_importance"): ui_plotly_shap(res["signal_importance"])
            with col_heat:
                if res.get("attention_weights"): ui_attention_heatmap(res["attention_weights"])
        disagr = res.get("disagreement",{})
        if disagr.get("disagreement"):
            st.warning(f"⚠️ **Modality conflict** — spread={disagr.get('spread',0):.3f}, std={disagr.get('std',0):.3f}. {disagr.get('note','')}")
        ui_download_btns(res, "fusion")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: BATCH SCAN
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Batch Scan":
    ui_page_header("Batch Text Scanner",
        "CSV UPLOAD · AUTOMATED PIPELINE · COLOR-CODED RESULTS · EXPORT",
        "📦")
    ui_clear(["batch_results"], "batch")

    cf = st.file_uploader("Upload CSV (must have a 'text' column)", type=["csv"])
    if cf:
        st.dataframe(pd.read_csv(cf, nrows=3), use_container_width=True)
        st.caption("Showing first 3 rows preview."); cf.seek(0)

    if cf and st.button("🔍 Run Batch Analysis", type="primary", use_container_width=True):
        content = cf.read().decode("utf-8"); reader = list(csv.DictReader(io.StringIO(content)))
        if not reader or "text" not in reader[0]:
            st.error("CSV must have a 'text' column.")
        else:
            results = []; prog = st.progress(0, text="Initializing…")
            stage_t = st.empty(); total = len(reader)
            for i, row in enumerate(reader):
                stage_t.caption(f"Analyzing {i+1}/{total}: {row['text'][:50]}…")
                r = _norm(_post("/predict", data={"text": row["text"]}, timeout=30))
                results.append({
                    "Row":        i+1,
                    "Text":       row["text"][:75] + ("…" if len(row["text"])>75 else ""),
                    "Verdict":    r.get("verdict","Error"),
                    "Confidence": f"{r.get('confidence',0):.1f}%",
                    "Risk":       r.get("risk_score",0),
                })
                prog.progress((i+1)/total, text=f"{i+1}/{total} — {r.get('verdict','…')}")
            stage_t.empty()
            st.session_state.batch_results = results
            st.success(f"✅ Complete — {len(results)} rows analyzed")

    if st.session_state.batch_results:
        df = pd.DataFrame(st.session_state.batch_results)

        def color_verdict(val):
            v = str(val).lower()
            if any(x in v for x in ["threat","fake","high"]): return "background-color:#ff1a1a18;color:#ff6060"
            if "suspicious" in v: return "background-color:#ffb80018;color:#ffd060"
            return "background-color:#00ff8814;color:#00ff88"

        if "Verdict" in df.columns:
            try:
                styled = df.style.applymap(color_verdict, subset=["Verdict"])
                st.dataframe(styled, use_container_width=True, height=400)
            except Exception:
                st.dataframe(df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

        vv = df["Verdict"]
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Total",    len(df))
        b2.metric("Threats",  int(vv.str.contains("Threat|Fake|fake|FAKE",na=False).sum()))
        b3.metric("Suspicious",int(vv.str.contains("Suspicious|suspicious",na=False).sum()))
        b4.metric("Genuine",  int(vv.str.contains("Genuine|Real|genuine|real",na=False).sum()))

        if PLOTLY:
            count_df = vv.value_counts().reset_index(); count_df.columns=["Verdict","Count"]
            fig = px.bar(count_df, x="Verdict", y="Count",
                         title="Batch verdict distribution",
                         color="Verdict",
                         color_discrete_map={"High Cyber Threat":"#ff1a1a","Suspicious":"#ffb800","Likely Genuine":"#00ff88"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,5,9,.9)",height=230,
                              margin=dict(l=0,r=0,t=36,b=0),showlegend=False,
                              xaxis=dict(color="#3d7a9a"),
                              yaxis=dict(color="#3d7a9a",gridcolor="#071524"),
                              title_font=dict(color="#3d7a9a",size=10,family="Share Tech Mono"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        d1, d2 = st.columns(2)
        with d1: st.download_button("⬇ CSV",  df.to_csv(index=False), "batch.csv",  "text/csv")
        with d2: st.download_button("⬇ JSON", json.dumps(st.session_state.batch_results, indent=2), "batch.json", "application/json")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Analytics":
    ui_page_header("Analytics Dashboard",
        "SCAN HISTORY · VERDICT DISTRIBUTION · CONFIDENCE HISTOGRAM · THREAT TIMELINE",
        "📊")

    cr, _ = st.columns([1,6])
    with cr:
        if st.button("🔄 Refresh"): st.session_state.history_data = None; st.rerun()

    if st.session_state.history_data is None:
        with st.spinner("Loading analytics…"):
            rh = _get("/history?limit=500", timeout=8)
            st.session_state.history_data = rh if isinstance(rh, list) else rh.get("results", rh.get("history", []))

    history = st.session_state.history_data or []

    if not history:
        st.markdown("""
        <div style="background:rgba(0,255,229,.02);border:1px solid rgba(0,255,229,.07);
        border-radius:9px;padding:3rem;text-align:center;
        font-family:'Share Tech Mono',monospace;font-size:.76rem;color:#3d7a9a">
        No scan history yet — run some analyses first.</div>""", unsafe_allow_html=True)
    else:
        df = pd.DataFrame(history); hv = "verdict" in df.columns
        n_total  = len(df)
        n_threat = df["verdict"].str.contains("Threat|Fake|fake|FAKE|threat",na=False).sum() if hv else 0
        n_susp   = df["verdict"].str.contains("Suspicious|suspicious",na=False).sum() if hv else 0
        n_safe   = n_total - n_threat - n_susp

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total scans", n_total)
        k2.metric("Threats",     int(n_threat))
        k3.metric("Suspicious",  int(n_susp))
        k4.metric("Safe",        int(n_safe))
        st.divider()

        if PLOTLY and hv:
            counts = df["verdict"].value_counts().reset_index(); counts.columns=["Verdict","Count"]
            CYBER_COLORS = ["#ff1a1a","#ffb800","#00ffe5","#9b30ff","#0088ff","#00ff88"]

            c_pie, c_bar = st.columns(2)
            with c_pie:
                fig = go.Figure(go.Pie(
                    labels=counts["Verdict"],values=counts["Count"],hole=.58,
                    marker_colors=CYBER_COLORS,
                    textfont=dict(color="#a8d8ea",size=9),
                    hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
                ))
                fig.update_layout(
                    title=dict(text="Verdict distribution",font=dict(color="#3d7a9a",size=10,family="Share Tech Mono")),
                    paper_bgcolor="rgba(0,0,0,0)",height=275,
                    margin=dict(l=0,r=0,t=36,b=0),
                    legend=dict(font=dict(color="#a8d8ea",size=9)),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            with c_bar:
                fig2 = go.Figure(go.Bar(
                    x=counts["Verdict"],y=counts["Count"],
                    marker_color=CYBER_COLORS[:len(counts)],
                    marker_opacity=.8,
                    text=counts["Count"],textposition="outside",
                    textfont=dict(color="#a8d8ea",size=9),
                ))
                fig2.update_layout(
                    title=dict(text="Scan counts",font=dict(color="#3d7a9a",size=10,family="Share Tech Mono")),
                    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,5,9,.9)",
                    height=275,margin=dict(l=0,r=0,t=36,b=0),
                    xaxis=dict(color="#3d7a9a",tickfont=dict(size=9)),
                    yaxis=dict(color="#3d7a9a",gridcolor="#071524"),
                )
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

            # Confidence histogram
            if "confidence" in df.columns:
                df["conf_num"] = pd.to_numeric(df["confidence"],errors="coerce")
                fig3 = px.histogram(df.dropna(subset=["conf_num"]),x="conf_num",nbins=20,
                                    title="Confidence score distribution",
                                    color_discrete_sequence=["#00ffe5"],
                                    labels={"conf_num":"Confidence (%)"})
                fig3.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,5,9,.9)",
                    height=235,margin=dict(l=0,r=0,t=36,b=0),
                    xaxis=dict(color="#3d7a9a"),yaxis=dict(color="#3d7a9a",gridcolor="#071524"),
                    title_font=dict(color="#3d7a9a",size=10,family="Share Tech Mono"),
                )
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

            # Timeline
            ts_col = next((c for c in ["created_at","timestamp","time"] if c in df.columns), None)
            if ts_col:
                try:
                    df[ts_col] = pd.to_datetime(df[ts_col],errors="coerce")
                    daily = df.dropna(subset=[ts_col]).set_index(ts_col).resample("D")["verdict"].count().reset_index()
                    daily.columns = ["Date","Count"]
                    fig4 = px.line(daily,x="Date",y="Count",title="Scans per day",
                                   color_discrete_sequence=["#00ffe5"])
                    fig4.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,5,9,.9)",
                        height=215,margin=dict(l=0,r=0,t=36,b=0),
                        xaxis=dict(color="#3d7a9a"),yaxis=dict(color="#3d7a9a",gridcolor="#071524"),
                        title_font=dict(color="#3d7a9a",size=10,family="Share Tech Mono"),
                    )
                    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
                except Exception: pass

        with st.expander("📋 Full history data"):
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇ Export CSV", df.to_csv(index=False), "history.csv", "text/csv")  
elif page == "🕰 History":
    ui_page_header("Scan History", "ALL SCANS · SEARCHABLE · COLOR-CODED · EXPORTABLE", "🕰")

    cr, cl, _ = st.columns([1,1,4])
    with cr:
        if st.button("🔄 Refresh"): st.session_state.history_data = None; st.rerun()
    with cl:
        limit = st.selectbox("Show last",[25,50,100,200],index=1,label_visibility="collapsed")

    rh = _get(f"/history?limit={limit}", timeout=6)
    history = rh if isinstance(rh,list) else rh.get("results",rh.get("history",[]))

    if not history: st.info("No scan history yet.")
    else:
        df = pd.DataFrame(history)
        search = st.text_input("🔎 Search / filter", placeholder="Filter by verdict, type…")
        if search:
            mask = df.apply(lambda row: row.astype(str).str.contains(search,case=False).any(), axis=1)
            df = df[mask]; st.caption(f"{len(df)} results matched")

        def color_row(row):
            v = str(row.get("verdict","")).lower()
            if any(x in v for x in ["threat","fake","high"]): return ["background-color:rgba(255,26,26,.07)"]*len(row)
            if "suspicious" in v: return ["background-color:rgba(255,184,0,.07)"]*len(row)
            return ["background-color:rgba(0,255,136,.03)"]*len(row)

        try:
            styled = df.style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True, height=520)
        except Exception:
            st.dataframe(df, use_container_width=True, height=520)

        st.download_button("⬇ Export CSV", df.to_csv(index=False), "history.csv", "text/csv")

elif page == "⚙ Model Control":
    if st.session_state.role != "admin": st.error("🔒 Admin access required."); st.stop()
    ui_page_header("Model Control Panel", "ADMIN ONLY · RETRAINING · SYSTEM INFO · HEALTH", "⚙")
    st.markdown('<span style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;background:rgba(255,26,26,.08);color:#ff6060;border:1px solid rgba(255,26,26,.22);padding:3px 10px;border-radius:3px;letter-spacing:1px">ADMIN ONLY</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🔁 Retrain", "🖥 System Info", "🏥 Health"])
    with t1:
        st.caption("Fine-tune models on accumulated user feedback.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔁 Retrain Text Model", type="primary"):
                with st.spinner("Triggering…"):
                    r = _post("/retrain-text-model", timeout=180)
                    if "error" not in r: st.success("✅ Retraining triggered in background.")
                    else: st.error(r["error"])
        with c2:
            if st.button("📊 Check Drift"):
                with st.spinner("Fetching drift report…"):
                    r = _get("/drift-report")
                    d = r.get("drift",{})
                    sev = d.get("overall_severity","NONE")
                    sc  = {"NONE":"#00ffe5","MINOR":"#0088ff","SIGNIFICANT":"#ffb800","CRITICAL":"#ff1a1a"}.get(sev,"#3d7a9a")
                    st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.72rem;background:rgba(0,255,229,.02);border:1px solid rgba(0,255,229,.08);border-radius:8px;padding:10px 14px"><span style="color:{sc}">Severity: {sev}</span> · <span style="color:#a8d8ea">Rec: {d.get("recommendation","MONITOR")}</span></div>', unsafe_allow_html=True)

    with t2:
        if st.button("🔄 Refresh"): st.rerun()
        info = _get("/system-info")
        if "error" not in info: st.json(info)
        else: st.warning("Could not fetch system info.")

    with t3:
        h = _get("/health")
        if "error" not in h:
            overall = h.get("status","unknown")
            oc = "#00ffe5" if overall == "healthy" else "#ffb800"
            st.markdown(f'<div style="font-family:\'Orbitron\',monospace;font-size:.95rem;color:{oc};margin-bottom:10px">● {overall.upper()}</div>', unsafe_allow_html=True)
            for svc, status in h.get("checks",{}).items():
                sc = "#00ffe5" if "ok" in str(status) else "#ffb800" if "degraded" in str(status) else "#ff1a1a"
                st.markdown(f'<div style="display:flex;justify-content:space-between;font-family:\'Share Tech Mono\',monospace;font-size:.64rem;padding:4px 0;border-bottom:1px solid rgba(0,255,229,.04)"><span style="color:#3d7a9a">{svc}</span><span style="color:{sc}">{status}</span></div>', unsafe_allow_html=True)
        else:
            st.error("❌ API unreachable — start uvicorn on port 8000.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DRIFT MONITOR (Admin)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Drift Monitor":
    if st.session_state.role != "admin": st.error("🔒 Admin access required."); st.stop()
    ui_page_header("Concept Drift Monitor",
        "PAGE-HINKLEY TEST · POPULATION STABILITY INDEX · AUTO-RETRAIN TRIGGERS",
        "📈")

    if st.button("🔄 Refresh"): st.session_state.drift_data = None; st.rerun()

    if st.session_state.drift_data is None:
        with st.spinner("Fetching drift report…"):
            r = _get("/drift-report"); st.session_state.drift_data = r.get("drift",r)

    drift = st.session_state.drift_data or {}
    if "error" in drift:
        st.info("Drift monitor not yet available — run some scans first.")
    else:
        sev = drift.get("overall_severity","NONE")
        rec = drift.get("recommendation","MONITOR")
        sev_clr = {"NONE":"#00ffe5","MINOR":"#0088ff","SIGNIFICANT":"#ffb800","CRITICAL":"#ff1a1a"}.get(sev,"#3d7a9a")

        ui_metric_grid([
            ("Drift severity",  sev,                               sev_clr),
            ("Recommendation",  rec,                               "#a8d8ea"),
            ("PSI value",       f"{drift.get('psi_value',0):.4f}", "#00ffe5"),
            ("Window size",     str(drift.get("window_size",0)),   "#3d7a9a"),
        ])
        st.markdown("<br>", unsafe_allow_html=True)

        if PLOTLY:
            c1, c2 = st.columns(2)
            with c1:
                fig = go.Figure(go.Indicator(
                    mode="number+delta",
                    value=drift.get("fake_rate_current",0)*100,
                    delta={"reference":drift.get("fake_rate_baseline",0)*100,
                           "valueformat":".1f","suffix":"%"},
                    title={"text":"Current fake rate","font":{"color":"#3d7a9a","size":10,"family":"Share Tech Mono"}},
                    number={"suffix":"%","font":{"size":28,"color":"#f0faff","family":"Orbitron,monospace"}},
                ))
                fig.update_layout(height=168, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=12,r=12,t=12,b=8))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            with c2:
                psi = drift.get("psi_value",0)
                fig2 = go.Figure(go.Indicator(
                    mode="gauge+number", value=psi,
                    number={"valueformat":".4f","font":{"size":20,"color":"#f0faff","family":"Orbitron,monospace"}},
                    title={"text":"PSI — Population Stability Index","font":{"color":"#3d7a9a","size":9,"family":"Share Tech Mono"}},
                    gauge={
                        "axis":{"range":[0,.3],"tickcolor":"#0f2d3f","tickfont":{"color":"#0f2d3f","size":7}},
                        "bar":{"color":"#00ffe5" if psi<.1 else "#ffb800" if psi<.2 else "#ff1a1a","thickness":.55},
                        "bgcolor":"rgba(0,5,9,.92)","borderwidth":1,"bordercolor":"rgba(0,255,229,.07)",
                        "steps":[{"range":[0,.1],"color":"rgba(0,255,229,.03)"},
                                 {"range":[.1,.2],"color":"rgba(255,184,0,.03)"},
                                 {"range":[.2,.3],"color":"rgba(255,26,26,.04)"}],
                    },
                ))
                fig2.update_layout(height=168, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=12,r=12,t=12,b=8))
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        events = drift.get("events",[])
        if events:
            ui_cyber_section("Recent drift events")
            for ev in events[:5]:
                sev_e = ev.get("severity","NONE")
                sc_e  = {"MINOR":"#0088ff","SIGNIFICANT":"#ffb800","CRITICAL":"#ff1a1a"}.get(sev_e,"#3d7a9a")
                st.markdown(f"""
                <div style="background:rgba(0,255,229,.02);border-left:2px solid {sc_e};
                padding:5px 10px;margin:2px 0;border-radius:0 5px 5px 0;
                font-family:'Share Tech Mono',monospace;font-size:.62rem">
                <span style="color:{sc_e}">[{sev_e}]</span>
                <span style="color:#a8d8ea;margin-left:6px">{ev.get('method','')} — stat={ev.get('statistic',0):.3f}</span>
                <span style="color:#0f2d3f;margin-left:8px">{str(ev.get('timestamp',''))[:19]}</span>
                </div>""", unsafe_allow_html=True)

        if sev in ("SIGNIFICANT","CRITICAL"):
            st.error("🔴 Significant drift — retraining is recommended.")
            if st.button("🔁 Retrain Now", type="primary"):
                r = _post("/retrain-text-model",timeout=180)
                if "error" not in r: st.success("✅ Retraining triggered.")
                else: st.error(r["error"])


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HASH DB (Admin)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🗃 Hash DB":
    if st.session_state.role != "admin": st.error("🔒 Admin access required."); st.stop()
    ui_page_header("Hash Database Manager",
        "KNOWN FAKE IMAGE REGISTRY · ADD · REMOVE · BROWSE · EXPORT",
        "🗃")

    info = _get("/system-info")
    n_hashes = info.get("memory",{}).get("known_fake_hashes","—")
    n_clip   = info.get("memory",{}).get("clip_vectors","—")
    ui_metric_grid([
        ("Known fake hashes", str(n_hashes), "#00ffe5"),
        ("CLIP vectors",      str(n_clip),   "#00ffe5"),
        ("Index type",        "HNSW Flat",   "#3d7a9a"),        ("Search method",     "Hamming dist","#3d7a9a"),
    ])
    st.divider()

    t1, t2 = st.tabs(["➕ Add fake image", "📋 Browse entries"])
    with t1:
        st.caption("Add a confirmed fake/reused image to the pHash + CLIP memory.")
        img_add = st.file_uploader("Confirmed fake image", type=["jpg","jpeg","png","webp"], key="hash_add")
        if img_add: st.image(img_add, width=200)
        a1, a2 = st.columns(2)
        with a1: ctx = st.text_input("Original context", placeholder="e.g. Kerala floods 2018")
        with a2: dt  = st.text_input("Original date",    placeholder="YYYY-MM-DD")
        src = st.text_input("Source URL (optional)", placeholder="https://factcheck.org/…")
        if st.button("➕ Add to Hash DB", type="primary"):
            if not img_add or not ctx: st.warning("Image and context required.")
            else:
                img_add.seek(0)
                r = _post("/admin/add-fake-hash",
                          files={"file":img_add},
                          data={"original_context":ctx,"original_date":dt,"source_url":src})
                if "error" not in r: st.success("✅ Hash + CLIP embedding registered.")
                else: st.error(f"Failed: {r['error']}")

    with t2:
        st.caption("Browse known-fake image registry.")
        entries_r = _get("/admin/hash-db-entries")
        entries   = entries_r.get("entries",[]) if "error" not in entries_r else []
        if entries:
            df_h = pd.DataFrame(entries)
            st.dataframe(df_h, use_container_width=True)
            st.download_button("⬇ Export", df_h.to_csv(index=False), "hash_db.csv","text/csv")
        else:
            st.info("No entries yet — add some confirmed fake images above.")
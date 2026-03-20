# ============================================================
# ENTERPRISE DATABASE MODELS
# Continual Learning + Cyber Intelligence + Research Ready
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Index,
    JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

# ============================================================
# USERS TABLE (Multi-User + Firebase Support)
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, nullable=False)
    firebase_uid = Column(String(255), unique=True, nullable=True)

    # Role & Access
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scans = relationship("Scan", back_populates="user")

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_firebase_uid", "firebase_uid"),
    )

# ============================================================
# SCAN RESULTS TABLE
# Core Intelligence Memory Store
# ============================================================

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)

    # Firebase support
    firebase_uid = Column(String(255), nullable=True)

    # User relation
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Content metadata
    content_type = Column(String(50))  # text, image, video, fusion
    input_length = Column(Integer, nullable=True)

    # ⭐ CORE CONTINUAL LEARNING FIELD
    raw_input = Column(Text, nullable=True)  # FULL original text / metadata

    # AI outputs
    risk_score = Column(Float)
    confidence = Column(Float)
    verdict = Column(String(100))

    # Multimodal breakdown
    text_score = Column(Float, nullable=True)
    image_score = Column(Float, nullable=True)
    video_score = Column(Float, nullable=True)
    fact_score = Column(Float, nullable=True)

    # Explainability + debugging
    raw_model_output = Column(JSON, nullable=True)

    # ⭐ FUTURE MEMORY EMBEDDINGS (vector storage metadata)
    embedding_vector_id = Column(String(255), nullable=True)

    # Model metadata
    model_name = Column(String(100), default="unified_threat_engine")
    model_version = Column(String(50), default="v2.3")
    processing_time = Column(Float, nullable=True)

    # Drift monitoring
    drift_flag = Column(Boolean, default=False)

    # Tracking
    source_ip = Column(String(100), nullable=True)

    # Soft delete
    is_deleted = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="scans")
    feedback = relationship("Feedback", back_populates="scan")

    __table_args__ = (
        Index("idx_scan_content_type", "content_type"),
        Index("idx_scan_created_at", "created_at"),
        Index("idx_scan_verdict", "verdict"),
        Index("idx_scan_risk_score", "risk_score"),
        Index("idx_scan_firebase_uid", "firebase_uid"),
        Index("idx_scan_model_version", "model_version"),
        Index("idx_scan_drift_flag", "drift_flag"),
    )

# ============================================================
# FEEDBACK TABLE
# Human-in-the-loop Learning Engine
# ============================================================

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)

    scan_id = Column(Integer, ForeignKey("scans.id"))

    correct_label = Column(String(100))
    notes = Column(Text, nullable=True)

    # ⭐ Active learning importance score
    feedback_weight = Column(Float, default=1.0)

    reviewed_by = Column(String(255), nullable=True)
    is_resolved = Column(Boolean, default=False)

    # AI disagreement tracking
    model_disagreement = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="feedback")

    __table_args__ = (
        Index("idx_feedback_scan_id", "scan_id"),
        Index("idx_feedback_correct_label", "correct_label"),
        Index("idx_feedback_weight", "feedback_weight"),
    )

# ============================================================
# MODEL PERFORMANCE TABLE
# Continual Learning Monitoring + Drift Analytics
# ============================================================

class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)

    model_name = Column(String(100))
    model_version = Column(String(50))

    average_confidence = Column(Float)
    average_risk_score = Column(Float)

    false_positive_rate = Column(Float, nullable=True)
    false_negative_rate = Column(Float, nullable=True)

    drift_detected = Column(Boolean, default=False)

    # ⭐ New research metrics
    uncertainty_score = Column(Float, nullable=True)
    feedback_rate = Column(Float, nullable=True)

    sample_size = Column(Integer, nullable=True)

    evaluated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_model_name", "model_name"),
        Index("idx_model_version", "model_version"),
        Index("idx_model_evaluated_at", "evaluated_at"),
    )
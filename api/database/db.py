# ============================================================
# ENTERPRISE DATABASE CONFIGURATION
# Supports SQLite (Dev) + PostgreSQL (Prod)
# Includes Auto Table Creation + Health Check
# ============================================================

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool

logger = logging.getLogger("CyberThreatAI.DB")

# ============================================================
# ENVIRONMENT CONFIG
# ============================================================

# Switch to PostgreSQL using:
# set DATABASE_URL=postgresql://user:pass@localhost:5432/cyber_ai

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./cyber_ai.db"  # Default for development
)

# ============================================================
# ENGINE CONFIGURATION
# ============================================================

engine_args = {}

if DATABASE_URL.startswith("sqlite"):
    # SQLite Development Mode
    engine_args["connect_args"] = {"check_same_thread": False}
    engine_args["poolclass"] = NullPool
    logger.info("Using SQLite database.")
else:
    # PostgreSQL Production Mode
    engine_args.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800
    })
    logger.info("Using PostgreSQL database.")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    **engine_args
)

# ============================================================
# SESSION FACTORY
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

# ============================================================
# FASTAPI DEPENDENCY
# ============================================================

def get_db():
    """
    Dependency injection for FastAPI routes.
    Ensures safe DB session lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

def check_database_connection():
    """
    Verifies database connectivity.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful.")
    except OperationalError as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

# ============================================================
# AUTO TABLE CREATION (CRITICAL FIX)
# ============================================================

def initialize_database():
    """
    Creates all tables defined in models.
    Should be called at application startup.
    """
    try:
        logger.info("🔧 Initializing database tables...")

        # Import models here to avoid circular imports
        from api.database import models  # noqa

        Base.metadata.create_all(bind=engine)

        logger.info("✅ Database tables verified/created successfully.")

    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

# ============================================================
# STARTUP INITIALIZER (SAFE)
# ============================================================

def init_db_on_startup():
    """
    Combines health check + table creation.
    """
    check_database_connection()
    initialize_database()
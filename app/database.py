from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration is now environment-driven. Set DATABASE_URL to your target DB.
# Default fallback set to the provided Render PostgreSQL connection string.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://jubair_user:qEU3AK2tyDRCeYyuR0AxwXxjnGLSB3vM@dpg-d2r540je5dus73croji0-a/jubair_boot_house_db"
)

engine = None
SessionLocal = None

if DATABASE_URL:
    # Normalize URL and SSL for Render PostgreSQL
    url = DATABASE_URL
    is_sqlite = url.startswith("sqlite")
    is_postgres = url.startswith("postgresql") or url.startswith("postgres://") or url.startswith("postgresql+")

    # Force psycopg2 driver for Render compatibility
    if is_postgres and not url.startswith("postgresql+psycopg2://"):
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    # Render often requires SSL; ensure sslmode=require when using psycopg2
    if is_postgres and "sslmode" not in url and "?" not in url:
        url = f"{url}?sslmode=require"
    elif is_postgres and "sslmode" not in url and "?" in url:
        url = f"{url}&sslmode=require"

    # Configure engine; apply SQLite-specific args only if using sqlite
    connect_args = {"check_same_thread": False} if is_sqlite else {}

    engine = create_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    if SessionLocal is None:
        raise RuntimeError(f"Database not configured. DATABASE_URL: {DATABASE_URL}")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration is now environment-driven. Set DATABASE_URL to your target DB.
DATABASE_URL = os.getenv("DATABASE_URL", "")

engine = None
SessionLocal = None

if DATABASE_URL:
    url = DATABASE_URL
    is_sqlite = url.startswith("sqlite")
    is_postgres = url.startswith("postgresql") or url.startswith("postgres://") or url.startswith("postgresql+") or url.startswith("postgres+")

    if is_postgres:
        # Try psycopg (v3)
        if not (url.startswith("postgresql+psycopg://") or url.startswith("postgresql+psycopg2://")):
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg://", 1)

        # Add sslmode=require if not present
        if "sslmode" not in url:
            url = url + ("&sslmode=require" if "?" in url else "?sslmode=require")

    connect_args = {"check_same_thread": False} if is_sqlite else {}

    try:
        # First try psycopg (v3)
        engine = create_engine(
            url,
            echo=False,
            pool_pre_ping=True,
            connect_args=connect_args
        )
    except ModuleNotFoundError:
        # If psycopg is not available, fallback to psycopg2
        if url.startswith("postgresql+psycopg://"):
            url = url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
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

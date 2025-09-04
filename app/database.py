from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Environment se DATABASE_URL le raha hai
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Render kabhi 'postgres://' deta hai jo psycopg v3 ke liye galat hai
# psycopg v3 ke liye sahi format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

# Ensure SSL (Render PostgreSQL requires TLS/SSL)
# Render PostgreSQL requires SSL
if "sslmode" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = DATABASE_URL + sep + "sslmode=require"

# Engine create karo
engine = create_engine(
    DATABASE_URL,
    echo=True,         # debug ke liye SQL queries log karega (production me False karna)
    future=True        # SQLAlchemy 2.0 style
    echo=True,      # debug ke liye SQL logs (production me False kar dena)
    future=True
)

# SessionLocal banate hain
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Base class for models
Base = declarative_base()

# Dependency function (FastAPI routes me use hota hai)
# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        

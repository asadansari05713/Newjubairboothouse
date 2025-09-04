import os
from sqlalchemy import create_engine
from app.database import Base
from app import models  # noqa: F401 ensure models are imported so Base has metadata


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set. Please export it to your PostgreSQL URL.")

    # Only apply SQLite connect_args if using sqlite
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

    engine = create_engine(database_url, echo=True, connect_args=connect_args)

    # Create all tables defined on Base.metadata
    Base.metadata.create_all(bind=engine)
    print("✅ Schema initialized successfully.")


if __name__ == "__main__":
    main()



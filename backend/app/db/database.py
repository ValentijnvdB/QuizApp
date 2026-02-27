from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.orm import sessionmaker
from typing import Generator, Any
import os

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

# Base class for all models
Base = declarative_base()


def init_db():
    global engine, SessionLocal
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=10,
        max_overflow=20
    )
    # Create SessionLocal class for database sessions
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for FastAPI routes to get database session
def get_db() -> Generator[Session, Any, None]:
    """
    Dependency function that yields a database session.
    Usage in FastAPI routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper function to create all tables (for testing/development)
def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)


# Helper function to drop all tables (for testing)
def drop_tables():
    """Drop all tables in the database - USE WITH CAUTION"""
    Base.metadata.drop_all(bind=engine)

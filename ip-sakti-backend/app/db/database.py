import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("ip_sakti_backend")

_db_url = settings.DATABASE_URL or "sqlite:///./ip_sakti.db"

def _build_engine(url: str):
    return create_engine(
        url,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
        pool_pre_ping=True,
    )

try:
    engine = _build_engine(_db_url)
    if not _db_url.startswith("sqlite"):
        with engine.connect() as conn:
            pass
        logger.info(f"Connected to remote PostgreSQL database successfully.")
except Exception as exc:
    logger.warning(
        f"Remote database connection failed ({exc}). Falling back to local SQLite."
    )
    _db_url = "sqlite:///./ip_sakti.db"
    settings.DATABASE_URL = _db_url
    engine = _build_engine(_db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

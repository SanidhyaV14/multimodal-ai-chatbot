import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

logger = logging.getLogger("chatbot.database")

Base = declarative_base()

def get_engine():
    """
    Attempts to initialize MySQL database engine.
    If MySQL is unreachable and fallback is enabled, connects to SQLite fallback.
    """
    engine = None
    try:
        # First attempt: MySQL
        logger.info(f"Connecting to MySQL database at {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}...")
        mysql_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        # Test connection
        with mysql_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to MySQL database.")
        return mysql_engine
    except Exception as e:
        logger.warning(f"Could not connect to MySQL ({e}).")
        if settings.FALLBACK_TO_SQLITE:
            logger.warning(f"Falling back to local SQLite engine ({settings.SQLITE_URL}) for active operation.")
            sqlite_engine = create_engine(
                settings.SQLITE_URL,
                connect_args={"check_same_thread": False},
                echo=False
            )
            return sqlite_engine
        else:
            raise RuntimeError(f"Failed to connect to MySQL database and fallback is disabled: {e}")

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all database tables based on registered models."""
    from backend import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")

def get_db():
    """FastAPI Dependency for database session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

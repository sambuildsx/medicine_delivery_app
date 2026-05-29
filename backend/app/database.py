import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    # Try connecting to the primary PostgreSQL url
    primary_url = settings.DATABASE_URL
    
    # If the configured URL is PostgreSQL, test connection
    if primary_url.startswith("postgresql"):
        try:
            logger.info("Attempting connection to PostgreSQL...")
            engine = create_engine(primary_url, connect_args={"connect_timeout": 3})
            # Test connection
            with engine.connect() as conn:
                logger.info("Successfully connected to PostgreSQL database.")
                return engine
        except (OperationalError, Exception) as e:
            logger.warning(
                f"PostgreSQL connection failed: {e}. "
                f"Falling back to SQLite database for ease of local evaluation."
            )
    
    # Fallback to SQLite
    logger.info(f"Initializing SQLite database at: {settings.SQLITE_URL}")
    # SQLite requires check_same_thread=False for multi-thread requests in FastAPI
    engine = create_engine(
        settings.SQLITE_URL,
        connect_args={"check_same_thread": False}
    )
    return engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get db session in API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

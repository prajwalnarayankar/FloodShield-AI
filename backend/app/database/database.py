import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

logger = logging.getLogger("FloodShield.Database")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = None

# 1. Attempt PostgreSQL first (primary database on development laptop)
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    try:
        test_engine = create_engine(
            DATABASE_URL,
            connect_args={"connect_timeout": 2},
            pool_pre_ping=True
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = test_engine
        logger.info("[Database] Connected successfully to primary PostgreSQL database.")
    except Exception as e:
        logger.warning(f"[Database] PostgreSQL unavailable ({e}). Automatically switching to local SQLite.")
        engine = None

# 2. Fallback to local SQLite database if PostgreSQL is not reachable (e.g. Lab PC)
if engine is None:
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "floodshield.db"))
    DATABASE_URL = f"sqlite:///{db_file}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    logger.info(f"[Database] Using local SQLite database at: {db_file}")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
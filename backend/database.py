import os
from pathlib import Path
from urllib.parse import quote_plus

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


ROOT_DIR = Path(__file__).resolve().parents[1]

if load_dotenv:
    load_dotenv(ROOT_DIR / ".env")


def build_database_url() -> str:
    direct_url = os.getenv("DATABASE_URL")
    if direct_url:
        return direct_url

    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "5430")
    name = os.getenv("DB_NAME", "test_erp")
    user = quote_plus(os.getenv("DB_USER", "loi"))
    password = quote_plus(os.getenv("DB_PASSWORD", "loi-erp"))
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


DATABASE_URL = build_database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base_chebdo(DeclarativeBase):
    pass


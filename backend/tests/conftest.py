"""Fixtures partagees pour les tests de l'API.

Les tests ne touchent jamais la vraie base PostgreSQL : on utilise une base
SQLite en memoire, recreee a zero avant chaque test (via StaticPool pour
que toutes les "connexions" pointent vers la meme base en memoire).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  # noqa: F401  (enregistre les modeles sur Base_chebdo.metadata)
import service.matching_service as matching_service
from database import Base_chebdo
from main import app, get_db

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db_session():
    Base_chebdo.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base_chebdo.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _reset_index_matching():
    """Le moteur de matching garde un index TF-IDF en cache au niveau du
    module (pour eviter de le reconstruire a chaque requete en prod). Sans
    ce reset, l'index d'un test contaminerait les suivants (chaque test a
    sa propre base SQLite en memoire, mais le cache, lui, est partage)."""
    matching_service._index = None
    yield
    matching_service._index = None

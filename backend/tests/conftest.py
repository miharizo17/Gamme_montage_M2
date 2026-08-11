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
from deps import get_current_user, get_db
from main import app
from models import Utilisateur

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


UTILISATEUR_TEST = Utilisateur(
    id=1, nom_utilisateur="test-admin", mot_de_passe_hash="x", role="administrateur", actif=True
)


@pytest.fixture()
def client(db_session):
    """Client authentifie par defaut (role administrateur) : la grande
    majorite des tests portent sur la logique metier, pas sur l'auth
    elle-meme, donc on evite de repeter un login JWT dans chaque test."""

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return UTILISATEUR_TEST

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def client_sans_auth(db_session):
    """Client sans override d'authentification, pour tester le flux JWT
    reel (login, token invalide, controle de role) dans test_auth.py."""

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

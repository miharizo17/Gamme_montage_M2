"""Fonctions pures de securite : hashing de mot de passe et JWT.

Ne depend ni de FastAPI ni de la base de donnees pour rester facilement
testable. Le secret JWT vient obligatoirement du fichier .env (jamais
commite), sur le meme principe que DB_PASSWORD dans database.py.
"""
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

ALGORITHM = "HS256"
DUREE_TOKEN_MINUTES = 480  # 8h, une journee de travail


def _secret_key() -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET_KEY manquant : definissez-le dans le fichier .env "
            "(a la racine de Gamme_montage_M2, jamais commite) plutot que dans le code source."
        )
    return secret


def hasher_mot_de_passe(mot_de_passe: str) -> str:
    return bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verifier_mot_de_passe(mot_de_passe: str, hash_stocke: str) -> bool:
    return bcrypt.checkpw(mot_de_passe.encode("utf-8"), hash_stocke.encode("utf-8"))


def creer_token(nom_utilisateur: str, role: str) -> str:
    maintenant = datetime.now(timezone.utc)
    payload = {
        "sub": nom_utilisateur,
        "role": role,
        "iat": maintenant,
        "exp": maintenant + timedelta(minutes=DUREE_TOKEN_MINUTES),
    }
    return jwt.encode(payload, _secret_key(), algorithm=ALGORITHM)


def decoder_token(token: str) -> dict:
    """Leve jwt.PyJWTError (ou une sous-classe) si le token est invalide/expire."""
    return jwt.decode(token, _secret_key(), algorithms=[ALGORITHM])

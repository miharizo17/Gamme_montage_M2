"""Dependances FastAPI transverses : session DB et authentification."""
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Utilisateur
from security import decoder_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Utilisateur:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentification requise")
    try:
        payload = decoder_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expire")

    utilisateur = db.query(Utilisateur).filter(Utilisateur.nom_utilisateur == payload.get("sub")).first()
    if utilisateur is None or not utilisateur.actif:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable ou inactif")
    return utilisateur


def exiger_role(*roles: str):
    def dependance(utilisateur: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if utilisateur.role not in roles:
            raise HTTPException(status_code=403, detail="Acces reserve a un role superieur")
        return utilisateur

    return dependance

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Utilisateur
from schema import TokenOut, UtilisateurCreateIn
from security import creer_token, hasher_mot_de_passe, verifier_mot_de_passe


class IdentifiantsInvalides(Exception):
    pass


class NomUtilisateurDejaExistant(Exception):
    pass


def authentifier(db: Session, nom_utilisateur: str, mot_de_passe: str) -> TokenOut:
    utilisateur = (
        db.query(Utilisateur).filter(func.lower(Utilisateur.nom_utilisateur) == nom_utilisateur.lower()).first()
    )
    if utilisateur is None or not utilisateur.actif:
        raise IdentifiantsInvalides()
    if not verifier_mot_de_passe(mot_de_passe, utilisateur.mot_de_passe_hash):
        raise IdentifiantsInvalides()

    token = creer_token(utilisateur.nom_utilisateur, utilisateur.role)
    return TokenOut(access_token=token, role=utilisateur.role, nom_utilisateur=utilisateur.nom_utilisateur)


def creer_utilisateur(db: Session, data: UtilisateurCreateIn) -> Utilisateur:
    existant = (
        db.query(Utilisateur).filter(func.lower(Utilisateur.nom_utilisateur) == data.nom_utilisateur.lower()).first()
    )
    if existant is not None:
        raise NomUtilisateurDejaExistant()

    utilisateur = Utilisateur(
        nom_utilisateur=data.nom_utilisateur,
        mot_de_passe_hash=hasher_mot_de_passe(data.mot_de_passe),
        role=data.role,
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


def lister_utilisateurs(db: Session) -> list[Utilisateur]:
    return db.query(Utilisateur).order_by(Utilisateur.nom_utilisateur).all()

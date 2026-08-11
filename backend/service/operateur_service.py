from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Competence, Operateur
from schema import CompetenceOut, OperateurCreate, OperateurListOut, OperateurOut, OperateurUpdate


def lister_operateurs(db: Session, skip: int = 0, limit: int = 20) -> OperateurListOut:
    total = db.query(func.count(Operateur.id)).scalar()
    operateurs = (
        db.query(Operateur)
        .order_by(Operateur.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return OperateurListOut(
        total=total,
        skip=skip,
        limit=limit,
        items=[OperateurOut.model_validate(o) for o in operateurs],
    )


def operateur_existe(db: Session, operateur_id: int) -> bool:
    return db.query(Operateur.id).filter(Operateur.id == operateur_id).first() is not None


def obtenir_competences(db: Session, operateur_id: int) -> list[CompetenceOut]:
    competences = (
        db.query(Competence)
        .filter(Competence.operateur_id == operateur_id)
        .order_by(Competence.nb_occurrences.desc())
        .all()
    )
    return [CompetenceOut.model_validate(c) for c in competences]


def creer_operateur(db: Session, data: OperateurCreate) -> OperateurOut:
    operateur = Operateur(nom=data.nom, matricule=data.matricule, actif=True)
    db.add(operateur)
    db.commit()
    db.refresh(operateur)
    return OperateurOut.model_validate(operateur)


def modifier_operateur(db: Session, operateur_id: int, data: OperateurUpdate) -> OperateurOut | None:
    operateur = db.query(Operateur).filter(Operateur.id == operateur_id).first()
    if operateur is None:
        return None

    for champ, valeur in data.model_dump(exclude_unset=True).items():
        setattr(operateur, champ, valeur)

    db.commit()
    db.refresh(operateur)
    return OperateurOut.model_validate(operateur)


def supprimer_operateur(db: Session, operateur_id: int) -> bool:
    operateur = db.query(Operateur).filter(Operateur.id == operateur_id).first()
    if operateur is None:
        return False
    db.delete(operateur)
    db.commit()
    return True

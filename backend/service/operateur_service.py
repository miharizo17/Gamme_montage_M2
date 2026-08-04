from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Competence, Operateur
from schema import CompetenceOut, OperateurListOut, OperateurOut


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

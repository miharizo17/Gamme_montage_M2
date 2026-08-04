"""Assemble le matching NLP (matching_service) et la matrice de
competences (Competence) pour proposer une gamme complete a partir d'une
description de prototype - V1 du coeur du projet.

Principe : on retrouve la gamme historique la plus proche par similarite
textuelle, on reprend ses operations/temps/machine, et pour chaque
operation on suggere l'operateur reel ayant le plus d'occurrences dessus.
"""
from sqlalchemy.orm import Session

from models import Article, Competence, Operateur
from schema import GammeGenereeOut, OperationProposeeOut
from service import matching_service


def _meilleur_operateur(db: Session, operation_libelle: str) -> tuple[str | None, int | None]:
    competence = (
        db.query(Competence)
        .join(Operateur, Competence.operateur_id == Operateur.id)
        .filter(Competence.operation_libelle == operation_libelle)
        .filter(Operateur.matricule.is_(None))  # exclut les operateurs fictifs (donnees demo)
        .order_by(Competence.nb_occurrences.desc())
        .first()
    )
    if competence is None:
        return None, None
    return competence.operateur.nom, competence.nb_occurrences


def generer_gamme(db: Session, description: str) -> GammeGenereeOut | None:
    matches = matching_service.rechercher_gammes_similaires(db, description, top_k=1)
    if not matches:
        return None

    meilleur = matches[0]
    article = db.query(Article).filter(Article.id == meilleur.article_id).first()
    if article is None:
        return None

    derniere_gamme = max(article.gammes, key=lambda g: g.date_creation, default=None)
    if derniere_gamme is None:
        return None

    operations = []
    for ligne in derniere_gamme.lignes:
        operateur_nom, nb_occurrences = _meilleur_operateur(db, ligne.operation_libelle)
        operations.append(
            OperationProposeeOut(
                ordre=ligne.ordre,
                operation_libelle=ligne.operation_libelle,
                temps_estime=ligne.temps_equilibre,
                machine=ligne.machine,
                operateur_suggere=operateur_nom,
                operateur_nb_occurrences=nb_occurrences,
            )
        )

    return GammeGenereeOut(
        article_reference_id=article.id,
        article_reference_code=article.code,
        article_reference_nom=article.nom,
        score_similarite=meilleur.score,
        operations=operations,
    )

"""Assemble le matching NLP (matching_service) et la matrice de
competences (Competence) pour proposer une gamme complete a partir d'une
description de prototype - coeur du projet.

Principe : on retrouve la gamme historique la plus proche par similarite
textuelle, on reprend ses operations/machine, et pour chaque operation on
suggere l'operateur reel ayant le plus d'occurrences dessus - en priorite
sur LA MEME CHAINE (une chaine a ses propres operateurs, on ne melange pas).

Le temps affiche suit trois niveaux de repli, du plus fiable au moins
fiable :
    1. temps reellement chronometre sur la ligne d'origine,
    2. a defaut, temps moyen historique de l'operateur suggere,
    3. a defaut (operation jamais realisee par cet operateur), temps
       predit par le modele Machine Learning (Random Forest) entraine
       sur l'ensemble des temps mesures reels (scripts/entrainer_modele_temps.py).
"""
from sqlalchemy.orm import Session

from models import Article, Competence, Operateur
from schema import GammeGenereeOut, OperationProposeeOut
from service import chaine_service, matching_service, ml_service


def _meilleure_competence(db: Session, operation_libelle: str, chaine: str | None):
    """Cherche l'operateur le plus experimente sur cette operation, en
    priorite sur la meme chaine. Repli sur toutes chaines confondues si
    rien trouve sur la chaine cible.

    Retourne (competence, meme_chaine) ou meme_chaine vaut True (trouve
    sur la bonne chaine), False (repli sur une autre chaine, la cible
    etait connue) ou None (chaine cible inconnue - la question n'a pas
    de sens)."""
    base_query = (
        db.query(Competence)
        .join(Operateur, Competence.operateur_id == Operateur.id)
        .filter(Competence.operation_libelle == operation_libelle)
        .filter(Operateur.matricule.is_(None))  # exclut les operateurs fictifs (donnees demo)
    )

    if chaine:
        competence = base_query.filter(Competence.chaine == chaine).order_by(Competence.nb_occurrences.desc()).first()
        if competence is not None:
            return competence, True
        competence = base_query.order_by(Competence.nb_occurrences.desc()).first()
        return competence, (False if competence is not None else None)

    competence = base_query.order_by(Competence.nb_occurrences.desc()).first()
    return competence, None


def generer_gamme(db: Session, description: str, chaine: str | None = None) -> GammeGenereeOut | None:
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

    # La chaine choisie par l'agent de methode prime sur celle de la gamme
    # historique retrouvee : la production ne se refera pas forcement sur
    # la meme chaine que la derniere fois.
    chaine_cible = chaine or article.chaine

    operations = []
    for ligne in derniere_gamme.lignes:
        competence, meme_chaine = _meilleure_competence(db, ligne.operation_libelle, chaine_cible)

        operateur_nom = competence.operateur.nom if competence else None
        nb_occurrences = competence.nb_occurrences if competence else None

        temps_estime = ligne.temps_equilibre
        temps_mesure = temps_estime is not None
        temps_source = "mesure" if temps_mesure else None

        if temps_estime is None and competence is not None and competence.temps_moyen is not None:
            temps_estime = competence.temps_moyen
            temps_source = "historique_operateur"

        if temps_estime is None:
            prediction = ml_service.predire_temps(ligne.operation_libelle, ligne.machine)
            if prediction is not None:
                temps_estime = prediction
                temps_source = "ml"

        operations.append(
            OperationProposeeOut(
                ordre=ligne.ordre,
                operation_libelle=ligne.operation_libelle,
                temps_estime=temps_estime,
                temps_mesure=temps_mesure,
                temps_source=temps_source,
                machine=ligne.machine,
                operateur_suggere=operateur_nom,
                operateur_nb_occurrences=nb_occurrences,
                operateur_meme_chaine=meme_chaine,
            )
        )

    chaines_suggerees = chaine_service.suggerer_chaines(
        db, [ligne.operation_libelle for ligne in derniere_gamme.lignes]
    )

    return GammeGenereeOut(
        article_reference_id=article.id,
        article_reference_code=article.code,
        article_reference_nom=article.nom,
        chaine=chaine_cible,
        score_similarite=meilleur.score,
        operations=operations,
        chaines_suggerees=chaines_suggerees,
    )

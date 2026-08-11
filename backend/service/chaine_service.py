from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Article, Competence, Operateur
from schema import CelluleCompetenceOut, ChaineOut, ChaineSuggereeOut, MatriceCompetencesOut, OperateurChaineOut


def lister_chaines(db: Session) -> list[ChaineOut]:
    rows = (
        db.query(Article.chaine, func.count(Article.id))
        .filter(Article.chaine.isnot(None))
        .filter(~Article.code.like("DEMO-%"))
        .group_by(Article.chaine)
        .order_by(Article.chaine)
        .all()
    )
    return [ChaineOut(chaine=chaine, nb_gammes=nb) for chaine, nb in rows]


def lister_operateurs_chaine(db: Session, chaine: str) -> list[OperateurChaineOut]:
    rows = (
        db.query(
            Operateur.id,
            Operateur.nom,
            func.count(func.distinct(Competence.operation_libelle)),
            func.sum(Competence.nb_occurrences),
        )
        .join(Competence, Competence.operateur_id == Operateur.id)
        .filter(Competence.chaine == chaine)
        .filter(Operateur.matricule.is_(None))
        .group_by(Operateur.id, Operateur.nom)
        .order_by(func.sum(Competence.nb_occurrences).desc())
        .all()
    )
    return [
        OperateurChaineOut(
            operateur_id=operateur_id,
            nom=nom,
            nb_operations_distinctes=nb_operations,
            nb_occurrences_total=int(nb_occurrences or 0),
        )
        for operateur_id, nom, nb_operations, nb_occurrences in rows
    ]


def suggerer_chaines(db: Session, operations_libelles: list[str], top_n: int = 3) -> list[ChaineSuggereeOut]:
    """Pour une liste d'operations donnee, indique quelles chaines ont le
    plus d'operateurs experimentes dessus - independamment de la chaine
    choisie par l'agent de methode. Sert a recommander la chaine la mieux
    equipee pour realiser cette production."""
    operations_uniques = set(operations_libelles)
    if not operations_uniques:
        return []

    rows = (
        db.query(Competence.chaine, Competence.operation_libelle, func.max(Competence.nb_occurrences))
        .join(Operateur, Competence.operateur_id == Operateur.id)
        .filter(Competence.operation_libelle.in_(operations_uniques))
        .filter(Competence.chaine.isnot(None))
        .filter(Operateur.matricule.is_(None))
        .group_by(Competence.chaine, Competence.operation_libelle)
        .all()
    )

    stats: dict[str, dict] = defaultdict(lambda: {"operations_couvertes": set(), "experience_totale": 0})
    for chaine, operation_libelle, meilleure_occurrence in rows:
        stats[chaine]["operations_couvertes"].add(operation_libelle)
        stats[chaine]["experience_totale"] += meilleure_occurrence

    classement = sorted(
        stats.items(),
        key=lambda item: (len(item[1]["operations_couvertes"]), item[1]["experience_totale"]),
        reverse=True,
    )

    return [
        ChaineSuggereeOut(
            chaine=chaine,
            nb_operations_couvertes=len(s["operations_couvertes"]),
            nb_operations_total=len(operations_uniques),
            experience_totale=s["experience_totale"],
        )
        for chaine, s in classement[:top_n]
    ]


def matrice_competences(
    db: Session, chaine: str, max_operations: int = 15, max_operateurs: int = 20
) -> MatriceCompetencesOut:
    """Heatmap operateurs x operations pour une chaine : limitee aux
    operations et operateurs les plus significatifs (volume d'occurrences)
    pour rester lisible - le catalogue d'operations reel comporte des
    milliers de libelles distincts, un tableau exhaustif serait inexploitable."""
    competences = (
        db.query(Competence)
        .join(Operateur, Competence.operateur_id == Operateur.id)
        .filter(Competence.chaine == chaine)
        .filter(Operateur.matricule.is_(None))
        .all()
    )

    total_par_operation: dict[str, int] = defaultdict(int)
    total_par_operateur: dict[str, int] = defaultdict(int)
    for c in competences:
        total_par_operation[c.operation_libelle] += c.nb_occurrences
        total_par_operateur[c.operateur.nom] += c.nb_occurrences

    operations = [
        op for op, _ in sorted(total_par_operation.items(), key=lambda kv: kv[1], reverse=True)[:max_operations]
    ]
    operateurs = [
        nom for nom, _ in sorted(total_par_operateur.items(), key=lambda kv: kv[1], reverse=True)[:max_operateurs]
    ]
    operations_retenues = set(operations)
    operateurs_retenus = set(operateurs)

    cellules = [
        CelluleCompetenceOut(
            operateur_nom=c.operateur.nom,
            operation_libelle=c.operation_libelle,
            nb_occurrences=c.nb_occurrences,
            temps_moyen=c.temps_moyen,
        )
        for c in competences
        if c.operation_libelle in operations_retenues and c.operateur.nom in operateurs_retenus
    ]

    return MatriceCompetencesOut(chaine=chaine, operateurs=operateurs, operations=operations, cellules=cellules)

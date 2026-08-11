"""Balancement de ligne : repartition de la charge de travail entre les
operateurs qualifies d'une chaine.

generation_service assigne, par defaut, a CHAQUE operation l'operateur le
plus experimente sur celle-ci - ce qui peut concentrer beaucoup de temps
sur un seul operateur et laisser les autres sous-charges. Ici on applique
une heuristique classique d'ordonnancement de charge, "Longest Processing
Time first" (LPT) : on traite les operations de la plus longue a la plus
courte et on assigne chacune a l'operateur QUALIFIE actuellement le moins
charge (a competence egale, on privilegie le plus experimente). LPT est un
algorithme glouton simple qui garantit une bonne approximation de
l'equilibrage optimal (facteur 4/3 dans le pire cas) et convient bien a un
usage industriel ou l'explicabilite du choix prime sur l'optimalite exacte.

Ne modifie que l'assignation operateur ; ne touche pas au temps estime ni a
l'ordre des operations (contrainte de sequencement de la gamme conservee).
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from models import Competence, Operateur
from schema import ChargeOperateurOut, OperationProposeeOut


@dataclass
class _Candidat:
    operateur_id: int
    operateur_nom: str
    nb_occurrences: int
    meme_chaine: bool


@dataclass
class _EtatOperateur:
    nom: str
    charge_secondes: float = 0.0
    nb_operations: int = 0


def _candidats_operation(db: Session, operation_libelle: str, chaine: str | None) -> list[_Candidat]:
    base_query = (
        db.query(Competence)
        .join(Operateur, Competence.operateur_id == Operateur.id)
        .filter(Competence.operation_libelle == operation_libelle)
        .filter(Operateur.matricule.is_(None))
    )

    competences = []
    meme_chaine = True
    if chaine:
        competences = base_query.filter(Competence.chaine == chaine).all()
        if not competences:
            competences = base_query.all()
            meme_chaine = False
    else:
        competences = base_query.all()
        meme_chaine = False

    return [
        _Candidat(
            operateur_id=c.operateur_id,
            operateur_nom=c.operateur.nom,
            nb_occurrences=c.nb_occurrences,
            meme_chaine=meme_chaine,
        )
        for c in competences
    ]


def equilibrer_charge(
    db: Session, operations: list[OperationProposeeOut], chaine: str | None
) -> list[OperationProposeeOut]:
    """Reassigne operateur_suggere sur chaque operation pour lisser la
    charge totale entre operateurs qualifies. Retourne une NOUVELLE liste
    (les operations sans temps estime ou sans candidat qualifie restent
    inchangees)."""

    indices_a_equilibrer = [
        i for i, op in enumerate(operations) if op.temps_estime is not None and op.temps_estime > 0
    ]
    # LPT : les operations les plus longues d'abord, pour eviter qu'une
    # grosse operation ne soit coincee en fin de repartition sur un
    # operateur deja charge.
    indices_a_equilibrer.sort(key=lambda i: operations[i].temps_estime, reverse=True)

    charges: dict[int, _EtatOperateur] = {}
    resultat = list(operations)

    for i in indices_a_equilibrer:
        op = operations[i]
        candidats = _candidats_operation(db, op.operation_libelle, chaine)
        if not candidats:
            continue

        for c in candidats:
            charges.setdefault(c.operateur_id, _EtatOperateur(nom=c.operateur_nom))

        # Le moins charge actuellement ; en cas d'egalite, le plus experimente.
        meilleur = min(
            candidats,
            key=lambda c: (charges[c.operateur_id].charge_secondes, -c.nb_occurrences),
        )

        etat = charges[meilleur.operateur_id]
        etat.charge_secondes += op.temps_estime
        etat.nb_operations += 1

        resultat[i] = op.model_copy(
            update={
                "operateur_suggere": meilleur.operateur_nom,
                "operateur_nb_occurrences": meilleur.nb_occurrences,
                "operateur_meme_chaine": meilleur.meme_chaine,
            }
        )

    return resultat


def calculer_charge_operateurs(operations: list[OperationProposeeOut]) -> list[ChargeOperateurOut]:
    """Vue de synthese : temps total et nombre d'operations par operateur
    suggere dans la liste donnee (quel que soit le mode d'assignation)."""
    par_operateur: dict[str, ChargeOperateurOut] = {}
    for op in operations:
        if not op.operateur_suggere:
            continue
        entree = par_operateur.setdefault(
            op.operateur_suggere,
            ChargeOperateurOut(operateur_nom=op.operateur_suggere, nb_operations=0, temps_total_secondes=0.0),
        )
        entree.nb_operations += 1
        entree.temps_total_secondes += op.temps_estime or 0.0

    return sorted(par_operateur.values(), key=lambda c: c.temps_total_secondes, reverse=True)

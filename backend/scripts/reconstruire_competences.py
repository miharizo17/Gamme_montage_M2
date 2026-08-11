"""Reconstruit la table Competence a partir de l'historique REEL des
GammeLigne : pour chaque (operateur, operation, chaine), on compte combien
de fois cet operateur a deja realise cette operation SUR CETTE CHAINE et le
temps moyen observe. C'est la matrice de competences qui alimentera
l'affectation operateur du moteur IA (croisement Skill Matrix).

La chaine fait partie de la cle : une chaine a ses propres operateurs, on
ne doit jamais suggerer un operateur d'une autre chaine.

Ignore volontairement les gammes DEMO-* (fictives) : la matrice de
competences ne doit refleter que de vraies observations.

A relancer apres chaque import/mise a jour des donnees reelles (script
idempotent : les competences des operateurs concernes sont entierement
recalculees a chaque execution, pas cumulees).

Usage:
    python reconstruire_competences.py
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # backend/

from database import Base_chebdo, SessionLocal, engine  # noqa: E402
from models import Article, Competence, Gamme, GammeLigne  # noqa: E402


def reconstruire(db):
    lignes = (
        db.query(GammeLigne, Article.chaine)
        .join(Gamme, GammeLigne.gamme_id == Gamme.id)
        .join(Article, Gamme.article_id == Article.id)
        .filter(~Article.code.like("DEMO-%"))
        .filter(GammeLigne.operateur_id.isnot(None))
        .all()
    )

    stats = defaultdict(lambda: {"nb": 0, "somme_temps": 0.0, "nb_temps": 0})
    for ligne, chaine in lignes:
        cle = (ligne.operateur_id, ligne.operation_libelle, chaine)
        stats[cle]["nb"] += 1
        if ligne.temps_equilibre is not None:
            stats[cle]["somme_temps"] += ligne.temps_equilibre
            stats[cle]["nb_temps"] += 1

    ids_operateurs_reels = {operateur_id for (operateur_id, _op, _chaine) in stats}
    if ids_operateurs_reels:
        db.query(Competence).filter(Competence.operateur_id.in_(ids_operateurs_reels)).delete(
            synchronize_session=False
        )

    for (operateur_id, operation_libelle, chaine), s in stats.items():
        temps_moyen = round(s["somme_temps"] / s["nb_temps"], 1) if s["nb_temps"] else None
        db.add(
            Competence(
                operateur_id=operateur_id,
                operation_libelle=operation_libelle,
                chaine=chaine,
                nb_occurrences=s["nb"],
                temps_moyen=temps_moyen,
            )
        )

    db.commit()
    return len(stats), len(ids_operateurs_reels)


def main():
    Base_chebdo.metadata.create_all(engine)
    db = SessionLocal()
    try:
        nb_competences, nb_operateurs = reconstruire(db)
    finally:
        db.close()
    print(f"Competences reconstruites : {nb_competences} lignes pour {nb_operateurs} operateurs reels.")


if __name__ == "__main__":
    main()

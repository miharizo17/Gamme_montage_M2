"""Assigne des dates d'enregistrement realistes et variees aux Gamme
reelles (jamais aux DEMO-*), a partir de l'annee reellement presente dans
le chemin source (ex: "ANDRY\\2023\\CH 7\\...") - segment 2 du chemin
pour la quasi-totalite des fichiers.

Pourquoi partir de l'annee reelle plutot que d'une date totalement
aleatoire : les dossiers sont deja organises par annee (2022 a 2026), on
garde donc une coherence avec la vraie donnee tout en variant le
jour/mois (qu'on ne connait pas). Si aucune annee n'est trouvee dans le
chemin, on tire une date uniforme entre le 01/01/2022 et aujourd'hui.
Les dates dans le futur (au-dela d'aujourd'hui) sont bornees a aujourd'hui.

Usage:
    python assigner_dates_realistes.py
"""
import random
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # backend/

from database import Base_chebdo, SessionLocal, engine  # noqa: E402
from models import Article, Gamme  # noqa: E402

random.seed(42)  # reproductible

AUJOURDHUI = datetime.now()
DEBUT_PLAGE = datetime(2022, 1, 1)


def extraire_annee(source: str) -> int | None:
    segments = source.split("\\")
    for segment in segments:
        segment = segment.strip()
        if re.fullmatch(r"\d{4}", segment):
            annee = int(segment)
            if 2000 <= annee <= AUJOURDHUI.year:
                return annee
    return None


def date_aleatoire_dans_annee(annee: int) -> datetime:
    debut = datetime(annee, 1, 1)
    fin = datetime(annee, 12, 31, 23, 59) if annee < AUJOURDHUI.year else AUJOURDHUI
    if fin <= debut:
        return debut
    delta = fin - debut
    return debut + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def date_aleatoire_uniforme() -> datetime:
    delta = AUJOURDHUI - DEBUT_PLAGE
    return DEBUT_PLAGE + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def assigner(db):
    lignes = (
        db.query(Gamme, Article.source)
        .join(Article, Gamme.article_id == Article.id)
        .filter(~Article.code.like("DEMO-%"))
        .all()
    )

    nb_par_annee_reelle = 0
    nb_par_tirage_uniforme = 0

    for gamme, source in lignes:
        annee = extraire_annee(source) if source else None
        if annee is not None:
            gamme.date_creation = date_aleatoire_dans_annee(annee)
            nb_par_annee_reelle += 1
        else:
            gamme.date_creation = date_aleatoire_uniforme()
            nb_par_tirage_uniforme += 1

    db.commit()
    return nb_par_annee_reelle, nb_par_tirage_uniforme


def main():
    Base_chebdo.metadata.create_all(engine)
    db = SessionLocal()
    try:
        nb_annee, nb_uniforme = assigner(db)
    finally:
        db.close()
    print(f"Dates assignees : {nb_annee} depuis l'annee reelle du chemin, {nb_uniforme} par tirage uniforme 2022-aujourd'hui.")


if __name__ == "__main__":
    main()

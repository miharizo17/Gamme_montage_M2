from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Article, Gamme, GammeLigne, Operateur
from schema import ArticleParChaineOut, GammeParMoisOut, StatistiquesOut


def obtenir_statistiques(db: Session) -> StatistiquesOut:
    nb_articles = db.query(func.count(Article.id)).scalar()
    nb_gammes = db.query(func.count(Gamme.id)).scalar()
    nb_operateurs_actifs = db.query(func.count(Operateur.id)).filter(Operateur.actif.is_(True)).scalar()
    nb_chaines = (
        db.query(func.count(func.distinct(Article.chaine))).filter(Article.chaine.isnot(None)).scalar()
    )

    smv_par_gamme = (
        db.query(GammeLigne.gamme_id, func.sum(GammeLigne.temps_equilibre).label("smv"))
        .filter(GammeLigne.temps_equilibre.isnot(None))
        .group_by(GammeLigne.gamme_id)
        .subquery()
    )
    smv_moyen_secondes = db.query(func.avg(smv_par_gamme.c.smv)).scalar()
    smv_moyen_minutes = round(smv_moyen_secondes / 60, 1) if smv_moyen_secondes else None

    # Regroupement par mois fait cote Python (pas de fonction de date SQL
    # portable entre SQLite - utilise pour les tests - et PostgreSQL).
    compte_par_mois: dict[str, int] = {}
    for (date_creation,) in db.query(Gamme.date_creation).all():
        if date_creation is None:
            continue
        cle = date_creation.strftime("%Y-%m")
        compte_par_mois[cle] = compte_par_mois.get(cle, 0) + 1
    gammes_par_mois = [
        GammeParMoisOut(mois=mois, nb_gammes=n) for mois, n in sorted(compte_par_mois.items())
    ]

    lignes_chaine = (
        db.query(Article.chaine, func.count(Article.id))
        .filter(Article.chaine.isnot(None))
        .group_by(Article.chaine)
        .order_by(func.count(Article.id).desc())
        .limit(15)
        .all()
    )
    articles_par_chaine = [ArticleParChaineOut(chaine=chaine, nb_articles=n) for chaine, n in lignes_chaine]

    return StatistiquesOut(
        nb_articles=nb_articles,
        nb_gammes=nb_gammes,
        nb_operateurs_actifs=nb_operateurs_actifs,
        nb_chaines=nb_chaines,
        smv_moyen_minutes=smv_moyen_minutes,
        gammes_par_mois=gammes_par_mois,
        articles_par_chaine=articles_par_chaine,
    )

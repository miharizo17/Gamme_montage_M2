from pydantic import BaseModel


class GammeParMoisOut(BaseModel):
    mois: str  # format "AAAA-MM"
    nb_gammes: int


class ArticleParChaineOut(BaseModel):
    chaine: str
    nb_articles: int


class StatistiquesOut(BaseModel):
    nb_articles: int
    nb_gammes: int
    nb_operateurs_actifs: int
    nb_chaines: int
    smv_moyen_minutes: float | None = None
    gammes_par_mois: list[GammeParMoisOut]
    articles_par_chaine: list[ArticleParChaineOut]

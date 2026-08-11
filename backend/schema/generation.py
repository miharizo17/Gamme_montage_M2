from pydantic import BaseModel, Field

from .chaine import ChaineSuggereeOut


class GenererGammeIn(BaseModel):
    description: str = Field(min_length=3)
    # Chaine choisie pour la production (prioritaire sur la chaine de la
    # gamme historique retrouvee, qui peut etre differente en pratique).
    chaine: str | None = None


class OperationProposeeOut(BaseModel):
    ordre: int
    operation_libelle: str
    temps_estime: float | None = None
    temps_mesure: bool = False  # False = pas de chrono reel, temps estime (historique ou ML)
    # Origine du temps affiche : "mesure" (chronometre reel),
    # "historique_operateur" (moyenne de l'operateur suggere) ou
    # "ml" (predit par le modele Random Forest, aucune autre donnee dispo).
    temps_source: str | None = None
    machine: str | None = None
    operateur_suggere: str | None = None
    operateur_nb_occurrences: int | None = None
    operateur_meme_chaine: bool | None = None  # None = chaine inconnue pour cette gamme


class GammeGenereeOut(BaseModel):
    article_reference_id: int
    article_reference_code: str
    article_reference_nom: str
    chaine: str | None = None
    score_similarite: float
    operations: list[OperationProposeeOut]
    # Chaines recommandees pour REALISER cette production (independamment
    # de la chaine choisie/deduite ci-dessus), classees par nombre
    # d'operations couvertes par un operateur experimente.
    chaines_suggerees: list[ChaineSuggereeOut] = []

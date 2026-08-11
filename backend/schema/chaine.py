from pydantic import BaseModel


class ChaineOut(BaseModel):
    chaine: str
    nb_gammes: int


class OperateurChaineOut(BaseModel):
    operateur_id: int
    nom: str
    nb_operations_distinctes: int
    nb_occurrences_total: int


class ChaineSuggereeOut(BaseModel):
    chaine: str
    nb_operations_couvertes: int
    nb_operations_total: int
    experience_totale: int


class CelluleCompetenceOut(BaseModel):
    operateur_nom: str
    operation_libelle: str
    nb_occurrences: int
    temps_moyen: float | None = None


class MatriceCompetencesOut(BaseModel):
    chaine: str
    # Operateurs/operations les plus significatifs de la chaine, deja
    # tries par volume d'occurrences decroissant (limites a un nombre
    # raisonnable pour rester lisible sous forme de heatmap).
    operateurs: list[str]
    operations: list[str]
    cellules: list[CelluleCompetenceOut]

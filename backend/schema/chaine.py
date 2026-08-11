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

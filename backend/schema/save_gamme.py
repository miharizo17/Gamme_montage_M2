from datetime import datetime

from pydantic import BaseModel, Field


class OperationAEnregistrerIn(BaseModel):
    ordre: int
    operation_libelle: str
    temps_estime: float | None = None
    machine: str | None = None
    operateur_nom: str | None = None


class EnregistrerGammeIn(BaseModel):
    nom: str = Field(min_length=1)
    chaine: str | None = None
    # Date d'enregistrement choisie par l'agent de methode. None = maintenant.
    date_creation: datetime | None = None
    operations: list[OperationAEnregistrerIn]

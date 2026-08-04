from pydantic import BaseModel


class GammeLigneOut(BaseModel):
    ordre: int
    operation_libelle: str
    temps_equilibre: float | None = None
    target: float | None = None
    machine: str | None = None
    operateur_nom: str | None = None

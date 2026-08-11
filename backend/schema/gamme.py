from pydantic import BaseModel


class GammeLigneOut(BaseModel):
    id: int
    ordre: int
    operation_libelle: str
    temps_equilibre: float | None = None
    target: float | None = None
    machine: str | None = None
    operateur_nom: str | None = None


class GammeLigneCreate(BaseModel):
    operation_libelle: str
    temps_equilibre: float | None = None
    target: float | None = None
    machine: str | None = None
    operateur_id: int | None = None
    # Alternative a operateur_id : resout (ou cree) l'operateur par son nom.
    # Utilise quand l'appelant ne connait que le nom (ex: interface de
    # generation, qui manipule des noms suggeres/corriges, pas des id).
    operateur_nom: str | None = None


class GammeLigneUpdate(BaseModel):
    operation_libelle: str | None = None
    temps_equilibre: float | None = None
    target: float | None = None
    machine: str | None = None
    operateur_id: int | None = None
    operateur_nom: str | None = None

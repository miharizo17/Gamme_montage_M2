from pydantic import BaseModel, ConfigDict


class OperateurOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    matricule: str | None = None
    actif: bool


class OperateurListOut(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[OperateurOut]


class CompetenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operation_libelle: str
    nb_occurrences: int
    temps_moyen: float | None = None

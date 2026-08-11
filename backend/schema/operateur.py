from pydantic import BaseModel, ConfigDict, Field


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


class OperateurCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=120)
    matricule: str | None = Field(default=None, max_length=30)


class OperateurUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=120)
    matricule: str | None = None
    actif: bool | None = None


class CompetenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operation_libelle: str
    nb_occurrences: int
    temps_moyen: float | None = None

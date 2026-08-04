from pydantic import BaseModel, Field


class GenererGammeIn(BaseModel):
    description: str = Field(min_length=3)


class OperationProposeeOut(BaseModel):
    ordre: int
    operation_libelle: str
    temps_estime: float | None = None
    machine: str | None = None
    operateur_suggere: str | None = None
    operateur_nb_occurrences: int | None = None


class GammeGenereeOut(BaseModel):
    article_reference_id: int
    article_reference_code: str
    article_reference_nom: str
    score_similarite: float
    operations: list[OperationProposeeOut]

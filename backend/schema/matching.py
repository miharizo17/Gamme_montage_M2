from pydantic import BaseModel, Field


class RechercheDescriptionIn(BaseModel):
    description: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)


class MatchGammeOut(BaseModel):
    article_id: int
    code: str
    nom: str
    score: float

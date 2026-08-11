from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .gamme import GammeLigneOut


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str
    description: str | None = None
    source: str | None = None
    chaine: str | None = None
    # Date d'enregistrement de la gamme (celle de sa derniere Gamme).
    date_creation: datetime | None = None


class ArticleListOut(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[ArticleOut]


class ArticleDetailOut(ArticleOut):
    gamme_id: int | None = None
    lignes_gamme: list[GammeLigneOut] = []


class ArticleCreate(BaseModel):
    code: str
    nom: str
    description: str | None = None
    source: str | None = None


class ArticleUpdate(BaseModel):
    code: str | None = None
    nom: str | None = None
    description: str | None = None
    source: str | None = None

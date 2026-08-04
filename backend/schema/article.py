from pydantic import BaseModel, ConfigDict

from .gamme import GammeLigneOut


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str
    description: str | None = None
    source: str | None = None


class ArticleListOut(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[ArticleOut]


class ArticleDetailOut(ArticleOut):
    gamme_id: int | None = None
    lignes_gamme: list[GammeLigneOut] = []

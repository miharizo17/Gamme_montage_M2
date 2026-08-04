from pydantic import BaseModel, ConfigDict


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

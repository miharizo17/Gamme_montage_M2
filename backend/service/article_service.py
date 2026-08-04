from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Article
from schema import ArticleListOut, ArticleOut


def lister_articles(db: Session, skip: int = 0, limit: int = 20) -> ArticleListOut:
    total = db.query(func.count(Article.id)).scalar()
    articles = (
        db.query(Article)
        .order_by(Article.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return ArticleListOut(
        total=total,
        skip=skip,
        limit=limit,
        items=[ArticleOut.model_validate(a) for a in articles],
    )

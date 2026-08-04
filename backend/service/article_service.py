from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Article
from schema import ArticleDetailOut, ArticleListOut, ArticleOut, GammeLigneOut


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


def obtenir_article_detail(db: Session, article_id: int) -> ArticleDetailOut | None:
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return None

    derniere_gamme = max(article.gammes, key=lambda g: g.date_creation, default=None)

    lignes_gamme = []
    if derniere_gamme is not None:
        lignes_gamme = [
            GammeLigneOut(
                ordre=ligne.ordre,
                operation_libelle=ligne.operation_libelle,
                temps_equilibre=ligne.temps_equilibre,
                target=ligne.target,
                machine=ligne.machine,
                operateur_nom=ligne.operateur.nom if ligne.operateur else None,
            )
            for ligne in derniere_gamme.lignes
        ]

    return ArticleDetailOut(
        id=article.id,
        code=article.code,
        nom=article.nom,
        description=article.description,
        source=article.source,
        gamme_id=derniere_gamme.id if derniere_gamme else None,
        lignes_gamme=lignes_gamme,
    )

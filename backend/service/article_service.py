from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Article, Gamme
from schema import ArticleCreate, ArticleDetailOut, ArticleListOut, ArticleOut, ArticleUpdate, GammeLigneOut


class CodeDejaExistant(Exception):
    """Leve quand on essaie de creer/modifier un article avec un code deja pris."""


def vers_article_detail(article: Article, gamme: Gamme | None) -> ArticleDetailOut:
    lignes_gamme = []
    if gamme is not None:
        lignes_gamme = [
            GammeLigneOut(
                id=ligne.id,
                ordre=ligne.ordre,
                operation_libelle=ligne.operation_libelle,
                temps_equilibre=ligne.temps_equilibre,
                target=ligne.target,
                machine=ligne.machine,
                operateur_nom=ligne.operateur.nom if ligne.operateur else None,
            )
            for ligne in gamme.lignes
        ]

    return ArticleDetailOut(
        id=article.id,
        code=article.code,
        nom=article.nom,
        description=article.description,
        source=article.source,
        gamme_id=gamme.id if gamme else None,
        lignes_gamme=lignes_gamme,
    )


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
    return vers_article_detail(article, derniere_gamme)


def creer_article(db: Session, data: ArticleCreate) -> ArticleOut:
    if db.query(Article.id).filter(Article.code == data.code).first() is not None:
        raise CodeDejaExistant(data.code)

    article = Article(code=data.code, nom=data.nom, description=data.description, source=data.source)
    db.add(article)
    db.commit()
    db.refresh(article)
    return ArticleOut.model_validate(article)


def modifier_article(db: Session, article_id: int, data: ArticleUpdate) -> ArticleOut | None:
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return None

    updates = data.model_dump(exclude_unset=True)

    nouveau_code = updates.get("code")
    if nouveau_code and nouveau_code != article.code:
        conflit = db.query(Article.id).filter(Article.code == nouveau_code).first()
        if conflit is not None:
            raise CodeDejaExistant(nouveau_code)

    for champ, valeur in updates.items():
        setattr(article, champ, valeur)

    db.commit()
    db.refresh(article)
    return ArticleOut.model_validate(article)

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
        chaine=article.chaine,
        date_creation=gamme.date_creation if gamme else None,
        gamme_id=gamme.id if gamme else None,
        lignes_gamme=lignes_gamme,
    )


SEUIL_SIMILARITE_TRIGRAMME = 0.15


def _est_postgres(db: Session) -> bool:
    bind = db.get_bind()
    return bind is not None and bind.dialect.name == "postgresql"


def lister_articles(
    db: Session, skip: int = 0, limit: int = 20, q: str | None = None, chaine: str | None = None
) -> ArticleListOut:
    # Derniere date de Gamme par article, jointe sans requete N+1.
    dates_par_article = (
        db.query(Gamme.article_id, func.max(Gamme.date_creation).label("date_creation"))
        .group_by(Gamme.article_id)
        .subquery()
    )

    filtre = db.query(Article, dates_par_article.c.date_creation).outerjoin(
        dates_par_article, dates_par_article.c.article_id == Article.id
    )

    similarite = None
    if q:
        motif = f"%{q}%"
        correspond_ilike = (Article.nom.ilike(motif)) | (Article.code.ilike(motif))
        if _est_postgres(db):
            # pg_trgm : tolere les fautes de frappe/variantes que ILIKE seul rate
            # (ex: "vest femme" retrouve "veste femme").
            similarite = func.greatest(func.similarity(Article.nom, q), func.similarity(Article.code, q))
            filtre = filtre.filter(correspond_ilike | (similarite > SEUIL_SIMILARITE_TRIGRAMME))
        else:
            filtre = filtre.filter(correspond_ilike)
    if chaine:
        filtre = filtre.filter(Article.chaine == chaine)

    total = filtre.with_entities(func.count(Article.id)).scalar()
    tri = filtre.order_by(similarite.desc(), Article.id) if similarite is not None else filtre.order_by(Article.id)
    lignes = tri.offset(skip).limit(limit).all()

    items = []
    for article, date_creation in lignes:
        item = ArticleOut.model_validate(article)
        item.date_creation = date_creation
        items.append(item)

    return ArticleListOut(total=total, skip=skip, limit=limit, items=items)


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


def supprimer_article(db: Session, article_id: int) -> bool:
    """Supprime l'article et, par cascade (ON DELETE CASCADE), ses gammes et
    leurs lignes. Ne touche pas aux operateurs ni a leur matrice de
    competences (l'historique de competence reste valable independamment)."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return False
    db.delete(article)
    db.commit()
    return True

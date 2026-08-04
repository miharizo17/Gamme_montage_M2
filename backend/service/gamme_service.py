from sqlalchemy.orm import Session

from models import Article, Gamme, GammeLigne
from schema import ArticleDetailOut, GammeLigneCreate, GammeLigneOut, GammeLigneUpdate
from service.article_service import vers_article_detail


def creer_gamme(db: Session, article_id: int, lignes: list[GammeLigneCreate]) -> ArticleDetailOut | None:
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return None

    gamme = Gamme(article_id=article.id)
    db.add(gamme)
    db.flush()  # recupere gamme.id sans committer

    for ordre, ligne_in in enumerate(lignes, start=1):
        db.add(
            GammeLigne(
                gamme_id=gamme.id,
                ordre=ordre,
                operation_libelle=ligne_in.operation_libelle,
                temps_equilibre=ligne_in.temps_equilibre,
                target=ligne_in.target,
                machine=ligne_in.machine,
                operateur_id=ligne_in.operateur_id,
            )
        )

    db.commit()
    db.refresh(article)
    db.refresh(gamme)
    return vers_article_detail(article, gamme)


def modifier_ligne_gamme(db: Session, ligne_id: int, data: GammeLigneUpdate) -> GammeLigneOut | None:
    ligne = db.query(GammeLigne).filter(GammeLigne.id == ligne_id).first()
    if ligne is None:
        return None

    updates = data.model_dump(exclude_unset=True)
    for champ, valeur in updates.items():
        setattr(ligne, champ, valeur)

    db.commit()
    db.refresh(ligne)

    return GammeLigneOut(
        id=ligne.id,
        ordre=ligne.ordre,
        operation_libelle=ligne.operation_libelle,
        temps_equilibre=ligne.temps_equilibre,
        target=ligne.target,
        machine=ligne.machine,
        operateur_nom=ligne.operateur.nom if ligne.operateur else None,
    )

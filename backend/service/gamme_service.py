import re
import unicodedata
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Article, Gamme, GammeLigne, Operateur
from schema import ArticleDetailOut, EnregistrerGammeIn, GammeLigneCreate, GammeLigneOut, GammeLigneUpdate
from service.article_service import vers_article_detail


def _resoudre_operateur(db: Session, operateur_id: int | None, operateur_nom: str | None) -> int | None:
    """operateur_id est prioritaire s'il est fourni. Sinon, resout (ou
    cree) l'operateur par son nom - insensible a la casse/aux espaces."""
    if operateur_id is not None:
        return operateur_id
    if not operateur_nom or not operateur_nom.strip():
        return None

    nom = operateur_nom.strip()
    operateur = db.query(Operateur).filter(func.lower(Operateur.nom) == nom.lower()).first()
    if operateur is None:
        operateur = Operateur(nom=nom, actif=True)
        db.add(operateur)
        db.flush()
    return operateur.id


def _slugifier(texte: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", texte) if not unicodedata.combining(c)).upper()
    s = re.sub(r"[^A-Z0-9]+", "-", s).strip("-")
    return s or "GAMME"


def _generer_code_unique(db: Session, base: str) -> str:
    slug = _slugifier(base)[:100]
    code = slug
    suffixe = 1
    while db.query(Article.id).filter(Article.code == code).first() is not None:
        suffixe += 1
        code = f"{slug}-{suffixe}"
    return code


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
                operateur_id=_resoudre_operateur(db, ligne_in.operateur_id, ligne_in.operateur_nom),
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
    operateur_nom = updates.pop("operateur_nom", None)
    if "operateur_id" in updates or operateur_nom is not None:
        ligne.operateur_id = _resoudre_operateur(db, updates.pop("operateur_id", None), operateur_nom)

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


def enregistrer_gamme_generee(db: Session, data: EnregistrerGammeIn) -> ArticleDetailOut:
    """Sauvegarde une gamme proposee par le moteur IA (et eventuellement
    corrigee par l'agent de methode) comme une vraie gamme reutilisable :
    un nouvel Article + une Gamme, jamais un ecrasement de la gamme
    historique qui a servi de reference au matching."""
    code = _generer_code_unique(db, data.nom)
    article = Article(
        code=code,
        nom=data.nom,
        description=None,
        source="Gamme enregistree manuellement (generation IA + corrections)",
        chaine=data.chaine,
    )
    db.add(article)
    db.flush()

    date_creation = data.date_creation or datetime.now(timezone.utc).replace(tzinfo=None)
    gamme = Gamme(article_id=article.id, date_creation=date_creation)
    db.add(gamme)
    db.flush()

    for operation in data.operations:
        db.add(
            GammeLigne(
                gamme_id=gamme.id,
                ordre=operation.ordre,
                operation_libelle=operation.operation_libelle,
                temps_equilibre=operation.temps_estime,
                target=None,
                machine=operation.machine,
                operateur_id=_resoudre_operateur(db, None, operation.operateur_nom),
            )
        )

    db.commit()
    db.refresh(article)
    db.refresh(gamme)
    return vers_article_detail(article, gamme)

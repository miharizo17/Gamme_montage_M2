"""Moteur de matching NLP baseline : TF-IDF + similarite cosinus entre la
description d'un prototype et les gammes historiques.

Chaque gamme historique est representee par un "document" texte = le nom
de l'article + les libelles de toutes ses operations. C'est necessaire
car les vraies fiches Excel n'ont pas de description libre du prototype -
seulement un nom de reference et une liste d'operations.

L'index (vectorizer + matrice TF-IDF) est mis en cache en memoire pour
eviter de le reconstruire a chaque requete. Utiliser reindexer() apres un
import de donnees pour le rafraichir.
"""
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from models import Article
from schema import MatchGammeOut


def construire_document_gamme(article: Article) -> str:
    derniere_gamme = max(article.gammes, key=lambda g: g.date_creation, default=None)
    operations = [ligne.operation_libelle for ligne in derniere_gamme.lignes] if derniere_gamme else []
    return " ".join([article.nom, *operations])


def construire_corpus(db: Session) -> tuple[list[int], list[str]]:
    article_ids: list[int] = []
    documents: list[str] = []
    for article in db.query(Article).all():
        doc = construire_document_gamme(article)
        if doc.strip():
            article_ids.append(article.id)
            documents.append(doc)
    return article_ids, documents


@dataclass
class _Index:
    article_ids: list[int]
    vectorizer: TfidfVectorizer
    matrice: object


_index: _Index | None = None


def reindexer(db: Session) -> int:
    """Reconstruit l'index TF-IDF depuis la base. Retourne le nombre de
    gammes indexees."""
    global _index
    article_ids, documents = construire_corpus(db)
    vectorizer = TfidfVectorizer()
    matrice = vectorizer.fit_transform(documents) if documents else None
    _index = _Index(article_ids=article_ids, vectorizer=vectorizer, matrice=matrice)
    return len(article_ids)


def rechercher_gammes_similaires(db: Session, description: str, top_k: int = 5) -> list[MatchGammeOut]:
    global _index
    if _index is None:
        reindexer(db)

    if not _index.article_ids:
        return []

    vecteur = _index.vectorizer.transform([description])
    similarites = cosine_similarity(vecteur, _index.matrice)[0]

    classement = sorted(zip(_index.article_ids, similarites), key=lambda x: x[1], reverse=True)[:top_k]
    ids_retenus = [article_id for article_id, _score in classement]

    articles_par_id = {a.id: a for a in db.query(Article).filter(Article.id.in_(ids_retenus)).all()}

    resultats = []
    for article_id, score in classement:
        article = articles_par_id.get(article_id)
        if article is None:
            continue
        resultats.append(
            MatchGammeOut(article_id=article.id, code=article.code, nom=article.nom, score=round(float(score), 4))
        )
    return resultats

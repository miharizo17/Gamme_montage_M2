from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from database import SessionLocal
from schema import (
    ArticleCreate,
    ArticleDetailOut,
    ArticleListOut,
    ArticleOut,
    ArticleUpdate,
    CompetenceOut,
    GammeLigneCreate,
    GammeLigneOut,
    GammeLigneUpdate,
    OperateurListOut,
)
from service import article_service, gamme_service, operateur_service
from service.article_service import CodeDejaExistant

app = FastAPI(title="Gamme Montage API")


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/articles", response_model=ArticleListOut)
def lister_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return article_service.lister_articles(db, skip=skip, limit=limit)


@app.get("/articles/{article_id}", response_model=ArticleDetailOut)
def obtenir_article(article_id: int, db: Session = Depends(get_db)):
    article = article_service.obtenir_article_detail(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return article


@app.post("/articles", response_model=ArticleOut, status_code=201)
def creer_article(data: ArticleCreate, db: Session = Depends(get_db)):
    try:
        return article_service.creer_article(db, data)
    except CodeDejaExistant:
        raise HTTPException(status_code=409, detail=f"Le code '{data.code}' existe deja")


@app.put("/articles/{article_id}", response_model=ArticleOut)
def modifier_article(article_id: int, data: ArticleUpdate, db: Session = Depends(get_db)):
    try:
        article = article_service.modifier_article(db, article_id, data)
    except CodeDejaExistant:
        raise HTTPException(status_code=409, detail=f"Le code '{data.code}' existe deja")
    if article is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return article


@app.post("/articles/{article_id}/gamme", response_model=ArticleDetailOut, status_code=201)
def creer_gamme(article_id: int, lignes: list[GammeLigneCreate], db: Session = Depends(get_db)):
    resultat = gamme_service.creer_gamme(db, article_id, lignes)
    if resultat is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return resultat


@app.put("/gamme-lignes/{ligne_id}", response_model=GammeLigneOut)
def modifier_ligne_gamme(ligne_id: int, data: GammeLigneUpdate, db: Session = Depends(get_db)):
    ligne = gamme_service.modifier_ligne_gamme(db, ligne_id, data)
    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne de gamme introuvable")
    return ligne


@app.get("/operateurs", response_model=OperateurListOut)
def lister_operateurs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return operateur_service.lister_operateurs(db, skip=skip, limit=limit)


@app.get("/operateurs/{operateur_id}/competences", response_model=list[CompetenceOut])
def obtenir_competences_operateur(operateur_id: int, db: Session = Depends(get_db)):
    if not operateur_service.operateur_existe(db, operateur_id):
        raise HTTPException(status_code=404, detail="Operateur introuvable")
    return operateur_service.obtenir_competences(db, operateur_id)


def main():
    print("Gamme de montage")


if __name__ == "__main__":
    main()

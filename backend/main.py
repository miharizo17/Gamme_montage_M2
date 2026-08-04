from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from database import SessionLocal
from schema import ArticleDetailOut, ArticleListOut
from service import article_service

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


def main():
    print("Gamme de montage")


if __name__ == "__main__":
    main()

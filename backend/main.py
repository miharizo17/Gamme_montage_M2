from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from database import SessionLocal
from schema import ArticleListOut
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


def main():
    print("Gamme de montage")


if __name__ == "__main__":
    main()

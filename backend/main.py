from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from deps import get_current_user, get_db, exiger_role
from models import Utilisateur
from schema import (
    ArticleCreate,
    ArticleDetailOut,
    ArticleListOut,
    ArticleOut,
    ArticleUpdate,
    ChaineOut,
    CompetenceOut,
    EnregistrerGammeIn,
    GammeGenereeOut,
    GammeLigneCreate,
    GammeLigneOut,
    GammeLigneUpdate,
    GenererGammeIn,
    LoginIn,
    MatchGammeOut,
    MatriceCompetencesOut,
    OperateurChaineOut,
    OperateurCreate,
    OperateurListOut,
    OperateurOut,
    OperateurUpdate,
    RechercheDescriptionIn,
    StatistiquesOut,
    TokenOut,
    UtilisateurCreateIn,
    UtilisateurOut,
)
from service import (
    article_service,
    auth_service,
    chaine_service,
    export_service,
    gamme_service,
    generation_service,
    matching_service,
    operateur_service,
    statistiques_service,
)
from service.article_service import CodeDejaExistant
from service.auth_service import IdentifiantsInvalides, NomUtilisateurDejaExistant

app = FastAPI(title="Gamme Montage API")


@app.post("/auth/login", response_model=TokenOut)
def se_connecter(data: LoginIn, db: Session = Depends(get_db)):
    try:
        return auth_service.authentifier(db, data.nom_utilisateur, data.mot_de_passe)
    except IdentifiantsInvalides:
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")


@app.get("/auth/moi", response_model=UtilisateurOut)
def qui_suis_je(utilisateur: Utilisateur = Depends(get_current_user)):
    return utilisateur


@app.get("/auth/utilisateurs", response_model=list[UtilisateurOut])
def lister_utilisateurs(
    db: Session = Depends(get_db), _admin: Utilisateur = Depends(exiger_role("administrateur"))
):
    return auth_service.lister_utilisateurs(db)


@app.post("/auth/utilisateurs", response_model=UtilisateurOut, status_code=201)
def creer_utilisateur(
    data: UtilisateurCreateIn,
    db: Session = Depends(get_db),
    _admin: Utilisateur = Depends(exiger_role("administrateur")),
):
    try:
        return auth_service.creer_utilisateur(db, data)
    except NomUtilisateurDejaExistant:
        raise HTTPException(status_code=409, detail=f"Le nom d'utilisateur '{data.nom_utilisateur}' existe deja")


@app.get("/articles", response_model=ArticleListOut)
def lister_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, description="Recherche texte libre sur le nom/code"),
    chaine: str | None = Query(None, description="Filtrer sur une chaine precise"),
    db: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(get_current_user),
):
    return article_service.lister_articles(db, skip=skip, limit=limit, q=q, chaine=chaine)


@app.get("/articles/{article_id}", response_model=ArticleDetailOut)
def obtenir_article(
    article_id: int, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    article = article_service.obtenir_article_detail(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return article


@app.get("/articles/{article_id}/export/excel")
def exporter_gamme_excel(
    article_id: int, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    article = article_service.obtenir_article_detail(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    contenu = export_service.generer_excel_gamme(article)
    return Response(
        content=contenu,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{article.code}.xlsx"'},
    )


@app.get("/articles/{article_id}/export/pdf")
def exporter_gamme_pdf(
    article_id: int, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    article = article_service.obtenir_article_detail(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    contenu = export_service.generer_pdf_gamme(article)
    return Response(
        content=contenu,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{article.code}.pdf"'},
    )


@app.post("/articles", response_model=ArticleOut, status_code=201)
def creer_article(
    data: ArticleCreate, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    try:
        return article_service.creer_article(db, data)
    except CodeDejaExistant:
        raise HTTPException(status_code=409, detail=f"Le code '{data.code}' existe deja")


@app.put("/articles/{article_id}", response_model=ArticleOut)
def modifier_article(
    article_id: int,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(get_current_user),
):
    try:
        article = article_service.modifier_article(db, article_id, data)
    except CodeDejaExistant:
        raise HTTPException(status_code=409, detail=f"Le code '{data.code}' existe deja")
    if article is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return article


@app.delete("/articles/{article_id}", status_code=204)
def supprimer_article(
    article_id: int, db: Session = Depends(get_db), _admin: Utilisateur = Depends(exiger_role("administrateur"))
):
    if not article_service.supprimer_article(db, article_id):
        raise HTTPException(status_code=404, detail="Article introuvable")


@app.post("/articles/{article_id}/gamme", response_model=ArticleDetailOut, status_code=201)
def creer_gamme(
    article_id: int,
    lignes: list[GammeLigneCreate],
    db: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(get_current_user),
):
    resultat = gamme_service.creer_gamme(db, article_id, lignes)
    if resultat is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return resultat


@app.put("/gamme-lignes/{ligne_id}", response_model=GammeLigneOut)
def modifier_ligne_gamme(
    ligne_id: int,
    data: GammeLigneUpdate,
    db: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(get_current_user),
):
    ligne = gamme_service.modifier_ligne_gamme(db, ligne_id, data)
    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne de gamme introuvable")
    return ligne


@app.get("/operateurs", response_model=OperateurListOut)
def lister_operateurs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(get_current_user),
):
    return operateur_service.lister_operateurs(db, skip=skip, limit=limit)


@app.post("/operateurs", response_model=OperateurOut, status_code=201)
def creer_operateur(
    data: OperateurCreate, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    return operateur_service.creer_operateur(db, data)


@app.put("/operateurs/{operateur_id}", response_model=OperateurOut)
def modifier_operateur(
    operateur_id: int,
    data: OperateurUpdate,
    db: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(get_current_user),
):
    operateur = operateur_service.modifier_operateur(db, operateur_id, data)
    if operateur is None:
        raise HTTPException(status_code=404, detail="Operateur introuvable")
    return operateur


@app.delete("/operateurs/{operateur_id}", status_code=204)
def supprimer_operateur(
    operateur_id: int, db: Session = Depends(get_db), _admin: Utilisateur = Depends(exiger_role("administrateur"))
):
    if not operateur_service.supprimer_operateur(db, operateur_id):
        raise HTTPException(status_code=404, detail="Operateur introuvable")


@app.get("/operateurs/{operateur_id}/competences", response_model=list[CompetenceOut])
def obtenir_competences_operateur(
    operateur_id: int, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    if not operateur_service.operateur_existe(db, operateur_id):
        raise HTTPException(status_code=404, detail="Operateur introuvable")
    return operateur_service.obtenir_competences(db, operateur_id)


@app.post("/gammes/similaires", response_model=list[MatchGammeOut])
def rechercher_gammes_similaires(
    data: RechercheDescriptionIn,
    db: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(get_current_user),
):
    return matching_service.rechercher_gammes_similaires(db, data.description, top_k=data.top_k)


@app.post("/gammes/reindexer")
def reindexer_moteur_matching(
    db: Session = Depends(get_db), _admin: Utilisateur = Depends(exiger_role("administrateur"))
):
    nb_gammes = matching_service.reindexer(db)
    return {"gammes_indexees": nb_gammes}


@app.post("/gammes/generer", response_model=GammeGenereeOut)
def generer_gamme(
    data: GenererGammeIn, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    resultat = generation_service.generer_gamme(
        db, data.description, chaine=data.chaine, equilibrer_charge=data.equilibrer_charge
    )
    if resultat is None:
        raise HTTPException(status_code=404, detail="Aucune gamme historique exploitable trouvee")
    return resultat


@app.post("/gammes/enregistrer", response_model=ArticleDetailOut, status_code=201)
def enregistrer_gamme(
    data: EnregistrerGammeIn, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    return gamme_service.enregistrer_gamme_generee(db, data)


@app.get("/chaines", response_model=list[ChaineOut])
def lister_chaines(db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)):
    return chaine_service.lister_chaines(db)


@app.get("/chaines/{chaine}/operateurs", response_model=list[OperateurChaineOut])
def lister_operateurs_chaine(
    chaine: str, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    return chaine_service.lister_operateurs_chaine(db, chaine)


@app.get("/chaines/{chaine}/matrice-competences", response_model=MatriceCompetencesOut)
def obtenir_matrice_competences(
    chaine: str, db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)
):
    return chaine_service.matrice_competences(db, chaine)


@app.get("/statistiques", response_model=StatistiquesOut)
def obtenir_statistiques(db: Session = Depends(get_db), _utilisateur: Utilisateur = Depends(get_current_user)):
    return statistiques_service.obtenir_statistiques(db)


def main():
    print("Gamme de montage")


if __name__ == "__main__":
    main()

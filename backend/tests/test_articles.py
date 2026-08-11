def test_lister_articles_vide(client):
    response = client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_creer_et_lister_article(client):
    payload = {"code": "T-001", "nom": "Veste test", "description": "desc"}
    response = client.post("/articles", json=payload)
    assert response.status_code == 201
    assert response.json()["code"] == "T-001"

    response = client.get("/articles")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["code"] == "T-001"


def test_pagination_articles(client):
    for i in range(5):
        client.post("/articles", json={"code": f"T-P{i}", "nom": f"Article {i}"})

    response = client.get("/articles?skip=3&limit=2")
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["items"][0]["code"] == "T-P3"


def test_recherche_articles_par_nom(client):
    client.post("/articles", json={"code": "T-VESTE", "nom": "Veste zippee"})
    client.post("/articles", json={"code": "T-PANTALON", "nom": "Pantalon droit"})

    response = client.get("/articles?q=veste")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["code"] == "T-VESTE"


def test_filtrer_articles_par_chaine(client, db_session):
    from models import Article

    a1 = client.post("/articles", json={"code": "T-CH7", "nom": "Article chaine 7"}).json()
    client.post("/articles", json={"code": "T-CH2", "nom": "Article chaine 2"})
    db_session.get(Article, a1["id"]).chaine = "ANDRY::CH7"
    db_session.commit()

    response = client.get("/articles?chaine=ANDRY::CH7")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["code"] == "T-CH7"


def test_creer_article_code_duplique(client):
    payload = {"code": "T-002", "nom": "Article"}
    client.post("/articles", json=payload)
    response = client.post("/articles", json=payload)
    assert response.status_code == 409


def test_obtenir_article_inexistant(client):
    response = client.get("/articles/999")
    assert response.status_code == 404


def test_modifier_article(client):
    creation = client.post("/articles", json={"code": "T-003", "nom": "Avant"})
    article_id = creation.json()["id"]

    response = client.put(f"/articles/{article_id}", json={"nom": "Apres"})
    assert response.status_code == 200
    assert response.json()["nom"] == "Apres"


def test_modifier_article_code_duplique(client):
    client.post("/articles", json={"code": "T-006", "nom": "Un"})
    creation = client.post("/articles", json={"code": "T-007", "nom": "Deux"})
    article_id = creation.json()["id"]

    response = client.put(f"/articles/{article_id}", json={"code": "T-006"})
    assert response.status_code == 409


def test_modifier_article_inexistant(client):
    response = client.put("/articles/999", json={"nom": "x"})
    assert response.status_code == 404


def test_creer_gamme_et_obtenir_detail(client):
    creation = client.post("/articles", json={"code": "T-004", "nom": "Robe"})
    article_id = creation.json()["id"]

    lignes = [
        {"operation_libelle": "PIQUAGE COL", "temps_equilibre": 30, "target": 120, "machine": "PIQUEUSE"},
        {"operation_libelle": "OURLET BAS", "temps_equilibre": 20, "target": 180, "machine": "OURLETEUSE"},
    ]
    response = client.post(f"/articles/{article_id}/gamme", json=lignes)
    assert response.status_code == 201
    detail = response.json()
    assert len(detail["lignes_gamme"]) == 2
    # L'ordre suit la position dans la liste envoyee, pas un numero de poste.
    assert [l["ordre"] for l in detail["lignes_gamme"]] == [1, 2]
    assert detail["lignes_gamme"][0]["operation_libelle"] == "PIQUAGE COL"


def test_creer_gamme_article_inexistant(client):
    response = client.post("/articles/999/gamme", json=[])
    assert response.status_code == 404


def test_date_creation_visible_dans_liste_et_detail(client):
    creation = client.post("/articles", json={"code": "T-DATE", "nom": "Article date"})
    article_id = creation.json()["id"]
    client.post(f"/articles/{article_id}/gamme", json=[{"operation_libelle": "PIQUAGE"}])

    detail = client.get(f"/articles/{article_id}").json()
    assert detail["date_creation"] is not None

    liste = client.get("/articles").json()
    article_liste = next(a for a in liste["items"] if a["id"] == article_id)
    assert article_liste["date_creation"] is not None


def test_date_creation_absente_sans_gamme(client):
    creation = client.post("/articles", json={"code": "T-SANS-GAMME", "nom": "Article sans gamme"})
    article_id = creation.json()["id"]

    detail = client.get(f"/articles/{article_id}").json()
    assert detail["date_creation"] is None


def test_modifier_ligne_gamme(client):
    creation = client.post("/articles", json={"code": "T-005", "nom": "Pantalon"})
    article_id = creation.json()["id"]
    gamme = client.post(
        f"/articles/{article_id}/gamme",
        json=[{"operation_libelle": "ASSEMBLAGE", "temps_equilibre": 40}],
    ).json()
    ligne_id = gamme["lignes_gamme"][0]["id"]

    response = client.put(f"/gamme-lignes/{ligne_id}", json={"temps_equilibre": 55.5})
    assert response.status_code == 200
    assert response.json()["temps_equilibre"] == 55.5
    # Les champs non fournis ne sont pas ecrases.
    assert response.json()["operation_libelle"] == "ASSEMBLAGE"


def test_modifier_ligne_gamme_inexistante(client):
    response = client.put("/gamme-lignes/999", json={"temps_equilibre": 1})
    assert response.status_code == 404


def test_supprimer_article(client):
    creation = client.post("/articles", json={"code": "T-DEL", "nom": "A supprimer"})
    article_id = creation.json()["id"]

    response = client.delete(f"/articles/{article_id}")
    assert response.status_code == 204

    assert client.get(f"/articles/{article_id}").status_code == 404


def test_supprimer_article_supprime_sa_gamme_par_cascade(client, db_session):
    from models import Gamme

    creation = client.post("/articles", json={"code": "T-DEL2", "nom": "A supprimer avec gamme"})
    article_id = creation.json()["id"]
    client.post(f"/articles/{article_id}/gamme", json=[{"operation_libelle": "PIQUAGE"}])

    response = client.delete(f"/articles/{article_id}")
    assert response.status_code == 204

    assert db_session.query(Gamme).filter(Gamme.article_id == article_id).count() == 0


def test_supprimer_article_inexistant(client):
    response = client.delete("/articles/999")
    assert response.status_code == 404


def test_exporter_gamme_excel(client):
    creation = client.post("/articles", json={"code": "T-EXP1", "nom": "Export Excel"})
    article_id = creation.json()["id"]
    client.post(f"/articles/{article_id}/gamme", json=[{"operation_libelle": "PIQUAGE", "temps_equilibre": 30}])

    response = client.get(f"/articles/{article_id}/export/excel")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.content[:2] == b"PK"  # signature ZIP (format xlsx)


def test_exporter_gamme_pdf(client):
    creation = client.post("/articles", json={"code": "T-EXP2", "nom": "Export PDF"})
    article_id = creation.json()["id"]
    client.post(f"/articles/{article_id}/gamme", json=[{"operation_libelle": "PIQUAGE", "temps_equilibre": 30}])

    response = client.get(f"/articles/{article_id}/export/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:5] == b"%PDF-"


def test_exporter_gamme_inexistante(client):
    assert client.get("/articles/999/export/excel").status_code == 404
    assert client.get("/articles/999/export/pdf").status_code == 404

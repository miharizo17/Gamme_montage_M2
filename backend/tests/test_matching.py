def test_similaires_sans_donnees(client):
    response = client.post("/gammes/similaires", json={"description": "veste avec zip"})
    assert response.status_code == 200
    assert response.json() == []


def test_similaires_retrouve_larticle_le_plus_proche(client):
    veste = client.post("/articles", json={"code": "M-VESTE", "nom": "Veste zippee"}).json()
    client.post(
        f"/articles/{veste['id']}/gamme",
        json=[
            {"operation_libelle": "POSER ZIP"},
            {"operation_libelle": "MONTAGE COL"},
            {"operation_libelle": "DOUBLURE"},
        ],
    )
    pantalon = client.post("/articles", json={"code": "M-PANTALON", "nom": "Pantalon"}).json()
    client.post(
        f"/articles/{pantalon['id']}/gamme",
        json=[
            {"operation_libelle": "OURLET BAS"},
            {"operation_libelle": "POSE CEINTURE"},
            {"operation_libelle": "ASSEMBLAGE ENTREJAMBE"},
        ],
    )

    response = client.post("/gammes/similaires", json={"description": "veste avec zip et col", "top_k": 1})
    assert response.status_code == 200
    resultats = response.json()
    assert len(resultats) == 1
    assert resultats[0]["code"] == "M-VESTE"
    assert resultats[0]["score"] > 0


def test_similaires_top_k_respecte(client):
    for i in range(4):
        article = client.post("/articles", json={"code": f"M-{i}", "nom": f"Modele robe {i}"}).json()
        client.post(f"/articles/{article['id']}/gamme", json=[{"operation_libelle": "OURLET ROBE"}])

    response = client.post("/gammes/similaires", json={"description": "robe", "top_k": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_reindexer(client):
    client.post("/articles", json={"code": "M-REINDEX", "nom": "Article"})
    response = client.post("/gammes/reindexer")
    assert response.status_code == 200
    # Un article sans gamme est quand meme indexe via son nom seul.
    assert response.json()["gammes_indexees"] == 1

    article = client.post("/articles", json={"code": "M-REINDEX-2", "nom": "Article avec gamme"}).json()
    client.post(f"/articles/{article['id']}/gamme", json=[{"operation_libelle": "PIQUAGE"}])
    response = client.post("/gammes/reindexer")
    assert response.json()["gammes_indexees"] == 2

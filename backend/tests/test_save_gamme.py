from models import Operateur


def test_enregistrer_gamme_creation_basique(client):
    payload = {
        "nom": "Veste generee corrigee",
        "chaine": "ANDRY::CH7",
        "operations": [
            {"ordre": 1, "operation_libelle": "POSER ZIP", "temps_estime": 40, "machine": "PP1", "operateur_nom": "Nadia"},
            {"ordre": 2, "operation_libelle": "MONTAGE COL", "temps_estime": 30, "machine": "PP1", "operateur_nom": None},
        ],
    }
    response = client.post("/gammes/enregistrer", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Veste generee corrigee"
    assert data["chaine"] == "ANDRY::CH7"
    assert len(data["lignes_gamme"]) == 2
    assert data["lignes_gamme"][0]["operateur_nom"] == "Nadia"
    assert data["lignes_gamme"][1]["operateur_nom"] is None

    # Doit apparaitre dans la liste (historique)
    liste = client.get("/articles").json()
    assert any(a["code"] == data["code"] for a in liste["items"])


def test_enregistrer_gamme_code_unique_si_nom_duplique(client):
    payload = {"nom": "Meme Nom", "operations": [{"ordre": 1, "operation_libelle": "PIQUAGE"}]}
    r1 = client.post("/gammes/enregistrer", json=payload)
    r2 = client.post("/gammes/enregistrer", json=payload)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["code"] != r2.json()["code"]


def test_enregistrer_gamme_date_choisie(client):
    payload = {
        "nom": "Gamme datee",
        "date_creation": "2025-01-15T10:00:00",
        "operations": [{"ordre": 1, "operation_libelle": "PIQUAGE"}],
    }
    response = client.post("/gammes/enregistrer", json=payload)
    assert response.status_code == 201


def test_enregistrer_gamme_reutilise_operateur_existant(client, db_session):
    operateur = Operateur(nom="Nadia", matricule=None, actif=True)
    db_session.add(operateur)
    db_session.commit()

    payload = {
        "nom": "Gamme avec operateur existant",
        "operations": [{"ordre": 1, "operation_libelle": "PIQUAGE", "operateur_nom": "nadia"}],  # casse differente
    }
    response = client.post("/gammes/enregistrer", json=payload)
    assert response.status_code == 201

    # Verifie qu'aucun doublon d'operateur n'a ete cree
    assert db_session.query(Operateur).filter(Operateur.nom.ilike("nadia")).count() == 1


def test_modifier_ligne_gamme_par_nom_operateur(client):
    creation = client.post("/articles", json={"code": "T-EDIT", "nom": "Article edit"})
    article_id = creation.json()["id"]
    gamme = client.post(f"/articles/{article_id}/gamme", json=[{"operation_libelle": "PIQUAGE"}]).json()
    ligne_id = gamme["lignes_gamme"][0]["id"]

    response = client.put(f"/gamme-lignes/{ligne_id}", json={"operateur_nom": "Nouvel Operateur"})
    assert response.status_code == 200
    assert response.json()["operateur_nom"] == "Nouvel Operateur"

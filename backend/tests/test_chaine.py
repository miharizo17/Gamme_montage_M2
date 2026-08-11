from models import Article, Competence, Operateur


def test_lister_chaines_vide(client):
    response = client.get("/chaines")
    assert response.status_code == 200
    assert response.json() == []


def test_lister_chaines(client, db_session):
    a1 = client.post("/articles", json={"code": "M-A1", "nom": "Article 1"}).json()
    a2 = client.post("/articles", json={"code": "M-A2", "nom": "Article 2"}).json()
    db_session.get(Article, a1["id"]).chaine = "ANDRY::CH7"
    db_session.get(Article, a2["id"]).chaine = "ANDRY::CH7"
    db_session.commit()

    response = client.get("/chaines")
    data = response.json()
    assert data == [{"chaine": "ANDRY::CH7", "nb_gammes": 2}]


def test_operateurs_par_chaine(client, db_session):
    operateur_ch7 = Operateur(nom="Operateur CH7", matricule=None, actif=True)
    operateur_ch2 = Operateur(nom="Operateur CH2", matricule=None, actif=True)
    db_session.add_all([operateur_ch7, operateur_ch2])
    db_session.commit()
    db_session.add_all(
        [
            Competence(operateur_id=operateur_ch7.id, operation_libelle="POSER ZIP", chaine="ANDRY::CH7", nb_occurrences=5, temps_moyen=30.0),
            Competence(operateur_id=operateur_ch7.id, operation_libelle="MONTAGE COL", chaine="ANDRY::CH7", nb_occurrences=3, temps_moyen=25.0),
            Competence(operateur_id=operateur_ch2.id, operation_libelle="POSER ZIP", chaine="ANDRY::CH2", nb_occurrences=9, temps_moyen=28.0),
        ]
    )
    db_session.commit()

    response = client.get("/chaines/ANDRY::CH7/operateurs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nom"] == "Operateur CH7"
    assert data[0]["nb_operations_distinctes"] == 2
    assert data[0]["nb_occurrences_total"] == 8

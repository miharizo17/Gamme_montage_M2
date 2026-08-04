from models import Competence, Operateur


def test_generer_sans_donnees(client):
    response = client.post("/gammes/generer", json={"description": "veste avec zip"})
    assert response.status_code == 404


def test_generer_reprend_la_gamme_la_plus_proche(client):
    article = client.post("/articles", json={"code": "M-VESTE2", "nom": "Veste test"}).json()
    client.post(
        f"/articles/{article['id']}/gamme",
        json=[
            {"operation_libelle": "POSER ZIP", "temps_equilibre": 40, "machine": "PP1"},
            {"operation_libelle": "MONTAGE COL", "temps_equilibre": 30, "machine": "PP1"},
        ],
    )

    response = client.post("/gammes/generer", json={"description": "veste avec zip et col"})
    assert response.status_code == 200
    data = response.json()
    assert data["article_reference_code"] == "M-VESTE2"
    assert [o["operation_libelle"] for o in data["operations"]] == ["POSER ZIP", "MONTAGE COL"]
    assert data["operations"][0]["temps_estime"] == 40


def test_generer_suggere_loperateur_le_plus_competent(client, db_session):
    article = client.post("/articles", json={"code": "M-VESTE3", "nom": "Veste test 3"}).json()
    client.post(f"/articles/{article['id']}/gamme", json=[{"operation_libelle": "POSER ZIP", "temps_equilibre": 40}])

    operateur_expert = Operateur(nom="Expert Zip", matricule=None, actif=True)
    operateur_novice = Operateur(nom="Novice Zip", matricule=None, actif=True)
    db_session.add_all([operateur_expert, operateur_novice])
    db_session.commit()
    db_session.add_all(
        [
            Competence(operateur_id=operateur_expert.id, operation_libelle="POSER ZIP", nb_occurrences=10, temps_moyen=38.0),
            Competence(operateur_id=operateur_novice.id, operation_libelle="POSER ZIP", nb_occurrences=1, temps_moyen=55.0),
        ]
    )
    db_session.commit()

    response = client.post("/gammes/generer", json={"description": "veste avec zip"})
    assert response.status_code == 200
    operation = response.json()["operations"][0]
    assert operation["operateur_suggere"] == "Expert Zip"
    assert operation["operateur_nb_occurrences"] == 10


def test_generer_ignore_les_operateurs_fictifs(client, db_session):
    """Un operateur avec matricule (convention des donnees DEMO-*) ne doit
    jamais etre suggere pour une vraie generation."""
    article = client.post("/articles", json={"code": "M-VESTE4", "nom": "Veste test 4"}).json()
    client.post(f"/articles/{article['id']}/gamme", json=[{"operation_libelle": "POSER ZIP"}])

    operateur_demo = Operateur(nom="Operateur Demo", matricule="OP-001", actif=True)
    db_session.add(operateur_demo)
    db_session.commit()
    db_session.add(
        Competence(operateur_id=operateur_demo.id, operation_libelle="POSER ZIP", nb_occurrences=50, temps_moyen=30.0)
    )
    db_session.commit()

    response = client.post("/gammes/generer", json={"description": "veste avec zip"})
    operation = response.json()["operations"][0]
    assert operation["operateur_suggere"] is None

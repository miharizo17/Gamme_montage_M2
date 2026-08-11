from models import Competence, Operateur


def _creer_operateur(db_session, nom="Op Test", matricule="OP-T1"):
    operateur = Operateur(nom=nom, matricule=matricule, actif=True)
    db_session.add(operateur)
    db_session.commit()
    db_session.refresh(operateur)
    return operateur


def test_lister_operateurs_vide(client):
    response = client.get("/operateurs")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_lister_operateurs(client, db_session):
    _creer_operateur(db_session, nom="Andry Test")

    response = client.get("/operateurs")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nom"] == "Andry Test"


def test_competences_operateur_inexistant(client):
    response = client.get("/operateurs/999/competences")
    assert response.status_code == 404


def test_competences_operateur_vide(client, db_session):
    operateur = _creer_operateur(db_session)

    response = client.get(f"/operateurs/{operateur.id}/competences")
    assert response.status_code == 200
    assert response.json() == []


def test_competences_operateur_triees_par_occurrences(client, db_session):
    operateur = _creer_operateur(db_session)
    db_session.add(Competence(operateur_id=operateur.id, operation_libelle="OURLET", nb_occurrences=2, temps_moyen=25.0))
    db_session.add(Competence(operateur_id=operateur.id, operation_libelle="PIQUAGE", nb_occurrences=8, temps_moyen=30.0))
    db_session.commit()

    response = client.get(f"/operateurs/{operateur.id}/competences")
    data = response.json()
    assert len(data) == 2
    # La plus frequente (PIQUAGE, 8 occurrences) doit arriver en premier.
    assert data[0]["operation_libelle"] == "PIQUAGE"
    assert data[1]["operation_libelle"] == "OURLET"


def test_creer_operateur(client):
    response = client.post("/operateurs", json={"nom": "Nouvel Operateur", "matricule": "OP-99"})
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Nouvel Operateur"
    assert data["matricule"] == "OP-99"
    assert data["actif"] is True


def test_modifier_operateur(client, db_session):
    operateur = _creer_operateur(db_session)

    response = client.put(f"/operateurs/{operateur.id}", json={"nom": "Nom Corrige", "actif": False})
    assert response.status_code == 200
    data = response.json()
    assert data["nom"] == "Nom Corrige"
    assert data["actif"] is False


def test_modifier_operateur_inexistant(client):
    response = client.put("/operateurs/999", json={"nom": "Peu importe"})
    assert response.status_code == 404


def test_supprimer_operateur(client, db_session):
    operateur = _creer_operateur(db_session)

    response = client.delete(f"/operateurs/{operateur.id}")
    assert response.status_code == 204

    response = client.get("/operateurs")
    assert response.json()["total"] == 0


def test_supprimer_operateur_inexistant(client):
    response = client.delete("/operateurs/999")
    assert response.status_code == 404

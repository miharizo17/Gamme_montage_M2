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

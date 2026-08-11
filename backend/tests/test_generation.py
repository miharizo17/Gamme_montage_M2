from models import Article, Competence, Operateur


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
    assert data["operations"][0]["temps_source"] == "mesure"


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


def test_generer_priorite_operateur_meme_chaine(client, db_session):
    """Une chaine a ses propres operateurs : meme moins experimente sur le
    papier, l'operateur de LA chaine cible doit passer avant un operateur
    plus experimente mais d'une autre chaine."""
    article = client.post("/articles", json={"code": "M-VESTE5", "nom": "Veste test 5"}).json()
    client.post(f"/articles/{article['id']}/gamme", json=[{"operation_libelle": "POSER ZIP"}])
    db_article = db_session.get(Article, article["id"])
    db_article.chaine = "ANDRY::CH7"
    db_session.commit()

    operateur_autre_chaine = Operateur(nom="Expert Autre Chaine", matricule=None, actif=True)
    operateur_bonne_chaine = Operateur(nom="Operateur CH7", matricule=None, actif=True)
    db_session.add_all([operateur_autre_chaine, operateur_bonne_chaine])
    db_session.commit()
    db_session.add_all(
        [
            Competence(
                operateur_id=operateur_autre_chaine.id, operation_libelle="POSER ZIP",
                chaine="ANDRY::CH2", nb_occurrences=100, temps_moyen=30.0,
            ),
            Competence(
                operateur_id=operateur_bonne_chaine.id, operation_libelle="POSER ZIP",
                chaine="ANDRY::CH7", nb_occurrences=2, temps_moyen=45.0,
            ),
        ]
    )
    db_session.commit()

    response = client.post("/gammes/generer", json={"description": "veste avec zip"})
    operation = response.json()["operations"][0]
    assert operation["operateur_suggere"] == "Operateur CH7"
    assert operation["operateur_meme_chaine"] is True


def test_generer_repli_autre_chaine_si_rien_sur_la_chaine_cible(client, db_session):
    article = client.post("/articles", json={"code": "M-VESTE6", "nom": "Veste test 6"}).json()
    client.post(f"/articles/{article['id']}/gamme", json=[{"operation_libelle": "POSER ZIP"}])
    db_article = db_session.get(Article, article["id"])
    db_article.chaine = "ANDRY::CH7"
    db_session.commit()

    operateur = Operateur(nom="Operateur Autre Chaine", matricule=None, actif=True)
    db_session.add(operateur)
    db_session.commit()
    db_session.add(
        Competence(operateur_id=operateur.id, operation_libelle="POSER ZIP", chaine="ANDRY::CH2", nb_occurrences=5, temps_moyen=30.0)
    )
    db_session.commit()

    response = client.post("/gammes/generer", json={"description": "veste avec zip"})
    operation = response.json()["operations"][0]
    assert operation["operateur_suggere"] == "Operateur Autre Chaine"
    assert operation["operateur_meme_chaine"] is False


def test_generer_temps_estime_depuis_historique_si_absent(client, db_session):
    """Si la ligne source n'a pas de temps chronometre, on retombe sur le
    temps moyen historique de l'operateur suggere, marque non mesure."""
    article = client.post("/articles", json={"code": "M-VESTE7", "nom": "Veste test 7"}).json()
    client.post(f"/articles/{article['id']}/gamme", json=[{"operation_libelle": "POSER ZIP"}])

    operateur = Operateur(nom="Operateur Zip", matricule=None, actif=True)
    db_session.add(operateur)
    db_session.commit()
    db_session.add(
        Competence(operateur_id=operateur.id, operation_libelle="POSER ZIP", nb_occurrences=5, temps_moyen=42.5)
    )
    db_session.commit()

    response = client.post("/gammes/generer", json={"description": "veste avec zip"})
    operation = response.json()["operations"][0]
    assert operation["temps_estime"] == 42.5
    assert operation["temps_mesure"] is False
    assert operation["temps_source"] == "historique_operateur"


def test_generer_temps_source_ml_si_rien_dautre_disponible(client):
    """Troisieme niveau de repli : si l'operation n'a ni temps mesure ni
    aucune competence, le temps predit par le modele ML est utilise (si
    le modele est present sur la machine qui fait tourner les tests)."""
    from service import ml_service

    if not ml_service.modele_disponible():
        import pytest
        pytest.skip("Modele ML non entraine sur cette machine (backend/ml_models/modele_temps.joblib absent)")

    article = client.post("/articles", json={"code": "M-VESTE9", "nom": "Veste test 9"}).json()
    client.post(f"/articles/{article['id']}/gamme", json=[{"operation_libelle": "POSER ZIP", "machine": "PP1"}])

    response = client.post("/gammes/generer", json={"description": "veste avec zip"})
    assert response.status_code == 200
    operation = response.json()["operations"][0]
    assert operation["temps_mesure"] is False
    assert operation["temps_source"] == "ml"
    assert operation["temps_estime"] is not None
    assert operation["temps_estime"] > 0


def test_generer_chaine_choisie_prime_sur_celle_de_larticle(client, db_session):
    """L'agent de methode choisit sur quelle chaine la production va se
    faire : ca doit primer sur la chaine de la gamme historique retrouvee,
    qui peut etre differente en pratique."""
    article = client.post("/articles", json={"code": "M-VESTE8", "nom": "Veste test 8"}).json()
    client.post(f"/articles/{article['id']}/gamme", json=[{"operation_libelle": "POSER ZIP"}])
    db_article = db_session.get(Article, article["id"])
    db_article.chaine = "ANDRY::CH7"  # chaine de la gamme historique
    db_session.commit()

    operateur_ch7 = Operateur(nom="Operateur CH7", matricule=None, actif=True)
    operateur_ch3 = Operateur(nom="Operateur CH3", matricule=None, actif=True)
    db_session.add_all([operateur_ch7, operateur_ch3])
    db_session.commit()
    db_session.add_all(
        [
            Competence(operateur_id=operateur_ch7.id, operation_libelle="POSER ZIP", chaine="ANDRY::CH7", nb_occurrences=20, temps_moyen=30.0),
            Competence(operateur_id=operateur_ch3.id, operation_libelle="POSER ZIP", chaine="ANDRY::CH3", nb_occurrences=1, temps_moyen=50.0),
        ]
    )
    db_session.commit()

    # On choisit explicitement CH3 pour CETTE production (pas CH7, la chaine historique)
    response = client.post("/gammes/generer", json={"description": "veste avec zip", "chaine": "ANDRY::CH3"})
    assert response.status_code == 200
    data = response.json()
    assert data["chaine"] == "ANDRY::CH3"
    operation = data["operations"][0]
    assert operation["operateur_suggere"] == "Operateur CH3"
    assert operation["operateur_meme_chaine"] is True

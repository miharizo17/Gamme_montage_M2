from datetime import datetime

from models import Article, Gamme, GammeLigne, Operateur


def test_statistiques_vides(client):
    response = client.get("/statistiques")
    assert response.status_code == 200
    data = response.json()
    assert data["nb_articles"] == 0
    assert data["nb_gammes"] == 0
    assert data["nb_operateurs_actifs"] == 0
    assert data["gammes_par_mois"] == []
    assert data["articles_par_chaine"] == []


def test_statistiques_agregent_correctement(client, db_session):
    article1 = Article(code="S-001", nom="Veste", chaine="ANDRY::CH1")
    article2 = Article(code="S-002", nom="Pantalon", chaine="ANDRY::CH1")
    db_session.add_all([article1, article2])
    db_session.commit()

    gamme1 = Gamme(article_id=article1.id, date_creation=datetime(2026, 1, 15))
    gamme2 = Gamme(article_id=article2.id, date_creation=datetime(2026, 1, 20))
    db_session.add_all([gamme1, gamme2])
    db_session.commit()

    db_session.add_all(
        [
            GammeLigne(gamme_id=gamme1.id, ordre=1, operation_libelle="OP1", temps_equilibre=60),
            GammeLigne(gamme_id=gamme1.id, ordre=2, operation_libelle="OP2", temps_equilibre=40),
            GammeLigne(gamme_id=gamme2.id, ordre=1, operation_libelle="OP1", temps_equilibre=100),
        ]
    )
    db_session.add(Operateur(nom="Op Actif", actif=True))
    db_session.add(Operateur(nom="Op Inactif", actif=False))
    db_session.commit()

    response = client.get("/statistiques")
    data = response.json()

    assert data["nb_articles"] == 2
    assert data["nb_gammes"] == 2
    assert data["nb_operateurs_actifs"] == 1
    assert data["nb_chaines"] == 1
    # SMV moyen = moyenne(100, 100) = 100s = 1.7 min
    assert data["smv_moyen_minutes"] == 1.7
    assert data["gammes_par_mois"] == [{"mois": "2026-01", "nb_gammes": 2}]
    assert data["articles_par_chaine"] == [{"chaine": "ANDRY::CH1", "nb_articles": 2}]

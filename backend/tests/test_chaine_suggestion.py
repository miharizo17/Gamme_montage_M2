from models import Article, Competence, Operateur


def test_generer_suggere_la_chaine_la_mieux_equipee(client, db_session):
    """Meme si l'agent de methode choisit une chaine, on doit quand meme
    lui indiquer quelle chaine est la mieux equipee pour cette production
    (celle qui couvre le plus d'operations avec des operateurs experimentes)."""
    article = client.post("/articles", json={"code": "M-VESTE9", "nom": "Veste test 9"}).json()
    client.post(
        f"/articles/{article['id']}/gamme",
        json=[
            {"operation_libelle": "POSER ZIP"},
            {"operation_libelle": "MONTAGE COL"},
        ],
    )
    db_article = db_session.get(Article, article["id"])
    db_article.chaine = "ANDRY::CH7"  # chaine choisie/deduite pour cette generation
    db_session.commit()

    # CH3 : experimentee sur les 2 operations (bien equipee)
    op_ch3_a = Operateur(nom="Op CH3 A", matricule=None, actif=True)
    op_ch3_b = Operateur(nom="Op CH3 B", matricule=None, actif=True)
    # CH9 : experimentee sur une seule operation
    op_ch9 = Operateur(nom="Op CH9", matricule=None, actif=True)
    db_session.add_all([op_ch3_a, op_ch3_b, op_ch9])
    db_session.commit()
    db_session.add_all(
        [
            Competence(operateur_id=op_ch3_a.id, operation_libelle="POSER ZIP", chaine="ANDRY::CH3", nb_occurrences=10, temps_moyen=30.0),
            Competence(operateur_id=op_ch3_b.id, operation_libelle="MONTAGE COL", chaine="ANDRY::CH3", nb_occurrences=8, temps_moyen=25.0),
            Competence(operateur_id=op_ch9.id, operation_libelle="POSER ZIP", chaine="ANDRY::CH9", nb_occurrences=50, temps_moyen=28.0),
        ]
    )
    db_session.commit()

    response = client.post("/gammes/generer", json={"description": "veste avec zip et col"})
    assert response.status_code == 200
    suggestions = response.json()["chaines_suggerees"]
    assert suggestions[0]["chaine"] == "ANDRY::CH3"
    assert suggestions[0]["nb_operations_couvertes"] == 2
    assert suggestions[0]["nb_operations_total"] == 2

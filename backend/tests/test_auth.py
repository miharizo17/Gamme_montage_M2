from models import Utilisateur
from security import hasher_mot_de_passe


def _creer_utilisateur(db_session, nom_utilisateur, mot_de_passe, role, actif=True):
    utilisateur = Utilisateur(
        nom_utilisateur=nom_utilisateur,
        mot_de_passe_hash=hasher_mot_de_passe(mot_de_passe),
        role=role,
        actif=actif,
    )
    db_session.add(utilisateur)
    db_session.commit()
    return utilisateur


def test_login_reussi_renvoie_un_token(client_sans_auth, db_session):
    _creer_utilisateur(db_session, "alice", "motdepasse123", "agent_methode")

    reponse = client_sans_auth.post(
        "/auth/login", json={"nom_utilisateur": "alice", "mot_de_passe": "motdepasse123"}
    )

    assert reponse.status_code == 200
    data = reponse.json()
    assert data["role"] == "agent_methode"
    assert data["nom_utilisateur"] == "alice"
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


def test_login_mauvais_mot_de_passe_refuse(client_sans_auth, db_session):
    _creer_utilisateur(db_session, "alice", "motdepasse123", "agent_methode")

    reponse = client_sans_auth.post("/auth/login", json={"nom_utilisateur": "alice", "mot_de_passe": "faux"})

    assert reponse.status_code == 401


def test_login_utilisateur_inconnu_refuse(client_sans_auth):
    reponse = client_sans_auth.post(
        "/auth/login", json={"nom_utilisateur": "inconnu", "mot_de_passe": "peuimporte"}
    )

    assert reponse.status_code == 401


def test_login_utilisateur_inactif_refuse(client_sans_auth, db_session):
    _creer_utilisateur(db_session, "bob", "motdepasse123", "agent_methode", actif=False)

    reponse = client_sans_auth.post("/auth/login", json={"nom_utilisateur": "bob", "mot_de_passe": "motdepasse123"})

    assert reponse.status_code == 401


def test_route_protegee_sans_token_refusee(client_sans_auth):
    reponse = client_sans_auth.get("/articles")
    assert reponse.status_code == 401


def test_route_protegee_avec_token_invalide_refusee(client_sans_auth):
    reponse = client_sans_auth.get("/articles", headers={"Authorization": "Bearer token-invalide"})
    assert reponse.status_code == 401


def test_route_protegee_avec_token_valide_acceptee(client_sans_auth, db_session):
    _creer_utilisateur(db_session, "alice", "motdepasse123", "agent_methode")
    token = client_sans_auth.post(
        "/auth/login", json={"nom_utilisateur": "alice", "mot_de_passe": "motdepasse123"}
    ).json()["access_token"]

    reponse = client_sans_auth.get("/articles", headers={"Authorization": f"Bearer {token}"})

    assert reponse.status_code == 200


def test_auth_moi_renvoie_utilisateur_courant(client_sans_auth, db_session):
    _creer_utilisateur(db_session, "alice", "motdepasse123", "agent_methode")
    token = client_sans_auth.post(
        "/auth/login", json={"nom_utilisateur": "alice", "mot_de_passe": "motdepasse123"}
    ).json()["access_token"]

    reponse = client_sans_auth.get("/auth/moi", headers={"Authorization": f"Bearer {token}"})

    assert reponse.status_code == 200
    assert reponse.json()["nom_utilisateur"] == "alice"
    assert reponse.json()["role"] == "agent_methode"


def test_route_admin_refusee_a_un_agent_methode(client_sans_auth, db_session):
    _creer_utilisateur(db_session, "alice", "motdepasse123", "agent_methode")
    token = client_sans_auth.post(
        "/auth/login", json={"nom_utilisateur": "alice", "mot_de_passe": "motdepasse123"}
    ).json()["access_token"]

    reponse = client_sans_auth.post(
        "/gammes/reindexer", headers={"Authorization": f"Bearer {token}"}
    )

    assert reponse.status_code == 403


def test_route_admin_acceptee_pour_un_administrateur(client_sans_auth, db_session):
    _creer_utilisateur(db_session, "admin1", "motdepasse123", "administrateur")
    token = client_sans_auth.post(
        "/auth/login", json={"nom_utilisateur": "admin1", "mot_de_passe": "motdepasse123"}
    ).json()["access_token"]

    reponse = client_sans_auth.post(
        "/gammes/reindexer", headers={"Authorization": f"Bearer {token}"}
    )

    assert reponse.status_code == 200


def test_creation_utilisateur_par_admin(client_sans_auth, db_session):
    _creer_utilisateur(db_session, "admin1", "motdepasse123", "administrateur")
    token = client_sans_auth.post(
        "/auth/login", json={"nom_utilisateur": "admin1", "mot_de_passe": "motdepasse123"}
    ).json()["access_token"]

    reponse = client_sans_auth.post(
        "/auth/utilisateurs",
        json={"nom_utilisateur": "nouveau", "mot_de_passe": "unautrepass", "role": "agent_methode"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert reponse.status_code == 201
    assert reponse.json()["nom_utilisateur"] == "nouveau"


def test_creation_utilisateur_nom_deja_pris(client_sans_auth, db_session):
    _creer_utilisateur(db_session, "admin1", "motdepasse123", "administrateur")
    _creer_utilisateur(db_session, "existant", "motdepasse123", "agent_methode")
    token = client_sans_auth.post(
        "/auth/login", json={"nom_utilisateur": "admin1", "mot_de_passe": "motdepasse123"}
    ).json()["access_token"]

    reponse = client_sans_auth.post(
        "/auth/utilisateurs",
        json={"nom_utilisateur": "existant", "mot_de_passe": "unautrepass", "role": "agent_methode"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert reponse.status_code == 409

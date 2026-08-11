"""Cree (ou reinitialise le mot de passe d')un compte administrateur.

Usage :
    python scripts/creer_utilisateur_admin.py <nom_utilisateur> <mot_de_passe> [--role administrateur|agent_methode]

Idempotent : si le nom d'utilisateur existe deja, son mot de passe et son
role sont mis a jour plutot que de creer un doublon.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import SessionLocal  # noqa: E402
from models import Utilisateur  # noqa: E402
from security import hasher_mot_de_passe  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("nom_utilisateur")
    parser.add_argument("mot_de_passe")
    parser.add_argument("--role", choices=["administrateur", "agent_methode"], default="administrateur")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        utilisateur = db.query(Utilisateur).filter(Utilisateur.nom_utilisateur == args.nom_utilisateur).first()
        if utilisateur is None:
            utilisateur = Utilisateur(nom_utilisateur=args.nom_utilisateur, role=args.role)
            db.add(utilisateur)
            action = "cree"
        else:
            utilisateur.role = args.role
            action = "mis a jour"

        utilisateur.mot_de_passe_hash = hasher_mot_de_passe(args.mot_de_passe)
        utilisateur.actif = True
        db.commit()
        print(f"Utilisateur '{args.nom_utilisateur}' ({args.role}) {action}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

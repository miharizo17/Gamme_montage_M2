"""Genere un jeu de donnees de test (FICTIF) pour demarrer le developpement
de l'API et du frontend sans attendre l'import des vraies gammes.

Toutes les references generees sont prefixees "DEMO-" pour qu'on puisse
les identifier et les supprimer facilement une fois les vraies donnees
disponibles (voir --reset).

Usage:
    python seed_fake_data.py            # cree les tables si besoin + insere les donnees demo
    python seed_fake_data.py --reset    # supprime les donnees DEMO-* existantes avant de reinserer
"""
import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # backend/

from database import Base_chebdo, SessionLocal, engine  # noqa: E402
from models import Article, Competence, Gamme, GammeLigne, Operateur  # noqa: E402

random.seed(42)  # resultats reproductibles d'une execution a l'autre

# --- Vocabulaire "metier" (base sur les libelles reels observes dans BASE MANING) ---

OPERATEURS = [
    "Andry RAKOTO", "Herizo RABE", "Hery RANDRIA", "Mamy Arline RASOA",
    "Rija ANDRIA", "Valisoa RAZAFY", "Fanja RAKOTOMALALA", "Lova RAZANAKOTO",
    "Tina RASOLOFO", "Njara RABEMANANJARA", "Sitraka RAZANADRAKOTO",
    "Faniry RAKOTONDRABE", "Miora RASOAMANARIVO", "Tahiry RANDRIANARISOA",
    "Zo RAKOTOARIVELO", "Nirina RAZAFINDRAKOTO",
]

MACHINES = [
    "PIQUEUSE PLATE", "SURJETEUSE", "RECOUVREUSE", "POINT NOUE",
    "BOUTONNIERE", "POSE BOUTON AUTO", "OURLETEUSE", "PRESSE", "MANUEL",
]

TYPES_VETEMENT = [
    ("Veste femme", "veste doublee, fermeture zip, deux poches passepoilees, col tailleur"),
    ("Chemise homme", "chemise manches longues, col chemisier, poignet boutonne, poche poitrine"),
    ("Pantalon", "pantalon droit, taille elastiquee, deux poches lateral, braguette zip"),
    ("Robe", "robe evasee, encolure ronde, manches courtes, fermeture zip dos"),
    ("Jupe", "jupe droite, taille haute, fente arriere, fermeture zip cote"),
    ("Short", "short taille elastiquee, deux poches, ourlet simple"),
    ("Blouson", "blouson zippe, col montant, poches plaquees, doublure filet"),
    ("Top", "top sans manches, encolure americaine, ourlet bas double"),
]

OPERATIONS_PAR_ETAPE = {
    "Preparation": [
        "TRACAGE REPERES", "THERMOCOLLAGE ENTOILAGE", "CRANTAGE", "MARQUAGE POCHE",
    ],
    "Assemblage": [
        "ASSEMBLAGE EPAULE", "ASSEMBLAGE COTE", "FERMETURE COTE DOUBLURE",
        "ASSEMBLAGE MANCHE", "MONTAGE COL", "MONTAGE POIGNET", "MONTAGE CEINTURE",
        "POSE PATTE BOUTONNAGE", "MONTAGE POCHE PASSEPOILEE", "MONTAGE FERMETURE ZIP",
        "ASSEMBLAGE ENTREJAMBE", "MONTAGE EMPIECEMENT DOS",
    ],
    "Finition": [
        "SURJET BORD", "SURPIQURE OURLET", "OURLET BAS MANCHE", "OURLET BAS VETEMENT",
        "BOUTONNIERE", "POSE BOUTON", "POSE ETIQUETTE", "SURPIQURE COL",
        "REPASSAGE INTERMEDIAIRE", "REPASSAGE FINAL",
    ],
    "Controle": [
        "CONTROLE QUALITE", "CONTROLE MESURES", "PLIAGE ET EMBALLAGE",
    ],
}

TOUTES_OPERATIONS = [op for ops in OPERATIONS_PAR_ETAPE.values() for op in ops]


def build_operateur_specialites(operateurs):
    """Simule des operateurs specialises (utile pour tester le futur moteur
    d'affectation par competence) : chacun maitrise bien un sous-ensemble
    d'operations, et peut depanner sur les autres avec un temps moins bon."""
    specialites = {}
    ops_cycle = TOUTES_OPERATIONS[:]
    random.shuffle(ops_cycle)
    chunk_size = max(3, len(ops_cycle) // len(operateurs))
    for i, nom in enumerate(operateurs):
        start = (i * chunk_size) % len(ops_cycle)
        specialites[nom] = set(ops_cycle[start:start + chunk_size] or ops_cycle[:chunk_size])
    return specialites


def choisir_operateur(operation_libelle, specialites, operateurs):
    """Priorite aux operateurs specialises sur cette operation, sinon
    n'importe qui (simule un remplacement)."""
    candidats = [nom for nom, ops in specialites.items() if operation_libelle in ops]
    if candidats and random.random() < 0.8:
        return random.choice(candidats)
    return random.choice(operateurs)


def generer_gamme_operations(nb_lignes=12):
    """Construit une sequence d'operations plausible : preparation, puis
    assemblage, puis finition, puis controle - dans cet ordre logique."""
    sequence = []
    sequence += random.sample(OPERATIONS_PAR_ETAPE["Preparation"], k=min(2, len(OPERATIONS_PAR_ETAPE["Preparation"])))
    sequence += random.sample(
        OPERATIONS_PAR_ETAPE["Assemblage"],
        k=min(nb_lignes - 5, len(OPERATIONS_PAR_ETAPE["Assemblage"])),
    )
    sequence += random.sample(OPERATIONS_PAR_ETAPE["Finition"], k=min(3, len(OPERATIONS_PAR_ETAPE["Finition"])))
    sequence += ["CONTROLE QUALITE", "PLIAGE ET EMBALLAGE"]
    return sequence


def reset_demo_data(session):
    demo_articles = session.query(Article).filter(Article.code.like("DEMO-%")).all()
    for article in demo_articles:
        session.delete(article)  # cascade sur Gamme puis GammeLigne
    session.query(Competence).delete()
    session.query(Operateur).delete()
    session.commit()


def seed(nb_articles=8):
    Base_chebdo.metadata.create_all(engine)
    session = SessionLocal()

    try:
        operateurs_db = {}
        for nom in OPERATEURS:
            matricule = f"OP-{len(operateurs_db) + 1:03d}"
            operateur = Operateur(nom=nom, matricule=matricule, actif=True)
            session.add(operateur)
            operateurs_db[nom] = operateur
        session.flush()  # recupere les id sans committer

        specialites = build_operateur_specialites(OPERATEURS)

        competence_stats = defaultdict(lambda: {"nb": 0, "somme_temps": 0.0})

        for i in range(1, nb_articles + 1):
            type_vetement, description_base = random.choice(TYPES_VETEMENT)
            code = f"DEMO-{i:03d}"
            nom_article = f"{type_vetement} {code}"
            description = f"{type_vetement} de test : {description_base}."

            article = Article(
                code=code,
                nom=nom_article,
                description=description,
                source="donnees de test generees (seed_fake_data.py)",
            )
            session.add(article)
            session.flush()

            gamme = Gamme(article_id=article.id)
            session.add(gamme)
            session.flush()

            operations = generer_gamme_operations(nb_lignes=random.randint(10, 15))
            for ordre, operation_libelle in enumerate(operations, start=1):
                nom_operateur = choisir_operateur(operation_libelle, specialites, OPERATEURS)
                operateur = operateurs_db[nom_operateur]

                est_specialiste = operation_libelle in specialites[nom_operateur]
                temps_base = random.uniform(15, 90)
                temps = round(temps_base * (0.9 if est_specialiste else 1.15), 1)
                target = round(3600 / temps, 1)

                ligne = GammeLigne(
                    gamme_id=gamme.id,
                    ordre=ordre,
                    operation_libelle=operation_libelle,
                    temps_equilibre=temps,
                    target=target,
                    machine=random.choice(MACHINES),
                    operateur_id=operateur.id,
                )
                session.add(ligne)

                key = (operateur.id, operation_libelle)
                competence_stats[key]["nb"] += 1
                competence_stats[key]["somme_temps"] += temps

        for (operateur_id, operation_libelle), stats in competence_stats.items():
            session.add(
                Competence(
                    operateur_id=operateur_id,
                    operation_libelle=operation_libelle,
                    nb_occurrences=stats["nb"],
                    temps_moyen=round(stats["somme_temps"] / stats["nb"], 1),
                )
            )

        session.commit()
        print(f"OK : {nb_articles} articles DEMO, {len(OPERATEURS)} operateurs, "
              f"{len(competence_stats)} lignes de competence inserees.")
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Supprime les donnees DEMO-* existantes avant de reinserer")
    parser.add_argument("--nb-articles", type=int, default=8, help="Nombre d'articles/gammes de test a generer")
    args = parser.parse_args()

    Base_chebdo.metadata.create_all(engine)

    if args.reset:
        session = SessionLocal()
        reset_demo_data(session)
        session.close()
        print("Anciennes donnees DEMO supprimees.")

    seed(nb_articles=args.nb_articles)


if __name__ == "__main__":
    main()

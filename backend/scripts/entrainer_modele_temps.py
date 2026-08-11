"""Entraine un modele de Machine Learning (Random Forest) qui predit le
temps standard (en secondes) d'une operation de montage, a partir de :
    - son libelle (texte, vectorise en TF-IDF),
    - la machine utilisee (categorielle).

C'est le troisieme niveau de repli du moteur de generation (voir
generation_service.py) :
    1. temps reellement chronometre sur la ligne de la gamme retrouvee,
    2. a defaut, temps moyen historique de l'operateur suggere,
    3. a defaut (aucune des deux precedentes disponible - ex: operation
       jamais vue par l'operateur suggere), prediction de ce modele.

Le modele est entraine UNIQUEMENT sur les donnees reelles (jamais les
gammes DEMO-*), et uniquement sur des temps strictement positifs (les
valeurs <= 0 sont des erreurs de saisie, pas des temps reels).

Usage:
    python entrainer_modele_temps.py
"""
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # backend/

from database import SessionLocal  # noqa: E402
from models import Article, Gamme, GammeLigne  # noqa: E402

MODELE_DIR = Path(__file__).resolve().parents[1] / "ml_models"
MODELE_PATH = MODELE_DIR / "modele_temps.joblib"


def charger_donnees(db) -> pd.DataFrame:
    lignes = (
        db.query(GammeLigne.operation_libelle, GammeLigne.machine, GammeLigne.temps_equilibre)
        .join(Gamme, GammeLigne.gamme_id == Gamme.id)
        .join(Article, Gamme.article_id == Article.id)
        .filter(~Article.code.like("DEMO-%"))
        .filter(GammeLigne.temps_equilibre.isnot(None))
        .filter(GammeLigne.temps_equilibre > 0)
        .all()
    )
    df = pd.DataFrame(lignes, columns=["operation_libelle", "machine", "temps_equilibre"])
    df["machine"] = df["machine"].fillna("INCONNUE")
    return df


def entrainer(df: pd.DataFrame):
    X = df[["operation_libelle", "machine"]]
    y = df["temps_equilibre"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pretraitement = ColumnTransformer(
        transformers=[
            ("texte", TfidfVectorizer(max_features=800, ngram_range=(1, 2)), "operation_libelle"),
            ("machine", OneHotEncoder(handle_unknown="ignore"), ["machine"]),
        ]
    )

    modele = Pipeline(
        steps=[
            ("pretraitement", pretraitement),
            ("regresseur", RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)),
        ]
    )

    modele.fit(X_train, y_train)

    predictions = modele.predict(X_test)
    metriques = {
        "mae": mean_absolute_error(y_test, predictions),
        "rmse": root_mean_squared_error(y_test, predictions),
        "r2": r2_score(y_test, predictions),
        "nb_train": len(X_train),
        "nb_test": len(X_test),
    }
    return modele, metriques


def main():
    db = SessionLocal()
    try:
        df = charger_donnees(db)
    finally:
        db.close()

    print(f"Donnees d'entrainement : {len(df)} lignes reelles avec temps mesure > 0")
    if len(df) < 100:
        raise SystemExit("Pas assez de donnees pour entrainer un modele fiable.")

    modele, metriques = entrainer(df)

    print()
    print("=== Evaluation sur le jeu de test (20% des donnees, jamais vu a l'entrainement) ===")
    print(f"Lignes d'entrainement : {metriques['nb_train']}")
    print(f"Lignes de test        : {metriques['nb_test']}")
    print(f"MAE  (erreur absolue moyenne)  : {metriques['mae']:.1f} s")
    print(f"RMSE (racine erreur quadratique): {metriques['rmse']:.1f} s")
    print(f"R2   (variance expliquee)       : {metriques['r2']:.3f}")

    MODELE_DIR.mkdir(exist_ok=True)
    joblib.dump(modele, MODELE_PATH)
    print()
    print(f"Modele sauvegarde : {MODELE_PATH}")


if __name__ == "__main__":
    main()

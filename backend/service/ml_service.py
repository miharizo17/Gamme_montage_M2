"""Charge le modele de prediction de temps (Random Forest, voir
scripts/entrainer_modele_temps.py) et l'expose pour le moteur de
generation. Chargement paresseux et mis en cache (le modele n'est lu du
disque qu'au premier appel).

Si le modele n'a pas encore ete entraine, predire_temps() renvoie
simplement None - le moteur de generation continue de fonctionner sans
ce troisieme niveau de repli.
"""
from pathlib import Path

import pandas as pd

MODELE_PATH = Path(__file__).resolve().parents[1] / "ml_models" / "modele_temps.joblib"

_modele = None
_modele_charge = False


def _charger_modele():
    global _modele, _modele_charge
    if _modele_charge:
        return _modele

    _modele_charge = True
    if MODELE_PATH.exists():
        import joblib

        _modele = joblib.load(MODELE_PATH)
    return _modele


def modele_disponible() -> bool:
    return _charger_modele() is not None


def predire_temps(operation_libelle: str, machine: str | None) -> float | None:
    modele = _charger_modele()
    if modele is None:
        return None

    entree = pd.DataFrame([{"operation_libelle": operation_libelle, "machine": machine or "INCONNUE"}])
    prediction = modele.predict(entree)[0]
    return round(float(prediction), 1)

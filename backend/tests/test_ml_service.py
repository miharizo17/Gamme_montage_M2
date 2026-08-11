import pytest

from service import ml_service


def test_predire_temps_sans_modele(monkeypatch):
    """Si le modele n'est pas present sur le disque, le service doit
    degrader proprement (None), jamais planter."""
    monkeypatch.setattr(ml_service, "_modele", None)
    monkeypatch.setattr(ml_service, "_modele_charge", False)
    monkeypatch.setattr(ml_service, "MODELE_PATH", ml_service.MODELE_PATH.with_name("inexistant.joblib"))

    assert ml_service.modele_disponible() is False
    assert ml_service.predire_temps("POSER ZIP", "PP1") is None


@pytest.mark.skipif(
    not ml_service.modele_disponible(),
    reason="Modele ML non entraine sur cette machine (backend/ml_models/modele_temps.joblib absent)",
)
def test_predire_temps_avec_modele():
    prediction = ml_service.predire_temps("POSER ZIP", "PP1")
    assert prediction is not None
    assert prediction > 0

    # Doit aussi fonctionner sans machine connue (operation totalement inedite).
    prediction_inconnue = ml_service.predire_temps("OPERATION JAMAIS VUE XYZ", None)
    assert prediction_inconnue is not None
    assert prediction_inconnue > 0

"""
Loads the trained model + scaler produced by notebooks/03_model_training.ipynb
and exposes a single predict() function the API route calls.

This file expects models/best_model.pkl and models/scaler.pkl to exist -
they are produced by the training notebook, not by this file. Run the
notebook pipeline before starting the API.
"""

from pathlib import Path
import joblib
import numpy as np
import shap

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "best_model.pkl"
SCALER_PATH = Path(__file__).resolve().parent.parent / "models" / "scaler.pkl"

_model = None
_scaler = None
_explainer = None


def _load_artifacts():
    """Lazy-loads model/scaler/explainer once, on first request."""
    global _model, _scaler, _explainer
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No trained model found at {MODEL_PATH}. "
                "Run notebooks/03_model_training.ipynb first."
            )
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        _explainer = shap.TreeExplainer(_model)
    return _model, _scaler, _explainer


def risk_level_from_probability(probability: float) -> str:
    if probability < 0.30:
        return "Low"
    elif probability < 0.60:
        return "Medium"
    return "High"


def predict(feature_row: np.ndarray, feature_names: list[str], top_n: int = 5):
    """
    feature_row: a single preprocessed, ordered feature vector (1D array)
    feature_names: column names matching feature_row's order
    """
    model, scaler, explainer = _load_artifacts()

    scaled = scaler.transform(feature_row.reshape(1, -1))
    probability = float(model.predict_proba(scaled)[0, 1])

    shap_values = explainer.shap_values(scaled)
    values = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]

    contributions = sorted(
        zip(feature_names, feature_row, values),
        key=lambda x: abs(x[2]),
        reverse=True,
    )[:top_n]

    return {
        "readmission_probability": probability,
        "risk_level": risk_level_from_probability(probability),
        "top_contributing_factors": [
            {"feature": f, "value": float(v), "contribution": float(c)}
            for f, v, c in contributions
        ],
    }

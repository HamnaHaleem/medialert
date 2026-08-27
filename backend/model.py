import joblib
import numpy as np
import pandas as pd
import shap

from config import (
    BEST_MODEL_PATH as MODEL_PATH,
    SCALER_PATH,
    BACKGROUND_PATH,
    ENCODERS_PATH,
    FEATURE_NAMES_PATH,
)
from backend.explain import format_display_value, generate_explanation

_model = None
_scaler = None
_explainer = None
_encoders = None
_feature_names = None

def _load_artifacts():
    """Lazy-loads all artifacts once, on first request."""
    global _model, _scaler, _explainer, _encoders, _feature_names
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No trained model found at {MODEL_PATH}. "
                "Run notebooks/02_preprocessing.ipynb and 03_model_training.ipynb first."
            )
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        _encoders = joblib.load(ENCODERS_PATH)
        _feature_names = joblib.load(FEATURE_NAMES_PATH)
        background = joblib.load(BACKGROUND_PATH)

        _explainer = shap.Explainer(_model.predict_proba, background)
    return _model, _scaler, _explainer, _encoders, _feature_names

class UnseenCategoryError(ValueError):
    """Raised when a request contains a category value the encoders were never fitted on."""
    pass

def get_feature_names() -> list[str]:
    _load_artifacts()
    return list(_feature_names)

def get_category_options() -> dict:
    _, _, _, encoders, _ = _load_artifacts()
    return {col: list(enc.classes_) for col, enc in encoders.items()}

def encode_request(raw: dict) -> np.ndarray:
    """
    Converts a raw request dict (matching PatientAssessmentRequest field
    names) into a feature vector ordered and encoded exactly the way the
    training data was — same label encoders, same missing-value handling,
    same column order.
    """
    _, _, _, encoders, feature_names = _load_artifacts()

    row = dict(raw)

    if row.get("medications") is None:
        raise ValueError(
            "medications is required - the trained model was never fitted "
            "on any 'missing medications' cases in the diabetic cohort."
        )

    for col, encoder in encoders.items():
        raw_value = str(row[col])
        if raw_value not in encoder.classes_:
            raise UnseenCategoryError(
                f"'{raw_value}' is not a recognised value for '{col}'. "
                f"Known values: {list(encoder.classes_)}"
            )
        row[col] = int(encoder.transform([raw_value])[0])

    # hypertension arrives as a Pydantic bool; training data used 0/1 ints
    if "hypertension" in row:
        row["hypertension"] = int(row["hypertension"])

    try:
        ordered = [row[name] for name in feature_names]
    except KeyError as e:
        raise ValueError(f"Request is missing required field: {e}") from e

    return np.array(ordered, dtype=float)

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
    model, scaler, explainer, encoders, _ = _load_artifacts()

    row_df = pd.DataFrame([feature_row], columns=feature_names)
    scaled = scaler.transform(row_df)
    probability = float(model.predict_proba(scaled)[0, 1])

    shap_values = explainer(scaled)
    values = shap_values.values[0, :, 1]

    contributions = sorted(
        zip(feature_names, feature_row, values),
        key=lambda x: abs(x[2]),
        reverse=True,
    )[:top_n]

    factors = []
    for feature, raw_value, contribution in contributions:
        display_value = format_display_value(feature, raw_value, encoders)
        factors.append({
            "feature": feature,
            "value": display_value,
            "contribution": float(contribution),
            "explanation": generate_explanation(feature, display_value, float(contribution)),
        })

    return {
        "readmission_probability": probability,
        "risk_level": risk_level_from_probability(probability),
        "top_contributing_factors": factors,
    }
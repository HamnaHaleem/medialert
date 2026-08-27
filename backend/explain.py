FEATURE_LABELS = {
    "age": "age",
    "sex": "sex",
    "bmi": "body mass index (BMI)",
    "systolic_bp": "systolic blood pressure",
    "diastolic_bp": "diastolic blood pressure",
    "cholesterol": "cholesterol level",
    "hdl": "HDL (\"good\") cholesterol",
    "ldl": "LDL (\"bad\") cholesterol",
    "glucose": "blood glucose level",
    "creatinine": "creatinine level (kidney function marker)",
    "hemoglobin": "hemoglobin level",
    "wbc": "white blood cell count",
    "smoking_status": "smoking history",
    "alcohol_use": "alcohol use",
    "hypertension": "hypertension status",
    "primary_diagnosis": "primary diagnosis",
    "medications": "current medications",
    "length_of_stay": "length of hospital stay",
}

FEATURE_UNITS = {
    "age": "years", "bmi": "kg/m²", "systolic_bp": "mmHg", "diastolic_bp": "mmHg",
    "cholesterol": "mg/dL", "hdl": "mg/dL", "ldl": "mg/dL", "glucose": "mg/dL",
    "creatinine": "mg/dL", "hemoglobin": "g/dL", "wbc": "x10^9/L", "length_of_stay": "days",
}


def format_display_value(feature: str, raw_value: float, encoders: dict) -> str:
    """Converts a raw feature value into a human-readable string - decodes
    categoricals back to their real label instead of showing the internal
    integer the model actually operates on."""
    if feature in encoders:
        encoder = encoders[feature]
        try:
            index = int(round(raw_value))
            label = encoder.inverse_transform([index])[0]
        except (ValueError, IndexError):
            label = str(raw_value)
        if feature == "hypertension":
            return "Yes" if str(label) in ("1", "True", "true") else "No"
        return str(label)

    if feature == "hypertension":
        return "Yes" if raw_value >= 0.5 else "No"

    unit = FEATURE_UNITS.get(feature, "")
    if float(raw_value).is_integer():
        return f"{int(raw_value)} {unit}".strip()
    return f"{raw_value:.1f} {unit}".strip()


def _magnitude_word(abs_contribution: float) -> str:
    if abs_contribution >= 0.05:
        return "substantially"
    if abs_contribution >= 0.02:
        return "moderately"
    return "slightly"


def generate_explanation(feature: str, display_value: str, contribution: float) -> str:
    """Produces a plain-language sentence for one contributing factor -
    no SHAP terminology, no coefficients, just what it means clinically."""
    label = FEATURE_LABELS.get(feature, feature.replace("_", " "))
    direction = "increasing" if contribution >= 0 else "decreasing"
    magnitude = _magnitude_word(abs(contribution))
    return f"{label.capitalize()} ({display_value}) is {magnitude} {direction} this patient's predicted readmission risk."
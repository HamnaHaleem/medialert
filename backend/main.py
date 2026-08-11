"""
MediAlert API entrypoint.
Run with: uvicorn backend.main:app --reload   (from the project root)
"""

import numpy as np
from fastapi import FastAPI, HTTPException

from backend.schemas import PatientAssessmentRequest, PredictionResponse
from backend.model import predict

app = FastAPI(
    title="MediAlert API",
    description="30-day diabetic readmission risk prediction with SHAP explainability.",
    version="0.1.0",
)

FEATURE_ORDER = [
    "age", "sex", "bmi", "blood_pressure", "cholesterol", "hdl", "ldl",
    "glucose", "creatinine", "haemoglobin", "wbc", "smoking_status",
    "alcohol_use", "hypertension", "primary_diagnosis", "medications",
    "length_of_stay",
]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict_readmission(request: PatientAssessmentRequest):
    try:
        # NOTE: replace this with the same encoding pipeline used in
        # notebooks/02_preprocessing.ipynb (label encoding for categoricals)
        # before this will produce a valid feature vector. This raw ordering
        # is a placeholder to be wired up once preprocessing is finalised.
        raw = request.model_dump()
        feature_row = np.array([raw[f] for f in FEATURE_ORDER], dtype=object)

        result = predict(feature_row, FEATURE_ORDER)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

"""
Pydantic request/response models for the /predict endpoint.
Field names match the preprocessed feature set produced by
notebooks/02_preprocessing.ipynb - keep these in sync if the
feature set changes.
"""

from pydantic import BaseModel, Field
from typing import Optional


class PatientAssessmentRequest(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: str
    bmi: float
    blood_pressure: float
    cholesterol: float
    hdl: float
    ldl: float
    glucose: float
    creatinine: float
    haemoglobin: float
    wbc: float
    smoking_status: str
    alcohol_use: str
    hypertension: bool
    primary_diagnosis: str
    medications: Optional[str] = None
    length_of_stay: int = Field(..., ge=0)


class ShapContribution(BaseModel):
    feature: str
    value: float
    contribution: float


class PredictionResponse(BaseModel):
    readmission_probability: float = Field(..., ge=0.0, le=1.0)
    risk_level: str  # "Low" | "Medium" | "High"
    top_contributing_factors: list[ShapContribution]

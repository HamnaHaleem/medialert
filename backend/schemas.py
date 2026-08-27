from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


class PatientAssessmentRequest(BaseModel):
    patient_reference: Optional[str] = Field(
        None,
        description="Optional hospital patient identifier (e.g. MRN), used only to link "
                    "assessments for risk-history lookup. Never used as a model feature.",
    )
    age: int = Field(..., ge=1, le=120)
    sex: str
    bmi: float
    systolic_bp: int
    diastolic_bp: int
    cholesterol: float
    hdl: float
    ldl: float
    glucose: float
    creatinine: float
    hemoglobin: float
    wbc: float
    smoking_status: str
    alcohol_use: str
    hypertension: bool
    primary_diagnosis: str
    medications: str
    length_of_stay: int = Field(..., ge=0)


class ShapContribution(BaseModel):
    feature: str
    value: str  
    contribution: float
    explanation: str = ""

class PredictionResponse(BaseModel):
    assessment_id: int
    readmission_probability: float = Field(..., ge=0.0, le=1.0)
    risk_level: str  # "Low" | "Medium" | "High"
    top_contributing_factors: list[ShapContribution]

class AssessmentHistoryItem(BaseModel):
    assessment_id: int
    created_at: datetime
    readmission_probability: float
    risk_level: str

    _fix_tz = field_validator("created_at")(_as_utc)

class DashboardSummary(BaseModel):
    total_assessments: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    average_probability: float
    recent_assessments: list[AssessmentHistoryItem]

class UserRegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8, description="Minimum 8 characters.")

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    _fix_tz = field_validator("created_at")(_as_utc)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
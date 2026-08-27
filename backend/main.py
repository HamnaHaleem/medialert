import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.schemas import (
    PatientAssessmentRequest, PredictionResponse,
    AssessmentHistoryItem, DashboardSummary,
    UserRegisterRequest, UserOut, TokenResponse,
)
from backend.model import encode_request, predict, get_feature_names, get_category_options, UnseenCategoryError
from backend.db import get_db, init_db
from backend.db_models import AssessmentRecord, User
from backend.pdf_export import generate_pdf
from backend.auth import hash_password, verify_password, create_access_token, get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="MediAlert API",
    description="30-day diabetic readmission risk prediction with SHAP explainability.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

# Authentication - registration

@app.post("/register", response_model=UserOut, status_code=201)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(email=request.email, hashed_password=hash_password(request.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user.email)
    return TokenResponse(access_token=token)

@app.get("/me", response_model=UserOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's own account info - backs the
    frontend Profile page. Deliberately returns only id/email/created_at
    (via UserOut), never hashed_password."""
    return current_user

@app.get("/form-options")
def form_options():
    try:
        return get_category_options()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/predict", response_model=PredictionResponse)
def predict_readmission(
    request: PatientAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        raw = request.model_dump()
        patient_reference = raw.pop("patient_reference", None)

        feature_names = get_feature_names()
        feature_row = encode_request(raw)
        result = predict(feature_row, feature_names)

        record = AssessmentRecord(
            patient_reference=patient_reference,
            age=raw["age"], sex=raw["sex"], bmi=raw["bmi"],
            systolic_bp=raw["systolic_bp"], diastolic_bp=raw["diastolic_bp"],
            cholesterol=raw["cholesterol"], hdl=raw["hdl"], ldl=raw["ldl"],
            glucose=raw["glucose"], creatinine=raw["creatinine"],
            hemoglobin=raw["hemoglobin"], wbc=raw["wbc"],
            smoking_status=raw["smoking_status"], alcohol_use=raw["alcohol_use"],
            hypertension=raw["hypertension"], primary_diagnosis=raw["primary_diagnosis"],
            medications=raw["medications"], length_of_stay=raw["length_of_stay"],
            readmission_probability=result["readmission_probability"],
            risk_level=result["risk_level"],
            top_contributing_factors_json=json.dumps(result["top_contributing_factors"]),
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return {**result, "assessment_id": record.id}

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except UnseenCategoryError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/history/{patient_reference}", response_model=list[AssessmentHistoryItem])
def patient_history(
    patient_reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Past assessments linked to a given patient reference, most recent first."""
    records = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.patient_reference == patient_reference)
        .order_by(AssessmentRecord.created_at.desc(), AssessmentRecord.id.desc())
        .all()
    )
    return [
        AssessmentHistoryItem(
            assessment_id=r.id,
            created_at=r.created_at,
            readmission_probability=r.readmission_probability,
            risk_level=r.risk_level,
        )
        for r in records
    ]

@app.get("/dashboard", response_model=DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate stats across all assessments made - the single dashboard
    for the one defined user role, not a per-role admin view."""
    total = db.query(func.count(AssessmentRecord.id)).scalar() or 0
    low = db.query(func.count(AssessmentRecord.id)).filter(AssessmentRecord.risk_level == "Low").scalar() or 0
    medium = db.query(func.count(AssessmentRecord.id)).filter(AssessmentRecord.risk_level == "Medium").scalar() or 0
    high = db.query(func.count(AssessmentRecord.id)).filter(AssessmentRecord.risk_level == "High").scalar() or 0
    avg_prob = db.query(func.avg(AssessmentRecord.readmission_probability)).scalar() or 0.0

    recent = (
        db.query(AssessmentRecord)
        .order_by(AssessmentRecord.created_at.desc(), AssessmentRecord.id.desc())
        .limit(10)
        .all()
    )

    return DashboardSummary(
        total_assessments=total,
        low_risk_count=low,
        medium_risk_count=medium,
        high_risk_count=high,
        average_probability=round(float(avg_prob), 4),
        recent_assessments=[
            AssessmentHistoryItem(
                assessment_id=r.id,
                created_at=r.created_at,
                readmission_probability=r.readmission_probability,
                risk_level=r.risk_level,
            )
            for r in recent
        ],
    )

@app.get("/assessments/{assessment_id}/pdf")
def download_pdf(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Renders a discharge summary PDF from the already-stored assessment -
    reuses the prediction and explanations computed at submission time,
    rather than recomputing anything."""
    record = db.query(AssessmentRecord).filter(AssessmentRecord.id == assessment_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail=f"No assessment found with id {assessment_id}")

    pdf_bytes = generate_pdf(record)
    filename = f"medialert-assessment-{assessment_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func

from backend.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AssessmentRecord(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    patient_reference = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Input fields
    age = Column(Integer)
    sex = Column(String)
    bmi = Column(Float)
    systolic_bp = Column(Integer)
    diastolic_bp = Column(Integer)
    cholesterol = Column(Float)
    hdl = Column(Float)
    ldl = Column(Float)
    glucose = Column(Float)
    creatinine = Column(Float)
    hemoglobin = Column(Float)
    wbc = Column(Float)
    smoking_status = Column(String)
    alcohol_use = Column(String)
    hypertension = Column(Boolean)
    primary_diagnosis = Column(String)
    medications = Column(String)
    length_of_stay = Column(Integer)

    # Output
    readmission_probability = Column(Float)
    risk_level = Column(String)
    top_contributing_factors_json = Column(Text)  # JSON-serialised list
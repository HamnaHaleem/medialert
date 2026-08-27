import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from config import ENCODERS_PATH
from tests._artifacts import artifacts_exist


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from backend.main import app
   
    with TestClient(app) as c:
        test_email = "pytest-test-user@medialert.test"
        test_password = "pytest-test-password-123"
        c.post("/register", json={"email": test_email, "password": test_password})
       
        login_response = c.post("/login", data={"username": test_email, "password": test_password})
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            c.headers.update({"Authorization": f"Bearer {token}"})
        yield c


@pytest.fixture(scope="session")
def real_category_values():
    """Returns the first valid category value for each encoded column,
    read from the actual fitted encoders - never hardcoded."""
    if not artifacts_exist():
        pytest.skip("No trained encoders found.")
    import joblib
    encoders = joblib.load(ENCODERS_PATH)
    return {col: str(enc.classes_[0]) for col, enc in encoders.items()}


@pytest.fixture(scope="session")
def valid_payload(real_category_values):
    """A minimal, always-valid /predict request body, built from real
    category values so it can never fail due to a stale assumed category."""
    return {
        "age": 65,
        "sex": real_category_values.get("sex", "Male"),
        "bmi": 27.5,
        "systolic_bp": 130,
        "diastolic_bp": 85,
        "cholesterol": 190,
        "hdl": 50,
        "ldl": 110,
        "glucose": 140,
        "creatinine": 1.1,
        "hemoglobin": 13.0,
        "wbc": 7.5,
        "smoking_status": real_category_values.get("smoking_status", "Never"),
        "alcohol_use": real_category_values.get("alcohol_use", "Never"),
        "hypertension": True,
        "primary_diagnosis": real_category_values.get("primary_diagnosis", "Diabetes"),
        "medications": real_category_values.get("medications", "Unknown"),
        "length_of_stay": 5,
    }
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests._artifacts import requires_trained_model
import pytest


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@requires_trained_model
class TestPredictEndpoint:

    def test_valid_request_returns_200(self, client, valid_payload):
        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 200

    def test_response_has_required_fields(self, client, valid_payload):
        response = client.post("/predict", json=valid_payload)
        body = response.json()
        assert "readmission_probability" in body
        assert "risk_level" in body
        assert "top_contributing_factors" in body

    def test_probability_is_valid_range(self, client, valid_payload):
        response = client.post("/predict", json=valid_payload)
        prob = response.json()["readmission_probability"]
        assert 0.0 <= prob <= 1.0

    def test_risk_level_is_valid_category(self, client, valid_payload):
        response = client.post("/predict", json=valid_payload)
        assert response.json()["risk_level"] in ("Low", "Medium", "High")

    def test_top_factors_not_empty(self, client, valid_payload):
        response = client.post("/predict", json=valid_payload)
        factors = response.json()["top_contributing_factors"]
        assert len(factors) > 0
        for f in factors:
            assert "feature" in f and "value" in f and "contribution" in f

    def test_unseen_category_returns_422_not_500(self, client, valid_payload):
        """This is the specific bug class caught manually during
        development - an unseen category must fail cleanly with a
        client error, never crash the server with a 500."""
        bad_payload = dict(valid_payload)
        bad_payload["primary_diagnosis"] = "NotARealDiagnosisXYZ"
        response = client.post("/predict", json=bad_payload)
        assert response.status_code == 422
        assert "NotARealDiagnosisXYZ" in response.json()["detail"]

    def test_missing_required_field_returns_422(self, client, valid_payload):
        incomplete_payload = dict(valid_payload)
        del incomplete_payload["age"]
        response = client.post("/predict", json=incomplete_payload)
        assert response.status_code == 422

    def test_negative_age_rejected_by_schema(self, client, valid_payload):
        bad_payload = dict(valid_payload)
        bad_payload["age"] = -5
        response = client.post("/predict", json=bad_payload)
        assert response.status_code == 422

    def test_missing_medications_now_returns_422(self, client, valid_payload):
        """medications is now required - see test_encoding.py for why:
        the real diabetic cohort has zero missing medications values, so
        there's no learned category to fall back to for a missing one."""
        payload = dict(valid_payload)
        payload["medications"] = None
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
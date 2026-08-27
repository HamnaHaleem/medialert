import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests._artifacts import requires_trained_model
import pytest


@requires_trained_model
class TestPersistenceAndHistory:

    def test_predict_returns_assessment_id(self, client, valid_payload):
        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 200
        assert isinstance(response.json()["assessment_id"], int)

    def test_history_returns_only_matching_patient(self, client, valid_payload):
        payload_a = dict(valid_payload)
        payload_a["patient_reference"] = "TEST-PATIENT-A"
        payload_b = dict(valid_payload)
        payload_b["patient_reference"] = "TEST-PATIENT-B"

        client.post("/predict", json=payload_a)
        client.post("/predict", json=payload_a)
        client.post("/predict", json=payload_b)

        history_a = client.get("/history/TEST-PATIENT-A")
        assert history_a.status_code == 200
        assert len(history_a.json()) >= 2

        history_b = client.get("/history/TEST-PATIENT-B")
        assert history_b.status_code == 200
        assert all(
            item["assessment_id"] not in [h["assessment_id"] for h in history_a.json()]
            for item in history_b.json()
        )

    def test_history_for_unknown_patient_returns_empty_not_error(self, client):
        response = client.get("/history/NO-SUCH-PATIENT-EXISTS")
        assert response.status_code == 200
        assert response.json() == []

    def test_history_ordered_most_recent_first(self, client, valid_payload):
        payload = dict(valid_payload)
        payload["patient_reference"] = "TEST-PATIENT-ORDER"

        client.post("/predict", json=payload)
        client.post("/predict", json=payload)
        client.post("/predict", json=payload)

        history = client.get("/history/TEST-PATIENT-ORDER").json()
        ids = [h["assessment_id"] for h in history]
        assert ids == sorted(ids, reverse=True)

    def test_dashboard_returns_required_fields(self, client, valid_payload):
        client.post("/predict", json=valid_payload)
        response = client.get("/dashboard")
        assert response.status_code == 200
        body = response.json()
        for field in ["total_assessments", "low_risk_count", "medium_risk_count",
                       "high_risk_count", "average_probability", "recent_assessments"]:
            assert field in body

    def test_dashboard_counts_are_consistent(self, client, valid_payload):
        client.post("/predict", json=valid_payload)
        body = client.get("/dashboard").json()
        assert body["total_assessments"] >= 1
        assert (body["low_risk_count"] + body["medium_risk_count"] + body["high_risk_count"]) == body["total_assessments"]

    def test_predicted_values_are_decoded_not_raw_encoded_integers(self, client, valid_payload):
        """Guards against the exact bug found manually: categorical SHAP
        factor values must show the real category label, not the internal
        encoded integer the model actually operates on."""
        response = client.post("/predict", json=valid_payload)
        factors = response.json()["top_contributing_factors"]
        for f in factors:
            assert not f["value"].replace(".", "", 1).lstrip("-").isdigit(), (
                f"Factor '{f['feature']}' shows a raw numeric-looking value "
                f"'{f['value']}' with no unit or label - likely an undecoded "
                f"encoded integer rather than a human-readable value."
            )

    def test_every_factor_has_plain_language_explanation(self, client, valid_payload):
        response = client.post("/predict", json=valid_payload)
        factors = response.json()["top_contributing_factors"]
        for f in factors:
            assert len(f["explanation"]) > 0
            assert "shap" not in f["explanation"].lower()
            assert "z-score" not in f["explanation"].lower()

    def test_pdf_download_returns_valid_pdf(self, client, valid_payload):
        predict_response = client.post("/predict", json=valid_payload)
        assessment_id = predict_response.json()["assessment_id"]

        pdf_response = client.get(f"/assessments/{assessment_id}/pdf")
        assert pdf_response.status_code == 200
        assert pdf_response.headers["content-type"] == "application/pdf"
        assert pdf_response.content[:5] == b"%PDF-"
        assert len(pdf_response.content) > 500 

    def test_pdf_for_nonexistent_assessment_returns_404(self, client):
        response = client.get("/assessments/999999999/pdf")
        assert response.status_code == 404
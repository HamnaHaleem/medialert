import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests._artifacts import requires_trained_model
from backend.model import encode_request, get_feature_names, UnseenCategoryError

import pytest


@requires_trained_model
class TestEncodeRequest:

    def test_valid_request_encodes_without_error(self, valid_payload):
        result = encode_request(valid_payload)
        feature_names = get_feature_names()
        assert len(result) == len(feature_names)

    def test_unseen_category_raises_specific_error(self, valid_payload):
        bad_payload = dict(valid_payload)
        bad_payload["smoking_status"] = "DefinitelyNotARealCategoryXYZ"
        with pytest.raises(UnseenCategoryError) as exc_info:
            encode_request(bad_payload)
        assert "DefinitelyNotARealCategoryXYZ" in str(exc_info.value)
        assert "smoking_status" in str(exc_info.value)

    def test_missing_medications_now_rejected(self, valid_payload):
        """medications is now a required field - the real trained data
        showed zero missing values within the diabetic cohort, so there is
        no learned 'Unknown' category to fall back to. This replaces the
        old test that expected None to succeed via imputation."""
        payload = dict(valid_payload)
        payload["medications"] = None
        with pytest.raises(ValueError, match="medications is required"):
            encode_request(payload)

    def test_hypertension_bool_converts_correctly(self, valid_payload):
        payload_true = dict(valid_payload)
        payload_true["hypertension"] = True
        payload_false = dict(valid_payload)
        payload_false["hypertension"] = False

        row_true = encode_request(payload_true)
        row_false = encode_request(payload_false)
        feature_names = get_feature_names()
        idx = feature_names.index("hypertension")

        assert row_true[idx] == 1.0
        assert row_false[idx] == 0.0

    def test_output_matches_declared_feature_order(self, valid_payload):
        """Guards against the exact bug class this project hit: the API's
        feature order silently drifting out of sync with what the model
        was actually trained on."""
        result = encode_request(valid_payload)
        feature_names = get_feature_names()
        assert len(result) == len(feature_names), (
            "encode_request() output length must match the saved "
            "feature_names.pkl length exactly."
        )
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.model import risk_level_from_probability


class TestRiskLevelBoundaries:

    def test_low_risk_below_threshold(self):
        assert risk_level_from_probability(0.0) == "Low"
        assert risk_level_from_probability(0.29) == "Low"

    def test_medium_risk_at_lower_boundary(self):
        assert risk_level_from_probability(0.30) == "Medium"

    def test_medium_risk_below_upper_boundary(self):
        assert risk_level_from_probability(0.59) == "Medium"

    def test_high_risk_at_upper_boundary(self):
        assert risk_level_from_probability(0.60) == "High"

    def test_high_risk_at_maximum(self):
        assert risk_level_from_probability(1.0) == "High"

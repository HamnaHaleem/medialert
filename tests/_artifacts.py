import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import ENCODERS_PATH, BEST_MODEL_PATH


def artifacts_exist() -> bool:
    return BEST_MODEL_PATH.exists() and ENCODERS_PATH.exists()


requires_trained_model = pytest.mark.skipif(
    not artifacts_exist(),
    reason="No trained model found - run notebooks 02 and 03 before running this test.",
)

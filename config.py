"""
Single source of truth for project paths.

Because this file lives at the project root, its own location IS the
root - no searching or guessing required. Every other part of the
project (notebooks, backend, tests) imports paths from here instead of
computing them independently, so there is exactly one place that knows
where anything lives.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_PROCESSED = DATA_DIR / "processed"

MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"

RAW_DATASET_PATH = DATA_RAW / "medical_dataset.csv"
BEST_MODEL_PATH = MODELS_DIR / "best_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
BACKGROUND_PATH = MODELS_DIR / "background_sample.pkl"
ENCODERS_PATH = MODELS_DIR / "label_encoders.pkl"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.pkl"
DATABASE_PATH = PROJECT_ROOT / "data" / "medialert.db"

# JWT signing secret - loaded from environment (.env, gitignored), with a
# fallback ONLY for local development. This fallback is intentionally
# insecure (fixed, publicly visible in source) and must never be relied on
# outside a local demo/viva environment - see Chapter 08 limitations.
import os
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")  # no-op if the file doesn't exist yet

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "INSECURE-DEV-ONLY-CHANGE-ME")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 60 * 8  # 8 hours - a clinical shift length, not a technical constraint

if JWT_SECRET_KEY == "INSECURE-DEV-ONLY-CHANGE-ME":
    import warnings
    warnings.warn(
        "JWT_SECRET_KEY is using the insecure default. Create a .env file "
        "with a real random JWT_SECRET_KEY before anything beyond local "
        "testing.", stacklevel=2,
    )

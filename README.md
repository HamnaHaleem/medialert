# MediAlert

AI-based 30-day diabetic patient readmission risk prediction for Colombo district hospitals.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Pipeline order

1. Place the raw Kaggle dataset at `data/raw/medical_dataset.csv`.
2. Run notebooks in order: `01_eda` -> `02_preprocessing` -> `03_model_training` -> `04_shap` -> `05_groupkfold_validation`.
3. `03_model_training.ipynb` must save `models/best_model.pkl` and `models/scaler.pkl` before the API will start.
4. Run the API: `uvicorn backend.main:app --reload`
5. Docs at `http://127.0.0.1:8000/docs`

## Structure

- `backend/` - FastAPI app (`/predict` endpoint, schemas, model loading + SHAP)
- `notebooks/` - EDA, preprocessing, six-model benchmarking, SHAP, GroupKFold validation
- `data/raw/` - original dataset (gitignored)
- `data/processed/` - cleaned/engineered dataset (gitignored)
- `models/` - serialized model + scaler (gitignored)
- `results/` - benchmark tables and figures for the thesis
- `tests/` - pytest suite

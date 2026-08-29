# MediAlert

AI-based 30-day diabetic patient readmission risk prediction and decision support tool for Colombo district hospitals.

## Software and Library Requirements

- **Python 3.12+**
- **Node.js 18+** and npm (for the frontend)
- **Git**

Python dependencies are listed in `requirements.txt` and include: pandas, scikit-learn, XGBoost, LightGBM, CatBoost, imbalanced-learn, SHAP, FastAPI, Uvicorn, SQLAlchemy, bcrypt, PyJWT, ReportLab, pytest.

Frontend dependencies are listed in `frontend/package.json` and include: React 19, Vite, Tailwind CSS 4, lucide-react.

No GPU is required. The system runs on standard consumer hardware.

## Project Setup Instructions

### 1. Clone the repository
```powershell
git clone https://github.com/<your-username>/medialert.git
cd medialert
```

### 2. Backend environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Frontend environment
```powershell
cd frontend
npm install
cd ..
```

### 4. Environment variables (required)
Create a `.env` file in the project root:
```powershell
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))" > .env
```
This generates a real random secret for signing login sessions. Without this file, the backend falls back to an insecure default key and prints a warning — fine for local testing, **not safe for anything beyond that**.

### 5. Dataset
Medical Dataset
https://www.kaggle.com/datasets/calebbrian/medical-daataset/data


## Installation / Pipeline Order

The machine learning pipeline must be run once, in order, before the API can start — each notebook depends on artifacts produced by the one before it:

1. `notebooks/01_eda.ipynb` — exploratory analysis of the full dataset
2. `notebooks/02_preprocessing.ipynb` — filters to the diabetic cohort, encodes features, saves `label_encoders.pkl`
3. `notebooks/03_model_training.ipynb` — benchmarks six models under GroupKFold, tunes hyperparameters, saves `models/best_model.pkl` and `models/scaler.pkl` (**the API will not start without these two files**)
4. `notebooks/04_shap.ipynb` — generates SHAP explainability figures
5. `notebooks/05_groupkfold_validation.ipynb` — empirically verifies zero patient overlap across folds

Run each top to bottom, in a fresh kernel (Restart & Run All), not by executing cells out of order interactively — several cells depend on execution order matching save order, not just having been run at some point.

## Execution Instructions

You need **two terminals running simultaneously** — the backend and frontend are separate processes.

**Terminal 1 — Backend** (from the project root):
```powershell
.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```
Wait for `Application startup complete.` API docs available at `http://127.0.0.1:8000/docs`.

**Terminal 2 — Frontend** (from `frontend/`):
```powershell
cd frontend
npm run dev
```
Wait for `Local: http://localhost:5173/`. Open that URL in a browser.

**Running the test suite** (from the project root, backend venv active):
```powershell
python -m pytest tests/ -v
```
Expect **48 passed**. Some tests require the trained model artifacts (step 3 of the pipeline) to already exist — they skip gracefully if not.

## Additional Information

- **No pre-seeded account exists.** On first use, go to the homepage and select "Create an account" before logging in — there is no default username/password.
- **Ports:** backend runs on `8000`, frontend on `5173`. Both are hardcoded in `frontend/src/api/predictClient.js` and `backend/main.py`'s CORS settings — if you change one, update the other.
- **Database:** SQLite, created automatically at `data/medialert.db` on first backend startup. Delete this file to reset all stored assessments and user accounts.
- **Timezone:** all timestamps are stored in UTC and displayed in Asia/Colombo time throughout the frontend and generated PDFs, regardless of the machine's local timezone.
- **If `npm run dev` fails with `Could not resolve '@tailwindcss/vite'` or similar**, check that `frontend/package.json` actually lists `tailwindcss`, `@tailwindcss/vite`, and `lucide-react` as dependencies — a fresh `npm install` only fetches what's already declared there, it won't add missing entries.
- **If the frontend shows "Cannot reach the prediction service,"** confirm the backend terminal is still running and printed `Application startup complete.` — the frontend depends on it being up first.

## Structure

- `backend/` — FastAPI app: authentication, `/predict`, patient history, dashboard, PDF export, schemas, model loading + SHAP
- `frontend/` — React + Vite + Tailwind single-page app: homepage, login/register, assessment form, risk result, history, dashboard, profile
- `notebooks/` — EDA, preprocessing, six-model benchmarking, SHAP, GroupKFold validation
- `data/raw/` — original dataset (gitignored)
- `data/processed/` — cleaned/engineered dataset (gitignored)
- `models/` — serialized model + scaler (gitignored)
- `results/` — benchmark tables and figures for the thesis
- `tests/` — pytest suite (48 tests)
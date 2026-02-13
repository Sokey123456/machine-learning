# Anomaly Viewer (No Node / No npm)

## What this is
- **Python only**: FastAPI serves both API and the single-page UI (HTML/JS via CDN).
- **No Node.js required**.
- Uses the included test CSVs under `backend/data/`.

## 1) Setup (Windows cmd)
```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Run
```cmd
python -m uvicorn main:app --reload --port 8000
```

Open:
- UI: http://localhost:8000/
- API: http://localhost:8000/api/meta

## Keyboard
- Arrow keys: move cell focus (AG Grid default)
- Home / Ctrl+Home: jump to **OIS×JPY**

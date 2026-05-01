# Full-Stack Monitoring & Reporting Dashboard

## Stack
- Backend: FastAPI + SQLite + SQLAlchemy + Pandas
- Frontend: React + Recharts + Vite

## Features
- Upload CSV/Excel datasets with replace/append modes.
- Schema normalization for `region`, `country`, `year`, plus dynamic metric columns.
- Data storage with upload batch timestamps.
- APIs for filters, raw data, summary, and aggregated views.
- Dynamic global filters (region, country dependency, year, metrics).
- Summary cards, line trend chart, bar comparison chart.
- Auto-refresh using polling against latest upload timestamp.
- Save filter state in localStorage.
- Export filtered results to CSV.
- Graceful missing-value handling (coercion to null / ignored in numeric aggregates).

## Run locally
### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend_requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on Vite default URL, backend on `http://localhost:8000`.

## API quick reference
- `POST /upload?mode=replace|append` (multipart file)
- `GET /filters`
- `GET /data`
- `GET /aggregate?group_by=region|country|year|metric&agg=sum|avg`
- `GET /summary`
- `GET /export`

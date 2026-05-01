# Monitoring and Reporting Dashboard

## Features
- Upload CSV/Excel datasets with schema auto-detection (`region`, `country`, `year`, plus metric fields).
- Replace or append dataset upload modes.
- SQLite-backed storage with upload timestamps.
- Filtered data and aggregation APIs.
- React dashboard with global sidebar filters, summary cards, line/bar charts, CSV export, and saved filter state.
- Auto-refresh metadata polling every 10 seconds to detect new uploads.

## Run locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. Open:
   - API docs: http://127.0.0.1:8000/docs
   - Dashboard: http://127.0.0.1:8000/

## API endpoints
- `POST /api/upload?mode=replace|append` with `file` multipart.
- `GET /api/filters`
- `GET /api/countries?region=...`
- `GET /api/data?region=...&country=...&year=...&metric=...`
- `GET /api/aggregate?group_by=region|country|year&metric=<name>&agg=sum|avg`
- `GET /api/export?...` (exports current filtered dataset to CSV)

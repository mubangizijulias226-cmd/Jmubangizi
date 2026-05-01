from datetime import datetime
from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./dashboard.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

PRIMARY_FIELDS = ["country", "plan_name", "plan_start_date", "plan_end_date", "start_date", "end_date"]


class DataRecord(Base):
    __tablename__ = "data_records"

    id = Column(Integer, primary_key=True, index=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    country = Column(String, nullable=True, index=True)
    plan_name = Column(String, nullable=True, index=True)
    year = Column(Integer, nullable=True, index=True)
    attributes = Column(JSON, nullable=False)
    metrics = Column(JSON, nullable=False)


class UploadEvent(Base):
    __tablename__ = "upload_events"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    rows_added = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Regional Monitoring Dashboard API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class UploadResult(BaseModel):
    filename: str
    rows_added: int
    mode: str
    detected_columns: list[str]
    filter_columns: list[str]
    metric_columns: list[str]
    uploaded_at: datetime


def normalize_columns(columns: list[str]) -> list[str]:
    return [c.strip().lower().replace(" ", "_").replace("/", "_").replace("-", "_") for c in columns]


def read_dataframe(upload: UploadFile) -> pd.DataFrame:
    suffix = upload.filename.lower().split(".")[-1]
    raw = upload.file.read()
    if suffix == "csv":
        return pd.read_csv(BytesIO(raw))
    if suffix in {"xlsx", "xls"}:
        return pd.read_excel(BytesIO(raw))
    raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")


def infer_schema(df: pd.DataFrame):
    df.columns = normalize_columns(list(df.columns))
    if "country" not in df.columns:
        df["country"] = "Unknown"
    if "plan_name" not in df.columns:
        df["plan_name"] = "Unknown"

    df["country"] = df["country"].fillna("Unknown").astype(str)
    df["plan_name"] = df["plan_name"].fillna("Unknown").astype(str)

    if "start_date" in df.columns:
        df["year"] = pd.to_datetime(df["start_date"], errors="coerce").dt.year
    elif "plan_start_date" in df.columns:
        df["year"] = pd.to_datetime(df["plan_start_date"], errors="coerce").dt.year
    elif "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
    else:
        df["year"] = None

    metric_columns = []
    filter_columns = []
    for col in df.columns:
        if col in {"year"}:
            continue
        if df[col].dtype == "object":
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() > max(5, len(df) * 0.5):
                df[col] = converted
        if pd.api.types.is_numeric_dtype(df[col]):
            metric_columns.append(col)
        elif col not in PRIMARY_FIELDS:
            filter_columns.append(col)

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.where(pd.notnull(df), None)
    return df, sorted(set(filter_columns)), sorted(set(metric_columns))


@app.post("/api/upload", response_model=UploadResult)
def upload_dataset(file: UploadFile = File(...), mode: str = Query("replace", pattern="^(replace|append)$")):
    df = read_dataframe(file)
    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded dataset is empty.")

    df, filter_columns, metric_columns = infer_schema(df)
    upload_time = datetime.utcnow()

    with SessionLocal() as db:
        if mode == "replace":
            db.query(DataRecord).delete()

        rows = []
        for _, row in df.iterrows():
            metrics = {k: (float(row[k]) if row.get(k) is not None else None) for k in metric_columns}
            attributes = {k: row.get(k) for k in filter_columns if k in df.columns}
            rows.append(DataRecord(upload_timestamp=upload_time, country=row.get("country"), plan_name=row.get("plan_name"), year=int(row["year"]) if row.get("year") is not None else None, attributes=attributes, metrics=metrics))

        db.bulk_save_objects(rows)
        db.add(UploadEvent(filename=file.filename, mode=mode, rows_added=len(rows), uploaded_at=upload_time))
        db.commit()

    return UploadResult(filename=file.filename, rows_added=len(df), mode=mode, detected_columns=list(df.columns), filter_columns=filter_columns, metric_columns=metric_columns, uploaded_at=upload_time)


@app.get('/api/filters')
def get_filters():
    with SessionLocal() as db:
        rows = db.query(DataRecord).all()
        years = sorted({r.year for r in rows if r.year is not None})
        countries = sorted({r.country for r in rows if r.country})
        plans = sorted({r.plan_name for r in rows if r.plan_name})
        latest = db.query(func.max(DataRecord.upload_timestamp)).scalar()

    attributes, metrics = {}, set()
    for r in rows:
        for k, v in (r.attributes or {}).items():
            attributes.setdefault(k, set())
            if v not in (None, ""):
                attributes[k].add(str(v))
        for k in (r.metrics or {}).keys():
            metrics.add(k)

    return {
        "countries": countries,
        "plans": plans,
        "years": years,
        "attribute_filters": {k: sorted(v) for k, v in attributes.items()},
        "metrics": sorted(metrics),
        "latest_upload": latest,
    }


@app.get('/api/data')
def get_data(country: list[str] = Query(default=[]), plan_name: list[str] = Query(default=[]), year: list[int] = Query(default=[]), attribute_key: list[str] = Query(default=[]), attribute_value: list[str] = Query(default=[]), metric: str | None = None):
    with SessionLocal() as db:
        rows = db.query(DataRecord).all()

    pairs = list(zip(attribute_key, attribute_value))
    out = []
    for r in rows:
        if country and r.country not in country:
            continue
        if plan_name and r.plan_name not in plan_name:
            continue
        if year and r.year not in year:
            continue
        if any(str((r.attributes or {}).get(k, "")) != str(v) for k, v in pairs):
            continue
        row = {"id": r.id, "country": r.country, "plan_name": r.plan_name, "year": r.year, **(r.attributes or {})}
        if metric:
            row[metric] = (r.metrics or {}).get(metric)
        else:
            row.update(r.metrics or {})
        out.append(row)

    return {"rows": out, "count": len(out)}


@app.get('/api/export')
def export_filtered_data(country: list[str] = Query(default=[]), plan_name: list[str] = Query(default=[]), year: list[int] = Query(default=[])):
    data = get_data(country=country, plan_name=plan_name, year=year)
    df = pd.DataFrame(data['rows'])
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    filename = f"regional_monitoring_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(BytesIO(csv_bytes), media_type='text/csv', headers={"Content-Disposition": f"attachment; filename={filename}"})


@app.get('/')
def serve_ui():
    return FileResponse('frontend/index.html')

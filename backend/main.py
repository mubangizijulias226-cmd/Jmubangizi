from datetime import datetime
from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, create_engine, func
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./dashboard.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

DIMENSION_FIELDS = ["region", "country", "year"]


class DataRecord(Base):
    __tablename__ = "data_records"

    id = Column(Integer, primary_key=True, index=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    region = Column(String, nullable=True, index=True)
    country = Column(String, nullable=True, index=True)
    year = Column(Integer, nullable=True, index=True)
    metrics = Column(JSON, nullable=False)


class UploadEvent(Base):
    __tablename__ = "upload_events"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    rows_added = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Monitoring Dashboard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class UploadResult(BaseModel):
    filename: str
    rows_added: int
    mode: str
    detected_columns: list[str]
    metric_columns: list[str]
    uploaded_at: datetime


def normalize_columns(columns: list[str]) -> list[str]:
    return [c.strip().lower().replace(" ", "_") for c in columns]


def read_dataframe(upload: UploadFile) -> pd.DataFrame:
    suffix = upload.filename.lower().split(".")[-1]
    raw = upload.file.read()
    if suffix == "csv":
        df = pd.read_csv(BytesIO(raw))
    elif suffix in {"xlsx", "xls"}:
        df = pd.read_excel(BytesIO(raw))
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")
    return df


def infer_schema(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    df.columns = normalize_columns(list(df.columns))
    for field in DIMENSION_FIELDS:
        if field not in df.columns:
            if field == "region":
                df[field] = "Unknown"
            elif field == "country":
                df[field] = "Unknown"
            else:
                df[field] = None

    df["region"] = df["region"].fillna("Unknown").astype(str)
    df["country"] = df["country"].fillna("Unknown").astype(str)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    metric_columns = [c for c in df.columns if c not in DIMENSION_FIELDS]
    for col in metric_columns:
        if df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.where(pd.notnull(df), None)
    return df, metric_columns


@app.post("/api/upload", response_model=UploadResult)
def upload_dataset(file: UploadFile = File(...), mode: str = Query("replace", pattern="^(replace|append)$")):
    df = read_dataframe(file)
    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded dataset is empty.")

    df, metric_columns = infer_schema(df)
    upload_time = datetime.utcnow()

    with SessionLocal() as db:
        if mode == "replace":
            db.query(DataRecord).delete()

        rows = []
        for _, row in df.iterrows():
            metrics = {k: (float(v) if isinstance(v, (int, float)) and v is not None else v) for k, v in row.items() if k in metric_columns}
            rows.append(
                DataRecord(
                    upload_timestamp=upload_time,
                    region=row.get("region"),
                    country=row.get("country"),
                    year=int(row["year"]) if row.get("year") is not None else None,
                    metrics=metrics,
                )
            )

        db.bulk_save_objects(rows)
        event = UploadEvent(filename=file.filename, mode=mode, rows_added=len(rows), uploaded_at=upload_time)
        db.add(event)
        db.commit()

    return UploadResult(
        filename=file.filename,
        rows_added=len(df),
        mode=mode,
        detected_columns=list(df.columns),
        metric_columns=metric_columns,
        uploaded_at=upload_time,
    )


@app.get("/api/filters")
def get_filters():
    with SessionLocal() as db:
        regions = [r[0] for r in db.query(DataRecord.region).distinct().order_by(DataRecord.region)]
        years = [y[0] for y in db.query(DataRecord.year).filter(DataRecord.year.is_not(None)).distinct().order_by(DataRecord.year)]
        latest = db.query(func.max(DataRecord.upload_timestamp)).scalar()

        sample = db.query(DataRecord).filter(DataRecord.metrics.is_not(None)).first()
        metrics = sorted(list(sample.metrics.keys())) if sample and sample.metrics else []

    return {"regions": regions, "years": years, "metrics": metrics, "latest_upload": latest}


@app.get("/api/countries")
def get_countries(region: list[str] = Query(default=[])):
    with SessionLocal() as db:
        q = db.query(DataRecord.country).distinct()
        if region:
            q = q.filter(DataRecord.region.in_(region))
        countries = [c[0] for c in q.order_by(DataRecord.country)]
    return {"countries": countries}


def apply_filters(query, regions: list[str], countries: list[str], years: list[int]):
    if regions:
        query = query.filter(DataRecord.region.in_(regions))
    if countries:
        query = query.filter(DataRecord.country.in_(countries))
    if years:
        query = query.filter(DataRecord.year.in_(years))
    return query


@app.get("/api/data")
def get_data(
    region: list[str] = Query(default=[]),
    country: list[str] = Query(default=[]),
    year: list[int] = Query(default=[]),
    metric: str | None = None,
):
    with SessionLocal() as db:
        q = apply_filters(db.query(DataRecord), region, country, year)
        rows = q.all()

    out = []
    for r in rows:
        entry: dict[str, Any] = {
            "id": r.id,
            "region": r.region,
            "country": r.country,
            "year": r.year,
            "upload_timestamp": r.upload_timestamp,
        }
        if metric:
            entry[metric] = r.metrics.get(metric) if r.metrics else None
        else:
            entry.update(r.metrics or {})
        out.append(entry)
    return {"rows": out, "count": len(out)}


@app.get("/api/aggregate")
def get_aggregate(
    group_by: str = Query("year", pattern="^(region|country|year)$"),
    metric: str = Query(...),
    agg: str = Query("sum", pattern="^(sum|avg)$"),
    region: list[str] = Query(default=[]),
    country: list[str] = Query(default=[]),
    year: list[int] = Query(default=[]),
):
    with SessionLocal() as db:
        q = apply_filters(db.query(DataRecord), region, country, year)
        rows = q.all()

    grouped: dict[str, list[float]] = {}
    for r in rows:
        key = str(getattr(r, group_by) or "Unknown")
        value = None
        if r.metrics:
            value = r.metrics.get(metric)
        if isinstance(value, (int, float)):
            grouped.setdefault(key, []).append(float(value))

    result = []
    for key, vals in grouped.items():
        if not vals:
            continue
        value = sum(vals) if agg == "sum" else sum(vals) / len(vals)
        result.append({group_by: key, "value": value})

    result = sorted(result, key=lambda x: x[group_by])
    return {"group_by": group_by, "metric": metric, "agg": agg, "results": result}


@app.get("/api/export")
def export_filtered_data(
    region: list[str] = Query(default=[]),
    country: list[str] = Query(default=[]),
    year: list[int] = Query(default=[]),
):
    data = get_data(region=region, country=country, year=year)
    df = pd.DataFrame(data["rows"])
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    filename = f"filtered_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/")
def serve_ui():
    return FileResponse("frontend/index.html")

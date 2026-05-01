from datetime import datetime
from io import BytesIO
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, create_engine, func
from sqlalchemy.orm import Session, declarative_base, sessionmaker

app = FastAPI(title="Monitoring Dashboard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///./dashboard.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class UploadBatch(Base):
    __tablename__ = "upload_batches"
    id = Column(Integer, primary_key=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    mode = Column(String, nullable=False)
    row_count = Column(Integer, nullable=False)
    schema_info = Column(JSON, nullable=False)


class DataRow(Base):
    __tablename__ = "data_rows"
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, nullable=False)
    region = Column(String, nullable=True)
    country = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=True)


Base.metadata.create_all(bind=engine)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapped = {}
    for col in df.columns:
        c = col.strip().lower()
        if c in {"region", "reg"}:
            mapped[col] = "region"
        elif c in {"country", "nation"}:
            mapped[col] = "country"
        elif c in {"year", "yr"}:
            mapped[col] = "year"
        else:
            mapped[col] = col.strip()
    return df.rename(columns=mapped)


def to_long(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    required = ["region", "country", "year"]
    for col in required:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

    metric_cols = [c for c in df.columns if c not in required]
    if not metric_cols:
        raise HTTPException(status_code=400, detail="No metric columns found")

    long_df = df.melt(
        id_vars=required,
        value_vars=metric_cols,
        var_name="metric",
        value_name="value",
    )
    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce")
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df = long_df.where(pd.notnull(long_df), None)
    return long_df


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/last-upload")
def last_upload():
    with SessionLocal() as db:
        row = db.query(UploadBatch).order_by(UploadBatch.uploaded_at.desc()).first()
        if not row:
            return {"uploaded_at": None}
        return {"uploaded_at": row.uploaded_at.isoformat(), "batch_id": row.id}


@app.post("/upload")
async def upload_dataset(mode: str = Query("replace", pattern="^(replace|append)$"), file: UploadFile = File(...)):
    content = await file.read()
    try:
        if file.filename.lower().endswith(".csv"):
            df = pd.read_csv(BytesIO(content))
        elif file.filename.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid dataset: {exc}") from exc

    long_df = to_long(df)
    schema = {"columns": list(df.columns), "normalized_columns": list(normalize_columns(df).columns)}

    with SessionLocal() as db:
        if mode == "replace":
            db.query(DataRow).delete()

        batch = UploadBatch(mode=mode, row_count=len(long_df), schema_info=schema)
        db.add(batch)
        db.flush()

        rows = [
            DataRow(
                batch_id=batch.id,
                region=r.get("region"),
                country=r.get("country"),
                year=int(r["year"]) if r.get("year") is not None else None,
                metric=r["metric"],
                value=float(r["value"]) if r.get("value") is not None else None,
            )
            for _, r in long_df.iterrows()
        ]
        db.bulk_save_objects(rows)
        db.commit()

    return {"message": "upload successful", "mode": mode, "rows": len(rows)}


def apply_filters(query, regions: Optional[list[str]], countries: Optional[list[str]], years: Optional[list[int]], metrics: Optional[list[str]]):
    if regions:
        query = query.filter(DataRow.region.in_(regions))
    if countries:
        query = query.filter(DataRow.country.in_(countries))
    if years:
        query = query.filter(DataRow.year.in_(years))
    if metrics:
        query = query.filter(DataRow.metric.in_(metrics))
    return query


@app.get("/filters")
def get_filters(regions: Optional[list[str]] = Query(None)):
    with SessionLocal() as db:
        region_q = db.query(DataRow.region).distinct().order_by(DataRow.region)
        country_q = db.query(DataRow.country).distinct().order_by(DataRow.country)
        year_q = db.query(DataRow.year).distinct().order_by(DataRow.year)
        metric_q = db.query(DataRow.metric).distinct().order_by(DataRow.metric)

        if regions:
            country_q = country_q.filter(DataRow.region.in_(regions))

        return {
            "regions": [r[0] for r in region_q if r[0]],
            "countries": [c[0] for c in country_q if c[0]],
            "years": [y[0] for y in year_q if y[0] is not None],
            "metrics": [m[0] for m in metric_q if m[0]],
        }


@app.get("/data")
def get_data(
    regions: Optional[list[str]] = Query(None),
    countries: Optional[list[str]] = Query(None),
    years: Optional[list[int]] = Query(None),
    metrics: Optional[list[str]] = Query(None),
):
    with SessionLocal() as db:
        q = db.query(DataRow)
        q = apply_filters(q, regions, countries, years, metrics)
        rows = q.limit(5000).all()
        return [
            {"region": r.region, "country": r.country, "year": r.year, "metric": r.metric, "value": r.value}
            for r in rows
        ]


@app.get("/aggregate")
def aggregate(
    group_by: str = Query("year", pattern="^(region|country|year|metric)$"),
    agg: str = Query("sum", pattern="^(sum|avg)$"),
    regions: Optional[list[str]] = Query(None),
    countries: Optional[list[str]] = Query(None),
    years: Optional[list[int]] = Query(None),
    metrics: Optional[list[str]] = Query(None),
):
    group_col = getattr(DataRow, group_by)
    agg_col = func.sum(DataRow.value) if agg == "sum" else func.avg(DataRow.value)

    with SessionLocal() as db:
        q = db.query(group_col.label("key"), agg_col.label("value"))
        q = apply_filters(q, regions, countries, years, metrics)
        q = q.group_by(group_col).order_by(group_col)
        return [{"key": r.key, "value": r.value} for r in q.all()]


@app.get("/summary")
def summary(
    regions: Optional[list[str]] = Query(None),
    countries: Optional[list[str]] = Query(None),
    years: Optional[list[int]] = Query(None),
    metrics: Optional[list[str]] = Query(None),
):
    with SessionLocal() as db:
        q = db.query(func.sum(DataRow.value), func.avg(DataRow.value), func.count(DataRow.id))
        q = apply_filters(q, regions, countries, years, metrics)
        total, avg, count = q.one()
        return {"total": total or 0, "average": avg or 0, "records": count}


@app.get("/export")
def export_csv(
    regions: Optional[list[str]] = Query(None),
    countries: Optional[list[str]] = Query(None),
    years: Optional[list[int]] = Query(None),
    metrics: Optional[list[str]] = Query(None),
):
    with SessionLocal() as db:
        q = db.query(DataRow)
        q = apply_filters(q, regions, countries, years, metrics)
        rows = q.all()
        df = pd.DataFrame(
            [{"region": r.region, "country": r.country, "year": r.year, "metric": r.metric, "value": r.value} for r in rows]
        )
    stream = BytesIO()
    df.to_csv(stream, index=False)
    stream.seek(0)
    return StreamingResponse(stream, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=filtered_data.csv"})

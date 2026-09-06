"""Live StatCan feed + trend-direction model serving.

Run from the repo root:
    .venv/bin/uvicorn api_service.main:app --reload --port 8000

Endpoints:
    GET  /health
    GET  /vectors                  list of known StatCan vectors (perceived_mh_annual only)
    GET  /live/{vector_id}         raw latest StatCan WDS values for a vector
    POST /predict                  direct model call, same shape as models/running.py
    GET  /live-predict/{vector_id} live StatCan value -> fed into the trend-direction model
"""

from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "06_trend_direction_model.joblib"
PERCEIVED_MH_ANNUAL = ROOT / "data" / "processed" / "02_cleaned" / "perceived_mh_annual.csv"
WDS_URL = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
TERRITORIES = {"Yukon", "Northwest Territories", "Nunavut"}

app = FastAPI(title="Mental Health Project - Live API + Model Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

model = None
vector_lookup: dict[str, dict] = {}


class PredictRow(BaseModel):
    source: str
    geo: str
    geo_level: str
    sex: str
    age_group: str
    indicator: str
    value_t: float
    year_t: int
    year_gap: int
    quality_flag_t: str
    ci_width_t: Optional[float] = None


def build_vector_lookup() -> dict[str, dict]:
    df = pd.read_csv(PERCEIVED_MH_ANNUAL)
    df["geo_level"] = df["geo"].apply(lambda g: "territory" if g in TERRITORIES else "province")

    lookup = {}
    for vector, grp in df.groupby("vector"):
        grp = grp.sort_values("start_year")
        latest = grp.iloc[-1]
        years = grp["start_year"].tolist()
        gap = int(years[-1] - years[-2]) if len(years) > 1 else 2
        quality_flag = latest["quality_flag"]
        vector_id = str(vector).lstrip("v")
        lookup[vector_id] = {
            "source": "perceived_mh_annual",
            "geo": latest["geo"],
            "geo_level": latest["geo_level"],
            "sex": latest["sex"],
            "age_group": latest["age_group"],
            "indicator": latest["indicator"],
            "year_gap": gap,
            "last_known_year": int(latest["start_year"]),
            "last_known_value": float(latest["value"]) if pd.notna(latest["value"]) else None,
            "last_known_quality_flag": quality_flag if pd.notna(quality_flag) else "ok",
        }
    return lookup


@app.on_event("startup")
def load_resources():
    global model, vector_lookup
    model = joblib.load(MODEL_PATH)
    vector_lookup = build_vector_lookup()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "vectors_indexed": len(vector_lookup),
    }


@app.get("/vectors")
def list_vectors():
    return [{"vector": f"v{vid}", **meta} for vid, meta in vector_lookup.items()]


def fetch_statcan_vector(vector_id: int, latest_n: int = 3) -> dict:
    payload = [{"vectorId": vector_id, "latestN": latest_n}]
    resp = requests.post(WDS_URL, json=payload, timeout=10)
    resp.raise_for_status()
    body = resp.json()
    if not body or body[0].get("status") != "SUCCESS":
        raise HTTPException(status_code=502, detail="StatCan WDS did not return SUCCESS")
    return body[0]["object"]


@app.get("/live/{vector_id}")
def live(vector_id: int, latest_n: int = 3):
    return fetch_statcan_vector(vector_id, latest_n)


@app.post("/predict")
def predict(row: PredictRow):
    frame = pd.DataFrame([row.model_dump()])
    prediction = model.predict(frame)[0]
    proba = model.predict_proba(frame)[0]
    classes = list(model.classes_)
    return {
        "prediction": prediction,
        "probabilities": dict(zip(classes, [round(float(p), 4) for p in proba])),
    }


@app.get("/live-predict/{vector_id}")
def live_predict(vector_id: int):
    key = str(vector_id)
    if key not in vector_lookup:
        raise HTTPException(
            status_code=404,
            detail="Unknown vector. Only perceived_mh_annual vectors are indexed today.",
        )
    meta = vector_lookup[key]

    live_data = fetch_statcan_vector(vector_id, latest_n=1)
    points = live_data.get("vectorDataPoint", [])
    if not points:
        raise HTTPException(status_code=502, detail="StatCan WDS returned no data points")
    point = points[-1]

    year_t = int(point["refPer"][:4])
    value_t = point["value"]
    quality_flag_t = "ok" if point.get("statusCode") == 0 else "flagged"

    row = PredictRow(
        source=meta["source"],
        geo=meta["geo"],
        geo_level=meta["geo_level"],
        sex=meta["sex"],
        age_group=meta["age_group"],
        indicator=meta["indicator"],
        value_t=value_t,
        year_t=year_t,
        year_gap=meta["year_gap"],
        quality_flag_t=quality_flag_t,
        ci_width_t=None,
    )
    frame = pd.DataFrame([row.model_dump()])
    prediction = model.predict(frame)[0]
    proba = model.predict_proba(frame)[0]
    classes = list(model.classes_)

    return {
        "vector": f"v{vector_id}",
        "geo": meta["geo"],
        "sex": meta["sex"],
        "age_group": meta["age_group"],
        "indicator": meta["indicator"],
        "live_year": year_t,
        "live_value": value_t,
        "release_time": point.get("releaseTime"),
        "compared_to_cleaned_snapshot": {
            "year": meta["last_known_year"],
            "value": meta["last_known_value"],
        },
        "prediction": prediction,
        "probabilities": dict(zip(classes, [round(float(p), 4) for p in proba])),
    }

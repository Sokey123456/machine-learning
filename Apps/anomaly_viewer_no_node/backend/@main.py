from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "data")
STATIC_DIR = os.path.join(HERE, "static")

HISTORY_CSV = os.path.join(DATA_DIR, "test_history_rates_long.csv")
SCALES_CSV = os.path.join(DATA_DIR, "test_product_scales_p95.csv")

app = FastAPI(title="Anomaly Viewer (Excel-like / No Node)", version="0.2.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@lru_cache(maxsize=1)
def load_all() -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(HISTORY_CSV)
    scales = pd.read_csv(SCALES_CSV)
    df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
    return df, scales


def ordered_unique(series: pd.Series) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in series.astype(str).tolist():
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/meta")
def meta() -> Dict[str, Any]:
    df, scales = load_all()
    products = ordered_unique(df["product"])
    currencies = ordered_unique(df["currency"])
    tenors = ordered_unique(df["tenor"])
    dates = sorted(ordered_unique(df["date"]))
    latest_date = dates[-1] if dates else None
    scale_map = dict(zip(scales["product"].astype(str), scales["S_product_bp_p95"].astype(float)))
    return {
        "products": products,
        "currencies": currencies,
        "tenors": tenors,
        "dates": dates,
        "latest_date": latest_date,
        "scales_bp_p95": scale_map,
    }


@app.get("/api/grid")
def grid(date: str = Query(...)) -> Dict[str, Any]:
    """
    Returns per-cell arrays aligned to tenor order.
    Includes today/prev/diff arrays so the UI can render Excel-like mini blocks in each cell.
    """
    df, scales = load_all()
    scale_map = dict(zip(scales["product"].astype(str), scales["S_product_bp_p95"].astype(float)))

    ddf = df[df["date"] == date].copy()
    if ddf.empty:
        return {"date": date, "products": [], "currencies": [], "tenors": [], "cells": []}

    products = ordered_unique(ddf["product"])
    currencies = ordered_unique(ddf["currency"])
    tenors = ordered_unique(ddf["tenor"])
    tenor_index = {t: i for i, t in enumerate(tenors)}

    cells = []
    for p in products:
        for c in currencies:
            sub = ddf[(ddf["product"] == p) & (ddf["currency"] == c)]
            today = np.full(len(tenors), np.nan, dtype=float)
            prev = np.full(len(tenors), np.nan, dtype=float)
            diffs = np.full(len(tenors), np.nan, dtype=float)

            for _, r in sub.iterrows():
                i = tenor_index[str(r["tenor"])]
                today[i] = float(r["today_rate_pct"]) if pd.notna(r["today_rate_pct"]) else np.nan
                prev[i] = float(r["prev_workday_rate_pct"]) if pd.notna(r["prev_workday_rate_pct"]) else np.nan
                diffs[i] = float(r["diff_bp"]) if pd.notna(r["diff_bp"]) else np.nan

            max_abs = float(np.nanmax(np.abs(diffs))) if np.isfinite(diffs).any() else float("nan")
            cells.append({
                "product": p,
                "currency": c,
                "today_rate_pct": today.tolist(),
                "prev_rate_pct": prev.tolist(),
                "diffs_bp": diffs.tolist(),
                "max_abs_diff_bp": max_abs,
                "scale_bp": float(scale_map.get(p, np.nan)),
            })

    return {"date": date, "products": products, "currencies": currencies, "tenors": tenors, "cells": cells}


@app.get("/api/detail")
def detail(date: str = Query(...), product: str = Query(...), currency: str = Query(...)) -> Dict[str, Any]:
    df, _ = load_all()
    sub = df[(df["date"] == date) & (df["product"] == product) & (df["currency"] == currency)].copy()
    if sub.empty:
        return {"date": date, "product": product, "currency": currency, "tenors": [], "today": [], "prev": [], "diff_bp": []}

    tenors = ordered_unique(sub["tenor"])
    sub["tenor"] = sub["tenor"].astype(str)
    sub = sub.set_index("tenor")

    today = [float(sub.loc[t, "today_rate_pct"]) for t in tenors]
    prev = [float(sub.loc[t, "prev_workday_rate_pct"]) if pd.notna(sub.loc[t, "prev_workday_rate_pct"]) else np.nan for t in tenors]
    diff = [float(sub.loc[t, "diff_bp"]) if pd.notna(sub.loc[t, "diff_bp"]) else np.nan for t in tenors]

    return {"date": date, "product": product, "currency": currency, "tenors": tenors, "today": today, "prev": prev, "diff_bp": diff}

from __future__ import annotations
import pandas as pd
from sqlalchemy import text, bindparam
from config import get_engine
from product import get_product_spec
from grid_sort import sort_grids_naturally

def make_df(product: str, *, dims: dict, date_from=None, date_to=None):
    spec = get_product_spec(product)
    engine = get_engine()

    where = []
    params = {}
    for k,v in dims.items():
        col = spec.dimensions[k]
        where.append(f"{col} = :{k}")
        params[k] = v

    if date_from:
        where.append("BaseDate >= :date_from")
        params["date_from"] = date_from
    if date_to:
        where.append("BaseDate <= :date_to")
        params["date_to"] = date_to

    sql = f"SELECT {','.join(spec.required_select_columns)} FROM {spec.table}"
    if where:
        sql += " WHERE " + " AND ".join(where)

    df = pd.read_sql_query(text(sql), engine, params=params)
    df = df.rename(columns=spec.column_map)
    df["base_date"] = pd.to_datetime(df["base_date"]).dt.date

    idx = df.groupby(spec.resolve_group_key_common())["quote_time"].idxmax()
    df = df.loc[idx]

    wide = df.pivot(index="grid", columns="base_date", values="rate")
    wide = wide.reindex(sort_grids_naturally(wide.index), axis=0)
    return wide

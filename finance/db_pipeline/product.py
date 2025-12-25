from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import yaml

@dataclass(frozen=True)
class ProductSpec:
    name: str
    table: str
    db_columns: List[str]
    column_map: Dict[str, str]
    dimensions: Dict[str, str]
    required_dimensions: List[str]
    required_select_columns: List[str]
    static_filters: Optional[List[str]] = None

    def resolve_group_key_common(self) -> List[str]:
        return ["base_date","grid",*self.required_dimensions]

def load_products_from_yaml(path: str | Path) -> Dict[str, ProductSpec]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)["products"]
    out = {}
    for name, spec in data.items():
        out[name] = ProductSpec(
            name=name,
            table=spec["table"],
            db_columns=spec["db_columns"],
            column_map=spec["column_map"],
            dimensions=spec["dimensions"],
            required_dimensions=spec["required_dimensions"],
            required_select_columns=spec["required_select_columns"],
            static_filters=spec.get("static_filters"),
        )
    return out

_PRODUCTS = load_products_from_yaml(Path(__file__).with_name("products.yaml"))

def get_product_spec(product: str) -> ProductSpec:
    return _PRODUCTS[product]

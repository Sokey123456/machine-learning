from __future__ import annotations
from dataclasses import dataclass
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

@dataclass(frozen=True)
class DBConfig:
    db_url: str
    echo: bool = False
    pool_pre_ping: bool = True

def load_db_config(prefix: str = "DB_") -> DBConfig:
    db_url = os.getenv(f"{prefix}URL")
    if not db_url:
        raise RuntimeError(f"Missing env var: {prefix}URL")
    echo = os.getenv(f"{prefix}ECHO", "0") in ("1","true","True")
    return DBConfig(db_url=db_url, echo=echo)

_ENGINE: Engine | None = None

def get_engine(config: DBConfig | None = None) -> Engine:
    global _ENGINE
    if _ENGINE:
        return _ENGINE
    if config is None:
        config = load_db_config()
    _ENGINE = create_engine(config.db_url, echo=config.echo, pool_pre_ping=config.pool_pre_ping)
    return _ENGINE

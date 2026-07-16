from __future__ import annotations

import time

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import OperationalError

from app.config import Settings
from app.models import Base


def build_engine(settings: Settings) -> Engine:
    connect_args = {"check_same_thread": False} if str(settings.sqlalchemy_url).startswith("sqlite") else {}
    return create_engine(
        settings.sqlalchemy_url,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


def initialize_database(
    engine: Engine,
    attempts: int = 20,
    delay_seconds: float = 1.5,
    create_schema: bool = True,
) -> None:
    for attempt in range(1, attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            if create_schema:
                Base.metadata.create_all(engine)
            return
        except OperationalError:
            if attempt == attempts:
                raise
            time.sleep(delay_seconds)


def database_is_healthy(engine: Engine) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

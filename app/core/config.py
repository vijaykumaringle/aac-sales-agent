import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path


def get_settings() -> Settings:
    return Settings(database_path=Path(os.getenv("DATABASE_PATH", "data/aac_sales_agent.db")))

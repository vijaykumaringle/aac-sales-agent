import sqlite3

from app.core.config import get_settings


def is_postgres_database(database) -> bool:
    module_name = type(database).__module__ or ""
    return module_name.startswith("psycopg")


def execute_query(database, query: str, params: tuple | None = None):
    params = params or ()
    if is_postgres_database(database):
        return database.execute(query.replace("?", "%s"), params)
    return database.execute(query, params)


def connection():
    settings = get_settings()
    if settings.database_url:
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(settings.database_url, row_factory=dict_row)

    path = settings.database_path
    path.parent.mkdir(parents=True, exist_ok=True)
    database = sqlite3.connect(path)
    database.row_factory = sqlite3.Row
    return database

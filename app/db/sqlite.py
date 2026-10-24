import sqlite3
from contextlib import closing

from app.core.config import get_settings


def connection() -> sqlite3.Connection:
    path = get_settings().database_path
    path.parent.mkdir(parents=True, exist_ok=True)
    database = sqlite3.connect(path)
    database.row_factory = sqlite3.Row
    return database


def initialize_database() -> None:
    with closing(connection()) as database:
        database.executescript(
            """
            CREATE TABLE IF NOT EXISTS enquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                location TEXT NOT NULL,
                requirement_summary TEXT NOT NULL,
                estimated_quantity TEXT,
                project_type TEXT,
                preferred_contact_time TEXT,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                review_notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS intake_sessions (
                id TEXT PRIMARY KEY,
                channel TEXT NOT NULL,
                contact_identifier TEXT NOT NULL,
                current_step TEXT NOT NULL,
                customer_name TEXT,
                location TEXT,
                project_type TEXT,
                estimated_quantity TEXT,
                requirement_summary TEXT,
                preferred_contact_time TEXT,
                enquiry_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(enquiry_id) REFERENCES enquiries(id)
            );

            CREATE UNIQUE INDEX IF NOT EXISTS active_intake_session
            ON intake_sessions(channel, contact_identifier)
            WHERE enquiry_id IS NULL;
            """
        )
        database.commit()

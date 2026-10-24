import sqlite3

import pytest


@pytest.fixture(autouse=True)
def prepare_sqlite_database(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "sales-agent.db"
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("DATABASE_PATH", str(database_path))

    with sqlite3.connect(database_path) as database:
        database.executescript(
            """
            CREATE TABLE enquiries (
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

            CREATE TABLE intake_sessions (
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

            CREATE UNIQUE INDEX active_intake_session
            ON intake_sessions(channel, contact_identifier)
            WHERE enquiry_id IS NULL;
            """
        )

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from uuid import uuid4

from app.db.sqlite import connection
from app.domain.intake import IntakeChannel, IntakeSession, IntakeStep


def _to_session(row: sqlite3.Row) -> IntakeSession:
    return IntakeSession(
        id=row["id"],
        channel=IntakeChannel(row["channel"]),
        contact_identifier=row["contact_identifier"],
        current_step=IntakeStep(row["current_step"]),
        customer_name=row["customer_name"],
        location=row["location"],
        project_type=row["project_type"],
        estimated_quantity=row["estimated_quantity"],
        requirement_summary=row["requirement_summary"],
        preferred_contact_time=row["preferred_contact_time"],
        enquiry_id=row["enquiry_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class IntakeSessionRepository:
    def find_active(self, channel: IntakeChannel, contact_identifier: str) -> IntakeSession | None:
        with closing(connection()) as database:
            row = database.execute(
                """
                SELECT * FROM intake_sessions
                WHERE channel = ? AND contact_identifier = ? AND enquiry_id IS NULL
                """,
                (channel, contact_identifier),
            ).fetchone()
        return _to_session(row) if row else None

    def create(self, channel: IntakeChannel, contact_identifier: str) -> IntakeSession:
        now = datetime.now(UTC).isoformat()
        session_id = str(uuid4())
        with closing(connection()) as database:
            database.execute(
                """
                INSERT INTO intake_sessions (id, channel, contact_identifier, current_step, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, channel, contact_identifier, IntakeStep.CUSTOMER_NAME, now, now),
            )
            database.commit()
        return self.get(session_id)

    def get(self, session_id: str) -> IntakeSession | None:
        with closing(connection()) as database:
            row = database.execute("SELECT * FROM intake_sessions WHERE id = ?", (session_id,)).fetchone()
        return _to_session(row) if row else None

    def update(self, session_id: str, *, field: str, value: str | None, next_step: IntakeStep) -> IntakeSession:
        allowed_fields = {
            "customer_name",
            "location",
            "project_type",
            "estimated_quantity",
            "requirement_summary",
            "preferred_contact_time",
        }
        if field not in allowed_fields:
            raise ValueError(f"Unsupported intake field: {field}")
        with closing(connection()) as database:
            database.execute(
                f"UPDATE intake_sessions SET {field} = ?, current_step = ?, updated_at = ? WHERE id = ?",
                (value, next_step, datetime.now(UTC).isoformat(), session_id),
            )
            database.commit()
        session = self.get(session_id)
        if session is None:
            raise LookupError("Intake session not found")
        return session

    def complete(self, session_id: str, enquiry_id: int) -> IntakeSession:
        with closing(connection()) as database:
            database.execute(
                """
                UPDATE intake_sessions
                SET enquiry_id = ?, current_step = ?, updated_at = ?
                WHERE id = ?
                """,
                (enquiry_id, IntakeStep.COMPLETED, datetime.now(UTC).isoformat(), session_id),
            )
            database.commit()
        session = self.get(session_id)
        if session is None:
            raise LookupError("Intake session not found")
        return session

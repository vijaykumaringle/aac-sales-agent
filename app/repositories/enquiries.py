import sqlite3
from contextlib import closing
from datetime import UTC, datetime

from app.db.sqlite import connection
from app.domain.enquiries import EnquiryRecord, EnquiryStatus


def _to_record(row: sqlite3.Row) -> EnquiryRecord:
    return EnquiryRecord(
        id=row["id"],
        customer_name=row["customer_name"],
        phone_number=row["phone_number"],
        location=row["location"],
        requirement_summary=row["requirement_summary"],
        estimated_quantity=row["estimated_quantity"],
        project_type=row["project_type"],
        preferred_contact_time=row["preferred_contact_time"],
        source=row["source"],
        status=EnquiryStatus(row["status"]),
        review_notes=row["review_notes"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class EnquiryRepository:
    def create(
        self,
        *,
        customer_name: str,
        phone_number: str,
        location: str,
        requirement_summary: str,
        estimated_quantity: str | None,
        project_type: str | None,
        preferred_contact_time: str | None,
        source: str,
    ) -> EnquiryRecord:
        now = datetime.now(UTC).isoformat()
        with closing(connection()) as database:
            cursor = database.execute(
                """
                INSERT INTO enquiries (
                    customer_name, phone_number, location, requirement_summary,
                    estimated_quantity, project_type, preferred_contact_time, source,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    customer_name,
                    phone_number,
                    location,
                    requirement_summary,
                    estimated_quantity,
                    project_type,
                    preferred_contact_time,
                    source,
                    EnquiryStatus.PENDING_REVIEW,
                    now,
                    now,
                ),
            )
            database.commit()
            row = database.execute("SELECT * FROM enquiries WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return _to_record(row)

    def get(self, enquiry_id: int) -> EnquiryRecord | None:
        with closing(connection()) as database:
            row = database.execute("SELECT * FROM enquiries WHERE id = ?", (enquiry_id,)).fetchone()
        return _to_record(row) if row else None

    def list(self, enquiry_status: EnquiryStatus | None = None) -> list[EnquiryRecord]:
        query = "SELECT * FROM enquiries"
        parameters: tuple[str, ...] = ()
        if enquiry_status:
            query += " WHERE status = ?"
            parameters = (enquiry_status,)
        query += " ORDER BY created_at DESC"
        with closing(connection()) as database:
            rows = database.execute(query, parameters).fetchall()
        return [_to_record(row) for row in rows]

    def update_review(
        self,
        enquiry_id: int,
        *,
        status: EnquiryStatus | None,
        review_notes: str | None,
        replace_notes: bool,
    ) -> EnquiryRecord | None:
        current = self.get(enquiry_id)
        if current is None:
            return None
        next_status = status or current.status
        next_notes = review_notes if replace_notes else current.review_notes
        with closing(connection()) as database:
            database.execute(
                "UPDATE enquiries SET status = ?, review_notes = ?, updated_at = ? WHERE id = ?",
                (next_status, next_notes, datetime.now(UTC).isoformat(), enquiry_id),
            )
            database.commit()
        return self.get(enquiry_id)

from contextlib import closing
from datetime import UTC, datetime

from app.db.database import connection, execute_query, is_postgres_database
from app.domain.enquiries import EnquiryRecord, EnquiryStatus


def _to_record(row) -> EnquiryRecord:
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
        created_at=datetime.fromisoformat(str(row["created_at"])),
        updated_at=datetime.fromisoformat(str(row["updated_at"])),
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
        insert_sql = """
            INSERT INTO enquiries (
                customer_name, phone_number, location, requirement_summary,
                estimated_quantity, project_type, preferred_contact_time, source,
                status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
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
        )

        with closing(connection()) as database:
            if is_postgres_database(database):
                row = execute_query(database, insert_sql + " RETURNING *", params).fetchone()
            else:
                cursor = execute_query(database, insert_sql, params)
                database.commit()
                row = execute_query(database, "SELECT * FROM enquiries WHERE id = ?", (cursor.lastrowid,)).fetchone()
            database.commit()
        return _to_record(row)

    def get(self, enquiry_id: int) -> EnquiryRecord | None:
        with closing(connection()) as database:
            row = execute_query(database, "SELECT * FROM enquiries WHERE id = ?", (enquiry_id,)).fetchone()
        return _to_record(row) if row else None

    def list(self, enquiry_status: EnquiryStatus | None = None) -> list[EnquiryRecord]:
        query = "SELECT * FROM enquiries"
        parameters: tuple = ()
        if enquiry_status:
            query += " WHERE status = ?"
            parameters = (enquiry_status,)
        query += " ORDER BY created_at DESC"
        with closing(connection()) as database:
            rows = execute_query(database, query, parameters).fetchall()
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
            execute_query(
                database,
                "UPDATE enquiries SET status = ?, review_notes = ?, updated_at = ? WHERE id = ?",
                (next_status, next_notes, datetime.now(UTC).isoformat(), enquiry_id),
            )
            database.commit()
        return self.get(enquiry_id)

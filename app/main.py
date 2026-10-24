import os
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field


class EnquiryStatus(StrEnum):
    PENDING_REVIEW = "pending_review"
    IN_REVIEW = "in_review"
    CONTACTED = "contacted"
    CLOSED = "closed"


class EnquiryCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    phone_number: str = Field(min_length=5, max_length=30)
    location: str = Field(min_length=1, max_length=160)
    requirement_summary: str = Field(min_length=1, max_length=1_000)
    estimated_quantity: str | None = Field(default=None, max_length=100)
    project_type: str | None = Field(default=None, max_length=100)
    preferred_contact_time: str | None = Field(default=None, max_length=100)
    source: str = Field(default="manual", max_length=50)


class Enquiry(EnquiryCreate):
    id: int
    status: EnquiryStatus
    created_at: datetime
    updated_at: datetime
    review_notes: str | None


class EnquiryReviewUpdate(BaseModel):
    status: EnquiryStatus | None = None
    review_notes: str | None = Field(default=None, max_length=2_000)


def database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", "data/aac_sales_agent.db"))


def connection() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    database = sqlite3.connect(path)
    database.row_factory = sqlite3.Row
    return database


def initialize_database() -> None:
    with closing(connection()) as database:
        database.execute(
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
            )
            """
        )
        database.commit()


def row_to_enquiry(row: sqlite3.Row) -> Enquiry:
    return Enquiry(
        id=row["id"],
        customer_name=row["customer_name"],
        phone_number=row["phone_number"],
        location=row["location"],
        requirement_summary=row["requirement_summary"],
        estimated_quantity=row["estimated_quantity"],
        project_type=row["project_type"],
        preferred_contact_time=row["preferred_contact_time"],
        source=row["source"],
        status=row["status"],
        review_notes=row["review_notes"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


app = FastAPI(
    title="AAC Sales Agent",
    description="Captures sales enquiries for human review before quotation.",
    version="0.1.0",
)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/enquiries", response_model=Enquiry, status_code=status.HTTP_201_CREATED)
def create_enquiry(payload: EnquiryCreate) -> Enquiry:
    initialize_database()
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
                payload.customer_name,
                payload.phone_number,
                payload.location,
                payload.requirement_summary,
                payload.estimated_quantity,
                payload.project_type,
                payload.preferred_contact_time,
                payload.source,
                EnquiryStatus.PENDING_REVIEW,
                now,
                now,
            ),
        )
        database.commit()
        row = database.execute("SELECT * FROM enquiries WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return row_to_enquiry(row)


@app.get("/enquiries", response_model=list[Enquiry])
def list_enquiries(
    enquiry_status: EnquiryStatus | None = Query(default=None, alias="status"),
) -> list[Enquiry]:
    initialize_database()
    query = "SELECT * FROM enquiries"
    parameters: tuple[str, ...] = ()
    if enquiry_status:
        query += " WHERE status = ?"
        parameters = (enquiry_status,)
    query += " ORDER BY created_at DESC"
    with closing(connection()) as database:
        rows = database.execute(query, parameters).fetchall()
    return [row_to_enquiry(row) for row in rows]


@app.get("/enquiries/{enquiry_id}", response_model=Enquiry)
def get_enquiry(enquiry_id: int) -> Enquiry:
    initialize_database()
    with closing(connection()) as database:
        row = database.execute("SELECT * FROM enquiries WHERE id = ?", (enquiry_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")
    return row_to_enquiry(row)


@app.patch("/enquiries/{enquiry_id}/review", response_model=Enquiry)
def review_enquiry(enquiry_id: int, payload: EnquiryReviewUpdate) -> Enquiry:
    initialize_database()
    with closing(connection()) as database:
        current = database.execute("SELECT * FROM enquiries WHERE id = ?", (enquiry_id,)).fetchone()
        if current is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")
        next_status = payload.status or current["status"]
        next_notes = payload.review_notes if payload.review_notes is not None else current["review_notes"]
        database.execute(
            "UPDATE enquiries SET status = ?, review_notes = ?, updated_at = ? WHERE id = ?",
            (next_status, next_notes, datetime.now(UTC).isoformat(), enquiry_id),
        )
        database.commit()
        row = database.execute("SELECT * FROM enquiries WHERE id = ?", (enquiry_id,)).fetchone()
    return row_to_enquiry(row)

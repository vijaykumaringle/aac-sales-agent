from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class EnquiryStatus(StrEnum):
    PENDING_REVIEW = "pending_review"
    IN_REVIEW = "in_review"
    CONTACTED = "contacted"
    CLOSED = "closed"


@dataclass(frozen=True)
class EnquiryRecord:
    id: int
    customer_name: str
    phone_number: str
    location: str
    requirement_summary: str
    estimated_quantity: str | None
    project_type: str | None
    preferred_contact_time: str | None
    source: str
    status: EnquiryStatus
    review_notes: str | None
    created_at: datetime
    updated_at: datetime

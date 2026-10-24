from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enquiries import EnquiryStatus


class EnquiryCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    phone_number: str = Field(min_length=5, max_length=30)
    location: str = Field(min_length=1, max_length=160)
    requirement_summary: str = Field(min_length=1, max_length=1_000)
    estimated_quantity: str | None = Field(default=None, max_length=100)
    project_type: str | None = Field(default=None, max_length=100)
    preferred_contact_time: str | None = Field(default=None, max_length=100)
    source: str = Field(default="manual", max_length=50)


class EnquiryReviewUpdate(BaseModel):
    status: EnquiryStatus | None = None
    review_notes: str | None = Field(default=None, max_length=2_000)


class EnquiryResponse(EnquiryCreate):
    id: int
    status: EnquiryStatus
    review_notes: str | None
    created_at: datetime
    updated_at: datetime

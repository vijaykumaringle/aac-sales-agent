from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class IntakeChannel(StrEnum):
    WHATSAPP = "whatsapp"
    PHONE = "phone"
    WEB = "web"


class IntakeStep(StrEnum):
    CUSTOMER_NAME = "customer_name"
    LOCATION = "location"
    PROJECT_TYPE = "project_type"
    ESTIMATED_QUANTITY = "estimated_quantity"
    REQUIREMENT_SUMMARY = "requirement_summary"
    PREFERRED_CONTACT_TIME = "preferred_contact_time"
    COMPLETED = "completed"


@dataclass(frozen=True)
class IntakeSession:
    id: str
    channel: IntakeChannel
    contact_identifier: str
    current_step: IntakeStep
    customer_name: str | None
    location: str | None
    project_type: str | None
    estimated_quantity: str | None
    requirement_summary: str | None
    preferred_contact_time: str | None
    enquiry_id: int | None
    created_at: datetime
    updated_at: datetime

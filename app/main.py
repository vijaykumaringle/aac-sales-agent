from fastapi import FastAPI, status
from pydantic import BaseModel, Field


app = FastAPI(
    title="AAC Sales Agent",
    description="Captures sales enquiries for human review before quotation.",
    version="0.1.0",
)


class EnquiryCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    phone_number: str = Field(min_length=5, max_length=30)
    location: str = Field(min_length=1, max_length=160)
    requirement_summary: str = Field(min_length=1, max_length=1_000)
    preferred_contact_time: str | None = Field(default=None, max_length=100)


class Enquiry(EnquiryCreate):
    id: int
    status: str


enquiries: list[Enquiry] = []


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/enquiries", response_model=Enquiry, status_code=status.HTTP_201_CREATED)
def create_enquiry(payload: EnquiryCreate) -> Enquiry:
    enquiry = Enquiry(id=len(enquiries) + 1, status="pending_review", **payload.model_dump())
    enquiries.append(enquiry)
    return enquiry

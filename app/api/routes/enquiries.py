from fastapi import APIRouter, HTTPException, Query, status

from app.domain.enquiries import EnquiryRecord, EnquiryStatus
from app.schemas.enquiries import EnquiryCreate, EnquiryResponse, EnquiryReviewUpdate
from app.services.enquiries import EnquiryService


router = APIRouter(prefix="/enquiries", tags=["enquiries"])
service = EnquiryService()


def to_response(record: EnquiryRecord) -> EnquiryResponse:
    return EnquiryResponse(**record.__dict__)


@router.post("", response_model=EnquiryResponse, status_code=status.HTTP_201_CREATED)
def create_enquiry(payload: EnquiryCreate) -> EnquiryResponse:
    return to_response(service.create(payload))


@router.get("", response_model=list[EnquiryResponse])
def list_enquiries(
    enquiry_status: EnquiryStatus | None = Query(default=None, alias="status"),
) -> list[EnquiryResponse]:
    return [to_response(record) for record in service.list(enquiry_status)]


@router.get("/{enquiry_id}", response_model=EnquiryResponse)
def get_enquiry(enquiry_id: int) -> EnquiryResponse:
    record = service.get(enquiry_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")
    return to_response(record)


@router.patch("/{enquiry_id}/review", response_model=EnquiryResponse)
def review_enquiry(enquiry_id: int, payload: EnquiryReviewUpdate) -> EnquiryResponse:
    record = service.update_review(enquiry_id, payload)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")
    return to_response(record)

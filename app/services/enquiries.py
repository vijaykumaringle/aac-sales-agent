from app.domain.enquiries import EnquiryRecord, EnquiryStatus
from app.repositories.enquiries import EnquiryRepository
from app.schemas.enquiries import EnquiryCreate, EnquiryReviewUpdate


class EnquiryService:
    def __init__(self, repository: EnquiryRepository | None = None) -> None:
        self.repository = repository or EnquiryRepository()

    def create(self, payload: EnquiryCreate) -> EnquiryRecord:
        return self.repository.create(**payload.model_dump())

    def get(self, enquiry_id: int) -> EnquiryRecord | None:
        return self.repository.get(enquiry_id)

    def list(self, enquiry_status: EnquiryStatus | None = None) -> list[EnquiryRecord]:
        return self.repository.list(enquiry_status)

    def update_review(self, enquiry_id: int, payload: EnquiryReviewUpdate) -> EnquiryRecord | None:
        return self.repository.update_review(
            enquiry_id,
            status=payload.status,
            review_notes=payload.review_notes,
            replace_notes="review_notes" in payload.model_fields_set,
        )

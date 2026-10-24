from app.domain.intake import IntakeSession, IntakeStep
from app.repositories.intake_sessions import IntakeSessionRepository
from app.schemas.enquiries import EnquiryCreate
from app.schemas.intake import IntakeMessage, IntakeReply
from app.services.enquiries import EnquiryService


PROMPTS = {
    IntakeStep.CUSTOMER_NAME: "Welcome. I can collect your AAC block requirement for our sales team. What is your name or company name?",
    IntakeStep.LOCATION: "Thanks. Which city or project location needs AAC blocks?",
    IntakeStep.PROJECT_TYPE: "What type of project is this, for example residential, commercial, or contractor supply?",
    IntakeStep.ESTIMATED_QUANTITY: "What is the estimated quantity you need? You can reply with blocks, cubic metres, or an approximate area.",
    IntakeStep.REQUIREMENT_SUMMARY: "Please share the block size, delivery timing, and any other requirement details.",
    IntakeStep.PREFERRED_CONTACT_TIME: "When would you prefer our sales team to contact you? Reply 'skip' if there is no preference.",
}


class IntakeService:
    def __init__(
        self,
        sessions: IntakeSessionRepository | None = None,
        enquiries: EnquiryService | None = None,
    ) -> None:
        self.sessions = sessions or IntakeSessionRepository()
        self.enquiries = enquiries or EnquiryService()

    def receive_message(self, message: IntakeMessage) -> IntakeReply:
        session = self.sessions.find_active(message.channel, message.contact_identifier)
        if session is None:
            session = self.sessions.create(message.channel, message.contact_identifier)
            return self._reply(session, PROMPTS[IntakeStep.CUSTOMER_NAME])

        cleaned_message = message.message_text.strip()
        if session.current_step is IntakeStep.CUSTOMER_NAME:
            session = self.sessions.update(
                session.id, field="customer_name", value=cleaned_message, next_step=IntakeStep.LOCATION
            )
        elif session.current_step is IntakeStep.LOCATION:
            session = self.sessions.update(
                session.id, field="location", value=cleaned_message, next_step=IntakeStep.PROJECT_TYPE
            )
        elif session.current_step is IntakeStep.PROJECT_TYPE:
            session = self.sessions.update(
                session.id, field="project_type", value=cleaned_message, next_step=IntakeStep.ESTIMATED_QUANTITY
            )
        elif session.current_step is IntakeStep.ESTIMATED_QUANTITY:
            session = self.sessions.update(
                session.id,
                field="estimated_quantity",
                value=cleaned_message,
                next_step=IntakeStep.REQUIREMENT_SUMMARY,
            )
        elif session.current_step is IntakeStep.REQUIREMENT_SUMMARY:
            session = self.sessions.update(
                session.id,
                field="requirement_summary",
                value=cleaned_message,
                next_step=IntakeStep.PREFERRED_CONTACT_TIME,
            )
        elif session.current_step is IntakeStep.PREFERRED_CONTACT_TIME:
            session = self.sessions.update(
                session.id,
                field="preferred_contact_time",
                value=None if cleaned_message.casefold() == "skip" else cleaned_message,
                next_step=IntakeStep.COMPLETED,
            )
            enquiry = self._create_enquiry(session)
            session = self.sessions.complete(session.id, enquiry.id)
            return IntakeReply(
                session_id=session.id,
                next_step=session.current_step,
                enquiry_id=enquiry.id,
                reply_text=(
                    "Thank you. Your requirement has been recorded for our sales team to review. "
                    "They will contact you; a quotation is not generated in this chat."
                ),
            )
        else:
            raise ValueError("Completed sessions cannot accept more messages")

        return self._reply(session, PROMPTS[session.current_step])

    def _reply(self, session: IntakeSession, reply_text: str) -> IntakeReply:
        return IntakeReply(session_id=session.id, next_step=session.current_step, reply_text=reply_text)

    def _create_enquiry(self, session: IntakeSession):
        if not all((session.customer_name, session.location, session.requirement_summary)):
            raise ValueError("Cannot create an enquiry without required intake details")
        return self.enquiries.create(
            EnquiryCreate(
                customer_name=session.customer_name,
                phone_number=session.contact_identifier,
                location=session.location,
                requirement_summary=session.requirement_summary,
                estimated_quantity=session.estimated_quantity,
                project_type=session.project_type,
                preferred_contact_time=session.preferred_contact_time,
                source=session.channel.value,
            )
        )

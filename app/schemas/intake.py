from pydantic import BaseModel, Field

from app.domain.intake import IntakeChannel, IntakeStep


class IntakeMessage(BaseModel):
    channel: IntakeChannel
    contact_identifier: str = Field(min_length=3, max_length=100)
    message_text: str = Field(min_length=1, max_length=1_000)


class IntakeReply(BaseModel):
    session_id: str
    next_step: IntakeStep
    reply_text: str
    enquiry_id: int | None = None

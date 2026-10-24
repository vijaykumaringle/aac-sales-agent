from fastapi import APIRouter, HTTPException

from app.schemas.intake import IntakeMessage, IntakeReply
from app.services.intake import IntakeService


router = APIRouter(prefix="/intake", tags=["intake"])
service = IntakeService()


@router.post("/messages", response_model=IntakeReply)
def receive_message(payload: IntakeMessage) -> IntakeReply:
    try:
        return service.receive_message(payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

# app/api/routes_ticket.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ticket_service import TicketService

router = APIRouter()
ticket_svc = TicketService()

class TicketRequest(BaseModel):
    session_id: str
    issue: str
    chat_history: list = None

class TicketResponse(BaseModel):
    ticket_id: str
    status: str

@router.post("/", response_model=TicketResponse)
async def create_ticket(req: TicketRequest):
    try:
        ticket_id = ticket_svc.create_ticket(issue=req.issue, session_id=req.session_id, chat_history=req.chat_history or [])
        return {"ticket_id": ticket_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

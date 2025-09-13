# app/api/routes_chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_pipeline import RAGPipeline
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter()
rag = RAGPipeline()  # singleton-ish for this process

class SimpleChatRequest(BaseModel):
    message: str
    session_id: str = None

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(req: SimpleChatRequest):
    try:
        reply, source_docs = rag.generate_response(req.message, session_id=req.session_id)
        return {"reply": reply, "sources": source_docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

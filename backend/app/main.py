# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_chat import router as chat_router
from app.api.routes_ticket import router as ticket_router
from app.utils.config import settings

app = FastAPI(title="AI Chatbot for INGRES")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN] if settings.FRONTEND_ORIGIN else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(ticket_router, prefix="/ticket", tags=["ticket"])

@app.get("/")
def health():
    return {"status": "ok", "service": "ai-chatbot-ingres backend"}

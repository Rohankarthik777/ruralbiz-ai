from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.auth import get_current_user
from app.ai_engine import generate_ai_chat_response

router = APIRouter(prefix="/api/chat", tags=["AI Advisory Chatbot"])

class ChatMessageRequest(BaseModel):
    message: str
    language: Optional[str] = "en"
    api_key: Optional[str] = None

@router.post("")
def chat_advisory(req: ChatMessageRequest):
    reply = generate_ai_chat_response(
        message=req.message,
        language=req.language or "en",
        api_key=req.api_key
    )
    return {"success": True, "reply": reply}

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatMessage(BaseModel):
    question: str
    pdf_name: str

@router.post("/ask")
async def chat_with_pdf(message: ChatMessage):
    return {
        "answer": "This is a placeholder response. LLM integration coming soon!",
        "context": "Placeholder context from PDF"
    }
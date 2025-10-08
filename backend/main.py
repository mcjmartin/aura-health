from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
from backend.chatbot import chat_with_aura  # import from your chatbot file

app = FastAPI(title="Aura Health API")

# Allow frontend requests (from your React dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

@app.post("/api/chat")
def chat_endpoint(msg: Message) -> Dict[str, Any]:
    """Send a message to Aura and get a response"""
    response = chat_with_aura(msg.message)
    return {"response": response}

@app.get("/")
def root():
    return {"status": "ok", "message": "Aura Health backend is running!"}

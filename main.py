"""FastAPI application — Serie A 2024/25 Chatbot."""
import os
import sys

# Aggiunge la directory backend al path così gli import locali funzionano
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from chatbot import Chatbot

app = FastAPI(title="Serie A 2024/25 Chatbot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

_chatbot = Chatbot()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return ChatResponse(response=_chatbot.respond(req.message))


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "season": "Serie A 2024/25"}


# Serve il frontend (deve essere montato dopo le route API)
_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="static")

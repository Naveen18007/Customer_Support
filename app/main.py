from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.auth_service import verify_user
from app.services.orchestrator import analyze_priority
from app.services.session_store import append_message

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Schemas --------
class VerifyRequest(BaseModel):
    email: str
    phone: str

class ChatRequest(BaseModel):
    message: str
    customer_id: str

# -------- Routes --------
@app.post("/verify-user")
def verify_user_endpoint(data: VerifyRequest):
    result = verify_user(data.email, data.phone)

    if not result["verified"]:
        raise HTTPException(status_code=401, detail="Account not found")

    return result

@app.post("/chat")
def chat_endpoint(data: ChatRequest):

    # Store user message in session
    append_message(
        customer_id=data.customer_id,
        role="user",
        content=data.message
    )

    priority = analyze_priority(
        customer_id=data.customer_id,
        message=data.message
    )

    bot_response = f"🧠 Sentiment Analysis Result:\nPriority: {priority}"

    # Store assistant response
    append_message(
        customer_id=data.customer_id,
        role="assistant",
        content=bot_response
    )

    return {"response": bot_response}

@app.get("/")
def health():
    return {"status": "ok"}

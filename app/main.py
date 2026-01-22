from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.auth_service import verify_user
app = FastAPI()

# CORS (already added)
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
        raise HTTPException(
            status_code=401,
            detail="Account not found"
        )
    return result

@app.post("/chat")
def chat_endpoint(data: ChatRequest):
    # TEMP response (we’ll replace with FAQ Agent)
    return {
        "response": f"Received your message: '{data.message}'"
    }

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional
import time

from app.services.auth_service import verify_user
from app.services.session_store import append_message, get_session_stats
from app.graph.support_graph import support_graph
from app.utils.logger import logger
from app.utils.rate_limiter import check_rate_limit, get_rate_limit_status

app = FastAPI(title="Customer Support API", version="2.0.0")

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
    email: str = Field(..., min_length=1, max_length=255, description="User email address")
    phone: str = Field(..., min_length=1, max_length=20, description="User phone number")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower().strip()

class ChatRequest(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=50, description="Customer ID")
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v.strip()) > 1000:
            raise ValueError('Message too long (max 1000 characters)')
        return v.strip()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


@app.post("/verify-user")
def verify_user_endpoint(data: VerifyRequest):
    """Verify user credentials"""
    try:
        logger.info(f"Verification attempt for email: {data.email}")
        result = verify_user(data.email, data.phone)

        if not result["verified"]:
            logger.warning(f"Verification failed for email: {data.email}")
            raise HTTPException(status_code=401, detail="Account not found")

        logger.info(f"Verification successful for customer: {result.get('customer', {}).get('customer_id')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Verification service error")


@app.post("/chat")
def chat_endpoint(data: ChatRequest):
    """Process chat message and return response"""
    start_time = time.time()
    
    try:
        # Check rate limit
        is_allowed, rate_limit_msg = check_rate_limit(data.customer_id)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for customer {data.customer_id}")
            raise HTTPException(status_code=429, detail=rate_limit_msg)
        
        logger.info(f"Chat request from customer {data.customer_id}: {data.message[:100]}")
        
        # Store user message FIRST
        append_message(
            customer_id=data.customer_id,
            role="user",
            content=data.message
        )

        # Run LangGraph
        try:
            final_state = support_graph.invoke({
                "customer_id": data.customer_id,
                "message": data.message
            })
            bot_response = final_state.get("response", "I apologize, but I couldn't process your request.")
        except Exception as e:
            logger.error(f"LangGraph execution error: {e}", exc_info=True)
            bot_response = (
                "I'm experiencing technical difficulties. "
                "Your message has been logged and our team will assist you shortly."
            )

        # Store assistant response
        append_message(
            customer_id=data.customer_id,
            role="assistant",
            content=bot_response
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Chat response generated in {processing_time:.2f}s for customer {data.customer_id}")

        return {
            "response": bot_response,
            "processing_time_ms": round(processing_time * 1000, 2)
        }
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Chat processing error")


@app.get("/")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "customer_support",
        "version": "2.0.0"
    }


@app.get("/health/detailed")
def detailed_health():
    """Detailed health check with session statistics"""
    try:
        stats = get_session_stats()
        return {
            "status": "ok",
            "service": "customer_support",
            "version": "2.0.0",
            "sessions": stats
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

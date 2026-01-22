from fastapi import FastAPI
from app.services.supabase_test_service import test_faq_connection

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/test-supabase")
def test_supabase():
    data = test_faq_connection()
    return {
        "message": "Supabase connection successful",
        "data": data
    }

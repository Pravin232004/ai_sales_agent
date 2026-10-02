from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.sales_agent import run_sales_agent


app = FastAPI(
    title="AI Sales Workforce Agent",
    description="Backend API for the AI Sales Workforce Agent",
    version="1.0.0"
)

# Request model

class ChatRequest(BaseModel):
    message: str

# Root endpoint

@app.get("/")
def root():
    return {
        "message": "AI Sales Workforce Agent API is running"
    }

# Health check

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

# Chat endpoint

@app.post("/chat")
def chat(request: ChatRequest):
    """
    Send a customer message to the AI Sales Agent.
    """

    response = run_sales_agent(request.message)

    return {
        "message": request.message,
        "response": response
    }
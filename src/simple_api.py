"""
Lightweight API for Zoho SalesIQ webhook - No vector DB required
"""
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import uvicorn

app = FastAPI(title="AceBuddy Chatbot API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AceBuddy Chatbot API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Simple chat endpoint"""
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are AceBuddy, a helpful IT support assistant for ACE Cloud Hosting. Help users with QuickBooks, RDP, email, and server issues."},
                {"role": "user", "content": request.message}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return ChatResponse(
            response=response.choices[0].message.content,
            conversation_id=request.conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/salesiq")
async def salesiq_webhook(request: Request):
    """Zoho SalesIQ webhook endpoint"""
    try:
        data = await request.json()
        
        # Extract message from SalesIQ webhook
        message = data.get("message", {}).get("text", "")
        visitor_id = data.get("visitor", {}).get("id", "unknown")
        
        if not message:
            return {"response": "Hello! How can I help you today?"}
        
        # Get AI response
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are AceBuddy, a helpful IT support assistant for ACE Cloud Hosting. Provide concise, helpful answers about QuickBooks, RDP connections, email setup, and server issues."},
                {"role": "user", "content": message}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        return {
            "response": response.choices[0].message.content,
            "visitor_id": visitor_id
        }
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return {
            "response": "I'm having trouble processing your request. Please try again or contact support."
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

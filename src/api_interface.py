from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from ai_enhanced_bot import AICustomerServiceBot

app = FastAPI()

class Query(BaseModel):
    text: str
    user_id: str
    context: Optional[Dict] = None

class Response(BaseModel):
    response: str
    suggestions: List[str]
    status: str
    confidence: float
    requires_human: bool

@app.post("/chat")
async def chat_endpoint(query: Query):
    company_data = {
        "name": "Your Company",
        "support_email": "support@example.com",
        "phone": "1-800-SUPPORT",
        "business_hours": "24/7"
    }
    
    try:
        bot = AICustomerServiceBot(company_data)
        response = await bot.handle_complex_query(
            query.text,
            query.user_id,
            query.context
        )
        return Response(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
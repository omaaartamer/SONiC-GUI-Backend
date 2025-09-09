from fastapi import APIRouter, Body
from app.services.Chatbot_Services import agent
import asyncio

router = APIRouter()
@router.post("/")
async def chatbot(request: str = Body(...)):
    ai_response = await asyncio.to_thread(agent.run, request)
    return {"ai_response": ai_response}
    # return await chatbot_service(request)
import os
from fastapi import WebSocket
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from app.services.Vlans_Services import fetch_vlans
# from app.services.SSH_Services import ssh_sessions

load_dotenv()


@tool(description = "get the vlans")
async def getVlans(temp : str):
    return await fetch_vlans()

llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=os.getenv("GOOGLE_API_KEY"),
        transport='rest'
    )
async def chatbot_service(websocket: WebSocket, username: str):
    await websocket.accept()
    print("i am here")
    try:
        while True:
            # Receive a message from frontend
            data = await websocket.receive_text()
            print("after send")
            # Pass to LLM / tools
            response = await getVlans.ainvoke(data)

            # Send back to frontend
            await websocket.send_text(str(response))
    except Exception as e:
        await websocket.close()




    


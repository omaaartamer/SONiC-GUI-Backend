import os
from fastapi import Websocket
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
async def chatbot_service(websocket : Websocket, username : str, temp : str):
    await websocket.accept()
    # conn = ssh_sessions.get(username)#if using cli

    response = await getVlans.ainvoke(temp)
    print("answer:\n", response)
    return response



    


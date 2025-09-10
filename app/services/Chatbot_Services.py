import os
import re
from fastapi import WebSocket
from dotenv import load_dotenv
from spellchecker import SpellChecker
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_core.tools import tool
# from app.services.Vlans_Services import fetch_vlans
from app.embeddings import db
# from app.services.SSH_Services import ssh_sessions

load_dotenv()
spell = SpellChecker()
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# @tool(description = "get the vlans")
# async def getVlans(temp : str):
#     return await fetch_vlans()

llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=os.getenv("GOOGLE_API_KEY"),
        transport='rest'
    )


def correct_spelling(text: str) -> str:
    words = text.split()
    corrected_sentence = []
    for word in words:
        correction = spell.correction(word)
        corrected_sentence.append(correction if correction else word)
    return " ".join(corrected_sentence)

def preprocess_input(text : str):
    text = re.sub(r"\s+", " ", text).strip()
    # text = correct_spelling(text)
    text = text.lower()
    return text 

async def chatbot_service(websocket: WebSocket, username: str):

    await websocket.accept()
    try:
        while True:

            input = await websocket.receive_text()
            clean_input = preprocess_input(input)
            results = db.similarity_search(clean_input, k = 3)
            context = "\n\n".join([doc.page_content for doc in results])
            final_prompt = f"""
                You are a helpful assistant. Use the following documentation of Sonic Switch context to answer the question.

                Context:
                {context}

                Question:
                {clean_input}

                Answer:
                """
            response = llm.invoke(final_prompt)
            await websocket.send_text(str(response))

    except Exception:
        await websocket.close()




    


import os
import re
from fastapi import WebSocket
from dotenv import load_dotenv
from spellchecker import SpellChecker   # ✅ enable spellchecker
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from app.embeddings import db   # your vector DB wrapper

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    transport="rest",
)

# ✅ Initialize spell checker
spell = SpellChecker()

# ✅ Lazy SONiC vocabulary loader
_sonic_vocab_loaded = False
def load_sonic_vocab():
    global _sonic_vocab_loaded
    if _sonic_vocab_loaded:
        return

    try:
        sonic_vocab = set()
        sample_docs = db.similarity_search("sonic", k=20)  # smaller for speed
        for doc in sample_docs:
            if not getattr(doc, "page_content", None):
                continue
            for word in doc.page_content.split():
                sonic_vocab.add(word.lower())

        if sonic_vocab:
            spell.word_frequency.load_words(list(sonic_vocab))
            print(f"✅ Loaded {len(sonic_vocab)} SONiC-specific words into spellchecker")

        _sonic_vocab_loaded = True
    except Exception as e:
        print("⚠️ Could not build SONiC vocabulary:", e)


# ✅ Define critical SONiC terms
SONIC_TERMS = {"vlans", "vlan", "interface", "interfaces", "port", "ports", "sonic", "routing"}

# ✅ Add them with high frequency so spellchecker prefers them
for term in SONIC_TERMS:
    spell.word_frequency.add(term, 10000)  # artificially boost frequency


def correct_spelling(text: str) -> str:
    words = text.split()
    corrected_sentence = []
    for word in words:
        lw = word.lower()

        # ✅ Always trust SONiC terms
        if lw in SONIC_TERMS:
            corrected_sentence.append(word)
            continue

        # ✅ If it's close to a SONiC term, force it
        candidates = spell.candidates(word)
        sonic_candidates = [c for c in candidates if c in SONIC_TERMS]
        if sonic_candidates:
            corrected_sentence.append(sonic_candidates[0])
            continue

        # ✅ Otherwise, normal correction
        correction = spell.correction(word)
        corrected_sentence.append(correction if correction else word)

    return " ".join(corrected_sentence)



# ✅ Preprocessing: clean + lowercase + correct spelling
def preprocess_input(text: str):
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = correct_spelling(text)
    return text


# ✅ WebSocket chatbot service
async def chatbot_service(websocket: WebSocket, username: str):
    await websocket.accept()

    
    # 🧠 Session memory (all exchanges until disconnect)
    conversation_history = []

    try:
        while True:
            user_input = await websocket.receive_text()

            # ✅ Ensure SONiC vocab is loaded (only once)
            load_sonic_vocab()

            clean_input = preprocess_input(user_input)

             # Save user input
            conversation_history.append({"role": "user", "content": clean_input})

            # Search in your vector DB
            results = db.similarity_search(clean_input, k=3)
            context = "\n\n".join([doc.page_content for doc in results])

            # Include full memory
            memory_context = "\n".join(
                [f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history]
            )

            final_prompt = f"""
                You are a helpful assistant. Use the following SONiC Switch documentation to answer the question.

                Context:
                {context}

                Conversation so far:
                {memory_context}

                Question:
                {clean_input}

                Answer:
                """

            response = llm.invoke(final_prompt)

             # Save assistant reply
            conversation_history.append({"role": "assistant", "content": response.content})
            
            await websocket.send_text(response.content)

    except Exception as e:
        print("⚠️ Chatbot crashed with error:", e)
        await websocket.close()

import os
import re
import asyncio
from fastapi import WebSocket
from dotenv import load_dotenv
from spellchecker import SpellChecker
from langchain_google_genai import ChatGoogleGenerativeAI
from app.embeddings import db
from langchain.agents import Tool
from app.services.SSH_Services import run_command
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    transport="rest",
)

spell = SpellChecker()

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



def preprocess_input(text: str):
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = correct_spelling(text)
    return text



prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant with access to tools.
If the user asks about a command or has an unclear query, use `search_sonic` to look it up. if he asks for a command send it without any additions.
You must NEVER write `OBSERVATION:` yourself.
Only the system (outside you) will fill that in.
If you decide on an ACTION, stop your response right after writing `INPUT:`.
Do not write OBSERVATION or FINAL yet.
                                                                             
Available tools:
- search_sonic: Search SONiC documentation for relevant info.

Follow this format:
THOUGHT: your reasoning
ACTION: the tool to use (if needed)
INPUT: the input for the tool
OBSERVATION: (this will be filled in later by the system, do NOT write this yourself)
FINAL: the final answer to the user

User question: {input}""")
chain = prompt | llm | StrOutputParser()

def search_sonic(query: str) -> str:
    """
    Search SONiC documentation for relevant info.
    Input: user query (string).
    Output: top matching result as a string.
    """
    results = db.similarity_search(query, k = 3)
    context = "\n\n".join([doc.page_content for doc in results])
    print("context in search docs: \n" ,context)
    return context
# Sync wrapper for LangChain
def make_run_command_tool(conn, loop):
    def sync_run(command: str) -> str:
        try:
            future = asyncio.run_coroutine_threadsafe(
                run_command(conn, command), loop
            )
            return future.result()
        except Exception as e:
            return f"Error executing command: {e}"
    return sync_run
tools = [
        # Tool(
            # name="execute_command",
            # func=run_with_conn,
            # description="Run SONiC CLI commands via SSH. Input should be a valid SONiC CLI command."
            # ),
        Tool(
        name="search_sonic",
        func=search_sonic,
        description="Search the SONiC documentation or database for the best matching command when the query is unclear."
        )
    ]
tool_map = {t.name: t.func for t in tools}

async def run_agent(user_input: str, max_steps: int = 5):
    context = f"User asked: {user_input}"
    for step in range(max_steps):
        response = await chain.ainvoke({"input": context})
        print(f"\n=== Step {step+1} ===\n{response}\n")

        if "FINAL:" in response:
            return response.split("FINAL:", 1)[1].strip()

        if "ACTION:" in response and "INPUT:" in response:
            lines = response.splitlines()
            action_line = next((line for line in lines if line.startswith("ACTION:")), None)
            input_line = next((line for line in lines if line.startswith("INPUT:")), None)

            tool_name = action_line.split(":", 1)[1].strip() if action_line else None
            tool_input = input_line.split(":", 1)[1].strip() if input_line else None

            if tool_name in tool_map:
                print(f"Invoking tool: {tool_name} with input: {tool_input}")

                result = tool_map[tool_name](tool_input)
                context += f"\nACTION: {tool_name}\nINPUT: {tool_input}\nOBSERVATION: {result}"
            else:
                context += f"\nOBSERVATION: Unknown tool {tool_name}"
        else:
            return f"Agent stopped early: {response}"

    return "Reached max steps without final answer."


async def chatbot_service(websocket: WebSocket, username: str):
    await websocket.accept()
    # conn = ssh_sessions.get(username)
    # if not conn:
    #     await websocket.send_json({"No active SSH session"})
    #     await websocket.close()
    #     return
    
    # loop = asyncio.get_running_loop()             # current FastAPI event loop
    # run_with_conn = make_run_command_tool(conn, loop)   # bind conn to tool
    
    conversation_history = []

    try:
        while True:
            user_input = await websocket.receive_text()

            load_sonic_vocab()

            clean_input = preprocess_input(user_input)

            conversation_history.append({"role": "user", "content": clean_input})

            # memory_context = "\n".join(
            #     [f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history]
            # )

            # final_prompt = f"""
            #     You are a helpful assistant. Use the following SONiC Switch documentation to answer the question.

            #     Context:
            #     {context}

            #     Conversation so far:
            #     {memory_context}

            #     Question:
            #     {clean_input}

            #     Answer:
            #     """

            # response = llm.invoke(final_prompt)
            response = await run_agent(clean_input)

            conversation_history.append({"role": "assistant", "content": response})
            
            await websocket.send_text(response)

    except Exception as e:
        print("⚠️ Chatbot crashed with error:", e)
        await websocket.close()

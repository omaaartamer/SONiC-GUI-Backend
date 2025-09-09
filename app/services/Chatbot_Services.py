import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, Tool
from app.services.Vlans_Services import fetch_vlans

CA_BUNDLE_PATH = r"E:\Orange\Fortinet_CA_SSL.pem"
os.environ["REQUESTS_CA_BUNDLE"] = CA_BUNDLE_PATH
os.environ["SSL_CERT_FILE"] = CA_BUNDLE_PATH

load_dotenv()

# Wrap async fetch_vlans for sync tool usage
def get_vlans_tool_wrapper(_input: str) -> list:
    return asyncio.run(fetch_vlans())

tools = [
    Tool(
        name="GetVlans",
        func=get_vlans_tool_wrapper,
        description="Fetch VLANs from the network"
    )
]


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    transport='rest'
)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS, 
    verbose=True
)




# @tool(description = "get the vlans")
# async def getVlans():
#     # return ["VLAN10", "VLAN20", "VLAN30"]
#     return await fetch_vlans()

# tools = [getVlans]

# async def chatbot_service(request: str = Body(...)):
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash-lite",
#         api_key=os.getenv("GOOGLE_API_KEY"),
#         transport='rest' 
#     )
#     llm_with_tools = llm.bind_tools(tools)
#     ai_response =  await llm_with_tools.ainvoke(request)
#     return {"response": ai_response}
    


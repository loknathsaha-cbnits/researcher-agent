from graph.state import ResearchState
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from mcp.client.stdio import stdio_client
# from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession
from mcp import StdioServerParameters
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
server_path = os.path.join(root_dir, "server", "vault.py")

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL")
API_KEY=os.getenv("API_KEY")
BASE_URL=os.getenv("BASE_URL")

#how to connect to mcp server:
search_params = StdioServerParameters(
    command="uv",
    args=["run", server_path],
)

llm = ChatOpenAI(
    model = LLM_MODEL,
    api_key = API_KEY,
    base_url = BASE_URL,
    temperature= 0.1,
)

async def agent_node(state: ResearchState):
    question = state["question"]
    search_results = state["search_results"]
    messages = state["messages"]

    messages = [
        {
            "role": "system",
            "content": "You are a research assistant. Answer the question using the search results. IMPORTANT: You must always save your final summary to the vault using the save_research_tool."
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nSearch Results:\n{search_results}"
        }
    ]

    async with stdio_client(search_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await load_mcp_tools(session)
            llm_with_tools = llm.bind_tools(mcp_tools)
    
            response = await llm_with_tools.ainvoke(messages)

            # if response.tool_calls:
            #     for tool_call in response.tool_calls:
            #         print(f"DEBUG: Node is now calling tool: {tool_call['name']}")
            #         await session.call_tool(tool_call["name"], tool_call["args" ])

            while response.tool_calls:
                messages.append(response)

                for tool_call in response.tool_calls:
                    result = await session.call_tool(tool_call["name"], tool_call["args"])

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": str(result) 
                    })

                response = await llm_with_tools.ainvoke(messages)
            
            return {
                "messages": [response],
                "answer": response.content if response.content else "Research processed and saved."
            }
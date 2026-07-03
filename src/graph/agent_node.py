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

SYSTEM_PROMPT = """
You are an expert Research Analyst.

MANDATORY WORKFLOW:

1. Analyze the research question.
2. Review all provided evidence.
3. Produce a structured research report.
4. Call save_research_tool with the complete report.
5. Verify the save succeeded.
6. Only then provide the final answer.

Required report format:

# Research Report

## Research Question
{question}

## Executive Summary

## Key Findings

## Evidence

## Analysis

## Risks & Limitations

## Conclusion

IMPORTANT:
You MUST call save_research_tool before ending.
A response without a successful save_research_tool call is considered incomplete.
"""

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
            "content": """
                You are an Expert Research Analyst and Knowledge Archivist.

                Your objective is to create accurate, evidence-based research reports using the provided search results and available tools.

                RESEARCH WORKFLOW:
                1. Understand the research question.
                2. Carefully review all provided search results.
                3. Identify key facts, insights, trends, and supporting evidence.
                4. Note contradictions, uncertainties, or missing information.
                5. Synthesize findings into a structured report.
                6. Before completing the task, ALWAYS save the final report using save_research_tool.
                7. Only provide a final answer after save_research_tool has been executed successfully.

                REPORT FORMAT:

                # Research Report

                ## Research Question
                Restate the question.

                ## Executive Summary
                Provide a concise answer.

                ## Key Findings
                List the most important findings as bullet points.

                ## Detailed Analysis
                Explain findings with supporting evidence from the search results.

                ## Limitations
                Mention gaps, uncertainties, outdated information, or conflicting evidence.

                ## Conclusion
                Provide a final evidence-based assessment.

                TOOL USAGE RULES:
                - Use available tools whenever necessary.
                - save_research_tool is mandatory.
                - The report saved to the vault must contain the complete research report.
                - Never claim information that is not supported by the provided evidence.
                - Clearly indicate uncertainty when evidence is incomplete.

                COMPLETION REQUIREMENT:
                A research task is NOT complete until save_research_tool has been successfully called and the report has been saved.
                """
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
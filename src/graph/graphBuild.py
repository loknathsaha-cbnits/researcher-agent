from src.graph.agent_node import agent_node
from src.graph.search_node import search_node
from langgraph.graph import END, StateGraph
from src.graph.state import ResearchState
from dotenv import load_dotenv

load_dotenv()

builder = StateGraph(ResearchState)

builder.add_node("search_node", search_node)
builder.add_node("agent_node", agent_node)

builder.set_entry_point("search_node")
builder.add_edge("search_node", "agent_node")
builder.add_edge("agent_node", END)

def compiler():
    graphRun = builder.compile()
    return graphRun
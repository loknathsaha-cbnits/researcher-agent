from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    question: str
    search_results: str
    answer: str
    messages: Annotated[list, add_messages]

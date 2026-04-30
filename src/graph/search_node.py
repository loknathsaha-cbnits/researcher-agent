from graph.state import ResearchState
# from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_tavily import TavilySearch

tavily = TavilySearch(max_results=3, topic="general")

def search_node(state: ResearchState):
    question = state['question']
    results = tavily.invoke(question)
    response = results["results"]
    content = "\n\n".join([r["content"] for r in response])
    return { "search_results": content }
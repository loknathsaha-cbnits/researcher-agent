import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.graph.graphBuild import compiler

async def main():
    graphRun = compiler()
    config = {"configurable": {"thread_id": "user-1"}}
    
    while True:
        question = input("You: ")
        
        try:
            result = await graphRun.ainvoke({"question": question}, config=config)
            print(f"\n--- Final Answer ---\n{result['answer']}")
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
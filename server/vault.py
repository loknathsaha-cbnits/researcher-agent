import sys

try:
    from fastmcp import FastMCP
except ImportError:
    print("ERROR: fastmcp not found. Run 'pip install fastmcp'", file=sys.stderr)
    sys.exit(1)

#creating mcp server
mcp = FastMCP("LocalResearchVault")

@mcp.tool
def save_research_tool(topic: str, content: str):
    """ Save research results into local .md file(vault) """
    print(f"DEBUG: MCP Server received request for {topic}", file=sys.stderr)
    filename = f"{topic.replace(" ", "_").lower()}.md"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully saved to {filename}"
    except Exception as e:
        return f"Error saving file: {str(e)}"

if __name__=='__main__':
    mcp.run()
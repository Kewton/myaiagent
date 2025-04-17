from app.main import mcp


if __name__ == "__main__":
    print("Starting weather MCP server...")
    mcp.run(transport='stdio')

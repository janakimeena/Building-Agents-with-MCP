# Create new project
uv init mcp-server-demo
cd mcp-server-demo
# Add MCP with CLI tools
uv add "mcp[cli]"

uv run mcp install server.py

uv run mcp dev server_sticky.py

**Add in Claude Desktop Config**
"ai-sticky-notes": {
      "command": "uv",
      "args": ["run", "/media/janaki/VIT Chennai/Building Agents with MCP/mcp-server-demo/server_sticky.py"]
    }

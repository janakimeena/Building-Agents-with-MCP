**Create new project** <br>
uv init mcp-server-demo <br>
cd mcp-server-demo <br><br>
**Add MCP with CLI tools** <br>
uv add "mcp[cli]" <br>

uv run mcp install server.py <br>

uv run mcp dev server_sticky.py <br>

**Add in Claude Desktop Config**<br>
"ai-sticky-notes": {<br>
      "command": "uv",<br>
      "args": ["run", "/media/janaki/VIT Chennai/Building Agents with MCP/mcp-server-demo/server_sticky.py"]<br>
    }<br>

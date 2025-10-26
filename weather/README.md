install uv<br>

#Mac/Linux<br>
curl -LsSf https://astral.sh/uv/install.sh | sh<br>

#Windows<br>
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

## Mac/Linux<br>
# Create a new directory for our project<br>
uv init weather<br>
cd weather<br>

# Create virtual environment and activate it<br>
uv venv<br>
source .venv/bin/activate<br>

# Install dependencies<br>
uv add "mcp[cli]" httpx<br>

# Create our server file<br>
touch weather.py<br>

##Windows<br>
# Create a new directory for our project<br>
uv init weather<br>
cd weather<br>

# Create virtual environment and activate it<br>
uv venv<br>
source .venv/bin/activate<br>

# Install dependencies<br>
uv add "mcp[cli]" httpx<br>

Copy

code ~/Library/Application\ Support/Claude/claude_desktop_config.json

You’ll then add your servers in the mcpServers key. The MCP UI elements will only show up in Claude for Desktop if at least one server is properly configured.In this case, we’ll add our single weather server like so:
Copy

{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT/FOLDER/weather",
        "run",
        "weather.py"
      ]
    }
  }
}

You may need to put the full path to the uv executable in the command field. You can get this by running which uv on macOS/Linux or where uv on Windows.


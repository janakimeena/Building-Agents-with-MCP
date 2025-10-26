## Building Client<br>

# Create project directory<br>
uv init mcp-client<br>
cd mcp-client<br>

# Create virtual environment<br>
uv venv<br>

# Activate virtual environment<br>
source .venv/bin/activate<br>

# Install required packages<br>
uv add mcp anthropic python-dotenv<br>

# Remove boilerplate files<br>
rm main.py<br>

# Create our main file<br>
touch client.py<br>

## Windows <br>

# Create project directory<br>
uv init mcp-client<br>
cd mcp-client<br>

# Create virtual environment<br>
uv venv<br>

# Activate virtual environment<br>
.venv\Scripts\activate<br>

# Install required packages<br>
uv add mcp anthropic python-dotenv<br>

# Remove boilerplate files<br>
del main.py<br>

# Create our main file<br>
new-item client.py<br>


## Get Anothropic key <br>
https://console.anthropic.com/settings/keys <br>

echo "ANTHROPIC_API_KEY=YOUR ANTHROPIC Key" > .env <br>

echo ".env" >> .gitignore <br>

uv run client.py path/to/server.py <br>


from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

app = FastAPI(title="Image Rotation MCP Tester")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML interface
HTML_CONTENT = '''
<!DOCTYPE html>
<html>
<head>
    <title>Image Rotation MCP Tester</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
        }
        .form-group {
            margin: 20px 0;
        }
        label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }
        input[type="file"],
        input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        .images {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        .image-box {
            text-align: center;
        }
        img {
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .success {
            color: #28a745;
            font-weight: bold;
        }
        .error {
            color: #dc3545;
            font-weight: bold;
        }
        .loading {
            text-align: center;
            color: #667eea;
            display: none;
        }
        small {
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Image Rotation MCP Tester</h1>
        <p style="text-align: center; color: #666;">Test your MCP server with a beautiful interface</p>
        
        <form id="rotateForm">
            <div class="form-group">
                <label>📸 Select Image:</label>
                <input type="file" id="imageFile" accept="image/*" required>
            </div>
            
            <div class="form-group">
                <label>🔄 Rotation Angle (degrees):</label>
                <input type="number" id="angle" value="45" step="1">
                <small>Positive = counterclockwise, Negative = clockwise</small>
            </div>
            
            <div class="form-group">
                <label>📏 Scale Factor:</label>
                <input type="number" id="scale" value="1.0" step="0.1" min="0.1" max="3.0">
                <small>1.0 = original size, > 1.0 = larger, < 1.0 = smaller</small>
            </div>
            
            <button type="submit">✨ Rotate Image</button>
        </form>
        
        <div class="loading" id="loading">
            <p>⏳ Processing image...</p>
        </div>
        
        <div id="result" class="result">
            <div id="message"></div>
            <div class="images" id="imageContainer"></div>
        </div>
    </div>

    <script>
        document.getElementById('rotateForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const fileInput = document.getElementById('imageFile');
            const angle = document.getElementById('angle').value;
            const scale = document.getElementById('scale').value;
            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('result');
            
            if (!fileInput.files[0]) {
                alert('Please select an image');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('angle', angle);
            formData.append('scale', scale);
            
            loading.style.display = 'block';
            resultDiv.style.display = 'none';
            
            try {
                const response = await fetch('/api/rotate', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                loading.style.display = 'none';
                resultDiv.style.display = 'block';
                
                const messageDiv = document.getElementById('message');
                const imageContainer = document.getElementById('imageContainer');
                
                if (data.success) {
                    messageDiv.innerHTML = `<p class="success">✓ ${data.message}</p>`;
                    imageContainer.innerHTML = `
                        <div class="image-box">
                            <h4>📥 Original Image</h4>
                            <img src="data:image/png;base64,${data.original_image}" alt="Original">
                        </div>
                        <div class="image-box">
                            <h4>📤 Rotated Image</h4>
                            <img src="data:image/png;base64,${data.rotated_image}" alt="Rotated">
                        </div>
                    `;
                } else {
                    messageDiv.innerHTML = `<p class="error">✗ Error: ${data.error}</p>`;
                    imageContainer.innerHTML = '';
                }
            } catch (error) {
                loading.style.display = 'none';
                resultDiv.style.display = 'block';
                document.getElementById('message').innerHTML = 
                    `<p class="error">✗ Request failed: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
'''

async def call_mcp_server(image_base64: str, angle: float, scale: float) -> str:
    """Call the MCP server to rotate the image"""
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "rotate_image",
                {
                    "image_data": image_base64,
                    "angle": angle,
                    "scale": scale
                }
            )
            
            if hasattr(result, 'content'):
                content = result.content
            else:
                content = result
            
            for item in content:
                if hasattr(item, 'text'):
                    text = item.text
                    if text.startswith('data:image/png;base64,'):
                        return text.split(',')[1]
            
            raise ValueError("No image returned from MCP server")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the HTML interface"""
    return HTML_CONTENT

@app.post("/api/rotate")
async def rotate_image(
    file: UploadFile = File(...),
    angle: float = Form(0),
    scale: float = Form(1.0)
):
    """Handle image rotation request"""
    try:
        # Read and encode image
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Call MCP server
        rotated_base64 = await call_mcp_server(image_base64, angle, scale)
        
        return JSONResponse({
            'success': True,
            'message': f'Image rotated by {angle}° with scale {scale}',
            'original_image': image_base64,
            'rotated_image': rotated_base64
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "MCP Image Rotation Tester is running"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server...")
    print("📍 Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)

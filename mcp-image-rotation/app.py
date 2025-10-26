from flask import Flask, request, jsonify, render_template_string
import base64
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Image Rotation MCP Tester</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .container {
            border: 2px solid #ccc;
            padding: 20px;
            border-radius: 10px;
        }
        input, button {
            margin: 10px 0;
            padding: 10px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            padding: 10px 20px;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f0f0f0;
            border-radius: 5px;
        }
        img {
            max-width: 100%;
            margin-top: 10px;
        }
        .error {
            color: red;
        }
        .success {
            color: green;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Image Rotation MCP Server Tester</h1>
        <form id="rotateForm" enctype="multipart/form-data">
            <div>
                <label>Select Image:</label><br>
                <input type="file" id="imageFile" accept="image/*" required>
            </div>
            <div>
                <label>Rotation Angle (degrees):</label><br>
                <input type="number" id="angle" value="45" step="1">
                <small>Positive = counterclockwise, Negative = clockwise</small>
            </div>
            <div>
                <label>Scale:</label><br>
                <input type="number" id="scale" value="1.0" step="0.1" min="0.1">
            </div>
            <button type="submit">Rotate Image</button>
        </form>
        
        <div id="result" class="result" style="display:none;">
            <h3>Result:</h3>
            <div id="message"></div>
            <div id="imageContainer"></div>
        </div>
    </div>

    <script>
        document.getElementById('rotateForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const fileInput = document.getElementById('imageFile');
            const angle = document.getElementById('angle').value;
            const scale = document.getElementById('scale').value;
            
            if (!fileInput.files[0]) {
                alert('Please select an image');
                return;
            }
            
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            formData.append('angle', angle);
            formData.append('scale', scale);
            
            try {
                const response = await fetch('/rotate', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                const resultDiv = document.getElementById('result');
                const messageDiv = document.getElementById('message');
                const imageContainer = document.getElementById('imageContainer');
                
                resultDiv.style.display = 'block';
                
                if (data.success) {
                    messageDiv.innerHTML = `<p class="success">✓ ${data.message}</p>`;
                    imageContainer.innerHTML = `
                        <h4>Original Image:</h4>
                        <img src="data:image/png;base64,${data.original_image}" alt="Original">
                        <h4>Rotated Image:</h4>
                        <img src="data:image/png;base64,${data.rotated_image}" alt="Rotated">
                    `;
                } else {
                    messageDiv.innerHTML = `<p class="error">✗ Error: ${data.error}</p>`;
                    imageContainer.innerHTML = '';
                }
            } catch (error) {
                document.getElementById('result').style.display = 'block';
                document.getElementById('message').innerHTML = 
                    `<p class="error">✗ Request failed: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
'''

async def call_mcp_server(image_base64, angle, scale):
    """Call the MCP server to rotate the image"""
    server_params = StdioServerParameters(
        command="python3",
        args=["server.py"]  # Adjust path if needed
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "rotate_image",
                {
                    "image_data": image_base64,
                    "angle": float(angle),
                    "scale": float(scale)
                }
            )
            
            # Extract the rotated image from result
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

@app.route('/')
def index():
    """Serve the HTML interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/rotate', methods=['POST'])
def rotate_image():
    """Handle image rotation request"""
    try:
        # Get uploaded file
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        file = request.files['image']
        angle = request.form.get('angle', 0)
        scale = request.form.get('scale', 1.0)
        
        # Read and encode image
        image_bytes = file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Call MCP server
        rotated_base64 = asyncio.run(call_mcp_server(image_base64, angle, scale))
        
        return jsonify({
            'success': True,
            'message': f'Image rotated by {angle}° with scale {scale}',
            'original_image': image_base64,
            'rotated_image': rotated_base64
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'MCP Image Rotation Tester is running'})

if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    print("📍 Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)

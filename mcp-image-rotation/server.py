import asyncio
import base64
import cv2
import numpy as np
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Create server instance
app = Server("image-rotation-server")

def rotate_image(image_data, angle, scale=1.0):
    """Rotate an image using OpenCV"""
    try:
        # Decode base64 image
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")
        
        # Get image dimensions
        height, width = img.shape[:2]
        center = (width // 2, height // 2)
        
        # Get rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
        
        # Perform rotation
        rotated = cv2.warpAffine(img, rotation_matrix, (width, height))
        
        # Encode back to base64
        _, buffer = cv2.imencode('.png', rotated)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Rotation failed: {str(e)}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="rotate_image",
            description="Rotate an image by a specified angle using OpenCV",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "Base64 encoded image data"
                    },
                    "angle": {
                        "type": "number",
                        "description": "Rotation angle in degrees (positive=counterclockwise, negative=clockwise)"
                    },
                    "scale": {
                        "type": "number",
                        "description": "Scaling factor (default: 1.0)",
                        "default": 1.0
                    }
                },
                "required": ["image_data", "angle"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    if name == "rotate_image":
        try:
            image_data = arguments["image_data"]
            angle = arguments["angle"]
            scale = arguments.get("scale", 1.0)
            
            rotated_image = rotatedef rotate_image(image_data, angle, scale=1.0):
    """Rotate an image using OpenCV"""
    try:
        # Decode base64 image
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")
        
        # Get image dimensions
        height, width = img.shape[:2]
        center = (width // 2, height // 2)
        
        # Get rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
        
        # Perform rotation
        rotated = cv2.warpAffine(img, rotation_matrix, (width, height))
        
        # Encode back to base64
        _, buffer = cv2.imencode('.png', rotated)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Rotation failed: {str(e)}")
_image(image_data, angle, scale)
            
            return [
                TextContent(
                    type="text",
                    text=f"Image successfully rotated by {angle} degrees (scale: {scale})"
                ),
                TextContent(
                    type="text",
                    text=f"data:image/png;base64,{rotated_image}"
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error rotating image: {str(e)}"
                )
            ]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

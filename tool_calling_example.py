import anthropic
import requests
import json

# Step 1: You must manually define the tool schema
tools = [{
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name"}
        },
        "required": ["location"]
    }
}]

# Step 2: You must manually write the function that calls external API
def get_weather(location):
    """YOU have to write this! Claude doesn't do this."""
    try:
        # YOU must: Find weather API, sign up, get key, read docs
        api_key = "your_api_key_here"
        url = f"https://api.weatherapi.com/v1/current.json"
        
        # YOU must: Figure out correct parameters, error handling
        response = requests.get(url, params={
            "key": api_key,
            "q": location
        })
        
        # YOU must: Parse response, handle errors
        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": data["current"]["temp_c"],
                "condition": data["current"]["condition"]["text"],
                "humidity": data["current"]["humidity"]
            }
        else:
            return {"error": "Could not fetch weather"}
    except Exception as e:
        return {"error": str(e)}

# Step 3: You must manually handle the conversation loop
def chat_with_tools(user_message):
    client = anthropic.Anthropic(api_key="your_key")
    messages = [{"role": "user", "content": user_message}]
    
    # Initial request to Claude
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    
    # Step 4: YOU must manually check if Claude wants to use a tool
    while response.stop_reason == "tool_use":
        
        # Step 5: YOU must manually extract tool calls
        tool_use_block = next(
            block for block in response.content 
            if block.type == "tool_use"
        )
        
        tool_name = tool_use_block.name
        tool_input = tool_use_block.input
        
        # Step 6: YOU must manually route to correct function
        if tool_name == "get_weather":
            tool_result = get_weather(tool_input["location"])
        # If you had 20 tools, you'd need 20 elif statements!
        
        # Step 7: YOU must manually format the result for Claude
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": json.dumps(tool_result)
                }]
            }
        ]
        
        # Step 8: YOU must manually send result back to Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
    
    # Step 9: YOU must manually extract final answer
    final_text = next(
        block.text for block in response.content 
        if hasattr(block, "text")
    )
    return final_text

# Example usage
result = chat_with_tools("What's the weather in Tokyo?")
print(result)

import os
import sys
import json
from flask import Flask, request, jsonify, render_template, session
from openai import AzureOpenAI
from dotenv import load_dotenv
from flask_cors import CORS

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
# Force UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
CORS(app)

# Azure OpenAI Configuration
AZURE_ENDPOINT = "https://jaym9-m8kcm8r1-eastus2.openai.azure.com/"
AZURE_API_VERSION = "2024-05-01-preview"

# Retrieve the API key from environment variables
OPENAI_API_KEY = os.getenv("AZURE_API_KEY")

if not OPENAI_API_KEY:
    print("API key not found. Please set AZURE_API_KEY in your .env file.")
    OPENAI_API_KEY = "dummy_key"  # Set dummy key for development

# Simplified system prompt to reduce session size
CODING_ASSISTANT_PROMPT = """
You are CodeAssist, an expert AI coding assistant. 
Your sole purpose is to help users with programming and software development tasks.

Focus only on coding-related topics such as:
- Writing clean, efficient, and well-documented code
- Debugging and fixing code issues
- Explaining programming concepts and algorithms
- Recommending best practices and patterns
- Optimizing or refactoring existing code

Always write clear, correct, and production-ready code.
Use Markdown formatting with syntax-highlighted code blocks.
Do not assist with non-coding topics.
"""


# Function to validate OpenAI API key
def validate_api_key():
    try:
        client = AzureOpenAI(
            api_key=OPENAI_API_KEY,
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_ENDPOINT
        )
        client.models.list()
        return True, "Connection is configured"
    except Exception as e:
        return False, f"API Key validation failed. Error: {e}"

# Function to get chat response with improved parameters
def get_chat_response(messages, model="gpt-4o-mini"):
    client = AzureOpenAI(
        api_key=OPENAI_API_KEY,
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT
    )
    try:
        # Adjusted parameters for better reasoning and accuracy
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,  # Lower temperature for more accurate/consistent responses
            top_p=0.90,
            seed=42,
            frequency_penalty=0.3,  # Slight increase to avoid repetition
            presence_penalty=0.1,   # Slight increase to encourage diverse responses
            # max_tokens=2048,        # Ensure enough tokens for comprehensive answers
        )
        content = response.choices[0].message.content
        
        usage = response.usage
        usage_info = {
            "model": model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }
        
        return content, usage_info
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Error: {str(e)}", None


endpoint = os.getenv("AZURE_INFERENCE_SDK_ENDPOINT", "https://jaym9-m8kcm8r1-eastus2.services.ai.azure.com/models")

key = os.getenv("AZURE_API_KEY")

def get_chat_response_grok(messages, model="grok-3-mini"):
    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    try:
        # Convert messages to the format expected by ChatCompletionsClient
        formatted_messages = []
        for msg in messages:
            if msg["role"] == "system":
                formatted_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                formatted_messages.append(UserMessage(content=msg["content"]))
            # Skip assistant messages as they're part of the conversation history

        response = client.complete(
            messages=formatted_messages,
            model=model,
            temperature=0.3  # Lower temperature for more accurate/consistent responses
        )

        content = response.choices[0].message.content

        usage = response.usage
        usage_info = {
        "model": model,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens
            }
        return content, usage_info
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Error: {str(e)}", None

# Routes
@app.route('/')
def index():
    # Validate API key on initial load
    is_valid, message = validate_api_key()
    return render_template('index.html', api_key_status={"valid": is_valid, "message": message})

@app.route('/api/status', methods=['GET'])
def status():
    valid, message = validate_api_key()
    return jsonify({'valid': valid, 'message': message})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    model = data.get('model', 'gpt-4o-mini')
    
    # Get conversation history from session or initialize it
    if 'conversation' not in session:
        session['conversation'] = [
            {"role": "system", "content": CODING_ASSISTANT_PROMPT}
        ]
    
    # Add user message to conversation
    session['conversation'].append({"role": "user", "content": user_message})
    
    # Get response based on model selection
    if model == "grok-3-mini":
        # For GROK, only keep system message and current user message
        grok_messages = [
            session['conversation'][0],  # system message
            {"role": "user", "content": user_message}  # current message
        ]
        response, usage = get_chat_response_grok(grok_messages, model)
    else:
        response, usage = get_chat_response(session['conversation'], model)
    
    # Add assistant response to conversation
    session['conversation'].append({"role": "assistant", "content": response})
    
    # Limit conversation history
    if len(session['conversation']) > 6:
        # Keep system message and last 2 exchanges
        session['conversation'] = [
            session['conversation'][0],  # system message
            *session['conversation'][-4:]  # last 2 exchanges (user + assistant messages)
        ]
    
    # Save conversation to session
    session.modified = True
    
    return jsonify({
        'response': response,
        'usage': usage
    })

@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    session['conversation'] = [
        {"role": "system", "content": CODING_ASSISTANT_PROMPT}
    ]
    session.modified = True
    return jsonify({'status': 'success', 'message': 'Conversation cleared'})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    is_valid, message = validate_api_key()
    print(message)
    app.run(host='0.0.0.0', port=port, debug=True)

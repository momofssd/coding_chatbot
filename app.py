import os
import sys
import json
from flask import Flask, request, jsonify, render_template, session
from openai import AzureOpenAI
from dotenv import load_dotenv
from flask_cors import CORS

# Force UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
CORS(app)

# Azure OpenAI Configuration
AZURE_ENDPOINT = "https://momofssd1.openai.azure.com/"
AZURE_API_VERSION = "2024-05-01-preview"

# Retrieve the API key from environment variables
OPENAI_API_KEY = os.getenv("AZURE_API_KEY")

if not OPENAI_API_KEY:
    print("API key not found. Please set AZURE_API_KEY in your .env file.")
    OPENAI_API_KEY = "dummy_key"  # Set dummy key for development

# Function to validate OpenAI API key
def validate_api_key():
    try:
        client = AzureOpenAI(
            api_key=OPENAI_API_KEY,
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_ENDPOINT
        )
        client.models.list()
        return True, "✅ Connection is configured"
    except Exception as e:
        return False, f"❌ API Key validation failed. Error: {e}"

# Function to get chat response
def get_chat_response(messages, model="gpt-4o-mini"):
    client = AzureOpenAI(
        api_key=OPENAI_API_KEY,
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            top_p=0.95,
            seed=42,
            frequency_penalty=0,
            presence_penalty=0,
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
        print(f"⚠ Error calling OpenAI API: {e}")
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
            {"role": "system", "content": "You are a helpful AI assistant. Format your responses using Markdown for better readability. Use headers, lists, code blocks, bold, italic, etc. when appropriate."}
        ]
    
    # Add user message to conversation
    session['conversation'].append({"role": "user", "content": user_message})
    
    # Get response from OpenAI
    response, usage = get_chat_response(session['conversation'], model)
    
    # Add assistant response to conversation
    session['conversation'].append({"role": "assistant", "content": response})
    
    # Limit conversation history (optional)
    if len(session['conversation']) > 20:
        # Keep system message and last 10 exchanges
        session['conversation'] = [session['conversation'][0]] + session['conversation'][-19:]
    
    # Save conversation to session
    session.modified = True
    
    return jsonify({
        'response': response,
        'usage': usage
    })

@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    session['conversation'] = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]
    session.modified = True
    return jsonify({'status': 'success', 'message': 'Conversation cleared'})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    is_valid, message = validate_api_key()
    print(message)
    app.run(host='0.0.0.0', port=port, debug=True)


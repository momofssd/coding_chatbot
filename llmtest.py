import os
import sys
from openai import AzureOpenAI
from dotenv import load_dotenv

# Force UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Configuration
AZURE_ENDPOINT = "https://momofssd1.openai.azure.com/"
AZURE_API_VERSION = "2024-05-01-preview"

# Retrieve the API key from environment variables
OPENAI_API_KEY = os.getenv("AZURE_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("API key not found. Please set AZURE_API_KEY in your .env file.")

# Function to validate OpenAI API key
def validate_api_key(openai_api_key):
    try:
        client = AzureOpenAI(
            api_key=openai_api_key,
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_ENDPOINT
        )
        client.models.list()
        return True, "✅ API Key validated successfully!"
    except Exception as e:
        return False, f"❌ Invalid API Key. Error: {e}"

# Function to extract data from text
def extract_data_from_text(openai_api_key, prompts, model="gpt-4o-mini"):
    client = AzureOpenAI(
        api_key=openai_api_key,
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=prompts,
            temperature=0,
            top_p=0,
            seed=42,  
            frequency_penalty=0,     
            presence_penalty=0,       
        )
        content = response.choices[0].message.content
        
        usage = response.usage
        print(f"Select Model: {model}")
        print(f"Token Usage:")
        print(f" - Prompt Tokens: {usage.prompt_tokens}")
        print(f" - Completion Tokens: {usage.completion_tokens}")
        print(f" - Total Tokens: {usage.total_tokens}")
        
        return content
    except Exception as e:
        print(f"⚠ Error calling OpenAI API: {e}")
        return None

# Example usage
if __name__ == "__main__":
    is_valid, message = validate_api_key(OPENAI_API_KEY)
    print(message)

    prompts = [
        {"role": "system", "content": "You are a coding developer assistant."},
        {"role": "user", "content": ""}
    ]
    
    if is_valid:
        result = extract_data_from_text(OPENAI_API_KEY, prompts)
        if result:
            print("Extracted Data:", result)
"""Check which DeepSeek models are available"""
import os
import requests

# Try to get model list
headers = {
    "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"
}

try:
    # Standard OpenAI-compatible endpoint
    response = requests.get("https://api.deepseek.com/v1/models", headers=headers)
    if response.status_code == 200:
        models = response.json()
        print("Available models:")
        for model in models.get('data', []):
            print(f"  - {model.get('id', 'unknown')}")
    else:
        print(f"Error getting models: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")

# Test if reasoning model exists
print("\nTesting deepseek-reasoner availability...")
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

try:
    # Try a minimal request
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=10
    )
    print("✓ deepseek-reasoner is available!")
except Exception as e:
    print(f"✗ deepseek-reasoner error: {e}")
    
print("\nTesting deepseek-chat...")
try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=10
    )
    print("✓ deepseek-chat is available!")
except Exception as e:
    print(f"✗ deepseek-chat error: {e}")
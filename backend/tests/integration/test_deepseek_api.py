import os
"""Test DeepSeek API connection"""
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one word"}
        ],
        max_tokens=10
    )
    
    print("API Response:", response.choices[0].message.content)
    print("API connection successful!")
    
except Exception as e:
    print(f"API Error: {type(e).__name__}: {e}")
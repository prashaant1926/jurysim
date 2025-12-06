import os
"""Test the improved natural dialogue prompts"""
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

print("TESTING IMPROVED DIALOGUE PROMPTS")
print("=" * 50)

# Test 1: Formal prompt (old way)
print("\n❌ OLD FORMAL PROMPT:")
print("-" * 30)
formal_prompt = """You are Margaret Smith, a 65-year-old retired teacher. 
Please analyze the evidence in this theft case and provide your professional assessment."""

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": formal_prompt},
            {"role": "user", "content": "What are your thoughts on the security footage evidence?"}
        ],
        max_tokens=150
    )
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Natural prompt (new way)
print("\n\n✓ NEW NATURAL PROMPT:")
print("-" * 30)
natural_prompt = """You are Margaret, a 65-year-old retired teacher from a small town.

SPEAKING STYLE: Talk like a normal person having a conversation, NOT like giving a speech. Use:
- Contractions (I'm, don't, can't, won't)
- Incomplete thoughts ('But the thing is...', 'I mean...')
- Personal references ('Back when I taught...', 'My husband always says...')
- Emotional reactions ('That's ridiculous!', 'Oh come on')
- Casual transitions ('Look', 'Listen', 'Well')

NO formal academic language. Sound like a real grandmother talking."""

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": natural_prompt},
            {"role": "user", "content": "Alright Margaret, what do you think about this security footage?"}
        ],
        max_tokens=150
    )
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}")

print("\n\nEXPECTED IMPROVEMENTS:")
print("=" * 50)
print("• More contractions (I'm vs I am)")
print("• Casual language (gonna vs going to)")
print("• Personal anecdotes (Back when I...)")
print("• Emotional reactions (That's crazy!)")
print("• Incomplete sentences (...but still)")
print("• Direct address of other jurors")
print("• Natural conversation flow")
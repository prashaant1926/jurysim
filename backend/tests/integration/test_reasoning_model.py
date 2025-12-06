import os
"""Test DeepSeek reasoning model capabilities"""
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

print("Testing DeepSeek Reasoning Model (deepseek-reasoner)")
print("=" * 50)

# Test basic reasoning
try:
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Which is greater, 9.11 or 9.8? Explain your reasoning."}
        ],
        max_tokens=1000
    )
    
    # Extract reasoning content
    reasoning = getattr(response.choices[0].message, 'reasoning_content', None)
    answer = response.choices[0].message.content
    
    print("\nCHAIN OF THOUGHT (reasoning_content):")
    print("-" * 40)
    if reasoning:
        print(reasoning[:500] + "..." if len(reasoning) > 500 else reasoning)
    else:
        print("No reasoning content available")
    
    print("\nFINAL ANSWER (content):")
    print("-" * 40)
    print(answer)
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

# Test JSON output for voting
print("\n\nTesting JSON Output for Voting:")
print("=" * 50)

try:
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You are a juror. Respond only with JSON."},
            {"role": "user", "content": 'Based on the evidence, provide your verdict as JSON: {"verdict": "guilty/not_guilty/undecided", "confidence": 0.0-1.0, "reasoning": "brief explanation"}'}
        ],
        max_tokens=500
    )
    
    reasoning = getattr(response.choices[0].message, 'reasoning_content', None)
    answer = response.choices[0].message.content
    
    if reasoning:
        print("\nREASONING PROCESS:")
        print("-" * 40)
        print(reasoning[:300] + "..." if len(reasoning) > 300 else reasoning)
    
    print("\nJSON OUTPUT:")
    print("-" * 40)
    print(answer)
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
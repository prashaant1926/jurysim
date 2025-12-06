import os
"""Test that AI jurors don't include physical gestures"""
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

print("TESTING GESTURE REMOVAL")
print("=" * 50)

# Test with explicit no-gesture instruction
prompt = """You are Sarah, a 45-year-old teacher serving on a jury.

IMPORTANT: Do NOT include physical actions or gestures in asterisks like *leans forward*, *taps table*, *adjusts glasses*. Just speak naturally without stage directions.

NO physical gestures (*leans*, *taps*, etc.) - just natural speech!"""

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Sarah, what do you think about the defendant claiming the items were a gift?"}
        ],
        max_tokens=200
    )
    
    content = response.choices[0].message.content
    
    print("\nRESPONSE:")
    print("-" * 40)
    print(content)
    
    # Check for common gesture patterns
    gesture_patterns = ["*", "leans", "taps", "adjusts", "gestures", "shrugs", "nods"]
    has_gestures = any(pattern in content.lower() for pattern in gesture_patterns)
    
    print("\n" + "=" * 50)
    if has_gestures:
        print("❌ FAILED: Response contains physical gestures")
    else:
        print("✓ SUCCESS: Response is gesture-free!")
        
except Exception as e:
    print(f"Error: {e}")
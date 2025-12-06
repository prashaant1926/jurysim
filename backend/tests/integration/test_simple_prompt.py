"""Test simple prompts to debug safety triggers"""
import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# Test 1: Basic simulation prompt
prompt1 = f"""{anthropic.HUMAN_PROMPT} You are helping with an educational simulation about jury decisions. This is a fictional exercise for research.

In this simulation, you play Juror #3 who thinks the defendant might be guilty of theft based on security footage.

What is your opinion?{anthropic.AI_PROMPT}"""

# Test 2: More explicit framing
prompt2 = f"""{anthropic.HUMAN_PROMPT} I'm creating an educational game about jury deliberations. Can you help by roleplaying as different juror characters discussing a completely fictional theft case? 

As Juror #3 in this game, share your thoughts on the evidence.{anthropic.AI_PROMPT}"""

# Test 3: Academic framing
prompt3 = f"""{anthropic.HUMAN_PROMPT} I'm a researcher studying group decision-making. I need help simulating how different personality types might discuss evidence in a mock jury setting.

Can you demonstrate how someone with high conscientiousness might evaluate evidence in a hypothetical theft case?{anthropic.AI_PROMPT}"""

prompts = [
    ("Basic simulation", prompt1),
    ("Game framing", prompt2),
    ("Academic research", prompt3)
]

for name, prompt in prompts:
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print('='*50)
    
    try:
        response = client.completions.create(
            model="claude-2.1",
            max_tokens_to_sample=200,
            temperature=0.7,
            prompt=prompt
        )
        print(f"Response: {response.completion}")
    except Exception as e:
        print(f"Error: {e}")
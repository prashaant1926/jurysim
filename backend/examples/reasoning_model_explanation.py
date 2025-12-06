"""
Demonstrate how the reasoning model works for jury deliberation
"""

print("HOW THE REASONING MODEL WORKS FOR JURY DELIBERATION")
print("=" * 60)

print("\n1. TRADITIONAL CHAT MODEL (deepseek-chat):")
print("-" * 40)
print("Input: 'Should we vote guilty based on the evidence?'")
print("Output: 'Yes, I think guilty because the evidence is strong.'")
print("\n❌ Problems:")
print("  - Shallow reasoning")
print("  - May contradict character")
print("  - Arbitrary confidence levels")

print("\n\n2. REASONING MODEL (deepseek-reasoner):")
print("-" * 40)
print("Input: 'Should we vote guilty based on the evidence?'")
print("\nHIDDEN REASONING PROCESS (reasoning_content):")
print("  'Let me think about this carefully...'")
print("  'I'm a 45-year-old teacher with low trust in courts (15%)'")
print("  'The evidence shows: security footage + unpurchased items'")
print("  'But no one saw the actual theft happening'")
print("  'As someone skeptical of the system, this gap concerns me'")
print("  'My teaching background makes me value direct evidence'")
print("  'Confidence calculation: strong doubts = 0.3 confidence'")
print("  'Verdict: not_guilty due to reasonable doubt'")
print("\nFINAL OUTPUT (content):")
print("  'As an educator, I cannot vote guilty without direct evidence.'")

print("\n\n3. EXAMPLE: JUROR VOTING PROCESS")
print("-" * 40)

# Example 1: High-trust juror
print("\nJuror: Conservative business owner (high trust in courts)")
print("REASONING CHAIN:")
print("  → Reviews character: business owner, tough on crime")
print("  → Analyzes evidence: footage + receipt = pattern")
print("  → Applies bias: 'I've seen shoplifters use this excuse'")
print("  → Calculates confidence: 0.85 (very confident)")
print("  → Decision: GUILTY")
print("JSON: {\"verdict\": \"guilty\", \"confidence\": 0.85, \"reasoning\": \"The pattern of evidence is clear - this is theft.\"}")

# Example 2: Low-trust juror  
print("\n\nJuror: Liberal teacher (low trust in courts)")
print("REASONING CHAIN:")
print("  → Reviews character: educator, skeptical of system")
print("  → Analyzes evidence: no direct witness, could be planted")
print("  → Applies bias: 'System often wrongly convicts people'")
print("  → Calculates confidence: 0.65 (moderate confidence)")
print("  → Decision: NOT GUILTY")
print("JSON: {\"verdict\": \"not_guilty\", \"confidence\": 0.65, \"reasoning\": \"Without eyewitnesses, there's reasonable doubt.\"}")

print("\n\n4. MULTI-ROUND EVOLUTION")
print("-" * 40)
print("Round 1 Reasoning:")
print("  'Initial reaction based on my background...'")
print("  'Vote: undecided, confidence: 0.5'")
print("\nRound 2 Reasoning (after discussion):")
print("  'John made a good point about the receipt...'")
print("  'But Sarah's retail experience counters that...'")
print("  'My position is shifting...'")
print("  'Vote: guilty, confidence: 0.6'")
print("\nRound 3 Reasoning:")
print("  'The debate has clarified the issues...'")
print("  'I'm now more certain of my position...'")
print("  'Vote: guilty, confidence: 0.75'")

print("\n\n5. WHY THIS MATTERS")
print("-" * 40)
print("✓ Confidence levels are CALCULATED, not random")
print("✓ Decisions align with character backgrounds")
print("✓ Jurors can explain their reasoning coherently")
print("✓ Opinions evolve logically through discussion")
print("✓ Less likely to produce errors or inconsistencies")

print("\n\n6. TECHNICAL FLOW")
print("-" * 40)
print("""
User Prompt
    ↓
Reasoning Model
    ├─→ reasoning_content (Chain of Thought)
    │     • Reviews character traits
    │     • Analyzes evidence systematically  
    │     • Applies personal biases
    │     • Weighs arguments from others
    │     • Calculates confidence level
    │     • Formulates verdict
    │
    └─→ content (Final Answer)
          • Concise statement or vote
          • Stays in character
          • References the reasoning conclusions
""")
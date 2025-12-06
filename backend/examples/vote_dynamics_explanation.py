"""
Explanation of jury vote dynamics and why votes may not change
"""

print("WHY JURY VOTES MAY NOT CHANGE")
print("="*60)
print()

print("1. REALISTIC JURY BEHAVIOR:")
print("-"*40)
print("• Real jurors often stick to initial impressions")
print("• Changing votes requires COMPELLING new evidence/arguments")
print("• Personality traits affect willingness to change:")
print("  - High openness → more likely to reconsider")
print("  - High conscientiousness → sticks to initial judgment")
print("  - Low confidence → more susceptible to persuasion")
print()

print("2. WHAT WAS HAPPENING (BEFORE FIX):")
print("-"*40)
print("• Jurors discussed evidence during deliberation")
print("• BUT when voting, they didn't consider the discussion")
print("• They voted based only on initial evidence assessment")
print("• Result: No vote changes despite doubts expressed")
print()

print("3. IMPROVEMENTS MADE:")
print("-"*40)
print("✓ Voting now considers recent discussion context")
print("✓ Personality traits influence vote change likelihood")
print("✓ Previous voting confidence affects flexibility")
print("✓ Round number considered (early rounds = more flexible)")
print()

print("4. FACTORS THAT ENCOURAGE VOTE CHANGES:")
print("-"*40)
print("• New evidence interpretation revealed in discussion")
print("• Compelling counterarguments to initial assumptions")
print("• Multiple jurors raising same concerns")
print("• Personal experiences shared that relate to evidence")
print("• Procedural issues (contamination, chain of custody)")
print()

print("5. FACTORS THAT PREVENT VOTE CHANGES:")
print("-"*40)
print("• Strong initial conviction (high confidence)")
print("• Personality: high conscientiousness, low openness")
print("• Jury instruction: 'Don't abandon honest conviction'")
print("• Lack of truly NEW arguments (just repetition)")
print("• Evidence strongly supports one side")
print()

print("6. EXAMPLE SCENARIOS:")
print("-"*40)

scenarios = [
    {
        "juror": "High Openness + Low Initial Confidence",
        "initial": "Guilty (65%)",
        "discussion": "Defense raises contamination concerns",
        "result": "May change to Not Guilty or Undecided"
    },
    {
        "juror": "High Conscientiousness + High Confidence", 
        "initial": "Not Guilty (85%)",
        "discussion": "Prosecution explains DNA evidence",
        "result": "Unlikely to change (needs overwhelming evidence)"
    },
    {
        "juror": "High Agreeableness + Split Jury",
        "initial": "Guilty (70%)",
        "discussion": "Majority shifting to Not Guilty",
        "result": "May change to seek consensus"
    },
    {
        "juror": "High Neuroticism + Serious Consequences",
        "initial": "Guilty (75%)",
        "discussion": "Death penalty mentioned",
        "result": "May become Undecided due to anxiety"
    }
]

for s in scenarios:
    print(f"\n{s['juror']}:")
    print(f"  Initial: {s['initial']}")
    print(f"  After: '{s['discussion']}'")
    print(f"  → {s['result']}")

print("\n" + "="*60)
print("KEY INSIGHT: Vote changes should be EARNED through")
print("compelling arguments, not forced for drama. The system")
print("now allows realistic vote evolution based on personality,")
print("discussion quality, and evidence strength.")
print("="*60)
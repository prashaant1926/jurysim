"""
Demo showing the difference between opening statements and natural discussion
"""

print("JURY DELIBERATION CONVERSATION STYLES")
print("="*60)
print()

print("1. OPENING STATEMENTS (Formal, Longer)")
print("-"*40)
print("Example opening statements:")
print()

opening_examples = [
    {
        "juror": "Sarah (Conservative)",
        "statement": "Looking at Evidence #1, #2, and #3 - the blood evidence - it's pretty clear to me what happened here. I've worked in retail security and I know how evidence tells a story. The DNA matches are particularly damning, and when you combine that with the history of domestic violence in Evidence #7 and #8, it paints a clear picture of guilt."
    },
    {
        "juror": "Michael (Liberal)",
        "statement": "I'm troubled by several aspects of this case, particularly Evidence #5 where the glove didn't fit. As an educator, I've learned to question assumptions and look deeper. The defense raises valid concerns about evidence contamination that we can't ignore. Evidence #9 about the timeline also makes me wonder if the prosecution's theory is even physically possible."
    }
]

for ex in opening_examples:
    print(f"{ex['juror']}:")
    print(f'"{ex["statement"]}"')
    print(f"[Word count: {len(ex['statement'].split())}]")
    print()

print("\n2. NATURAL DISCUSSION (Short, Conversational)")
print("-"*40)
print("Example discussion exchanges:")
print()

discussion_examples = [
    ("John", "But wait, how do you explain the blood in his Bronco?"),
    ("Sarah", "Exactly! That's Evidence #3 right there."),
    ("Michael", "Hold on though - couldn't it have been planted like the defense said?"),
    ("Linda", "That's what I'm thinking too. The chain of custody was a mess."),
    ("John", "Are you seriously buying that conspiracy theory?"),
    ("David", "I've seen cops do worse, honestly."),
    ("Sarah", "Fair point, but ALL that evidence?"),
    ("Michael", "Remember the glove didn't fit. That's huge."),
    ("Linda", "Right! If it doesn't fit, you must acquit."),
    ("John", "Oh come on, leather shrinks when it dries."),
    ("David", "Does it though? Mine never have."),
    ("Sarah", "Wait, weren't there two gloves?"),
    ("Michael", "Yeah, one at each scene. That's Evidence #5."),
    ("Linda", "See, that's what makes me doubt the whole thing."),
]

for name, statement in discussion_examples:
    print(f"{name}: {statement}")
    print(f"[{len(statement.split())} words]")
    print()

print("\n3. KEY DIFFERENCES:")
print("-"*40)
print("Opening Statements:")
print("• 40-80 words (3-4 complete sentences)")
print("• Formal tone, complete thoughts")
print("• References multiple evidence items")
print("• Establishes initial position clearly")
print()
print("Discussion Phase:")
print("• 5-20 words (1-2 sentences max)")
print("• Natural, conversational tone")
print("• Quick reactions and questions")
print("• Interruptions and interjections")
print("• Direct responses to others")
print("• Personal anecdotes kept brief")

print("\n4. CONVERSATION FLOW PATTERNS:")
print("-"*40)
print("• Question → Direct answer → Follow-up")
print("• Statement → Agreement + addition")
print("• Claim → Challenge → Defense")
print("• Evidence mention → Personal experience")
print("• Strong opinion → Multiple reactions")

print("\n" + "="*60)
print("The system now creates natural dialogue where jurors")
print("interrupt, question, agree, and challenge each other")
print("in short bursts, just like real jury deliberations.")
print("="*60)
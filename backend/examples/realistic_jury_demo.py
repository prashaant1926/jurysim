"""
Demonstration of realistic jury behaviors
"""

print("REALISTIC JURY DELIBERATION BEHAVIORS")
print("="*60)
print()

print("1. EMOTIONAL WEIGHT OF DECISION:")
print("-"*40)
examples = [
    ("Sarah (High Neuroticism)", "This is too much... someone's life is in our hands. What if we're wrong? I couldn't live with myself."),
    ("Michael (Overwhelmed)", "I didn't sleep at all last night. Keep seeing those crime scene photos. This is horrible."),
    ("Linda (Breaking Down)", "*voice shaking* I can't... I just can't send someone to prison. What if it was my son?")
]
for name, statement in examples:
    print(f"{name}: \"{statement}\"")
print()

print("2. LEGAL CONFUSION:")
print("-"*40)
examples = [
    ("Bob (Low Education)", "Wait, so reasonable doubt means like... 51% sure? Or 99%? I don't get it."),
    ("Janet (Confused)", "Hold up - if he didn't testify, doesn't that mean he's guilty? Why wouldn't an innocent person speak up?"),
    ("Tom (Misunderstanding)", "But the judge said 'beyond reasonable doubt' - isn't ANY doubt reasonable? So we can't convict?"),
    ("Mary (Lost)", "Which one was Evidence #5 again? The glove or the blood? I'm so confused.")
]
for name, statement in examples:
    print(f"{name}: \"{statement}\"")
print()

print("3. PERSONALITY CLASHES:")
print("-"*40)
print("Know-it-all vs Others:")
print('  Steve: "Actually, let me explain how DNA really works. I watch CSI, so..."')
print('  Linda: "Oh my God, not the TV shows again!"')
print('  Steve: "No, listen, the probability calculations they mentioned..."')
print('  Mike: "STEVE! We\'ve heard your theories five times already!"')
print()
print("Domineering vs Quiet:")
print('  Barbara: "Everyone SHUT UP and listen! Here\'s what we\'re going to do..."')
print('  Amy: *quietly* "I... um... I had a thought about..."')
print('  Barbara: "Not now Amy! As I was saying..."')
print('  John: "Let Amy speak for once, Barbara!"')
print()

print("4. IRRELEVANT TANGENTS:")
print("-"*40)
examples = [
    ("During evidence discussion", "This reminds me of my divorce actually. My ex was a liar too..."),
    ("After 4 hours", "Anyone else starving? There's a great taco place around the corner."),
    ("Random interruption", "You know, the defendant looks exactly like my dentist. Same mustache."),
    ("Off-topic story", "Speaking of knives, I once cut myself real bad making dinner. Blood everywhere!")
]
for context, statement in examples:
    print(f"{context}: \"{statement}\"")
print()

print("5. FATIGUE PROGRESSION:")
print("-"*40)
print("Hour 2: \"Let's carefully review each piece of evidence.\"")
print("Hour 4: \"Can we speed this up? My back is killing me.\"")
print("Hour 6: \"I need coffee. Or vodka. Definitely vodka.\"")
print("Hour 8: \"I'll vote whatever just to get out of here!\"")
print("Hour 10: \"If I hear about that damn glove ONE MORE TIME...\"")
print()

print("6. STUBBORN HOLDOUTS:")
print("-"*40)
print("11-1 Split Scenario:")
print('  Foreperson: "Robert, you\'re the only one voting not guilty."')
print('  Robert: "I don\'t care. My gut says he\'s innocent."')
print('  Sarah: "But the DNA evidence!"')
print('  Robert: "Don\'t trust it. Period."')
print('  Michael: "Can you at least explain why?"')
print('  Robert: "I said what I said. Not changing."')
print('  Group: *collective groan*')
print()

print("7. REALISTIC VOTE CHANGES:")
print("-"*40)
print("Peer Pressure:")
print('  "Fine! If all 11 of you think so... maybe I\'m wrong. I\'ll change to guilty."')
print()
print("Exhaustion:")
print('  "I\'m too tired to fight anymore. Whatever. Not guilty. Can we go now?"')
print()
print("Genuine Persuasion:")
print('  "You know what... when you explain it that way, I hadn\'t considered that angle."')
print()
print("Emotional:")
print('  "Looking at those photos again... *crying* ...we can\'t let a killer walk free."')
print()

print("8. UNCONSCIOUS BIAS SLIPPING THROUGH:")
print("-"*40)
examples = [
    "\"I mean, look at his lifestyle... says something about character.\"",
    "\"People from that neighborhood, you know how they are...\"",
    "\"He just LOOKS guilty to me. Can't explain it.\"",
    "\"I'm not prejudiced, but where there's smoke...\"",
    "\"A man with that much money probably did something wrong.\""
]
for statement in examples:
    print(f"  {statement}")

print("\n" + "="*60)
print("KEY INSIGHT: Real juries are messy, emotional, confused,")
print("and human. They struggle with the weight of their decision,")
print("misunderstand legal concepts, and let personal biases creep in.")
print("This creates authentic drama and realistic deliberation dynamics.")
print("="*60)
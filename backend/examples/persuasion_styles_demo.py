"""
Demo showing how different personality types approach persuasion
"""

def show_persuasion_styles():
    """Demonstrate different persuasion approaches based on personality"""
    
    print("PERSUASION STYLES BASED ON PERSONALITY")
    print("="*60)
    
    personalities = [
        {
            "name": "Sarah (High Extraversion)",
            "traits": {"extraversion": 4.5, "conscientiousness": 3.0},
            "style": "Passionate, direct appeal",
            "example": "Listen, we HAVE to convict! The DNA evidence (#1) is overwhelming - 1 in 170 million! How can you ignore that? Think about the victims' families waiting for justice. We can't let them down because of some conspiracy theory!"
        },
        {
            "name": "Michael (High Conscientiousness)",
            "traits": {"extraversion": 3.0, "conscientiousness": 4.5},
            "style": "Methodical, evidence-based argument",
            "example": "Let's review the facts systematically. Evidence #1 shows DNA match with astronomical odds. Evidence #2 confirms blood trail from scene to defendant's home. Evidence #11 places him at the scene. When we combine these three independent pieces of evidence, the probability of innocence becomes vanishingly small."
        },
        {
            "name": "Jennifer (High Agreeableness)",
            "traits": {"agreeableness": 4.5, "extraversion": 3.0},
            "style": "Appeal to shared values and common ground",
            "example": "I understand why you're hesitant - we all want to be absolutely certain. But think about what we all agree on: we want justice and safety for our community. The evidence shows a pattern that we can't ignore. Can we at least agree that Evidence #7 and #8 show concerning behavior?"
        },
        {
            "name": "Robert (High Openness, Not Guilty)",
            "traits": {"openness": 4.5, "conscientiousness": 3.5},
            "style": "Challenge assumptions and present alternatives",
            "example": "But wait - are we really considering all possibilities? Evidence #3, the glove not fitting, suggests our theory might be wrong. What if the timeline (#9) makes the prosecution's story physically impossible? We need to think beyond the obvious narrative here."
        },
        {
            "name": "Linda (Low Trust in System)",
            "traits": {"trust_courts": 0.2, "neuroticism": 3.5},
            "style": "Question reliability of evidence and system",
            "example": "How do we know Evidence #1 and #2 weren't contaminated or planted? We've seen cases of police misconduct before. The chain of custody issues alone create reasonable doubt. Can we really trust evidence handled by officers with questionable histories?"
        },
        {
            "name": "David (High Neuroticism, Undecided)",
            "traits": {"neuroticism": 4.0, "conscientiousness": 3.5},
            "style": "Express deep concerns about convicting",
            "example": "I'm really struggling here... What if we're wrong? Someone's life is in our hands. The death penalty issue makes this even harder. Evidence #5 shows they were unarmed - doesn't that matter? I need to be absolutely sure before I can vote guilty."
        }
    ]
    
    for p in personalities:
        print(f"\n{p['name']}")
        print(f"Style: {p['style']}")
        print("-" * 40)
        print(f'"{p["example"]}"')
    
    print("\n" + "="*60)
    print("KEY INSIGHTS:")
    print("="*60)
    print("""
1. High Extraversion → Emotional, passionate appeals
2. High Conscientiousness → Systematic, evidence-focused
3. High Agreeableness → Bridge-building, finding common ground  
4. High Openness → Question assumptions, alternative theories
5. Low Trust → Challenge system and evidence reliability
6. High Neuroticism → Express anxiety about consequences

The post-vote persuasion phase allows these personality-driven
approaches to emerge naturally, creating realistic jury dynamics
where different types of people try to convince others in their
own characteristic ways.
""")

if __name__ == "__main__":
    show_persuasion_styles()
#!/usr/bin/env python3
"""
Example of how to generate AI jurors using personality + election data
"""
import numpy as np
import json

def generate_juror_personality(county_dem_pct, is_urban=True):
    """
    Generate personality traits based on county political lean and urban/rural
    """
    # Base personality from global averages
    base_personality = {
        'extraversion': 3.02,
        'neuroticism': 3.02,
        'agreeableness': 3.16,
        'conscientiousness': 3.12,
        'openness': 3.27
    }
    
    # Political lean adjustments (research-based correlations)
    political_factor = (county_dem_pct - 50) / 100  # -0.5 to +0.5
    
    # Liberal counties: higher openness, lower conscientiousness
    # Conservative counties: opposite
    personality = {
        'openness': base_personality['openness'] + (political_factor * 0.4),
        'conscientiousness': base_personality['conscientiousness'] - (political_factor * 0.3),
        'extraversion': base_personality['extraversion'] + (0.2 if is_urban else -0.2),
        'agreeableness': base_personality['agreeableness'] + (political_factor * 0.1),
        'neuroticism': base_personality['neuroticism'] + np.random.normal(0, 0.1)
    }
    
    # Add individual variation
    for trait in personality:
        personality[trait] += np.random.normal(0, 0.3)
        personality[trait] = max(1, min(5, personality[trait]))  # Keep in 1-5 range
    
    return personality

def generate_jury_pool(county_name, dem_pct, rep_pct, num_jurors=12):
    """
    Generate a jury pool for a specific county
    """
    print(f"=== GENERATING JURY POOL FOR {county_name.upper()} ===")
    print(f"County voting: {dem_pct}% Democratic, {rep_pct}% Republican\n")
    
    jurors = []
    
    # Determine if urban (simplified - in reality would use Census data)
    is_urban = dem_pct > 60
    
    for i in range(num_jurors):
        # Generate personality based on county characteristics
        personality = generate_juror_personality(dem_pct, is_urban)
        
        # Simulate demographics (in reality, sample from Census PUMS)
        age = np.random.choice(range(25, 70), p=np.exp(-np.arange(45)/20)/np.exp(-np.arange(45)/20).sum())
        gender = np.random.choice(['Male', 'Female'], p=[0.48, 0.52])
        
        # Political affiliation weighted by county
        # Calculate probabilities ensuring they sum to 1
        dem_prob = dem_pct/100 * 0.8  # 80% of county % are party affiliated
        rep_prob = rep_pct/100 * 0.8
        ind_prob = 1 - dem_prob - rep_prob
        
        political_lean = np.random.choice(
            ['Democratic', 'Republican', 'Independent'],
            p=[dem_prob, rep_prob, ind_prob]
        )
        
        juror = {
            'id': i + 1,
            'age': age,
            'gender': gender,
            'political_lean': political_lean,
            'personality': {
                'openness': round(personality['openness'], 2),
                'conscientiousness': round(personality['conscientiousness'], 2),
                'extraversion': round(personality['extraversion'], 2),
                'agreeableness': round(personality['agreeableness'], 2),
                'neuroticism': round(personality['neuroticism'], 2)
            },
            'personality_summary': get_personality_summary(personality)
        }
        jurors.append(juror)
    
    return jurors

def get_personality_summary(personality):
    """
    Create a text summary of personality traits
    """
    summaries = []
    
    if personality['openness'] > 3.5:
        summaries.append("creative and open to new ideas")
    elif personality['openness'] < 2.5:
        summaries.append("traditional and conventional")
    
    if personality['extraversion'] > 3.5:
        summaries.append("outgoing and sociable")
    elif personality['extraversion'] < 2.5:
        summaries.append("reserved and introspective")
    
    if personality['conscientiousness'] > 3.5:
        summaries.append("organized and disciplined")
    elif personality['conscientiousness'] < 2.5:
        summaries.append("flexible and spontaneous")
    
    if personality['agreeableness'] > 3.5:
        summaries.append("cooperative and trusting")
    elif personality['agreeableness'] < 2.5:
        summaries.append("competitive and skeptical")
    
    return ", ".join(summaries) if summaries else "balanced personality"

def simulate_deliberation_tendencies(jurors):
    """
    Show how personality affects deliberation style
    """
    print("\n=== DELIBERATION TENDENCIES ===")
    print("Based on personality traits:\n")
    
    # Find natural leaders (high extraversion + low agreeableness)
    leaders = [j for j in jurors if j['personality']['extraversion'] > 3.5 and j['personality']['agreeableness'] < 3.2]
    if leaders:
        print("Likely to take leadership roles:")
        for leader in leaders[:3]:
            print(f"  - Juror #{leader['id']}: {leader['personality_summary']}")
    
    # Find mediators (high agreeableness + low neuroticism)
    mediators = [j for j in jurors if j['personality']['agreeableness'] > 3.5 and j['personality']['neuroticism'] < 3]
    if mediators:
        print("\nLikely to mediate conflicts:")
        for mediator in mediators[:3]:
            print(f"  - Juror #{mediator['id']}: {mediator['personality_summary']}")
    
    # Find analytical thinkers (high openness + high conscientiousness)
    analytical = [j for j in jurors if j['personality']['openness'] > 3.3 and j['personality']['conscientiousness'] > 3.3]
    if analytical:
        print("\nLikely to focus on evidence and logic:")
        for thinker in analytical[:3]:
            print(f"  - Juror #{thinker['id']}: {thinker['personality_summary']}")

# Example usage
if __name__ == "__main__":
    # Los Angeles County (Liberal Urban)
    la_jurors = generate_jury_pool("Los Angeles County, CA", 71, 27)
    
    print("\nJURY COMPOSITION:")
    for juror in la_jurors[:6]:  # Show first 6
        print(f"\nJuror #{juror['id']}:")
        print(f"  Demographics: {juror['age']} year old {juror['gender']}")
        print(f"  Political lean: {juror['political_lean']}")
        print(f"  Personality: {juror['personality_summary']}")
        print(f"  Trait scores: O={juror['personality']['openness']}, "
              f"C={juror['personality']['conscientiousness']}, "
              f"E={juror['personality']['extraversion']}, "
              f"A={juror['personality']['agreeableness']}, "
              f"N={juror['personality']['neuroticism']}")
    
    simulate_deliberation_tendencies(la_jurors)
    
    print("\n" + "="*60 + "\n")
    
    # Rural Texas County (Conservative Rural)
    print("COMPARISON: Conservative Rural County\n")
    rural_jurors = generate_jury_pool("Rural Texas County", 25, 73)
    
    print("\nNOTICE THE DIFFERENCES:")
    print("- Lower openness scores (more traditional)")
    print("- Higher conscientiousness (more rule-focused)")
    print("- Lower extraversion (rural = less social)")
    print("- Different political distribution")
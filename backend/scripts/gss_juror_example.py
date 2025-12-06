#!/usr/bin/env python3
"""
Practical example of generating a juror using GSS data
"""
import pandas as pd
import numpy as np
from pathlib import Path

def load_gss_sample():
    """Load the sample GSS data we created"""
    sample_path = Path("data/raw/gss_sample.csv")
    if sample_path.exists():
        return pd.read_csv(sample_path)
    else:
        print("Sample GSS data not found. Run explore_gss_data.py first.")
        return None

def find_gss_match(df, age, education, region):
    """
    Find GSS respondents matching demographics
    """
    # Start with exact matches
    matches = df[
        (df['age'].between(age-5, age+5)) &
        (df['educ'].between(education-2, education+2)) &
        (df['region'] == region)
    ]
    
    # If too few matches, broaden criteria
    if len(matches) < 10:
        matches = df[
            (df['age'].between(age-10, age+10)) &
            (df['region'] == region)
        ]
    
    return matches

def generate_juror_from_gss(county_name, state, age, education_years):
    """
    Generate a complete juror profile using GSS data
    """
    print(f"\n=== GENERATING JUROR FOR {county_name.upper()}, {state} ===")
    print(f"Demographics: {age} years old, {education_years} years education\n")
    
    # Map state to GSS region
    state_to_region = {
        'CA': 9, 'NY': 2, 'TX': 7, 'FL': 5, 'IL': 3,
        'PA': 2, 'OH': 3, 'GA': 5, 'NC': 5, 'MI': 3
    }
    region = state_to_region.get(state, 5)  # Default to South Atlantic
    
    # Load GSS data
    df = load_gss_sample()
    if df is None:
        return None
    
    # Find matching GSS respondents
    matches = find_gss_match(df, age, education_years, region)
    print(f"Found {len(matches)} similar GSS respondents\n")
    
    if len(matches) == 0:
        print("No matches found")
        return None
    
    # Analyze the matched group
    profile = analyze_gss_group(matches)
    
    # Generate personality based on GSS profile
    personality = generate_personality_from_gss(profile)
    
    # Create complete juror
    juror = {
        'demographics': {
            'age': age,
            'education_years': education_years,
            'region': region,
            'county': county_name,
            'state': state
        },
        'gss_profile': profile,
        'personality': personality,
        'deliberation_traits': generate_deliberation_traits(profile, personality)
    }
    
    return juror

def analyze_gss_group(matches):
    """
    Analyze GSS respondents to create profile
    """
    profile = {
        'sample_size': len(matches),
        'political_view': {
            'mean': matches['polviews'].mean(),
            'mode': matches['polviews'].mode()[0] if len(matches['polviews'].mode()) > 0 else 4
        },
        'attitudes': {
            'death_penalty_support': (matches['cappun'] == 1).mean(),
            'gun_control_support': (matches['gunlaw'] == 1).mean(),
            'marijuana_legalization': (matches['grass'] == 1).mean()
        },
        'trust': {
            'general_trust': (matches['trust'] == 1).mean(),
            'trust_courts': (matches['conjudge'] == 1).mean(),
            'trust_government': (matches['confed'] == 1).mean()
        },
        'political_distribution': matches['polviews'].value_counts().to_dict()
    }
    
    return profile

def generate_personality_from_gss(profile):
    """
    Generate Big Five personality traits based on GSS profile
    """
    # Base personality (population averages)
    personality = {
        'openness': 3.27,
        'conscientiousness': 3.12,
        'extraversion': 3.02,
        'agreeableness': 3.16,
        'neuroticism': 3.02
    }
    
    # Adjust based on political views
    pol_view = profile['political_view']['mean']
    
    # Liberal (1-3) vs Conservative (5-7) adjustments
    if pol_view < 3.5:  # Liberal
        personality['openness'] += 0.3
        personality['conscientiousness'] -= 0.2
    elif pol_view > 4.5:  # Conservative
        personality['openness'] -= 0.3
        personality['conscientiousness'] += 0.3
    
    # Trust affects agreeableness
    general_trust = profile['trust']['general_trust']
    personality['agreeableness'] += (general_trust - 0.35) * 0.5
    
    # Add individual variation
    for trait in personality:
        personality[trait] += np.random.normal(0, 0.2)
        personality[trait] = max(1, min(5, personality[trait]))
        personality[trait] = round(personality[trait], 2)
    
    return personality

def generate_deliberation_traits(profile, personality):
    """
    Generate jury deliberation characteristics
    """
    traits = []
    
    # Leadership tendency
    if personality['extraversion'] > 3.5 and personality['agreeableness'] < 3.2:
        traits.append("Likely to emerge as jury leader")
    
    # Evidence focus
    if personality['conscientiousness'] > 3.5:
        traits.append("Focus on facts and evidence")
    
    # Openness to arguments
    if personality['openness'] > 3.5:
        traits.append("Open to alternative interpretations")
    else:
        traits.append("Prefers straightforward interpretations")
    
    # Conflict style
    if personality['agreeableness'] > 3.5:
        traits.append("Seeks consensus and compromise")
    else:
        traits.append("Willing to hold unpopular positions")
    
    # Trust in system
    if profile['trust']['trust_courts'] > 0.3:
        traits.append("High deference to judge instructions")
    else:
        traits.append("Questions authority and procedures")
    
    # Political influence
    if profile['political_view']['mean'] < 3:
        traits.append("Liberal perspective on justice")
    elif profile['political_view']['mean'] > 5:
        traits.append("Conservative law-and-order focus")
    
    return traits

def print_juror_profile(juror):
    """
    Print formatted juror profile
    """
    if not juror:
        return
    
    print("\n📋 COMPLETE JUROR PROFILE")
    print("="*50)
    
    print("\n1. DEMOGRAPHICS:")
    demo = juror['demographics']
    print(f"   Age: {demo['age']}")
    print(f"   Education: {demo['education_years']} years")
    print(f"   Location: {demo['county']}, {demo['state']}")
    
    print("\n2. GSS-BASED ATTITUDES:")
    gss = juror['gss_profile']
    print(f"   Political view: {gss['political_view']['mean']:.1f} "
          f"(1=very liberal, 7=very conservative)")
    print(f"   Death penalty support: {gss['attitudes']['death_penalty_support']*100:.0f}%")
    print(f"   Gun control support: {gss['attitudes']['gun_control_support']*100:.0f}%")
    print(f"   Marijuana legalization: {gss['attitudes']['marijuana_legalization']*100:.0f}%")
    print(f"   Trust others: {gss['trust']['general_trust']*100:.0f}%")
    print(f"   Trust courts: {gss['trust']['trust_courts']*100:.0f}%")
    
    print("\n3. PERSONALITY (Big Five):")
    pers = juror['personality']
    print(f"   Openness: {pers['openness']} - "
          f"{'High' if pers['openness'] > 3.5 else 'Low' if pers['openness'] < 2.5 else 'Average'}")
    print(f"   Conscientiousness: {pers['conscientiousness']} - "
          f"{'High' if pers['conscientiousness'] > 3.5 else 'Low' if pers['conscientiousness'] < 2.5 else 'Average'}")
    print(f"   Extraversion: {pers['extraversion']} - "
          f"{'High' if pers['extraversion'] > 3.5 else 'Low' if pers['extraversion'] < 2.5 else 'Average'}")
    print(f"   Agreeableness: {pers['agreeableness']} - "
          f"{'High' if pers['agreeableness'] > 3.5 else 'Low' if pers['agreeableness'] < 2.5 else 'Average'}")
    print(f"   Neuroticism: {pers['neuroticism']} - "
          f"{'High' if pers['neuroticism'] > 3.5 else 'Low' if pers['neuroticism'] < 2.5 else 'Average'}")
    
    print("\n4. JURY DELIBERATION TRAITS:")
    for trait in juror['deliberation_traits']:
        print(f"   • {trait}")
    
    print("\n5. CASE-SPECIFIC PREDICTIONS:")
    print_case_predictions(juror)

def print_case_predictions(juror):
    """
    Predict juror behavior for different case types
    """
    gss = juror['gss_profile']
    
    # Drug case
    if gss['attitudes']['marijuana_legalization'] > 0.6:
        print("   Drug case: Likely sympathetic to defendant")
    else:
        print("   Drug case: Likely to support prosecution")
    
    # Death penalty case
    if gss['attitudes']['death_penalty_support'] > 0.6:
        print("   Capital case: Willing to impose death penalty")
    else:
        print("   Capital case: Prefers life imprisonment")
    
    # Police case
    if gss['trust']['trust_government'] > 0.3 and gss['political_view']['mean'] > 4:
        print("   Police case: Likely to trust officer testimony")
    else:
        print("   Police case: May be skeptical of police")

# Example usage
if __name__ == "__main__":
    print("=== GSS-BASED JUROR GENERATION EXAMPLES ===")
    
    # Example 1: Liberal urban professional
    print("\nEXAMPLE 1: San Francisco Tech Worker")
    juror1 = generate_juror_from_gss("San Francisco", "CA", 35, 16)
    print_juror_profile(juror1)
    
    # Example 2: Conservative rural resident
    print("\n\nEXAMPLE 2: Rural Texas Farmer")
    juror2 = generate_juror_from_gss("Smith County", "TX", 55, 12)
    print_juror_profile(juror2)
    
    # Example 3: Moderate suburban
    print("\n\nEXAMPLE 3: Chicago Suburban Teacher")
    juror3 = generate_juror_from_gss("Cook County", "IL", 42, 18)
    print_juror_profile(juror3)
    
    print("\n\n" + "="*60)
    print("KEY INSIGHT: GSS data creates jurors with:")
    print("• Realistic attitude correlations")
    print("• Evidence-based personality traits")
    print("• Predictable deliberation patterns")
    print("• Case-specific biases")
    print("="*60)
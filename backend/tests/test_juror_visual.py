#!/usr/bin/env python3
"""
Visual test of juror generation with formatted output
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def print_juror_card(juror):
    """Print a formatted juror card"""
    print("\n" + "="*60)
    print(f"JUROR #{juror['id']}")
    print("="*60)
    
    # Demographics
    demo = juror['demographics']
    print(f"👤 DEMOGRAPHICS")
    print(f"   Age: {demo['age']} years old")
    print(f"   Gender: {demo['gender']}")
    print(f"   Race: {demo['race']}")
    print(f"   Education: {demo['education_level']}")
    print(f"   Income: ${demo['income']:,}/year")
    print(f"   Location: {'Urban' if demo['urban'] else 'Rural'}")
    
    # Attitudes
    att = juror['attitudes']
    pol_label = "Very Liberal" if att['political_view'] <= 2 else \
                "Liberal" if att['political_view'] <= 3 else \
                "Moderate" if att['political_view'] <= 5 else \
                "Conservative" if att['political_view'] <= 6 else \
                "Very Conservative"
    
    print(f"\n🗳️ ATTITUDES")
    print(f"   Political View: {pol_label} ({att['political_view']}/7)")
    print(f"   Party: {att['party_affiliation']}")
    print(f"   Death Penalty: {'Supports' if att['death_penalty'] > 0.5 else 'Opposes'} ({att['death_penalty']*100:.0f}%)")
    print(f"   Marijuana: {'Legalize' if att['marijuana_legal'] > 0.5 else 'Keep Illegal'} ({att['marijuana_legal']*100:.0f}%)")
    print(f"   Trust Others: {'High' if att['trust_others'] > 0.4 else 'Low'} ({att['trust_others']:.2f})")
    print(f"   Trust Courts: {'High' if att['trust_courts'] > 0.4 else 'Low'} ({att['trust_courts']:.2f})")
    
    # Personality
    pers = juror['personality']
    print(f"\n🧠 PERSONALITY (Big Five)")
    print(f"   Openness:          {'█' * int(pers['openness'])}{'░' * (5-int(pers['openness']))} {pers['openness']}")
    print(f"   Conscientiousness: {'█' * int(pers['conscientiousness'])}{'░' * (5-int(pers['conscientiousness']))} {pers['conscientiousness']}")
    print(f"   Extraversion:      {'█' * int(pers['extraversion'])}{'░' * (5-int(pers['extraversion']))} {pers['extraversion']}")
    print(f"   Agreeableness:     {'█' * int(pers['agreeableness'])}{'░' * (5-int(pers['agreeableness']))} {pers['agreeableness']}")
    print(f"   Neuroticism:       {'█' * int(pers['neuroticism'])}{'░' * (5-int(pers['neuroticism']))} {pers['neuroticism']}")
    
    # Deliberation traits
    print(f"\n⚖️ JURY BEHAVIOR")
    for trait in juror['deliberation_traits']:
        print(f"   • {trait}")
    
    # Case biases
    print(f"\n📋 CASE-SPECIFIC BIASES")
    for case_type, bias in juror['case_biases'].items():
        print(f"   {case_type.replace('_', ' ').title()}: {bias}")

def test_diverse_counties():
    """Test juror generation for diverse counties"""
    print("\n" + "🏛️ " * 20)
    print("FREUDLAW AI JUROR GENERATION TEST")
    print("🏛️ " * 20)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_cases = [
        {
            "county": "San Francisco",
            "state": "CA",
            "description": "Liberal Urban County",
            "case_type": "drug"
        },
        {
            "county": "Harris",
            "state": "TX",
            "description": "Conservative Urban County",
            "case_type": "capital"
        },
        {
            "county": "Cuyahoga",
            "state": "OH",
            "description": "Swing State County",
            "case_type": "police"
        }
    ]
    
    for test in test_cases:
        print(f"\n\n{'*' * 70}")
        print(f"TESTING: {test['county'].upper()}, {test['state']} - {test['description']}")
        print(f"Case Type: {test['case_type'].upper()}")
        print('*' * 70)
        
        response = requests.post(
            f"{BASE_URL}/jurors/generate",
            params={
                "county": test['county'],
                "state": test['state'],
                "pool_size": 6,  # Minimum pool size
                "case_type": test['case_type']
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            for juror in data['jurors']:
                print_juror_card(juror)
        else:
            print(f"Error: {response.status_code}")

def test_jury_dynamics():
    """Show how a jury pool might interact"""
    print("\n\n" + "🤝 " * 20)
    print("JURY DYNAMICS ANALYSIS")
    print("🤝 " * 20)
    
    # Generate a full 12-person jury
    response = requests.post(
        f"{BASE_URL}/jurors/generate",
        params={
            "county": "Cook",
            "state": "IL",
            "pool_size": 12,
            "case_type": "capital"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        jurors = data['jurors']
        
        # Analyze jury composition
        print(f"\n📊 JURY COMPOSITION (Cook County, IL)")
        print(f"   Total Jurors: {len(jurors)}")
        
        # Age distribution
        ages = [j['demographics']['age'] for j in jurors]
        print(f"\n   Age Range: {min(ages)} - {max(ages)}")
        print(f"   Average Age: {sum(ages)/len(ages):.1f}")
        
        # Gender balance
        male_count = sum(1 for j in jurors if j['demographics']['gender'] == 'Male')
        print(f"\n   Gender Balance:")
        print(f"   - Male: {male_count} ({male_count/len(jurors)*100:.0f}%)")
        print(f"   - Female: {len(jurors)-male_count} ({(len(jurors)-male_count)/len(jurors)*100:.0f}%)")
        
        # Political distribution
        political_views = [j['attitudes']['political_view'] for j in jurors]
        liberal = sum(1 for p in political_views if p <= 3)
        moderate = sum(1 for p in political_views if 3 < p < 5)
        conservative = sum(1 for p in political_views if p >= 5)
        
        print(f"\n   Political Distribution:")
        print(f"   - Liberal: {liberal} jurors")
        print(f"   - Moderate: {moderate} jurors")
        print(f"   - Conservative: {conservative} jurors")
        
        # Leadership potential
        leaders = [j for j in jurors if any("leader" in trait.lower() for trait in j['deliberation_traits'])]
        print(f"\n   Potential Forepersons: {len(leaders)}")
        for leader in leaders:
            print(f"   - Juror #{leader['id']}: {leader['demographics']['age']} y/o {leader['demographics']['gender']}")
        
        # Death penalty stance (for capital case)
        death_penalty_support = sum(j['attitudes']['death_penalty'] for j in jurors) / len(jurors)
        willing = sum(1 for j in jurors if j['attitudes']['death_penalty'] > 0.5)
        print(f"\n   Death Penalty Stance:")
        print(f"   - Willing to impose: {willing} jurors")
        print(f"   - Prefer life sentence: {len(jurors)-willing} jurors")
        print(f"   - Overall support: {death_penalty_support*100:.0f}%")

if __name__ == "__main__":
    test_diverse_counties()
    test_jury_dynamics()
    
    print("\n\n" + "✅ " * 20)
    print("JUROR GENERATION TEST COMPLETE!")
    print("✅ " * 20)
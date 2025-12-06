#!/usr/bin/env python3
"""
Test juror generation API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_generate_jury_pool():
    """Test generating a full jury pool"""
    print("=== TESTING JUROR GENERATION ===\n")
    
    # Test 1: Los Angeles County (Liberal Urban)
    print("1. LOS ANGELES COUNTY, CA (Liberal Urban)")
    print("-" * 50)
    
    response = requests.post(
        f"{BASE_URL}/jurors/generate",
        params={
            "county": "Los Angeles",
            "state": "CA",
            "pool_size": 12,
            "case_type": "drug"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Generated {len(data['jurors'])} jurors")
        
        # Show first 3 jurors
        for i, juror in enumerate(data['jurors'][:3]):
            print(f"\nJuror #{juror['id']}:")
            demo = juror['demographics']
            print(f"  Demographics: {demo['age']} y/o {demo['gender']}, {demo['race']}")
            print(f"  Education: {demo['education_level']} ({demo['education_years']} years)")
            print(f"  Income: ${demo['income']:,}")
            
            att = juror['attitudes']
            print(f"  Political view: {att['political_view']} (1=lib, 7=cons)")
            print(f"  Death penalty support: {att['death_penalty']*100:.0f}%")
            print(f"  Marijuana legalization: {att['marijuana_legal']*100:.0f}%")
            
            pers = juror['personality']
            print(f"  Personality: O={pers['openness']}, C={pers['conscientiousness']}, "
                  f"E={pers['extraversion']}, A={pers['agreeableness']}, N={pers['neuroticism']}")
            
            print(f"  Deliberation traits:")
            for trait in juror['deliberation_traits'][:2]:
                print(f"    - {trait}")
            
            print(f"  Drug case bias: {juror['case_biases'].get('drug_case', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    # Test 2: Harris County, TX (Conservative)
    print("\n\n2. HARRIS COUNTY, TX (Conservative)")
    print("-" * 50)
    
    response = requests.post(
        f"{BASE_URL}/jurors/generate",
        params={
            "county": "Harris",
            "state": "TX",
            "pool_size": 6,
            "case_type": "capital"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Generated {len(data['jurors'])} jurors")
        
        # Show summary statistics
        jurors = data['jurors']
        avg_age = sum(j['demographics']['age'] for j in jurors) / len(jurors)
        avg_political = sum(j['attitudes']['political_view'] for j in jurors) / len(jurors)
        death_penalty_support = sum(j['attitudes']['death_penalty'] for j in jurors) / len(jurors)
        
        print(f"\nPool Statistics:")
        print(f"  Average age: {avg_age:.1f}")
        print(f"  Average political view: {avg_political:.1f} (more conservative)")
        print(f"  Death penalty support: {death_penalty_support*100:.0f}%")
        
        # Count deliberation traits
        all_traits = []
        for juror in jurors:
            all_traits.extend(juror['deliberation_traits'])
        
        print(f"\nTop deliberation traits:")
        from collections import Counter
        trait_counts = Counter(all_traits)
        for trait, count in trait_counts.most_common(3):
            print(f"  - {trait}: {count} jurors")

def test_demographic_stats():
    """Test demographic statistics endpoint"""
    print("\n\n3. DEMOGRAPHIC STATISTICS")
    print("-" * 50)
    
    counties = [
        ("San Francisco", "CA"),
        ("Cook", "IL"),
        ("Harris", "TX"),
        ("Miami-Dade", "FL")
    ]
    
    for county, state in counties:
        response = requests.get(
            f"{BASE_URL}/jurors/demographics/stats",
            params={"county": county, "state": state}
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"\n{county}, {state}:")
            print(f"  Political lean: {stats['attitudes']['political_lean']['mean']:.1f}")
            print(f"  Death penalty support: {stats['attitudes']['death_penalty_support']:.0f}%")
            print(f"  Marijuana legalization: {stats['attitudes']['marijuana_legalization']:.0f}%")
            print(f"  College degree: {stats['demographics']['education']['college_degree_pct']:.0f}%")

def test_single_juror():
    """Test single juror generation"""
    print("\n\n4. SINGLE JUROR WITH SPECIFIC DEMOGRAPHICS")
    print("-" * 50)
    
    response = requests.get(
        f"{BASE_URL}/jurors/sample/CA",
        params={
            "age": 28,
            "gender": "Female",
            "education": 18
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        juror = data['juror']
        
        print(f"Generated custom juror:")
        demo = juror['demographics']
        print(f"  Demographics: {demo['age']} y/o {demo['gender']}")
        print(f"  Education: {demo['education_level']}")
        
        print(f"\n  Full personality profile:")
        pers = juror['personality']
        for trait, value in pers.items():
            print(f"    {trait.capitalize()}: {value}")

if __name__ == "__main__":
    test_generate_jury_pool()
    test_demographic_stats()
    test_single_juror()
    
    print("\n\n" + "="*60)
    print("JUROR GENERATION TESTING COMPLETE!")
    print("="*60)
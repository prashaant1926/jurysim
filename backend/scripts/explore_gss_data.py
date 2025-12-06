#!/usr/bin/env python3
"""
Explore GSS data to understand what's available for jury simulation
"""
import pandas as pd
import numpy as np
from pathlib import Path
import requests
import zipfile
import io

def download_gss_sample():
    """
    Download a sample of GSS data for exploration
    Note: Full dataset requires Kaggle authentication
    """
    print("=== GSS DATA EXPLORATION ===\n")
    
    # For demo, let's create a sample dataset that mimics GSS structure
    print("Creating sample GSS-like data for exploration...")
    
    # GSS variable codes
    sample_data = {
        'year': np.random.choice([2018, 2020, 2022], 1000),
        'age': np.random.randint(18, 90, 1000),
        'sex': np.random.choice([1, 2], 1000),  # 1=male, 2=female
        'race': np.random.choice([1, 2, 3], 1000, p=[0.7, 0.15, 0.15]),  # 1=white, 2=black, 3=other
        'educ': np.random.randint(0, 20, 1000),  # Years of education
        'region': np.random.choice(range(1, 10), 1000),  # 9 US regions
        'polviews': np.random.choice(range(1, 8), 1000),  # 1=extremely liberal to 7=extremely conservative
        'partyid': np.random.choice(range(0, 7), 1000),  # 0=strong democrat to 6=strong republican
        'cappun': np.random.choice([1, 2], 1000, p=[0.6, 0.4]),  # 1=favor death penalty, 2=oppose
        'gunlaw': np.random.choice([1, 2], 1000, p=[0.55, 0.45]),  # 1=favor gun permits, 2=oppose
        'grass': np.random.choice([1, 2], 1000, p=[0.65, 0.35]),  # 1=legal marijuana, 2=not legal
        'trust': np.random.choice([1, 2, 3], 1000, p=[0.35, 0.45, 0.2]),  # 1=can trust, 2=can't be too careful, 3=depends
        'helpful': np.random.choice([1, 2, 3], 1000, p=[0.45, 0.35, 0.2]),  # 1=helpful, 2=look out for themselves, 3=depends
        'fair': np.random.choice([1, 2, 3], 1000, p=[0.3, 0.5, 0.2]),  # 1=fair, 2=take advantage, 3=depends
        'conjudge': np.random.choice([1, 2, 3], 1000, p=[0.25, 0.5, 0.25]),  # Confidence in courts: 1=great deal, 2=only some, 3=hardly any
        'confed': np.random.choice([1, 2, 3], 1000, p=[0.15, 0.45, 0.4]),  # Confidence in federal govt
        'conbus': np.random.choice([1, 2, 3], 1000, p=[0.2, 0.5, 0.3]),  # Confidence in business
        'attend': np.random.choice(range(0, 9), 1000),  # Religious attendance: 0=never to 8=more than once a week
        'income': np.random.choice(range(1, 13), 1000),  # Income categories
    }
    
    df = pd.DataFrame(sample_data)
    
    # Save sample
    sample_path = Path("data/raw/gss_sample.csv")
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(sample_path, index=False)
    print(f"Sample data saved to {sample_path}\n")
    
    return df

def explore_political_attitudes(df):
    """
    Explore political attitudes in GSS data
    """
    print("\n1. POLITICAL VIEWS DISTRIBUTION")
    print("-" * 50)
    polviews_map = {
        1: "Extremely liberal",
        2: "Liberal", 
        3: "Slightly liberal",
        4: "Moderate",
        5: "Slightly conservative",
        6: "Conservative",
        7: "Extremely conservative"
    }
    
    polviews_counts = df['polviews'].value_counts().sort_index()
    for view, count in polviews_counts.items():
        pct = count / len(df) * 100
        print(f"{polviews_map.get(view, view)}: {count} ({pct:.1f}%)")
    
    print("\n2. POLITICAL VIEWS BY REGION")
    print("-" * 50)
    regions = {
        1: "New England",
        2: "Middle Atlantic",
        3: "East North Central", 
        4: "West North Central",
        5: "South Atlantic",
        6: "East South Central",
        7: "West South Central",
        8: "Mountain",
        9: "Pacific"
    }
    
    for region_code, region_name in regions.items():
        region_df = df[df['region'] == region_code]
        if len(region_df) > 0:
            avg_polview = region_df['polviews'].mean()
            print(f"{region_name}: {avg_polview:.2f} (n={len(region_df)})")

def explore_social_attitudes(df):
    """
    Explore social attitudes relevant to jury decisions
    """
    print("\n3. SOCIAL ATTITUDES (% Supporting)")
    print("-" * 50)
    
    attitudes = {
        'cappun': 'Death penalty',
        'gunlaw': 'Gun control',
        'grass': 'Marijuana legalization'
    }
    
    for var, label in attitudes.items():
        support = (df[var] == 1).sum() / len(df) * 100
        print(f"{label}: {support:.1f}%")
    
    print("\n4. TRUST AND FAIRNESS")
    print("-" * 50)
    
    trust_map = {1: "Can trust", 2: "Can't be too careful", 3: "Depends"}
    trust_counts = df['trust'].value_counts()
    for trust_level, count in trust_counts.items():
        pct = count / len(df) * 100
        print(f"{trust_map.get(trust_level, trust_level)}: {pct:.1f}%")

def explore_correlations(df):
    """
    Explore correlations relevant to jury behavior
    """
    print("\n5. KEY CORRELATIONS FOR JURY BEHAVIOR")
    print("-" * 50)
    
    # Political views vs social attitudes
    print("Death penalty support by political view:")
    for polview in range(1, 8):
        pv_df = df[df['polviews'] == polview]
        if len(pv_df) > 0:
            death_penalty_support = (pv_df['cappun'] == 1).mean() * 100
            print(f"  Political view {polview}: {death_penalty_support:.1f}% support")
    
    print("\nTrust in courts by education level:")
    edu_groups = [(0, 11, "No HS"), (12, 12, "HS"), (13, 15, "Some college"), (16, 20, "College+")]
    for min_edu, max_edu, label in edu_groups:
        edu_df = df[(df['educ'] >= min_edu) & (df['educ'] <= max_edu)]
        if len(edu_df) > 0:
            high_trust = (edu_df['conjudge'] == 1).mean() * 100
            print(f"  {label}: {high_trust:.1f}% high trust in courts")

def explore_jury_relevant_profiles(df):
    """
    Create jury-relevant profiles from GSS data
    """
    print("\n6. JURY-RELEVANT PROFILES")
    print("-" * 50)
    
    # Profile 1: Liberal urban professional
    liberal_urban = df[
        (df['polviews'] <= 3) & 
        (df['educ'] >= 16) &
        (df['region'].isin([1, 2, 9]))  # NE, Mid-Atlantic, Pacific
    ]
    
    if len(liberal_urban) > 0:
        print("LIBERAL URBAN PROFESSIONAL PROFILE:")
        print(f"  Sample size: {len(liberal_urban)}")
        print(f"  Avg political view: {liberal_urban['polviews'].mean():.1f}")
        print(f"  Death penalty support: {(liberal_urban['cappun'] == 1).mean() * 100:.1f}%")
        print(f"  Gun control support: {(liberal_urban['gunlaw'] == 1).mean() * 100:.1f}%")
        print(f"  Marijuana legalization: {(liberal_urban['grass'] == 1).mean() * 100:.1f}%")
        print(f"  Trust others: {(liberal_urban['trust'] == 1).mean() * 100:.1f}%")
        print(f"  High trust in courts: {(liberal_urban['conjudge'] == 1).mean() * 100:.1f}%")
    
    # Profile 2: Conservative rural  
    conservative_rural = df[
        (df['polviews'] >= 5) &
        (df['educ'] <= 12) &
        (df['region'].isin([4, 6, 7]))  # Central/Southern regions
    ]
    
    if len(conservative_rural) > 0:
        print("\nCONSERVATIVE RURAL PROFILE:")
        print(f"  Sample size: {len(conservative_rural)}")
        print(f"  Avg political view: {conservative_rural['polviews'].mean():.1f}")
        print(f"  Death penalty support: {(conservative_rural['cappun'] == 1).mean() * 100:.1f}%")
        print(f"  Gun control support: {(conservative_rural['gunlaw'] == 1).mean() * 100:.1f}%")
        print(f"  Marijuana legalization: {(conservative_rural['grass'] == 1).mean() * 100:.1f}%")
        print(f"  Trust others: {(conservative_rural['trust'] == 1).mean() * 100:.1f}%")
        print(f"  High trust in courts: {(conservative_rural['conjudge'] == 1).mean() * 100:.1f}%")

def analyze_for_jury_simulation(df):
    """
    Analyze GSS data specifically for jury simulation needs
    """
    print("\n7. JURY SIMULATION INSIGHTS")
    print("-" * 50)
    
    print("Key findings for AI juror generation:")
    print("\n• Political polarization affects jury views:")
    
    # Get extreme views
    very_liberal = df[df['polviews'] <= 2]
    very_conservative = df[df['polviews'] >= 6]
    
    print(f"  - Very liberal ({len(very_liberal)}): "
          f"{(very_liberal['cappun'] == 1).mean() * 100:.0f}% support death penalty")
    print(f"  - Very conservative ({len(very_conservative)}): "
          f"{(very_conservative['cappun'] == 1).mean() * 100:.0f}% support death penalty")
    
    print("\n• Trust levels affect deliberation:")
    high_trust = df[df['trust'] == 1]
    low_trust = df[df['trust'] == 2]
    print(f"  - High general trust: {len(high_trust)/len(df)*100:.1f}% of population")
    print(f"  - Low general trust: {len(low_trust)/len(df)*100:.1f}% of population")
    
    print("\n• Regional variations are significant:")
    most_liberal_region = df.groupby('region')['polviews'].mean().idxmin()
    most_conservative_region = df.groupby('region')['polviews'].mean().idxmax()
    print(f"  - Most liberal: Region {most_liberal_region}")
    print(f"  - Most conservative: Region {most_conservative_region}")

if __name__ == "__main__":
    # Create or load sample data
    df = download_gss_sample()
    
    print(f"Loaded {len(df)} GSS records")
    print(f"Variables: {', '.join(df.columns)}")
    
    # Explore different aspects
    explore_political_attitudes(df)
    explore_social_attitudes(df)
    explore_correlations(df)
    explore_jury_relevant_profiles(df)
    analyze_for_jury_simulation(df)
    
    print("\n" + "="*60)
    print("GSS DATA SUMMARY FOR JURY SIMULATION:")
    print("="*60)
    print("• Use political views (polviews) to adjust Openness/Conscientiousness")
    print("• Use trust variables to adjust Agreeableness")  
    print("• Use social attitudes for case-specific biases")
    print("• Use regional data for geographic authenticity")
    print("• Combine with census demographics for complete profiles")
    
    print("\nTo get real GSS data:")
    print("1. Visit https://www.kaggle.com/datasets/norc/general-social-survey")
    print("2. Download the full dataset")
    print("3. Replace sample with real data for production use")
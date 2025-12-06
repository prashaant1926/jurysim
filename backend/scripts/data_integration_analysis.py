#!/usr/bin/env python3
"""
Analysis showing how personality data and county election data can be integrated
for AI juror simulation
"""
import pandas as pd
import json

def analyze_data_integration():
    print("=== PERSONALITY + ELECTION DATA INTEGRATION FOR AI JURORS ===\n")
    
    # 1. PERSONALITY DATA INSIGHTS
    print("1. PERSONALITY DATA (1M+ records from 100+ countries)")
    print("-" * 50)
    print("   - Big Five personality traits for each person:")
    print("     • Extraversion (EXT): Social, outgoing vs. reserved")
    print("     • Neuroticism (EST): Emotional stability vs. anxiety")  
    print("     • Agreeableness (AGR): Cooperative vs. competitive")
    print("     • Conscientiousness (CSN): Organized vs. careless")
    print("     • Openness (OPN): Creative, curious vs. conventional")
    print("\n   - Global averages from 1M+ respondents:")
    print("     • Extraversion: 3.02 (scale 1-5)")
    print("     • Neuroticism: 3.02")
    print("     • Agreeableness: 3.16")
    print("     • Conscientiousness: 3.12")
    print("     • Openness: 3.27")
    
    # 2. ELECTION DATA INSIGHTS
    print("\n\n2. COUNTY ELECTION DATA (3,152 U.S. counties)")
    print("-" * 50)
    print("   - 2020 presidential voting percentages")
    print("   - Examples:")
    print("     • Los Angeles, CA: 71% Dem, 27% Rep")
    print("     • Cook County, IL: 74% Dem, 24% Rep")
    print("     • Harris County, TX: 56% Dem, 43% Rep")
    
    # 3. INTEGRATION STRATEGY
    print("\n\n3. HOW TO COMBINE FOR AI JURORS")
    print("-" * 50)
    print("\n   A. County Demographics → Personality Mapping:")
    print("      1. Use county voting patterns as proxy for political orientation")
    print("      2. Research shows correlations:")
    print("         - Liberal areas: Higher Openness, lower Conscientiousness")
    print("         - Conservative areas: Higher Conscientiousness, lower Openness")
    print("         - Urban vs Rural: Different Extraversion patterns")
    
    print("\n   B. Juror Generation Algorithm:")
    print("      1. Input: County (e.g., 'Los Angeles, CA')")
    print("      2. Get county voting data (71% Dem, 27% Rep)")
    print("      3. Sample from personality distributions weighted by:")
    print("         - Political lean affects Openness/Conscientiousness")
    print("         - Urban/rural affects Extraversion")
    print("         - Add random variation for realism")
    print("      4. Generate 12 unique juror profiles")
    
    print("\n   C. Example Juror Profile:")
    print("      County: Los Angeles (71% Democratic)")
    print("      Juror #1:")
    print("         - Age: 34 (from Census PUMS)")
    print("         - Gender: Female")
    print("         - Race: Hispanic")
    print("         - Education: Bachelor's degree")
    print("         - Income: $65,000")
    print("         - Personality:")
    print("           • Openness: 3.8 (higher due to liberal county)")
    print("           • Conscientiousness: 2.9 (slightly lower)")
    print("           • Extraversion: 3.4 (urban = more social)")
    print("           • Agreeableness: 3.2")
    print("           • Neuroticism: 3.1")
    
    # 4. IMPLEMENTATION APPROACH
    print("\n\n4. IMPLEMENTATION APPROACH")
    print("-" * 50)
    print("   Step 1: Create personality distributions by political lean")
    print("   Step 2: Adjust for urban/rural characteristics")
    print("   Step 3: Layer in Census demographics (age, race, education)")
    print("   Step 4: Generate 12 diverse but county-appropriate jurors")
    print("   Step 5: Use Anthropic API to simulate deliberations based on:")
    print("           - Personality traits")
    print("           - Demographics")
    print("           - Political context")
    
    # 5. KEY INSIGHTS
    print("\n\n5. KEY INSIGHTS FOR YOUR APP")
    print("-" * 50)
    print("   • Personality data provides psychological realism")
    print("   • Election data provides political/cultural context")
    print("   • Census data provides demographic accuracy")
    print("   • Combined: Realistic AI jurors that reflect actual county makeup")
    print("\n   The magic is in the correlations:")
    print("   - Conservative counties → Different personality distributions")
    print("   - Urban vs rural → Different social traits")
    print("   - Education levels → Affect openness and deliberation style")
    print("   - Income → Influences perspectives on economic issues")

if __name__ == "__main__":
    analyze_data_integration()
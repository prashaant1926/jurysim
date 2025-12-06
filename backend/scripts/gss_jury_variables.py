#!/usr/bin/env python3
"""
Key GSS variables for jury simulation with explanations
"""

def show_gss_jury_variables():
    print("=== KEY GSS VARIABLES FOR AI JURY SIMULATION ===\n")
    
    print("1. CORE DEMOGRAPHICS")
    print("-" * 60)
    demographics = {
        'age': 'Age of respondent (18-89+)',
        'sex': 'Sex (1=Male, 2=Female)',
        'race': 'Race (1=White, 2=Black, 3=Other)',
        'educ': 'Years of education (0-20+)',
        'income': 'Total family income (1-12 scale)',
        'region': 'Region of interview (1-9, see below)',
        'srcbelt': 'City size (1=12 largest SMSAs to 6=Other rural)'
    }
    for var, desc in demographics.items():
        print(f"  {var:10} - {desc}")
    
    print("\n  REGIONS:")
    regions = {
        1: "New England (ME, VT, NH, MA, CT, RI)",
        2: "Middle Atlantic (NY, NJ, PA)", 
        3: "East North Central (WI, IL, IN, MI, OH)",
        4: "West North Central (MN, IA, MO, ND, SD, NE, KS)",
        5: "South Atlantic (DE, MD, DC, WV, VA, NC, SC, GA, FL)",
        6: "East South Central (KY, TN, AL, MS)",
        7: "West South Central (AR, OK, LA, TX)",
        8: "Mountain (MT, ID, WY, NV, UT, CO, AZ, NM)",
        9: "Pacific (WA, OR, CA, AK, HI)"
    }
    for code, region in regions.items():
        print(f"    {code}: {region}")
    
    print("\n2. POLITICAL ORIENTATION")
    print("-" * 60)
    political = {
        'polviews': 'Political views scale',
        'partyid': 'Political party affiliation',
        'vote16': 'Did R vote in 2016 election',
        'pres16': 'Vote for Clinton, Trump, other',
        'polint': 'Interest in politics'
    }
    for var, desc in political.items():
        print(f"  {var:10} - {desc}")
    
    print("\n  POLVIEWS SCALE:")
    print("    1 = Extremely liberal")
    print("    2 = Liberal")
    print("    3 = Slightly liberal")
    print("    4 = Moderate")
    print("    5 = Slightly conservative")
    print("    6 = Conservative")
    print("    7 = Extremely conservative")
    
    print("\n3. CRIMINAL JUSTICE ATTITUDES (Critical for jury duty)")
    print("-" * 60)
    criminal_justice = {
        'cappun': 'Favor or oppose death penalty for murder',
        'courts': 'Courts dealing with criminals (too harsh/not harsh enough)',
        'gunlaw': 'Favor or oppose gun permits',
        'grass': 'Should marijuana be made legal',
        'polhitok': 'Are there situations where police hitting citizen OK',
        'polescap': 'Citizen right to escape if unjustly imprisoned',
        'polmurdr': 'OK for citizen to kill to escape oppression'
    }
    for var, desc in criminal_justice.items():
        print(f"  {var:10} - {desc}")
    
    print("\n4. TRUST & INSTITUTIONAL CONFIDENCE (Affects witness credibility)")
    print("-" * 60)
    trust = {
        'trust': 'Can people be trusted',
        'helpful': 'People try to be helpful or looking out for selves',
        'fair': 'People try to be fair or take advantage',
        'conjudge': 'Confidence in courts and legal system',
        'confed': 'Confidence in federal government',
        'conlegis': 'Confidence in Congress',
        'conpolice': 'Confidence in police',
        'conpress': 'Confidence in press'
    }
    for var, desc in trust.items():
        print(f"  {var:10} - {desc}")
    
    print("\n  CONFIDENCE SCALE:")
    print("    1 = A great deal")
    print("    2 = Only some")
    print("    3 = Hardly any")
    
    print("\n5. SOCIAL ATTITUDES (Affects case biases)")
    print("-" * 60)
    social = {
        'abany': 'Abortion if woman wants for any reason',
        'divlaw': 'Should divorce be easier/more difficult',
        'premarsx': 'Sex before marriage wrong',
        'homosex': 'Sexual relations between same sex',
        'racmar': 'Favor law against interracial marriage',
        'affrmact': 'Affirmative action views',
        'natrace': 'Improving conditions of Blacks (spending too much/little)'
    }
    for var, desc in social.items():
        print(f"  {var:10} - {desc}")
    
    print("\n6. PERSONALITY PROXIES (For Big Five mapping)")
    print("-" * 60)
    personality = {
        'getahead': 'How people get ahead (hard work vs luck/help)',
        'workhard': 'Importance of hard work for getting ahead',
        'obey': 'Child should learn to obey (relates to Conscientiousness)',
        'popular': 'Child should be popular (relates to Extraversion)',
        'thnkself': 'Child should think for self (relates to Openness)',
        'helpoth': 'Child should help others (relates to Agreeableness)',
        'workhard': 'Child should work hard (relates to Conscientiousness)'
    }
    for var, desc in personality.items():
        print(f"  {var:10} - {desc}")
    
    print("\n7. HOW TO USE FOR JURY SIMULATION")
    print("-" * 60)
    print("STEP 1: Match juror demographics to GSS respondents")
    print("  - Filter by age, education, region")
    print("  - Find similar demographic profiles")
    
    print("\nSTEP 2: Extract attitude profile")
    print("  - Political orientation → Initial verdict lean")
    print("  - Criminal justice attitudes → Sentencing preferences")
    print("  - Trust levels → Witness credibility assessment")
    
    print("\nSTEP 3: Map to personality traits")
    print("  - Liberal (polviews 1-3) → +0.4 Openness, -0.3 Conscientiousness")
    print("  - Conservative (polviews 5-7) → -0.3 Openness, +0.4 Conscientiousness")
    print("  - High trust → +0.3 Agreeableness")
    print("  - Urban (srcbelt 1-3) → +0.2 Extraversion")
    
    print("\nSTEP 4: Apply to specific case types")
    print("  - Drug case: Check 'grass' variable")
    print("  - Death penalty case: Check 'cappun' variable")
    print("  - Police brutality: Check 'polhitok' variable")
    print("  - White collar crime: Check 'conbus' confidence in business")

def show_case_specific_analysis():
    print("\n\n=== CASE-SPECIFIC GSS VARIABLES ===\n")
    
    cases = {
        "MURDER/DEATH PENALTY CASE": {
            'variables': ['cappun', 'courts', 'conjudge'],
            'insights': [
                "cappun=1 (favor death penalty) → More likely guilty verdict",
                "courts=3 (not harsh enough) → Harsher sentencing preference",
                "Low conjudge → May discount judge instructions"
            ]
        },
        
        "DRUG POSSESSION CASE": {
            'variables': ['grass', 'polviews', 'age'],
            'insights': [
                "grass=1 (legalize) → More sympathetic to defendant",
                "Younger + liberal → Focus on rehabilitation",
                "Older + conservative → Focus on punishment"
            ]
        },
        
        "POLICE BRUTALITY CASE": {
            'variables': ['polhitok', 'conpolice', 'race', 'polviews'],
            'insights': [
                "polhitok=1 (hitting OK sometimes) → Pro-police bias",
                "High conpolice → Trust police testimony more",
                "Race affects perspective on police interactions",
                "Liberal → More critical of police actions"
            ]
        },
        
        "WHITE COLLAR CRIME": {
            'variables': ['conbus', 'confed', 'income', 'educ'],
            'insights': [
                "Low conbus → Harsher on corporate defendants",
                "High education → Better understands complex evidence",
                "High income → May relate to defendant",
                "Low confed → Skeptical of regulatory violations"
            ]
        },
        
        "SEXUAL ASSAULT CASE": {
            'variables': ['feminism', 'sex', 'age', 'trust'],
            'insights': [
                "Support feminism → Believe victims more",
                "Low general trust → More skeptical of testimony",
                "Generational differences in attitudes",
                "Gender affects perspective but not deterministic"
            ]
        }
    }
    
    for case_type, details in cases.items():
        print(f"{case_type}:")
        print(f"  Key variables: {', '.join(details['variables'])}")
        print("  Insights:")
        for insight in details['insights']:
            print(f"    - {insight}")
        print()

if __name__ == "__main__":
    show_gss_jury_variables()
    show_case_specific_analysis()
    
    print("\n" + "="*60)
    print("IMPLEMENTATION TIPS:")
    print("="*60)
    print("1. Download full GSS dataset from Kaggle")
    print("2. Create lookup tables for each variable")
    print("3. Build probability distributions by demographics")
    print("4. Sample from distributions when generating jurors")
    print("5. Adjust personality traits based on attitudes")
    print("6. Use case-specific variables for initial positions")
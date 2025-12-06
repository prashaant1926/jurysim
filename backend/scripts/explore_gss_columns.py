#!/usr/bin/env python3
"""
Find key GSS variables for jury simulation
"""
import pandas as pd

# Key variables we're looking for
key_vars = [
    'age', 'sex', 'race', 'educ', 'region', 'polviews', 'partyid',
    'cappun', 'gunlaw', 'grass', 'trust', 'helpful', 'fair',
    'conjudge', 'confed', 'conpolice', 'courts', 'income'
]

print("Loading GSS data...")
df = pd.read_csv('data/raw/gss_data.csv', nrows=1000)

print(f"\nTotal columns: {len(df.columns)}")
print("\nSearching for key variables...")

# Find columns that match our key variables
found_columns = {}
for var in key_vars:
    matching = [col for col in df.columns if var.upper() in col.upper() and not col.endswith('_labels')]
    if matching:
        found_columns[var] = matching

print("\nFound columns:")
for var, cols in found_columns.items():
    print(f"\n{var}:")
    for col in cols[:3]:  # Show first 3 matches
        print(f"  - {col}")
        if len(cols) > 3:
            print(f"  ... and {len(cols)-3} more")

# Check specific important columns
print("\n\nChecking specific columns:")
specific_checks = [
    'AGE OF RESPONDENT',
    'RESPONDENTS SEX',
    'RACE OF RESPONDENT',
    'HIGHEST YEAR OF SCHOOL COMPLETED',
    'REGION OF INTERVIEW',
    'THINK OF SELF AS LIBERAL OR CONSERVATIVE',
    'POLITICAL PARTY AFFILIATION',
    'FAVOR OR OPPOSE DEATH PENALTY FOR MURDER',
    'SHOULD MARIJUANA BE MADE LEGAL',
    'CAN PEOPLE BE TRUSTED',
    'CONFIDENCE IN BANKS & FINANCIAL INSTITUTIONS',
    'TOTAL FAMILY INCOME'
]

for check in specific_checks:
    matches = [col for col in df.columns if check in col.upper()]
    if matches:
        print(f"\n{check}:")
        print(f"  Found: {matches[0]}")

# Save a mapping file
mapping = {
    'age': 'AGE OF RESPONDENT',
    'sex': 'RESPONDENTS SEX', 
    'race': 'RACE OF RESPONDENT',
    'educ': 'HIGHEST YEAR OF SCHOOL COMPLETED',
    'region': 'REGION OF INTERVIEW',
    'polviews': 'THINK OF SELF AS LIBERAL OR CONSERVATIVE',
    'partyid': 'POLITICAL PARTY AFFILIATION',
    'cappun': 'FAVOR OR OPPOSE DEATH PENALTY FOR MURDER',
    'grass': 'SHOULD MARIJUANA BE MADE LEGAL',
    'trust': 'CAN PEOPLE BE TRUSTED'
}

# Check if these exact columns exist
print("\n\nVerifying exact column names:")
for var, col_name in mapping.items():
    exists = any(col_name in c for c in df.columns)
    print(f"{var}: {col_name} - {'FOUND' if exists else 'NOT FOUND'}")
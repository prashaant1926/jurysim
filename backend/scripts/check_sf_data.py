#!/usr/bin/env python3
import pandas as pd

# Load GSS data
df = pd.read_csv('data/raw/gss_data.csv', nrows=60000, low_memory=False)

# Check Pacific region (9) data
pacific = df[df['REGION OF INTERVIEW'] == 9]
print(f"Total Pacific region responses: {len(pacific)}")

# Check gun permit attitudes in Pacific
gun_col = 'FAVOR OR OPPOSE GUN PERMITS'
gun_label = 'FAVOR OR OPPOSE GUN PERMITS_labels'

if gun_col in pacific.columns and gun_label in pacific.columns:
    valid_gun = pacific[(pacific[gun_label] != 'IAP') & (pacific[gun_label].notna())]
    print(f"\nGun permit responses in Pacific: {len(valid_gun)}")
    
    if len(valid_gun) > 0:
        favor = (valid_gun[gun_col] == 1).sum()
        oppose = (valid_gun[gun_col] == 2).sum()
        print(f"Favor: {favor}, Oppose: {oppose}")
        if favor + oppose > 0:
            print(f"Actual Pacific gun permit support: {favor / (favor + oppose) * 100:.1f}%")

# Check by political views
pol_col = 'THINK OF SELF AS LIBERAL OR CONSERVATIVE'
pol_label = 'THINK OF SELF AS LIBERAL OR CONSERVATIVE_labels'

if pol_col in df.columns and gun_col in df.columns:
    # Very liberal (1-2)
    very_lib = df[(df[pol_col].isin([1, 2])) & (df[gun_label] != 'IAP')]
    if len(very_lib) > 0:
        vl_gun_support = (very_lib[gun_col] == 1).sum() / len(very_lib[very_lib[gun_col].isin([1,2])])
        print(f"\nVery Liberal gun permit support: {vl_gun_support * 100:.1f}%")
    
    # Liberal (3)
    lib = df[(df[pol_col] == 3) & (df[gun_label] != 'IAP')]
    if len(lib) > 0:
        l_gun_support = (lib[gun_col] == 1).sum() / len(lib[lib[gun_col].isin([1,2])])
        print(f"Liberal gun permit support: {l_gun_support * 100:.1f}%")
    
    # Conservative (5-7)
    cons = df[(df[pol_col].isin([5, 6, 7])) & (df[gun_label] != 'IAP')]
    if len(cons) > 0:
        c_gun_support = (cons[gun_col] == 1).sum() / len(cons[cons[gun_col].isin([1,2])])
        print(f"Conservative gun permit support: {c_gun_support * 100:.1f}%")
# FreudLaw Data Collection Summary

## Current Data Sources

### 1. ✅ Census Data (ACS PUMS)
- **Status**: Configured with API key
- **Source**: 2022 ACS 1-Year PUMS data
- **Key**: Already set in .env
- **Variables**: Age, Sex, Race, Education, Income, PUMA codes
- **API**: `/api/v1/data/census/fetch`

### 2. ✅ Personality Data (Big Five)
- **Status**: Successfully downloaded (1M+ records)
- **Source**: IPIP-FFM dataset from OpenPsychometrics
- **Location**: `data/raw/IPIP-FFM-data-8Nov2018/data-final.csv`
- **Variables**: Big Five scores (EXT, EST, AGR, CSN, OPN)
- **API**: `/api/v1/data/personality/download`

### 3. ✅ Election Data
- **Status**: Downloaded (3,152 counties)
- **Source**: MIT Election Data Lab
- **Location**: `data/raw/county_election_2020.csv`
- **Variables**: County-level 2020 presidential results
- **API**: `/api/v1/data/election/county`

### 4. ⏳ GSS Data (General Social Survey)
- **Status**: Ready to download (requires Kaggle auth)
- **Source**: NORC/University of Chicago via Kaggle
- **Variables**: 
  - Political views, party affiliation
  - Social attitudes (death penalty, gun control, etc.)
  - Trust in institutions
  - Regional variations
- **Setup Required**:
  1. Create Kaggle account
  2. Get API token from kaggle.com/account
  3. Save to ~/.kaggle/kaggle.json
  4. Run: `python download_gss_simple.py`

## Data Integration Flow

```
County Selection
     ↓
Census Data → Demographics (age, race, education, income)
     ↓
Election Data → Political context (% Dem/Rep)
     ↓
GSS Data → Social attitudes based on demographics
     ↓
Personality Data → Big Five traits adjusted by attitudes
     ↓
Complete AI Juror Profile
```

## API Endpoints

- `GET /api/v1/data/sources` - List all data sources
- `POST /api/v1/data/census/fetch` - Fetch census data
- `POST /api/v1/data/personality/download` - Download personality data
- `POST /api/v1/data/election/download` - Download election data
- `GET /api/v1/data/election/county` - Get county election results
- `GET /api/v1/data/gss/info` - GSS information and setup
- `GET /api/v1/data/gss/political-attitudes` - Political attitudes by region
- `POST /api/v1/data/gss/jury-profile` - Get jury-relevant GSS profile

## How Data Works Together

1. **Census**: Provides base demographics
2. **Election**: Adds political context
3. **GSS**: Adds social attitudes and trust levels
4. **Personality**: Adjusted based on all above factors

Example:
- Los Angeles County → 71% Democratic
- 35-year-old college graduate → GSS liberal profile
- Liberal + urban → Higher Openness (+0.4)
- Result: Juror open to novel legal arguments

## Next Steps

1. **Download GSS Data** (follow setup instructions)
2. **Test Full Integration** with all data sources
3. **Build Juror Generation Engine** combining all data
4. **Add Anthropic API** for deliberation simulation
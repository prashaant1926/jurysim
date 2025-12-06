# Census Data Integration

## Overview

The FreudLaw backend now integrates real U.S. Census data to create demographically accurate jurors for each county.

## Data Sources

### Census API Tables Used

1. **Age and Sex (Table B01001)**
   - Detailed age breakdowns by gender
   - Groups: 18-29, 30-39, 40-49, 50-59, 60-69, 70-80

2. **Race (Table B02001)**
   - White, Black, Asian, American Indian, Pacific Islander
   - Two or more races
   - Hispanic/Latino ethnicity (Table B03002)

3. **Education (Table B15003)**
   - Detailed educational attainment for population 25+
   - Maps to: High school, Some college, Bachelor's, Graduate degrees

4. **Income (Tables B19001 & B19013)**
   - Household income distribution in 16 brackets
   - Median household income for the county

## Implementation

### Data Flow

1. **API Call**: When generating jurors for a county, the system:
   - Converts state abbreviation to FIPS code
   - Fetches county FIPS by matching county name
   - Makes 4 API calls for demographic tables

2. **Caching**: Data is cached in `data/raw/census_cache/`
   - Format: `{state_fips}_{county_name}_demographics.json`
   - Prevents repeated API calls

3. **Distribution Calculation**:
   - Converts raw counts to probability distributions
   - Handles race/ethnicity overlap
   - Maps education categories to years

### Usage in Juror Generation

```python
# Real age distribution
age_key = random.choices(
    list(distributions['age_weights'].keys()),
    weights=list(distributions['age_weights'].values())
)[0]

# Real race distribution
race = random.choices(
    list(distributions['race_weights'].keys()),
    weights=list(distributions['race_weights'].values())
)[0]

# Income based on county median
income = int(random.gauss(median, median * 0.4))
```

## Benefits

1. **County-Specific Demographics**: Each county has unique:
   - Age distribution
   - Racial/ethnic composition
   - Education levels
   - Income distribution

2. **Realistic Representation**:
   - San Francisco: High Asian population, high education
   - Rural Texas: Less diverse, lower education
   - Urban Ohio: Higher Black population, mixed income

3. **Data-Driven**: No more hardcoded urban/rural assumptions

## Cached Counties

The following counties have been pre-cached:
- San Francisco, CA (06075)
- Los Angeles, CA (06037)
- Harris, TX (48201)
- Cook, IL (17031)
- Cuyahoga, OH (39035)
- New York, NY (36001)
- Miami-Dade, FL (12086)

## API Key

Uses the Census API key from `.env`:
```
CENSUS_API_KEY=00306956484ad723c26d84b932fa6d1307284d50
```

## Fallback Behavior

If Census data is unavailable:
1. Logs warning
2. Uses original demographic generation
3. Still incorporates election and GSS data
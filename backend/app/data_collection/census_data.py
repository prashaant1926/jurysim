import httpx
import pandas as pd
from typing import List, Dict, Optional, Tuple
import asyncio
from app.core.config import settings
from app.models.demographics import ACSPUMSRecord, DataSource
import logging
import json
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class CensusDataCollector:
    def __init__(self):
        self.api_key = settings.CENSUS_API_KEY
        self.base_url = "https://api.census.gov/data"
        self.year = "2022"
        self.dataset = "acs/acs5"  # Changed to 5-year for county-level data
        self.cache_dir = Path("data/raw/census_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    async def get_state_puma_data(
        self, 
        state_fips: str, 
        puma_codes: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Fetch ACS PUMS data for a specific state and optionally specific PUMAs
        """
        fields = "AGEP,SEX,RAC1P,SCHL,HINCP,PUMA,PWGTP"
        
        url = f"{self.base_url}/{self.year}/{self.dataset}"
        
        params = {
            "get": fields,
            "for": f"state:{state_fips}",
            "key": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                df = pd.DataFrame(data[1:], columns=data[0])
                
                if puma_codes:
                    df = df[df['PUMA'].isin(puma_codes)]
                
                return df
                
            except httpx.HTTPError as e:
                logger.error(f"Error fetching census data: {e}")
                raise
    
    def parse_pums_records(self, df: pd.DataFrame) -> List[ACSPUMSRecord]:
        """
        Convert raw census data to structured records
        """
        records = []
        
        for _, row in df.iterrows():
            try:
                record = ACSPUMSRecord(
                    AGEP=int(row['AGEP']) if pd.notna(row['AGEP']) else 0,
                    SEX=row['SEX'],
                    RAC1P=row['RAC1P'],
                    SCHL=row['SCHL'] if pd.notna(row['SCHL']) else "01",
                    HINCP=int(row['HINCP']) if pd.notna(row['HINCP']) else None,
                    PUMA=row['PUMA'],
                    STATEFIP=row['state']
                )
                records.append(record)
            except Exception as e:
                logger.warning(f"Error parsing record: {e}")
                continue
                
        return records
    
    async def get_county_puma_mapping(self, state_fips: str) -> Dict[str, List[str]]:
        """
        Get mapping of counties to PUMA codes for a state
        """
        url = f"https://www2.census.gov/geo/docs/maps-data/data/rel2020/puma520/tab20_puma520_county20_{state_fips}.txt"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                df = pd.read_csv(
                    pd.io.common.StringIO(response.text),
                    delimiter='|'
                )
                
                county_puma_map = {}
                for county in df['COUNTYNAME'].unique():
                    pumas = df[df['COUNTYNAME'] == county]['PUMA5'].unique().tolist()
                    county_puma_map[county] = [str(p).zfill(5) for p in pumas]
                
                return county_puma_map
                
            except Exception as e:
                logger.error(f"Error fetching PUMA mapping: {e}")
                return {}
    
    def get_data_source_info(self) -> DataSource:
        """
        Return metadata about the data source
        """
        return DataSource(
            name="American Community Survey",
            url=f"{self.base_url}/{self.year}/{self.dataset}",
            last_updated=f"{self.year} 5-year estimates",
            fields_used=["AGEP", "SEX", "RAC1P", "SCHL", "HINCP", "PUMA", "STATEFIP"],
            description="American Community Survey data from the U.S. Census Bureau"
        )
    
    async def get_county_demographics(self, state_fips: str, county_name: str) -> Dict[str, any]:
        """
        Fetch detailed demographic data for a specific county
        """
        # Check cache first
        cache_file = self.cache_dir / f"{state_fips}_{county_name.replace(' ', '_')}_demographics.json"
        if cache_file.exists():
            logger.info(f"Loading cached demographics for {county_name}, {state_fips}")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        logger.info(f"Fetching demographics for {county_name}, {state_fips}")
        
        # Get county FIPS code
        county_fips = await self._get_county_fips(state_fips, county_name)
        if not county_fips:
            logger.error(f"Could not find FIPS code for {county_name}, {state_fips}")
            return None
        
        # Fetch all demographic data
        demographics = {
            'state_fips': state_fips,
            'county_fips': county_fips,
            'county_name': county_name
        }
        
        # Fetch different demographic tables
        demographics['age_sex'] = await self._fetch_age_sex_data(state_fips, county_fips)
        demographics['race'] = await self._fetch_race_data(state_fips, county_fips)
        demographics['education'] = await self._fetch_education_data(state_fips, county_fips)
        demographics['income'] = await self._fetch_income_data(state_fips, county_fips)
        
        # Calculate distributions
        demographics['distributions'] = self._calculate_distributions(demographics)
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(demographics, f, indent=2)
        
        return demographics
    
    async def _get_county_fips(self, state_fips: str, county_name: str) -> Optional[str]:
        """Get county FIPS code from county name"""
        url = f"{self.base_url}/{self.year}/{self.dataset}"
        params = {
            "get": "NAME",
            "for": f"county:*",
            "in": f"state:{state_fips}",
            "key": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Find matching county
                for row in data[1:]:  # Skip header
                    if county_name.lower() in row[0].lower():
                        return row[2]  # County FIPS is third element
                
                return None
            except Exception as e:
                logger.error(f"Error getting county FIPS: {e}")
                return None
    
    async def _fetch_age_sex_data(self, state_fips: str, county_fips: str) -> Dict:
        """Fetch age and sex distribution data"""
        # Age groups we care about for jury eligibility (18+)
        age_vars = [
            "B01001_007E", "B01001_008E", "B01001_009E", "B01001_010E",  # Male 18-34
            "B01001_011E", "B01001_012E", "B01001_013E", "B01001_014E",  # Male 35-54
            "B01001_015E", "B01001_016E", "B01001_017E", "B01001_018E",  # Male 55-74
            "B01001_019E", "B01001_020E", "B01001_021E", "B01001_022E",  # Male 75+
            "B01001_031E", "B01001_032E", "B01001_033E", "B01001_034E",  # Female 18-34
            "B01001_035E", "B01001_036E", "B01001_037E", "B01001_038E",  # Female 35-54
            "B01001_039E", "B01001_040E", "B01001_041E", "B01001_042E",  # Female 55-74
            "B01001_043E", "B01001_044E", "B01001_045E", "B01001_046E"   # Female 75+
        ]
        
        url = f"{self.base_url}/{self.year}/{self.dataset}"
        params = {
            "get": ",".join(["NAME", "B01001_002E", "B01001_026E"] + age_vars),
            "for": f"county:{county_fips}",
            "in": f"state:{state_fips}",
            "key": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if len(data) > 1:
                    headers = data[0]
                    values = data[1]
                    result = dict(zip(headers, values))
                    
                    # Group age data
                    age_groups = {
                        '18-29': sum(int(result.get(f"B01001_{i:03d}E", 0)) for i in [7,8,31,32]),
                        '30-39': sum(int(result.get(f"B01001_{i:03d}E", 0)) for i in [9,10,33,34]),
                        '40-49': sum(int(result.get(f"B01001_{i:03d}E", 0)) for i in [11,12,35,36]),
                        '50-59': sum(int(result.get(f"B01001_{i:03d}E", 0)) for i in [13,14,37,38]),
                        '60-69': sum(int(result.get(f"B01001_{i:03d}E", 0)) for i in [15,16,39,40]),
                        '70-80': sum(int(result.get(f"B01001_{i:03d}E", 0)) for i in [17,18,19,41,42,43])
                    }
                    
                    return {
                        'total_male': int(result.get('B01001_002E', 0)),
                        'total_female': int(result.get('B01001_026E', 0)),
                        'age_groups': age_groups
                    }
                    
            except Exception as e:
                logger.error(f"Error fetching age/sex data: {e}")
                return {}
    
    async def _fetch_race_data(self, state_fips: str, county_fips: str) -> Dict:
        """Fetch race and ethnicity data"""
        url = f"{self.base_url}/{self.year}/{self.dataset}"
        params = {
            "get": "NAME,B02001_002E,B02001_003E,B02001_004E,B02001_005E,B02001_006E,B02001_007E,B02001_008E,B03002_012E",
            "for": f"county:{county_fips}",
            "in": f"state:{state_fips}",
            "key": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if len(data) > 1:
                    headers = data[0]
                    values = data[1]
                    result = dict(zip(headers, values))
                    
                    return {
                        'white': int(result.get('B02001_002E', 0)),
                        'black': int(result.get('B02001_003E', 0)),
                        'american_indian': int(result.get('B02001_004E', 0)),
                        'asian': int(result.get('B02001_005E', 0)),
                        'pacific_islander': int(result.get('B02001_006E', 0)),
                        'other': int(result.get('B02001_007E', 0)),
                        'two_or_more': int(result.get('B02001_008E', 0)),
                        'hispanic': int(result.get('B03002_012E', 0))
                    }
                    
            except Exception as e:
                logger.error(f"Error fetching race data: {e}")
                return {}
    
    async def _fetch_education_data(self, state_fips: str, county_fips: str) -> Dict:
        """Fetch education attainment data for population 25+"""
        # Education variables from table B15003
        edu_vars = {
            'less_than_hs': ["B15003_002E", "B15003_003E", "B15003_004E", "B15003_005E", 
                            "B15003_006E", "B15003_007E", "B15003_008E", "B15003_009E",
                            "B15003_010E", "B15003_011E", "B15003_012E", "B15003_013E",
                            "B15003_014E", "B15003_015E", "B15003_016E"],
            'high_school': ["B15003_017E", "B15003_018E"],
            'some_college': ["B15003_019E", "B15003_020E", "B15003_021E"],
            'bachelors': ["B15003_022E"],
            'graduate': ["B15003_023E", "B15003_024E", "B15003_025E"]
        }
        
        all_vars = [var for vars in edu_vars.values() for var in vars]
        
        url = f"{self.base_url}/{self.year}/{self.dataset}"
        params = {
            "get": ",".join(["NAME"] + all_vars),
            "for": f"county:{county_fips}",
            "in": f"state:{state_fips}",
            "key": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if len(data) > 1:
                    headers = data[0]
                    values = data[1]
                    result = dict(zip(headers, values))
                    
                    education = {}
                    for level, vars in edu_vars.items():
                        education[level] = sum(int(result.get(var, 0)) for var in vars)
                    
                    return education
                    
            except Exception as e:
                logger.error(f"Error fetching education data: {e}")
                return {}
    
    async def _fetch_income_data(self, state_fips: str, county_fips: str) -> Dict:
        """Fetch household income distribution"""
        # Income brackets from table B19001
        income_vars = [
            "B19001_002E", "B19001_003E", "B19001_004E", "B19001_005E",
            "B19001_006E", "B19001_007E", "B19001_008E", "B19001_009E",
            "B19001_010E", "B19001_011E", "B19001_012E", "B19001_013E",
            "B19001_014E", "B19001_015E", "B19001_016E", "B19001_017E"
        ]
        
        url = f"{self.base_url}/{self.year}/{self.dataset}"
        params = {
            "get": ",".join(["NAME", "B19013_001E"] + income_vars),  # B19013_001E is median income
            "for": f"county:{county_fips}",
            "in": f"state:{state_fips}",
            "key": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if len(data) > 1:
                    headers = data[0]
                    values = data[1]
                    result = dict(zip(headers, values))
                    
                    income_brackets = {
                        'under_10k': int(result.get('B19001_002E', 0)),
                        '10k_15k': int(result.get('B19001_003E', 0)),
                        '15k_20k': int(result.get('B19001_004E', 0)),
                        '20k_25k': int(result.get('B19001_005E', 0)),
                        '25k_30k': int(result.get('B19001_006E', 0)),
                        '30k_35k': int(result.get('B19001_007E', 0)),
                        '35k_40k': int(result.get('B19001_008E', 0)),
                        '40k_45k': int(result.get('B19001_009E', 0)),
                        '45k_50k': int(result.get('B19001_010E', 0)),
                        '50k_60k': int(result.get('B19001_011E', 0)),
                        '60k_75k': int(result.get('B19001_012E', 0)),
                        '75k_100k': int(result.get('B19001_013E', 0)),
                        '100k_125k': int(result.get('B19001_014E', 0)),
                        '125k_150k': int(result.get('B19001_015E', 0)),
                        '150k_200k': int(result.get('B19001_016E', 0)),
                        '200k_plus': int(result.get('B19001_017E', 0))
                    }
                    
                    return {
                        'median_income': int(result.get('B19013_001E', 0)),
                        'brackets': income_brackets
                    }
                    
            except Exception as e:
                logger.error(f"Error fetching income data: {e}")
                return {}
    
    def _calculate_distributions(self, demographics: Dict) -> Dict:
        """Calculate probability distributions from raw counts"""
        distributions = {}
        
        # Age distribution
        if 'age_sex' in demographics and 'age_groups' in demographics['age_sex']:
            age_groups = demographics['age_sex']['age_groups']
            total_age = sum(age_groups.values())
            if total_age > 0:
                distributions['age_weights'] = {
                    k: v / total_age for k, v in age_groups.items()
                }
                distributions['age_ranges'] = {
                    '18-29': (18, 29),
                    '30-39': (30, 39),
                    '40-49': (40, 49),
                    '50-59': (50, 59),
                    '60-69': (60, 69),
                    '70-80': (70, 80)
                }
        
        # Sex distribution
        if 'age_sex' in demographics:
            total_male = demographics['age_sex'].get('total_male', 0)
            total_female = demographics['age_sex'].get('total_female', 0)
            total_pop = total_male + total_female
            if total_pop > 0:
                distributions['sex_weights'] = {
                    'Male': total_male / total_pop,
                    'Female': total_female / total_pop
                }
        
        # Race distribution
        if 'race' in demographics:
            race_data = demographics['race']
            # Adjust for Hispanic ethnicity (can be any race)
            hispanic_count = race_data.get('hispanic', 0)
            
            # Simple approach: proportionally reduce other races by Hispanic percentage
            total_race = sum(v for k, v in race_data.items() if k != 'hispanic')
            
            if total_race > 0:
                # Map to simplified categories
                distributions['race_weights'] = {
                    'White': race_data.get('white', 0) / total_race * 0.7,  # Adjust for Hispanic white
                    'Black': race_data.get('black', 0) / total_race,
                    'Hispanic': hispanic_count / total_race,
                    'Asian': race_data.get('asian', 0) / total_race,
                    'Other': (race_data.get('american_indian', 0) + 
                             race_data.get('pacific_islander', 0) + 
                             race_data.get('other', 0) + 
                             race_data.get('two_or_more', 0)) / total_race
                }
        
        # Education distribution
        if 'education' in demographics:
            edu_data = demographics['education']
            total_edu = sum(edu_data.values())
            if total_edu > 0:
                # Map to years of education
                distributions['education_weights'] = {
                    12: edu_data.get('high_school', 0) / total_edu,  # HS diploma
                    14: edu_data.get('some_college', 0) / total_edu,  # Some college
                    16: edu_data.get('bachelors', 0) / total_edu,  # Bachelor's
                    18: edu_data.get('graduate', 0) / total_edu * 0.6,  # Master's
                    20: edu_data.get('graduate', 0) / total_edu * 0.4   # Doctorate
                }
        
        # Income distribution
        if 'income' in demographics:
            distributions['median_income'] = demographics['income'].get('median_income', 50000)
        
        return distributions
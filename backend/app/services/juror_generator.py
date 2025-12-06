"""
Juror generation service combining all data sources
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import random
import json
import anthropic
from app.models.demographics import PersonalityTraits
from app.data_collection.census_data import CensusDataCollector
from app.data_collection.election_data import ElectionDataFetcher
from app.data_collection.personality_data import PersonalityDataProcessor
from app.data_collection.gss_data import GSSDataCollector
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class JurorGenerator:
    def __init__(self):
        self.census_collector = CensusDataCollector()
        self.election_fetcher = ElectionDataFetcher()
        self.personality_processor = PersonalityDataProcessor()
        self.gss_collector = GSSDataCollector()

        # Initialize Anthropic client for AI-generated demographics
        self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Load data if available
        self._load_data_sources()
    
    def _load_data_sources(self):
        """Load available data sources"""
        try:
            # Election data
            election_path = Path("data/raw/county_election_2020.csv")
            if election_path.exists():
                self.election_df = pd.read_csv(election_path)
                logger.info("Loaded election data")
            
            # GSS data (sample for memory efficiency)
            gss_path = Path("data/raw/gss_data.csv")
            if gss_path.exists():
                # Load only key columns to save memory
                key_cols = [
                    'AGE OF RESPONDENT',
                    'RESPONDENTS SEX',
                    'RACE OF RESPONDENT',
                    'HIGHEST YEAR OF SCHOOL COMPLETED',
                    'REGION OF INTERVIEW',
                    'THINK OF SELF AS LIBERAL OR CONSERVATIVE',
                    'FAVOR OR OPPOSE DEATH PENALTY FOR MURDER',
                    'SHOULD MARIJUANA BE MADE LEGAL',
                    'CAN PEOPLE BE TRUSTED',
                    'POLITICAL PARTY AFFILIATION',
                    'FAVOR OR OPPOSE GUN PERMITS',
                    'COURTS DEALING WITH CRIMINALS',
                    'HOMOSEXUAL SEX RELATIONS',
                    'AFRAID TO WALK AT NIGHT IN NEIGHBORHOOD'
                ]
                # Skip early rows that are mostly IAP, load rows with actual data
                self.gss_df = pd.read_csv(gss_path, usecols=key_cols, skiprows=range(1, 1000), nrows=50000, low_memory=False)
                
                # Also load the label columns
                label_cols = [col + '_labels' for col in key_cols if col != 'AGE OF RESPONDENT' and col != 'REGION OF INTERVIEW']
                self.gss_labels_df = pd.read_csv(gss_path, usecols=label_cols, skiprows=range(1, 1000), nrows=50000, low_memory=False)
                
                # Combine data and labels
                self.gss_df = pd.concat([self.gss_df, self.gss_labels_df], axis=1)
                
                # Filter out IAP responses
                pol_label = 'THINK OF SELF AS LIBERAL OR CONSERVATIVE_labels'
                if pol_label in self.gss_df.columns:
                    valid_mask = (self.gss_df[pol_label] != 'IAP') & (self.gss_df[pol_label].notna())
                    logger.info(f"Loaded GSS data: {len(self.gss_df)} total rows, {valid_mask.sum()} with valid political views")
        except Exception as e:
            logger.error(f"Error loading data sources: {e}")
    
    def generate_jury_pool(
        self,
        county: str,
        state: str,
        pool_size: int = 12,
        case_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate a complete jury pool for a county"""
        
        jurors = []
        
        # Get county data
        county_data = self._get_county_profile(county, state)
        
        # Generate diverse jurors
        for i in range(pool_size):
            juror = self._generate_single_juror(i + 1, county_data, case_type)
            jurors.append(juror)
        
        # Ensure diversity
        jurors = self._ensure_diversity(jurors)
        
        return jurors
    
    def _get_county_profile(self, county: str, state: str) -> Dict[str, Any]:
        """Get county demographic and political profile"""
        profile = {
            'county': county,
            'state': state,
            'state_fips': self._state_to_fips(state),
            'region': self._state_to_region(state),
            'voting_data': {'democratic': 50, 'republican': 50, 'other': 0},  # Default
            'urban': False,
            'census_data': None
        }
        
        # Get election data
        if hasattr(self, 'election_df'):
            county_election = self.election_fetcher.get_county_voting_data(
                self.election_df, state, county
            )
            if county_election:
                profile['voting_data'] = county_election
                # Determine if urban based on voting pattern
                profile['urban'] = county_election['democratic'] > 55
        
        # Skip census data fetching for now to avoid async issues
        # TODO: Refactor to use async properly throughout the application
        logger.info(f"Census data fetching temporarily disabled for {county}, {state}")
        profile['census_data'] = None
        
        return profile
    
    def _generate_single_juror(
        self,
        juror_id: int,
        county_data: Dict[str, Any],
        case_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a single juror with all attributes"""
        
        # 1. Generate demographics
        demographics = self._generate_demographics(county_data)
        
        # 2. Get GSS-based attitudes
        attitudes = self._get_gss_attitudes(demographics, county_data['region'])
        
        # 3. Generate personality based on all factors
        personality = self._generate_personality(demographics, attitudes, county_data)
        
        # 4. Create complete juror profile
        juror = {
            'id': juror_id,
            'demographics': demographics,
            'attitudes': attitudes,
            'personality': personality,
            'deliberation_traits': self._generate_deliberation_traits(personality, attitudes),
            'case_biases': self._generate_case_biases(attitudes, case_type)
        }
        
        return juror
    
    def _generate_demographics(self, county_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate demographics using real Census data when available"""
        
        # Check if we have census data
        if county_data.get('census_data') and county_data['census_data'].get('distributions'):
            distributions = county_data['census_data']['distributions']
            
            # Age - use real distribution
            if 'age_weights' in distributions and 'age_ranges' in distributions:
                age_key = random.choices(
                    list(distributions['age_weights'].keys()),
                    weights=list(distributions['age_weights'].values())
                )[0]
                age_range = distributions['age_ranges'][age_key]
                age = random.randint(age_range[0], age_range[1])
            else:
                # Fallback
                age = random.randint(18, 80)
            
            # Gender - use real distribution
            if 'sex_weights' in distributions:
                gender = random.choices(
                    list(distributions['sex_weights'].keys()),
                    weights=list(distributions['sex_weights'].values())
                )[0]
            else:
                gender = random.choice(['Male', 'Female'])
            
            # Race - use real distribution
            if 'race_weights' in distributions:
                race = random.choices(
                    list(distributions['race_weights'].keys()),
                    weights=list(distributions['race_weights'].values())
                )[0]
            else:
                # Fallback based on urban/rural
                if county_data['urban']:
                    race_options = ['White', 'Black', 'Hispanic', 'Asian', 'Other']
                    race_weights = [0.45, 0.20, 0.25, 0.08, 0.02]
                else:
                    race_options = ['White', 'Black', 'Hispanic', 'Asian', 'Other']
                    race_weights = [0.75, 0.10, 0.10, 0.03, 0.02]
                race = random.choices(race_options, weights=race_weights)[0]
            
            # Education - use real distribution
            if 'education_weights' in distributions:
                education_years = random.choices(
                    list(distributions['education_weights'].keys()),
                    weights=list(distributions['education_weights'].values())
                )[0]
                # Ensure it's an integer
                education_years = int(education_years)
            else:
                # Fallback
                if county_data['urban'] and county_data['voting_data']['democratic'] > 60:
                    education_years = random.choices([12, 14, 16, 18, 20], weights=[0.20, 0.25, 0.35, 0.15, 0.05])[0]
                else:
                    education_years = random.choices([12, 14, 16, 18, 20], weights=[0.40, 0.30, 0.20, 0.08, 0.02])[0]
            
            # Income - use median as base with variation
            if 'median_income' in distributions:
                median = distributions['median_income']
                # Generate income with normal distribution around median
                # Standard deviation roughly 40% of median
                income = int(random.gauss(median, median * 0.4))
                # Constrain to reasonable bounds
                income = max(10000, min(500000, income))
            else:
                # Fallback
                base_income = 20000 + (education_years - 12) * 8000
                income = base_income + random.randint(-10000, 30000)
            
        else:
            # Use AI to generate region-specific demographics
            logger.info(f"Using AI to generate demographics for {county_data['county']}, {county_data['state']}")
            ai_demographics = self._get_ai_demographics(county_data)

            age = ai_demographics['age']
            gender = ai_demographics['gender']
            race = ai_demographics['race']
            education_years = ai_demographics['education_years']
            income = ai_demographics['income']
        
        return {
            'age': age,
            'gender': gender,
            'race': race,
            'education_years': education_years,
            'education_level': self._education_label(education_years),
            'income': income,
            'urban': county_data['urban']
        }
    
    def _get_ai_demographics(self, county_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to generate realistic demographics for a specific county"""
        county = county_data['county']
        state = county_data['state']
        urban = county_data['urban']
        voting = county_data['voting_data']

        prompt = f"""Generate realistic demographic data for ONE person who could serve as a juror in {county} County, {state}.

Context:
- County: {county} County, {state}
- Urban/Suburban: {"Urban" if urban else "Rural/Suburban"}
- Political lean: {voting['democratic']:.0f}% Democratic, {voting['republican']:.0f}% Republican

Based on your knowledge of {county} County, {state}, generate realistic demographics for a single potential juror.

Respond with ONLY valid JSON in this exact format:
{{
  "age": <number between 18-80>,
  "gender": "Male" or "Female",
  "race": "White" or "Black" or "Hispanic" or "Asian" or "Other",
  "education_years": <number: 12, 14, 16, 18, or 20>,
  "income": <number: realistic annual income for this county>
}}

NO OTHER TEXT. ONLY JSON."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=0.9,  # Higher temperature for diversity
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text.strip()

            # Extract JSON if there's extra text
            if not response_text.startswith('{'):
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    response_text = response_text[start:end+1]

            demographics = json.loads(response_text)

            logger.info(f"AI generated demographics: {demographics}")
            return demographics

        except Exception as e:
            logger.error(f"Error getting AI demographics: {e}")
            # Fallback to generic demographics
            return {
                'age': random.randint(25, 65),
                'gender': random.choice(['Male', 'Female']),
                'race': random.choice(['White', 'Hispanic', 'Asian', 'Black']),
                'education_years': random.choice([12, 14, 16]),
                'income': random.randint(40000, 100000)
            }

    def _get_gss_attitudes(self, demographics: Dict[str, Any], region: int) -> Dict[str, Any]:
        """Get attitudes from GSS data or generate based on demographics"""
        # Set defaults based on region - Pacific (CA) is more liberal
        if region == 9:  # Pacific
            default_gun_permits = 0.55  # Lower for liberal areas
        elif region in [5, 6, 7]:  # South
            default_gun_permits = 0.75  # Higher for conservative areas
        else:
            default_gun_permits = 0.65  # National average
            
        attitudes = {
            'political_view': 4,  # Default moderate
            'death_penalty': 0.5,
            'marijuana_legal': 0.5,
            'trust_others': 0.35,
            'trust_courts': 0.3,
            'party_affiliation': 'Independent',
            'gun_permits': default_gun_permits,
            'tough_on_crime': 0.5,  # Courts too harsh/not harsh enough
            'abortion_rights': 0.5,  # Support for abortion rights
            'lgbt_acceptance': 0.5,  # Acceptance of homosexual relations
            'police_force': 0.3,  # Approval of police striking citizen
            'fear_crime': 0.3,  # Afraid to walk at night
            'trust_financial': 0.3,  # Trust in financial institutions
            'trust_corporations': 0.3,  # Trust in major companies
            'trust_government': 0.3,  # Trust in executive branch
            'trust_supreme_court': 0.4  # Trust in Supreme Court
        }
        
        if hasattr(self, 'gss_df') and len(self.gss_df) > 0:
            # Filter by region and remove IAP responses
            pol_label = 'THINK OF SELF AS LIBERAL OR CONSERVATIVE_labels'
            death_label = 'FAVOR OR OPPOSE DEATH PENALTY FOR MURDER_labels'
            marijuana_label = 'SHOULD MARIJUANA BE MADE LEGAL_labels'
            
            # Get data for this region with valid responses
            region_mask = self.gss_df['REGION OF INTERVIEW'] == region
            
            # Political views
            if pol_label in self.gss_df.columns:
                pol_mask = region_mask & (self.gss_df[pol_label] != 'IAP') & (self.gss_df[pol_label].notna())
                pol_data = self.gss_df[pol_mask]
                
                if len(pol_data) > 10:
                    # Get a random sample from the region
                    sample = pol_data.sample(n=1)
                    pol_value = sample['THINK OF SELF AS LIBERAL OR CONSERVATIVE'].iloc[0]
                    # GSS uses 1-7 scale: 1=extremely liberal, 4=moderate, 7=extremely conservative
                    attitudes['political_view'] = int(pol_value) if not pd.isna(pol_value) else 4
                else:
                    # If not enough regional data, use all valid data
                    all_pol_mask = (self.gss_df[pol_label] != 'IAP') & (self.gss_df[pol_label].notna())
                    all_pol_data = self.gss_df[all_pol_mask]
                    if len(all_pol_data) > 0:
                        sample = all_pol_data.sample(n=1)
                        pol_value = sample['THINK OF SELF AS LIBERAL OR CONSERVATIVE'].iloc[0]
                        attitudes['political_view'] = int(pol_value) if not pd.isna(pol_value) else 4
            
            # Death penalty
            if death_label in self.gss_df.columns:
                death_mask = region_mask & (self.gss_df[death_label] != 'IAP') & (self.gss_df[death_label].notna())
                death_data = self.gss_df[death_mask]
                
                if len(death_data) > 10:
                    # Calculate regional support rate - 1 = favor, 2 = oppose
                    favor_count = (death_data['FAVOR OR OPPOSE DEATH PENALTY FOR MURDER'] == 1).sum()
                    valid_count = death_data[death_data['FAVOR OR OPPOSE DEATH PENALTY FOR MURDER'].isin([1, 2])].shape[0]
                    if valid_count > 0:
                        attitudes['death_penalty'] = favor_count / valid_count
                else:
                    # Use national average
                    all_death_mask = (self.gss_df[death_label] != 'IAP') & (self.gss_df[death_label].notna())
                    all_death_data = self.gss_df[all_death_mask]
                    if len(all_death_data) > 0:
                        favor_count = (all_death_data['FAVOR OR OPPOSE DEATH PENALTY FOR MURDER'] == 1).sum()
                        valid_count = all_death_data[all_death_data['FAVOR OR OPPOSE DEATH PENALTY FOR MURDER'].isin([1, 2])].shape[0]
                        if valid_count > 0:
                            attitudes['death_penalty'] = favor_count / valid_count
            
            # Marijuana
            if marijuana_label in self.gss_df.columns:
                marijuana_mask = region_mask & (self.gss_df[marijuana_label] != 'IAP') & (self.gss_df[marijuana_label].notna())
                marijuana_data = self.gss_df[marijuana_mask]
                
                if len(marijuana_data) > 10:
                    # Calculate regional support rate - 1 = legal, 2 = not legal
                    legal_count = (marijuana_data['SHOULD MARIJUANA BE MADE LEGAL'] == 1).sum()
                    valid_count = marijuana_data[marijuana_data['SHOULD MARIJUANA BE MADE LEGAL'].isin([1, 2])].shape[0]
                    if valid_count > 0:
                        attitudes['marijuana_legal'] = legal_count / valid_count
                else:
                    # Use national average
                    all_marijuana_mask = (self.gss_df[marijuana_label] != 'IAP') & (self.gss_df[marijuana_label].notna())
                    all_marijuana_data = self.gss_df[all_marijuana_mask]
                    if len(all_marijuana_data) > 0:
                        legal_count = (all_marijuana_data['SHOULD MARIJUANA BE MADE LEGAL'] == 1).sum()
                        valid_count = all_marijuana_data[all_marijuana_data['SHOULD MARIJUANA BE MADE LEGAL'].isin([1, 2])].shape[0]
                        if valid_count > 0:
                            attitudes['marijuana_legal'] = legal_count / valid_count
            
            # Gun permits
            gun_label = 'FAVOR OR OPPOSE GUN PERMITS_labels'
            if gun_label in self.gss_df.columns:
                gun_mask = region_mask & (self.gss_df[gun_label] != 'IAP') & (self.gss_df[gun_label].notna())
                gun_data = self.gss_df[gun_mask]
                
                if len(gun_data) > 10:
                    # 1 = favor, 2 = oppose
                    favor_count = (gun_data['FAVOR OR OPPOSE GUN PERMITS'] == 1).sum()
                    valid_count = gun_data[gun_data['FAVOR OR OPPOSE GUN PERMITS'].isin([1, 2])].shape[0]
                    if valid_count > 0:
                        attitudes['gun_permits'] = favor_count / valid_count
            
            # Courts dealing with criminals
            courts_label = 'COURTS DEALING WITH CRIMINALS_labels'
            if courts_label in self.gss_df.columns:
                courts_mask = region_mask & (self.gss_df[courts_label] != 'IAP') & (self.gss_df[courts_label].notna())
                courts_data = self.gss_df[courts_mask]
                
                if len(courts_data) > 10:
                    # 1 = too harsh, 2 = not harsh enough, 3 = about right
                    harsh_count = (courts_data['COURTS DEALING WITH CRIMINALS'] == 2).sum()
                    valid_count = courts_data[courts_data['COURTS DEALING WITH CRIMINALS'].isin([1, 2, 3])].shape[0]
                    if valid_count > 0:
                        attitudes['tough_on_crime'] = harsh_count / valid_count
            
            # LGBT acceptance
            lgbt_label = 'HOMOSEXUAL SEX RELATIONS_labels'
            if lgbt_label in self.gss_df.columns:
                lgbt_mask = region_mask & (self.gss_df[lgbt_label] != 'IAP') & (self.gss_df[lgbt_label].notna())
                lgbt_data = self.gss_df[lgbt_mask]
                
                if len(lgbt_data) > 10:
                    # 1 = always wrong, 2 = almost always wrong, 3 = sometimes wrong, 4 = not wrong at all
                    accepting_count = (lgbt_data['HOMOSEXUAL SEX RELATIONS'] == 4).sum()
                    valid_count = lgbt_data[lgbt_data['HOMOSEXUAL SEX RELATIONS'].isin([1, 2, 3, 4])].shape[0]
                    if valid_count > 0:
                        attitudes['lgbt_acceptance'] = accepting_count / valid_count
            
            # Trust in people
            trust_label = 'CAN PEOPLE BE TRUSTED_labels'
            if trust_label in self.gss_df.columns:
                trust_mask = region_mask & (self.gss_df[trust_label] != 'IAP') & (self.gss_df[trust_label].notna())
                trust_data = self.gss_df[trust_mask]
                
                if len(trust_data) > 10:
                    # 1 = can trust, 2 = can't be too careful, 3 = depends
                    trust_count = (trust_data['CAN PEOPLE BE TRUSTED'] == 1).sum()
                    valid_count = trust_data[trust_data['CAN PEOPLE BE TRUSTED'].isin([1, 2])].shape[0]
                    if valid_count > 0:
                        attitudes['trust_others'] = trust_count / valid_count
        
        # Adjust based on demographics to add individual variation
        # Younger people more liberal
        if demographics['age'] < 35:
            attitudes['political_view'] = max(1, attitudes['political_view'] - 1)
            attitudes['marijuana_legal'] = min(1.0, attitudes['marijuana_legal'] + 0.2)
            attitudes['lgbt_acceptance'] = min(1.0, attitudes['lgbt_acceptance'] + 0.3)
            attitudes['gun_permits'] = max(0, attitudes['gun_permits'] - 0.15)  # Younger less pro-gun
        
        # Education affects attitudes
        if demographics['education_years'] >= 16:
            attitudes['political_view'] = max(1, attitudes['political_view'] - 1)
            attitudes['death_penalty'] = max(0, attitudes['death_penalty'] - 0.1)
            attitudes['lgbt_acceptance'] = min(1.0, attitudes['lgbt_acceptance'] + 0.2)
            attitudes['tough_on_crime'] = max(0, attitudes['tough_on_crime'] - 0.15)
            attitudes['gun_permits'] = max(0, attitudes['gun_permits'] - 0.1)  # Educated less pro-gun
        
        # Urban areas more liberal
        if demographics['urban']:
            attitudes['political_view'] = max(1, attitudes['political_view'] - 1)
            attitudes['marijuana_legal'] = min(1.0, attitudes['marijuana_legal'] + 0.15)
            attitudes['lgbt_acceptance'] = min(1.0, attitudes['lgbt_acceptance'] + 0.2)
            attitudes['gun_permits'] = max(0, attitudes['gun_permits'] - 0.1)  # Urban less pro-gun
        
        # Political views strongly affect gun attitudes
        if attitudes['political_view'] <= 2:  # Very liberal
            attitudes['gun_permits'] = max(0, attitudes['gun_permits'] - 0.25)
        elif attitudes['political_view'] == 3:  # Liberal
            attitudes['gun_permits'] = max(0, attitudes['gun_permits'] - 0.15)
        elif attitudes['political_view'] >= 6:  # Conservative
            attitudes['gun_permits'] = min(1.0, attitudes['gun_permits'] + 0.15)
        
        # Add random variation to all attitudes
        for key in attitudes:
            if key == 'political_view':
                attitudes[key] = max(1, min(7, attitudes[key] + random.randint(-1, 1)))
            elif key == 'party_affiliation':
                continue  # Skip string values
            else:
                # Add 10-20% random variation
                variation = random.uniform(-0.15, 0.15)
                attitudes[key] = max(0, min(1, attitudes[key] + variation))
        
        return attitudes
    
    def _generate_personality(
        self,
        demographics: Dict[str, Any],
        attitudes: Dict[str, Any],
        county_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Generate Big Five personality traits based on all factors"""
        
        # Base personality (population averages)
        personality = {
            'openness': 3.27,
            'conscientiousness': 3.12,
            'extraversion': 3.02,
            'agreeableness': 3.16,
            'neuroticism': 3.02
        }
        
        # Political lean adjustments
        political_factor = (attitudes['political_view'] - 4) / 3  # -1 to +1
        personality['openness'] -= political_factor * 0.4  # Liberals higher openness
        personality['conscientiousness'] += political_factor * 0.3  # Conservatives higher conscientiousness
        
        # Urban/rural adjustments
        if county_data['urban']:
            personality['extraversion'] += 0.2
            personality['openness'] += 0.1
        else:
            personality['extraversion'] -= 0.2
            personality['agreeableness'] += 0.1
        
        # Age adjustments
        if demographics['age'] > 50:
            personality['conscientiousness'] += 0.2
            personality['openness'] -= 0.1
        elif demographics['age'] < 30:
            personality['openness'] += 0.2
            personality['neuroticism'] += 0.1
        
        # Trust affects agreeableness
        personality['agreeableness'] += (attitudes['trust_others'] - 0.35) * 0.5
        
        # Add individual variation
        for trait in personality:
            personality[trait] += random.gauss(0, 0.3)
            personality[trait] = max(1, min(5, personality[trait]))
            personality[trait] = round(personality[trait], 2)
        
        return personality
    
    def _generate_deliberation_traits(
        self,
        personality: Dict[str, float],
        attitudes: Dict[str, Any]
    ) -> List[str]:
        """Generate jury deliberation characteristics"""
        traits = []
        
        # Leadership tendency
        if personality['extraversion'] > 3.5 and personality['agreeableness'] < 3.2:
            traits.append("Natural leader - likely foreperson candidate")
        elif personality['extraversion'] > 3.7:
            traits.append("Very vocal in discussions")
        elif personality['extraversion'] < 2.5:
            traits.append("Reserved - speaks only when necessary")
        
        # Decision-making style
        if personality['conscientiousness'] > 3.5:
            traits.append("Detail-oriented - focuses on evidence")
        if personality['openness'] > 3.5:
            traits.append("Open to alternative interpretations")
        elif personality['openness'] < 2.5:
            traits.append("Prefers straightforward explanations")
        
        # Social dynamics
        if personality['agreeableness'] > 3.5:
            traits.append("Seeks consensus and compromise")
        elif personality['agreeableness'] < 2.5:
            traits.append("Willing to be lone holdout")
        
        # Emotional stability
        if personality['neuroticism'] > 3.5:
            traits.append("May be swayed by emotional appeals")
        elif personality['neuroticism'] < 2.5:
            traits.append("Remains calm under pressure")
        
        # Trust in system
        if attitudes['trust_courts'] > 0.5:
            traits.append("High deference to judge instructions")
        elif attitudes['trust_courts'] < 0.3:
            traits.append("Questions authority and procedures")
        
        return traits
    
    def _generate_case_biases(
        self,
        attitudes: Dict[str, Any],
        case_type: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate case-specific biases based on attitudes"""
        biases = {}
        
        # Death penalty cases
        if attitudes['death_penalty'] > 0.6:
            biases['capital_case'] = "Willing to impose death penalty"
        elif attitudes['death_penalty'] < 0.4:
            biases['capital_case'] = "Prefers life imprisonment"
        else:
            biases['capital_case'] = "Could go either way on death penalty"
        
        # Drug cases
        if attitudes['marijuana_legal'] > 0.6:
            biases['drug_case'] = "Sympathetic to drug defendants"
        elif attitudes['marijuana_legal'] < 0.4:
            biases['drug_case'] = "Tough on drug crimes"
        else:
            biases['drug_case'] = "Moderate on drug offenses"
        
        # Based on political views
        if attitudes['political_view'] < 3:
            biases['police_case'] = "May be skeptical of police"
            biases['corporate_crime'] = "Tough on white collar crime"
        elif attitudes['political_view'] > 5:
            biases['police_case'] = "Generally trusts police testimony"
            biases['corporate_crime'] = "May sympathize with business"
        
        return biases
    
    def _ensure_diversity(self, jurors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure jury pool has appropriate diversity"""
        # Check demographics
        ages = [j['demographics']['age'] for j in jurors]
        genders = [j['demographics']['gender'] for j in jurors]
        
        # Ensure age diversity
        if max(ages) - min(ages) < 20:
            # Adjust some ages
            jurors[0]['demographics']['age'] = random.randint(20, 30)
            jurors[-1]['demographics']['age'] = random.randint(55, 70)
        
        # Ensure gender balance (roughly)
        male_count = sum(1 for g in genders if g == 'Male')
        if male_count < 4 or male_count > 8:
            # Adjust some genders
            target_male = 6
            for i, juror in enumerate(jurors):
                if male_count < target_male and juror['demographics']['gender'] == 'Female':
                    juror['demographics']['gender'] = 'Male'
                    male_count += 1
                elif male_count > target_male and juror['demographics']['gender'] == 'Male':
                    juror['demographics']['gender'] = 'Female'
                    male_count -= 1
        
        return jurors
    
    def _state_to_region(self, state: str) -> int:
        """Convert state to GSS region code"""
        state_to_region_map = {
            # New England (1)
            'ME': 1, 'NH': 1, 'VT': 1, 'MA': 1, 'RI': 1, 'CT': 1,
            # Middle Atlantic (2)
            'NY': 2, 'NJ': 2, 'PA': 2,
            # East North Central (3)
            'OH': 3, 'IN': 3, 'IL': 3, 'MI': 3, 'WI': 3,
            # West North Central (4)
            'MN': 4, 'IA': 4, 'MO': 4, 'ND': 4, 'SD': 4, 'NE': 4, 'KS': 4,
            # South Atlantic (5)
            'DE': 5, 'MD': 5, 'DC': 5, 'VA': 5, 'WV': 5, 'NC': 5, 'SC': 5, 'GA': 5, 'FL': 5,
            # East South Central (6)
            'KY': 6, 'TN': 6, 'AL': 6, 'MS': 6,
            # West South Central (7)
            'AR': 7, 'LA': 7, 'OK': 7, 'TX': 7,
            # Mountain (8)
            'MT': 8, 'ID': 8, 'WY': 8, 'CO': 8, 'NM': 8, 'AZ': 8, 'UT': 8, 'NV': 8,
            # Pacific (9)
            'WA': 9, 'OR': 9, 'CA': 9, 'AK': 9, 'HI': 9
        }
        return state_to_region_map.get(state, 5)  # Default to South Atlantic
    
    def _state_to_fips(self, state: str) -> str:
        """Convert state abbreviation to FIPS code"""
        state_to_fips = {
            'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06',
            'CO': '08', 'CT': '09', 'DE': '10', 'DC': '11', 'FL': '12',
            'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18',
            'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23',
            'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28',
            'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33',
            'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38',
            'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44',
            'SC': '45', 'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49',
            'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55',
            'WY': '56'
        }
        return state_to_fips.get(state, '00')
    
    def _education_label(self, years: int) -> str:
        """Convert education years to label"""
        if years < 12:
            return "Some high school"
        elif years == 12:
            return "High school graduate"
        elif years < 16:
            return "Some college"
        elif years == 16:
            return "Bachelor's degree"
        elif years < 18:
            return "Some graduate school"
        else:
            return "Graduate degree"
    
    def _map_political_view(self, gss_value: Any) -> int:
        """Map GSS political view to 1-7 scale"""
        # This would need proper mapping based on GSS codebook
        # For now, return moderate
        return 4
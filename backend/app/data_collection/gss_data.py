import pandas as pd
import httpx
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from app.models.demographics import DataSource
import zipfile
import io

logger = logging.getLogger(__name__)


class GSSDataCollector:
    """
    General Social Survey data collector
    GSS contains detailed social attitudes, political views, and demographics
    """
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Note: You'll need to download this manually from Kaggle
        # or use Kaggle API with authentication
        self.gss_file_path = self.data_dir / "gss_data.csv"
        
    async def download_gss_data_info(self) -> Dict[str, Any]:
        """
        Return information about GSS data and how to obtain it
        """
        return {
            "source": "NORC at University of Chicago",
            "kaggle_url": "https://www.kaggle.com/datasets/norc/general-social-survey",
            "description": "The General Social Survey (GSS) is a nationally representative survey of adults in the United States conducted since 1972",
            "key_variables": {
                "demographics": ["age", "sex", "race", "educ", "income", "region", "srcbelt"],
                "political": ["polviews", "partyid", "vote", "pres", "polint"],
                "social_attitudes": ["cappun", "gunlaw", "grass", "divlaw", "abany", "prayer"],
                "trust_institutions": ["confinan", "conbus", "conclerg", "coneduc", "confed", "conjudge"],
                "personal_values": ["helpful", "fair", "trust", "getahead", "fework", "workhard"],
                "religion": ["relig", "attend", "postlife", "pray"]
            },
            "years_available": "1972-2022",
            "sample_size": "Over 64,000 respondents",
            "download_instructions": [
                "1. Go to https://www.kaggle.com/datasets/norc/general-social-survey",
                "2. Download the dataset (requires Kaggle account)",
                "3. Place the CSV file in data/raw/gss_data.csv",
                "4. Or use Kaggle API: kaggle datasets download -d norc/general-social-survey"
            ]
        }
    
    def load_gss_data(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load GSS data with specified columns
        """
        if not self.gss_file_path.exists():
            raise FileNotFoundError(
                f"GSS data not found at {self.gss_file_path}. "
                "Please download from Kaggle first."
            )
        
        try:
            # GSS columns mapping to actual column names
            column_mapping = {
                'year': 'GSS YEAR FOR THIS RESPONDENT',
                'age': 'AGE OF RESPONDENT',
                'sex': 'RESPONDENTS SEX',
                'race': 'RACE OF RESPONDENT',
                'educ': 'HIGHEST YEAR OF SCHOOL COMPLETED',
                'region': 'REGION OF INTERVIEW',
                'polviews': 'THINK OF SELF AS LIBERAL OR CONSERVATIVE',
                'partyid': 'POLITICAL PARTY AFFILIATION',
                'cappun': 'FAVOR OR OPPOSE DEATH PENALTY FOR MURDER',
                'grass': 'SHOULD MARIJUANA BE MADE LEGAL',
                'trust': 'CAN PEOPLE BE TRUSTED',
                'helpful': 'PEOPLE HELPFUL OR LOOKING OUT FOR SELVES',
                'fair': 'PEOPLE FAIR OR TRY TO TAKE ADVANTAGE',
                'courts': 'COURTS DEALING WITH CRIMINALS',
                'income': 'TOTAL FAMILY INCOME'
            }
            
            # Use actual column names if available
            if columns:
                use_columns = columns
            else:
                use_columns = list(column_mapping.values())
            
            # Try to load only needed columns to save memory
            df = pd.read_csv(
                self.gss_file_path,
                usecols=lambda x: x.lower() in [c.lower() for c in use_columns],
                low_memory=False
            )
            
            logger.info(f"Loaded GSS data with {len(df)} records and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error loading GSS data: {e}")
            raise
    
    def get_political_attitudes_by_region(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Analyze political attitudes by region
        """
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
        
        results = {}
        
        for region_code, region_name in regions.items():
            region_df = df[df['region'] == region_code]
            
            if len(region_df) > 0:
                # Political views: 1=extremely liberal to 7=extremely conservative
                polviews_mean = region_df['polviews'].mean()
                
                # Party ID: 0=strong democrat to 6=strong republican
                partyid_mean = region_df['partyid'].mean()
                
                results[region_name] = {
                    'political_views': round(polviews_mean, 2) if pd.notna(polviews_mean) else None,
                    'party_id': round(partyid_mean, 2) if pd.notna(partyid_mean) else None,
                    'sample_size': len(region_df)
                }
        
        return results
    
    def get_social_attitudes_profile(self, df: pd.DataFrame, filters: Dict[str, Any] = None) -> Dict[str, float]:
        """
        Get social attitudes profile for a demographic group
        """
        if filters:
            for key, value in filters.items():
                if key in df.columns:
                    df = df[df[key] == value]
        
        attitudes = {}
        
        # Map GSS codes to meaningful values
        attitude_vars = {
            'cappun': 'death_penalty_support',  # 1=favor, 2=oppose
            'gunlaw': 'gun_control_support',    # 1=favor, 2=oppose
            'grass': 'marijuana_legalization',   # 1=legal, 2=not legal
            'divlaw': 'easier_divorce',          # 1=easier, 2=more difficult, 3=stay same
            'abany': 'abortion_any_reason'       # 1=yes, 2=no
        }
        
        for gss_var, friendly_name in attitude_vars.items():
            if gss_var in df.columns:
                # Calculate percentage supporting (value=1)
                support = (df[gss_var] == 1).sum()
                total = df[gss_var].notna().sum()
                if total > 0:
                    attitudes[friendly_name] = round(support / total * 100, 1)
        
        return attitudes
    
    def create_personality_mapping(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Map GSS responses to Big Five personality traits
        Based on research correlations
        """
        mappings = {}
        
        # Political views to Openness/Conscientiousness
        # Liberal (1-3) -> Higher Openness, Lower Conscientiousness
        # Conservative (5-7) -> Lower Openness, Higher Conscientiousness
        
        polviews_groups = {
            'liberal': df[df['polviews'].isin([1, 2, 3])],
            'moderate': df[df['polviews'] == 4],
            'conservative': df[df['polviews'].isin([5, 6, 7])]
        }
        
        for group_name, group_df in polviews_groups.items():
            if len(group_df) > 0:
                # Base personality + adjustments
                if group_name == 'liberal':
                    openness_adj = 0.4
                    conscientiousness_adj = -0.3
                elif group_name == 'conservative':
                    openness_adj = -0.3
                    conscientiousness_adj = 0.4
                else:  # moderate
                    openness_adj = 0
                    conscientiousness_adj = 0
                
                # Trust affects Agreeableness
                trust_mean = group_df['trust'].mean() if 'trust' in group_df else 2
                agreeableness_adj = (trust_mean - 2) * 0.2  # Scale around middle
                
                mappings[group_name] = {
                    'openness': 3.27 + openness_adj,
                    'conscientiousness': 3.12 + conscientiousness_adj,
                    'agreeableness': 3.16 + agreeableness_adj,
                    'extraversion': 3.02,  # No direct mapping
                    'neuroticism': 3.02    # No direct mapping
                }
        
        return mappings
    
    def get_jury_relevant_profile(self, age: int, education: int, region: int, 
                                 political_view: int) -> Dict[str, Any]:
        """
        Get a profile relevant for jury simulation based on GSS data
        """
        if not self.gss_file_path.exists():
            return {
                "error": "GSS data not available",
                "instructions": "Download from Kaggle: https://www.kaggle.com/datasets/norc/general-social-survey"
            }
        
        df = self.load_gss_data()
        
        # Filter to similar demographics
        similar = df[
            (df['age'].between(age - 5, age + 5)) &
            (df['educ'].between(education - 2, education + 2)) &
            (df['region'] == region)
        ]
        
        if len(similar) == 0:
            similar = df[df['region'] == region]  # Fallback to region only
        
        profile = {
            'sample_size': len(similar),
            'political_views': {
                'mean': similar['polviews'].mean(),
                'distribution': similar['polviews'].value_counts().to_dict()
            },
            'social_attitudes': self.get_social_attitudes_profile(similar),
            'trust_levels': {
                'general_trust': (similar['trust'] == 1).mean() * 100 if 'trust' in similar else None,
                'trust_federal_gov': (similar['confed'] == 1).mean() * 100 if 'confed' in similar else None,
                'trust_courts': (similar['conjudge'] == 1).mean() * 100 if 'conjudge' in similar else None
            }
        }
        
        return profile
    
    def get_data_source_info(self) -> DataSource:
        """
        Return metadata about the data source
        """
        return DataSource(
            name="General Social Survey (GSS)",
            url="https://www.kaggle.com/datasets/norc/general-social-survey",
            last_updated="2022 (ongoing since 1972)",
            fields_used=[
                "demographics (age, sex, race, education)",
                "political views and party affiliation",
                "social attitudes (death penalty, gun control, etc.)",
                "institutional trust",
                "regional variations"
            ],
            description="Nationally representative survey of US adults with detailed social and political attitudes"
        )
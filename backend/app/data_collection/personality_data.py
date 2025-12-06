import pandas as pd
import httpx
from typing import Dict, List, Optional, Tuple
from app.models.demographics import PersonalityTraits, DemographicCluster, DataSource
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PersonalityDataProcessor:
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Using the IPIP-FFM dataset which contains Big Five personality data
        self.personality_data_url = "https://openpsychometrics.org/_rawdata/IPIP-FFM-data-8Nov2018.zip"
        
    async def download_personality_data(self) -> Path:
        """
        Download Big Five personality dataset from OpenPsychometrics
        """
        file_path = self.data_dir / "IPIP-FFM-data-8Nov2018" / "data-final.csv"
        
        if file_path.exists():
            logger.info(f"Personality data already exists at {file_path}")
            return file_path
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                logger.info("Downloading personality data...")
                response = await client.get(self.personality_data_url)
                response.raise_for_status()
                
                zip_path = self.data_dir / "IPIP-FFM-data-8Nov2018.zip"
                zip_path.write_bytes(response.content)
                
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)
                
                zip_path.unlink()
                
                # The actual CSV is in the extracted folder
                csv_path = self.data_dir / "IPIP-FFM-data-8Nov2018" / "data-final.csv"
                logger.info(f"Personality data downloaded to {csv_path}")
                return csv_path
                
            except Exception as e:
                logger.error(f"Error downloading personality data: {e}")
                raise
    
    def load_personality_data(self, file_path: Path) -> pd.DataFrame:
        """
        Load and preprocess personality data
        """
        try:
            # The IPIP-FFM data uses tab delimiters
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8', on_bad_lines='skip')
            
            # This dataset doesn't have age/gender columns, so we'll use the Big Five scores only
            required_cols = ['EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5',
                           'EXT6', 'EXT7', 'EXT8', 'EXT9', 'EXT10',
                           'EST1', 'EST2', 'EST3', 'EST4', 'EST5',
                           'EST6', 'EST7', 'EST8', 'EST9', 'EST10',
                           'AGR1', 'AGR2', 'AGR3', 'AGR4', 'AGR5',
                           'AGR6', 'AGR7', 'AGR8', 'AGR9', 'AGR10',
                           'CSN1', 'CSN2', 'CSN3', 'CSN4', 'CSN5',
                           'CSN6', 'CSN7', 'CSN8', 'CSN9', 'CSN10',
                           'OPN1', 'OPN2', 'OPN3', 'OPN4', 'OPN5',
                           'OPN6', 'OPN7', 'OPN8', 'OPN9', 'OPN10']
            
            available_cols = [col for col in required_cols if col in df.columns]
            personality_df = df[available_cols + ['country'] if 'country' in df.columns else available_cols]
            
            personality_df = personality_df.dropna()
            
            personality_df['extraversion'] = personality_df[[f'EXT{i}' for i in range(1, 11) if f'EXT{i}' in personality_df.columns]].mean(axis=1)
            personality_df['neuroticism'] = personality_df[[f'EST{i}' for i in range(1, 11) if f'EST{i}' in personality_df.columns]].mean(axis=1)
            personality_df['agreeableness'] = personality_df[[f'AGR{i}' for i in range(1, 11) if f'AGR{i}' in personality_df.columns]].mean(axis=1)
            personality_df['conscientiousness'] = personality_df[[f'CSN{i}' for i in range(1, 11) if f'CSN{i}' in personality_df.columns]].mean(axis=1)
            personality_df['openness'] = personality_df[[f'OPN{i}' for i in range(1, 11) if f'OPN{i}' in personality_df.columns]].mean(axis=1)
            
            return personality_df
            
        except Exception as e:
            logger.error(f"Error loading personality data: {e}")
            raise
    
    def calculate_demographic_personality_averages(
        self, 
        df: pd.DataFrame,
        age_ranges: List[Tuple[int, int]] = [(18, 25), (26, 35), (36, 45), (46, 55), (56, 65), (66, 100)]
    ) -> Dict[str, PersonalityTraits]:
        """
        Calculate average personality traits by country (since age/gender not available)
        """
        demographic_personalities = {}
        
        # Group by country if available
        if 'country' in df.columns:
            for country in df['country'].value_counts().head(10).index:  # Top 10 countries
                country_df = df[df['country'] == country]
                
                if len(country_df) > 50:  # Only include countries with sufficient data
                    demographic_personalities[f"country_{country}"] = PersonalityTraits(
                        extraversion=float(country_df['extraversion'].mean()),
                        neuroticism=float(country_df['neuroticism'].mean()),
                        agreeableness=float(country_df['agreeableness'].mean()),
                        conscientiousness=float(country_df['conscientiousness'].mean()),
                        openness=float(country_df['openness'].mean())
                    )
        
        # Overall traits
        overall_traits = PersonalityTraits(
            extraversion=float(df['extraversion'].mean()),
            neuroticism=float(df['neuroticism'].mean()),
            agreeableness=float(df['agreeableness'].mean()),
            conscientiousness=float(df['conscientiousness'].mean()),
            openness=float(df['openness'].mean())
        )
        demographic_personalities['overall'] = overall_traits
        
        return demographic_personalities
    
    def get_data_source_info(self) -> DataSource:
        """
        Return metadata about the data source
        """
        return DataSource(
            name="IPIP-FFM Big Five Personality Dataset",
            url=self.personality_data_url,
            last_updated="November 8, 2018",
            fields_used=["age", "gender", "Big Five scores (EXT, EST, AGR, CSN, OPN)"],
            description="IPIP Five-Factor Model personality inventory data from OpenPsychometrics.org"
        )
import httpx
import pandas as pd
from typing import Dict, Optional
import logging
from pathlib import Path
from app.models.demographics import DataSource

logger = logging.getLogger(__name__)


class ElectionDataFetcher:
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.mit_election_data_url = "https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/VOQCHQ/HEIJCQ"
        
    async def download_county_election_data(self) -> Path:
        """
        Download county-level presidential election data
        """
        file_path = self.data_dir / "county_election_2020.csv"
        
        if file_path.exists():
            logger.info(f"Election data already exists at {file_path}")
            return file_path
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                logger.info("Downloading election data from MIT Election Lab...")
                response = await client.get(self.mit_election_data_url)
                response.raise_for_status()
                
                file_path.write_bytes(response.content)
                logger.info(f"Election data downloaded to {file_path}")
                return file_path
                
            except Exception as e:
                logger.error(f"Error downloading election data: {e}")
                logger.info("Attempting alternative source...")
                return await self.download_alternative_election_data()
    
    async def download_alternative_election_data(self) -> Path:
        """
        Alternative method using a direct CSV source
        """
        alternative_url = "https://raw.githubusercontent.com/tonmcg/US_County_Level_Election_Results_08-20/master/2020_US_County_Level_Presidential_Results.csv"
        file_path = self.data_dir / "county_election_2020.csv"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(alternative_url)
                response.raise_for_status()
                
                file_path.write_text(response.text)
                logger.info(f"Alternative election data downloaded to {file_path}")
                return file_path
                
            except Exception as e:
                logger.error(f"Error downloading alternative election data: {e}")
                raise
    
    def load_election_data(self, file_path: Path) -> pd.DataFrame:
        """
        Load and preprocess county election data
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
            
            required_cols = ['state_name', 'county_name', 'per_dem', 'per_gop']
            if all(col in df.columns for col in required_cols):
                return df[['state_name', 'county_name', 'per_dem', 'per_gop']]
            
            if 'county_name' in df.columns and 'votes_dem' in df.columns and 'votes_gop' in df.columns:
                df['total_votes'] = df['votes_dem'] + df['votes_gop']
                df['per_dem'] = (df['votes_dem'] / df['total_votes'] * 100).round(2)
                df['per_gop'] = (df['votes_gop'] / df['total_votes'] * 100).round(2)
                
            return df
            
        except Exception as e:
            logger.error(f"Error loading election data: {e}")
            raise
    
    def get_county_voting_data(
        self, 
        df: pd.DataFrame, 
        state: str, 
        county: str
    ) -> Optional[Dict[str, float]]:
        """
        Get voting percentages for a specific county
        """
        try:
            county_data = df[
                (df['state_name'].str.lower() == state.lower()) & 
                (df['county_name'].str.lower() == county.lower())
            ]
            
            if county_data.empty:
                county_data = df[
                    df['county_name'].str.contains(county, case=False, na=False)
                ]
            
            if not county_data.empty:
                row = county_data.iloc[0]
                dem_pct = float(row.get('per_dem', 0)) * 100
                gop_pct = float(row.get('per_gop', 0)) * 100
                return {
                    'democratic': round(dem_pct, 2),
                    'republican': round(gop_pct, 2),
                    'other': round(max(0, 100 - dem_pct - gop_pct), 2)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting county voting data: {e}")
            return None
    
    def get_data_source_info(self) -> DataSource:
        """
        Return metadata about the data source
        """
        return DataSource(
            name="County Presidential Election Returns 2020",
            url="MIT Election Data and Science Lab",
            last_updated="2020 Presidential Election",
            fields_used=["state_name", "county_name", "per_dem", "per_gop"],
            description="County-level presidential election results from 2020"
        )
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.data_collection.census_data import CensusDataCollector
from app.data_collection.personality_data import PersonalityDataProcessor
from app.data_collection.election_data import ElectionDataFetcher
from app.data_collection.gss_data import GSSDataCollector
from app.models.demographics import CountyData, DataSource
import logging

router = APIRouter(tags=["data_collection"])
logger = logging.getLogger(__name__)


@router.get("/sources", response_model=List[DataSource])
async def get_data_sources():
    """
    Get information about all data sources used
    """
    sources = []
    
    census_collector = CensusDataCollector()
    sources.append(census_collector.get_data_source_info())
    
    personality_processor = PersonalityDataProcessor()
    sources.append(personality_processor.get_data_source_info())
    
    election_fetcher = ElectionDataFetcher()
    sources.append(election_fetcher.get_data_source_info())
    
    gss_collector = GSSDataCollector()
    sources.append(gss_collector.get_data_source_info())
    
    return sources


@router.post("/census/fetch")
async def fetch_census_data(
    state_fips: str = Query(..., description="State FIPS code (e.g., '06' for California)"),
    puma_codes: Optional[List[str]] = Query(None, description="Optional list of PUMA codes")
):
    """
    Fetch ACS PUMS data for a specific state and optionally specific PUMAs
    """
    try:
        collector = CensusDataCollector()
        
        df = await collector.get_state_puma_data(state_fips, puma_codes)
        
        records = collector.parse_pums_records(df)
        
        return {
            "state_fips": state_fips,
            "record_count": len(records),
            "puma_codes": df['PUMA'].unique().tolist() if 'PUMA' in df.columns else [],
            "sample_records": records[:5] if records else []
        }
        
    except Exception as e:
        logger.error(f"Error fetching census data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/census/puma-mapping/{state_fips}")
async def get_puma_mapping(state_fips: str):
    """
    Get county to PUMA mapping for a state
    """
    try:
        collector = CensusDataCollector()
        mapping = await collector.get_county_puma_mapping(state_fips)
        
        return {
            "state_fips": state_fips,
            "county_count": len(mapping),
            "mapping": mapping
        }
        
    except Exception as e:
        logger.error(f"Error fetching PUMA mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/personality/download")
async def download_personality_data():
    """
    Download Big Five personality dataset
    """
    try:
        processor = PersonalityDataProcessor()
        file_path = await processor.download_personality_data()
        
        df = processor.load_personality_data(file_path)
        demographics = processor.calculate_demographic_personality_averages(df)
        
        return {
            "status": "success",
            "file_path": str(file_path),
            "record_count": len(df),
            "demographic_groups": len(demographics),
            "overall_personality": demographics.get('overall')
        }
        
    except Exception as e:
        logger.error(f"Error downloading personality data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/election/download")
async def download_election_data():
    """
    Download county-level election data
    """
    try:
        fetcher = ElectionDataFetcher()
        file_path = await fetcher.download_county_election_data()
        
        df = fetcher.load_election_data(file_path)
        
        return {
            "status": "success",
            "file_path": str(file_path),
            "county_count": len(df),
            "states": df['state_name'].unique().tolist() if 'state_name' in df.columns else []
        }
        
    except Exception as e:
        logger.error(f"Error downloading election data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/election/county")
async def get_county_election_data(
    state: str = Query(..., description="State name"),
    county: str = Query(..., description="County name")
):
    """
    Get election data for a specific county
    """
    try:
        fetcher = ElectionDataFetcher()
        file_path = fetcher.data_dir / "county_election_2020.csv"
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404, 
                detail="Election data not found. Please download first using /election/download"
            )
        
        df = fetcher.load_election_data(file_path)
        voting_data = fetcher.get_county_voting_data(df, state, county)
        
        if voting_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {county}, {state}"
            )
        
        return {
            "state": state,
            "county": county,
            "voting_data": voting_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting county election data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gss/info")
async def get_gss_info():
    """
    Get information about GSS data and how to obtain it
    """
    try:
        collector = GSSDataCollector()
        info = await collector.download_gss_data_info()
        
        # Add download status
        info["download_status"] = "available" if collector.gss_file_path.exists() else "not_downloaded"
        info["setup_instructions"] = [
            "1. Create Kaggle account at kaggle.com",
            "2. Go to kaggle.com/account and create API token",
            "3. Save kaggle.json to ~/.kaggle/",
            "4. Run: chmod 600 ~/.kaggle/kaggle.json",
            "5. Run: python download_gss_simple.py"
        ]
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting GSS info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gss/political-attitudes")
async def get_political_attitudes_by_region():
    """
    Get political attitudes by US region from GSS data
    """
    try:
        collector = GSSDataCollector()
        
        # Check if data exists
        if not collector.gss_file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="GSS data not found. Please download from Kaggle first. See /gss/info for instructions."
            )
        
        df = collector.load_gss_data()
        attitudes = collector.get_political_attitudes_by_region(df)
        
        return {
            "status": "success",
            "data": attitudes,
            "description": "Political views by US region (1=extremely liberal to 7=extremely conservative)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing GSS political attitudes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gss/jury-profile")
async def get_jury_relevant_profile(
    age: int = Query(..., ge=18, le=90, description="Age of juror"),
    education: int = Query(..., ge=0, le=20, description="Years of education"),
    region: int = Query(..., ge=1, le=9, description="US region code (1-9)"),
    political_view: int = Query(..., ge=1, le=7, description="Political view (1=very liberal, 7=very conservative)")
):
    """
    Get jury-relevant profile based on GSS data for similar demographics
    """
    try:
        collector = GSSDataCollector()
        profile = collector.get_jury_relevant_profile(age, education, region, political_view)
        
        return {
            "status": "success",
            "input": {
                "age": age,
                "education": education,
                "region": region,
                "political_view": political_view
            },
            "profile": profile
        }
        
    except Exception as e:
        logger.error(f"Error getting jury profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))
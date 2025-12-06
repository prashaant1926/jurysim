#!/usr/bin/env python3
"""
Download and cache census data for test counties
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data_collection.census_data import CensusDataCollector
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def download_county_data():
    """Download census data for key test counties"""
    
    collector = CensusDataCollector()
    
    # Test counties
    test_counties = [
        ("06", "San Francisco"),     # California
        ("06", "Los Angeles"),       # California
        ("48", "Harris"),           # Texas
        ("17", "Cook"),             # Illinois
        ("39", "Cuyahoga"),         # Ohio
        ("36", "New York"),         # New York (Manhattan)
        ("12", "Miami-Dade"),       # Florida
    ]
    
    for state_fips, county_name in test_counties:
        logger.info(f"\nDownloading data for {county_name} County, FIPS {state_fips}")
        try:
            data = await collector.get_county_demographics(state_fips, county_name)
            if data:
                logger.info(f"✓ Successfully downloaded data for {county_name}")
                if 'distributions' in data:
                    dist = data['distributions']
                    if 'race_weights' in dist:
                        logger.info(f"  Race distribution: {dist['race_weights']}")
                    if 'median_income' in dist:
                        logger.info(f"  Median income: ${dist['median_income']:,}")
            else:
                logger.error(f"✗ Failed to download data for {county_name}")
        except Exception as e:
            logger.error(f"✗ Error downloading {county_name}: {e}")

if __name__ == "__main__":
    logger.info("Starting census data download...")
    asyncio.run(download_county_data())
    logger.info("\nCensus data download complete!")
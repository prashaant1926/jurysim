#!/usr/bin/env python3
"""
Test script to demonstrate data collection capabilities
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_data_sources():
    """List all available data sources"""
    print("=== DATA SOURCES ===")
    response = requests.get(f"{BASE_URL}/data/sources")
    sources = response.json()
    for source in sources:
        print(f"\n{source['name']}:")
        print(f"  - URL: {source['url']}")
        print(f"  - Updated: {source['last_updated']}")
        print(f"  - Fields: {', '.join(source['fields_used'])}")

def test_election_data():
    """Test election data retrieval"""
    print("\n\n=== ELECTION DATA ===")
    
    # Test some major counties
    counties = [
        ("California", "Los Angeles"),
        ("Texas", "Harris"),
        ("Florida", "Miami-Dade"),
        ("New York", "New York"),
        ("Illinois", "Cook"),
    ]
    
    for state, county in counties:
        response = requests.get(
            f"{BASE_URL}/data/election/county",
            params={"state": state, "county": county}
        )
        if response.status_code == 200:
            data = response.json()
            voting = data['voting_data']
            print(f"\n{county}, {state}:")
            print(f"  Democratic: {voting['democratic']}%")
            print(f"  Republican: {voting['republican']}%")
            print(f"  Other: {voting['other']}%")

def test_census_puma_mapping():
    """Test PUMA mapping retrieval"""
    print("\n\n=== CENSUS PUMA MAPPING ===")
    
    # Get PUMA mapping for California
    response = requests.get(f"{BASE_URL}/data/census/puma-mapping/06")
    if response.status_code == 200:
        data = response.json()
        print(f"California has {data['county_count']} counties")
        print("\nSample county-PUMA mappings:")
        
        # Show first 3 counties
        for i, (county, pumas) in enumerate(data['mapping'].items()):
            if i >= 3:
                break
            print(f"  {county}: {len(pumas)} PUMAs - {', '.join(pumas[:3])}...")

if __name__ == "__main__":
    print("Testing FreudLaw Backend Data Collection\n")
    
    test_data_sources()
    test_election_data()
    test_census_puma_mapping()
    
    print("\n\nData collection test complete!")
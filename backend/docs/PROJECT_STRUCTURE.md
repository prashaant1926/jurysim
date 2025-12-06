# FreudLaw Backend Project Structure

## Directory Layout

```
backend/
├── app/                        # Main application package
│   ├── __init__.py
│   ├── main.py                # FastAPI application entry point
│   │
│   ├── api/                   # API endpoint definitions
│   │   ├── __init__.py
│   │   ├── data_collection.py # Data source management endpoints
│   │   ├── health.py          # Health check endpoint
│   │   └── jurors.py          # Juror generation endpoints
│   │
│   ├── core/                  # Core configuration
│   │   ├── __init__.py
│   │   └── config.py          # Settings and environment config
│   │
│   ├── data_collection/       # Data fetching modules
│   │   ├── __init__.py
│   │   ├── census_data.py     # U.S. Census ACS PUMS fetcher
│   │   ├── election_data.py   # MIT Election Lab data fetcher
│   │   ├── gss_data.py        # General Social Survey collector
│   │   └── personality_data.py # IPIP-FFM personality data processor
│   │
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   └── demographics.py    # Pydantic models for demographics
│   │
│   └── services/              # Business logic
│       ├── __init__.py
│       └── juror_generator.py # Core juror generation service
│
├── data/                      # Data storage
│   └── raw/                   # Raw downloaded data
│       ├── county_election_2020.csv      # Election results
│       ├── gss_data.csv                  # GSS survey data (1.9GB)
│       └── IPIP-FFM-data-8Nov2018/      # Personality data
│           ├── codebook.txt
│           └── data-final.csv
│
├── docs/                      # Documentation
│   ├── README.md
│   ├── DATA_COLLECTION_SUMMARY.md
│   ├── GSS_DATA_SUCCESS.md
│   └── KAGGLE_SETUP.md
│
├── scripts/                   # Utility scripts
│   ├── README.md
│   ├── download_gss_*.py      # GSS download scripts
│   ├── explore_gss_*.py       # GSS exploration scripts
│   └── *_example.py           # Integration examples
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── README.md
│   ├── test_data_collection.py
│   ├── test_juror_generation.py
│   ├── test_juror_visual.py
│   └── test_complete_data_integration.py
│
├── .env                       # Environment variables (not in git)
├── .env.example              # Example environment configuration
├── .gitignore                # Git ignore rules
├── PROJECT_STRUCTURE.md      # This file
├── README.md                 # Main project documentation
├── requirements.txt          # Python dependencies
└── run_dev.py               # Development server runner
```

## Key Files

### Application Core
- `app/main.py` - FastAPI application with CORS and routing
- `app/core/config.py` - Settings management using environment variables

### Data Collection
- `app/data_collection/census_data.py` - Fetches demographic data from Census API
- `app/data_collection/election_data.py` - Downloads and processes election results
- `app/data_collection/gss_data.py` - Handles GSS survey data with column mappings
- `app/data_collection/personality_data.py` - Processes IPIP-FFM personality data

### Juror Generation
- `app/services/juror_generator.py` - Main service that:
  - Loads all data sources
  - Generates demographically accurate jurors
  - Assigns attitudes based on GSS data
  - Creates personality profiles
  - Generates deliberation traits

### API Endpoints
- `/api/v1/jurors/generate` - Generate jury pool for a county
- `/api/v1/data/*` - Various data collection endpoints
- `/api/v1/health` - Service health check

## Data Flow

1. **Data Collection**: Scripts fetch data from various sources
2. **Data Storage**: Raw data stored in `data/raw/`
3. **Data Loading**: JurorGenerator loads data on initialization
4. **Juror Generation**: 
   - County demographics determine base characteristics
   - GSS data provides attitudes
   - Personality traits adjusted based on demographics
   - Election data provides political context
5. **API Response**: Complete juror profiles returned as JSON

## Environment Variables

Required in `.env`:
- `CENSUS_API_KEY` - U.S. Census Bureau API key
- `ANTHROPIC_API_KEY` - Anthropic API key for AI features
- `PROJECT_NAME` - Application name
- `VERSION` - API version
- `API_V1_STR` - API path prefix
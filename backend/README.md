# FreudLaw Backend - AI Jury Simulation System

## Overview
Backend system for generating AI jurors based on county-level U.S. demographic data and simulating their deliberations using the Anthropic API.

## Features

- **Data Integration**: Combines multiple data sources for realistic juror profiles
  - U.S. Census ACS PUMS data for demographics
  - Big Five personality traits (IPIP-FFM dataset)
  - MIT Election Lab data for county voting patterns
  - General Social Survey (GSS) data for social attitudes
- **AI Juror Generation**: Creates 12-person jury pools with realistic characteristics
- **County-Specific**: Generates juries based on actual county demographics and political lean
- **Personality Modeling**: Assigns Big Five personality traits correlated with demographics and attitudes
- **RESTful API**: FastAPI-based backend with automatic documentation

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- PostgreSQL (optional, for production)
- Virtual environment tool (venv)

### 2. Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Running the Development Server

```bash
# Run the FastAPI server
python run_dev.py

# Or use uvicorn directly
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000
API documentation: http://localhost:8000/api/v1/docs

## API Endpoints

### Health Check
- `GET /api/v1/health` - Service health status

### Data Collection
- `GET /api/v1/data/sources` - List all data sources
- `POST /api/v1/data/census/fetch` - Fetch census data for a state
- `GET /api/v1/data/census/puma-mapping/{state_fips}` - Get county-PUMA mapping
- `POST /api/v1/data/personality/download` - Download personality data
- `POST /api/v1/data/election/download` - Download election data
- `GET /api/v1/data/election/county` - Get county election results

### Juror Generation
- `POST /api/v1/jurors/generate` - Generate a jury pool for a county
  - Parameters: county, state, pool_size (default: 12), case_type
- `GET /api/v1/jurors/sample/{state}` - Generate a single sample juror
- `GET /api/v1/jurors/demographics/stats` - Get demographic statistics for a county

## Data Sources

1. **American Community Survey (ACS) PUMS**
   - Source: U.S. Census Bureau
   - Fields: Age, Sex, Race, Education, Income, PUMA codes

2. **Big Five Personality Data**
   - Source: OpenPsychometrics.org
   - Dataset: IPIP-FFM (50-item personality inventory)
   - Over 1 million respondents with demographics

3. **Election Data**
   - Source: MIT Election Data Lab
   - Data: 2020 county-level presidential results

4. **General Social Survey (GSS)**
   - Source: NORC at University of Chicago (via Kaggle)
   - Fields: Political views, social attitudes, trust metrics
   - Years: 1972-2022 cumulative data file

## Testing

```bash
# Run API tests
python tests/test_juror_generation.py

# Run visual test (shows formatted juror output)
python tests/test_juror_visual.py

# Run data collection tests
python tests/test_data_collection.py
```

## Project Structure

```
backend/
├── app/                    # Main application code
│   ├── api/               # API endpoints
│   │   ├── data_collection.py
│   │   ├── deliberations.py
│   │   ├── health.py
│   │   └── jurors.py
│   ├── cli/               # Command-line interface
│   │   └── deliberation_interface.py
│   ├── core/              # Core configuration
│   │   └── config.py
│   ├── data_collection/   # Data fetching modules
│   │   ├── census_data.py
│   │   ├── election_data.py
│   │   ├── gss_data.py
│   │   └── personality_data.py
│   ├── models/            # Data models
│   │   ├── deliberation.py
│   │   └── demographics.py
│   ├── services/          # Business logic
│   │   ├── ai_juror_agent.py
│   │   ├── deliberation_engine.py
│   │   ├── discussion_tracker.py
│   │   ├── juror_generator.py
│   │   ├── responsive_deliberation_engine.py
│   │   └── ...
│   └── main.py           # FastAPI app
├── data/                  # Data storage
│   ├── raw/              # Raw data files
│   │   ├── county_election_2020.csv
│   │   ├── gss_data.csv (1.9GB)
│   │   └── IPIP-FFM-data-8Nov2018/
│   └── case_files/       # Case documents (OJ Simpson, Zimmerman)
├── docs/                  # Documentation
├── examples/              # Example scripts and demos
├── scripts/               # Utility scripts
│   ├── scrapers/         # Web scrapers for case data
│   └── ...
├── tests/                 # Test files
│   └── integration/      # Integration tests
├── transcripts/           # Deliberation transcripts
├── .env                   # Environment variables (not in git)
├── requirements.txt       # Python dependencies
├── run_dev.py            # Development server runner
└── run_deliberation.py   # CLI deliberation runner
```
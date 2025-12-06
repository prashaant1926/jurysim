# FreudLaw - AI Jury Simulation Platform

An AI-powered jury simulation system that generates realistic 12-person jury pools based on county-level U.S. demographics and simulates deliberations using advanced psychological modeling.

## Overview

FreudLaw combines demographic data, personality psychology, and AI to create realistic jury simulations for legal research and case strategy testing. The system generates jurors with authentic personality traits, attitudes, and biases based on actual U.S. Census data, election results, and social survey data.

## Key Features

- **Demographically Accurate Jury Pools**: Generate 12-person juries based on actual county-level demographic distributions
- **Psychological Modeling**: Apply Big Five personality traits and Freudian concepts to juror behavior
- **Multi-Source Data Integration**: Combines U.S. Census ACS PUMS, MIT Election Lab, General Social Survey, and IPIP-FFM personality data
- **AI-Powered Deliberation**: Realistic jury deliberation simulation using Anthropic's Claude API
- **County-Specific Analysis**: Select any U.S. county for location-specific jury composition
- **Real Case Studies**: Includes case files and deliberation transcripts from notable trials (OJ Simpson, George Zimmerman)

## Project Structure

```
FreudLaw/
├── backend/              # Python/FastAPI backend
│   ├── app/             # Application code
│   ├── data/            # Data files and case documents
│   ├── docs/            # Documentation
│   ├── scripts/         # Utility scripts
│   └── tests/           # Test suite
├── frontend-app/        # React/Next.js web application
│   └── src/             # Frontend source code
├── landing-page/        # Marketing/landing page
│   └── src/             # Landing page components
└── README.md           # This file
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI**: Anthropic Claude API
- **Data Processing**: Pandas, Polars
- **Testing**: Pytest

### Frontend
- **Framework**: React 19 + Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Build**: Next.js with Turbopack

### Data Sources
- U.S. Census Bureau ACS PUMS (demographics)
- MIT Election Data Lab (county voting patterns)
- General Social Survey (NORC - social attitudes)
- OpenPsychometrics IPIP-FFM (personality data)

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (optional, for production)
- **Git LFS** (for accessing large datasets)
- Anthropic API key
- U.S. Census API key (optional)

**Important**: This repository uses Git LFS for large data files. Install Git LFS before cloning:
```bash
# macOS
brew install git-lfs

# Ubuntu/Debian
sudo apt-get install git-lfs

# Windows: Download from git-lfs.github.com
```

See [DATA_SETUP.md](DATA_SETUP.md) for detailed data access instructions.

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY (required)
# - CENSUS_API_KEY (optional)
# - DATABASE_URL (optional, defaults to SQLite)

# Run development server
python run_dev.py
```

The API will be available at http://localhost:8000

API documentation: http://localhost:8000/api/v1/docs

### Frontend Setup

```bash
cd frontend-app

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:3000

## Usage

### Generate a Jury Pool

```bash
# Via API
curl -X POST "http://localhost:8000/api/v1/jurors/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "county": "Cook County",
    "state": "Illinois",
    "pool_size": 12,
    "case_type": "criminal"
  }'
```

### Run a Deliberation Simulation

```bash
cd backend
python run_deliberation.py
```

Follow the CLI prompts to:
1. Select a county
2. Choose a case (or provide custom case details)
3. Watch the AI jury deliberate in real-time
4. View final verdict and analysis

## Data Collection

The system automatically downloads and processes public datasets:

- **Census data**: Fetched via Census API
- **Election data**: Downloaded from MIT Election Lab
- **Personality data**: Retrieved from OpenPsychometrics
- **GSS data**: Downloaded from Kaggle (requires Kaggle API setup)

See `backend/docs/DATA_COLLECTION_SUMMARY.md` for detailed information.

## API Endpoints

### Health & Status
- `GET /api/v1/health` - Health check

### Jury Generation
- `POST /api/v1/jurors/generate` - Generate jury pool
- `GET /api/v1/jurors/sample/{state}` - Get sample juror
- `GET /api/v1/jurors/demographics/stats` - County statistics

### Data Collection
- `GET /api/v1/data/sources` - List data sources
- `POST /api/v1/data/census/fetch` - Fetch census data
- `POST /api/v1/data/personality/download` - Download personality data
- `POST /api/v1/data/election/download` - Download election results

### Deliberation
- `POST /api/v1/deliberations/start` - Start deliberation
- `GET /api/v1/deliberations/{id}/stream` - Stream deliberation progress

## Documentation

- **[Data Setup Guide](DATA_SETUP.md)** - Git LFS and dataset access instructions
- [Backend README](backend/README.md) - Detailed backend documentation
- [Project Structure](backend/docs/PROJECT_STRUCTURE.md) - Codebase organization
- [Jury Deliberation System](backend/docs/JURY_DELIBERATION.md) - Deliberation mechanics
- [Prompt Engineering](backend/docs/JURY_DELIBERATION_PROMPTS.md) - AI prompt design
- [Data Collection](backend/docs/DATA_COLLECTION_SUMMARY.md) - Data sources and integration
- [Census Integration](backend/docs/CENSUS_INTEGRATION.md) - Census API usage
- [Kaggle Setup](backend/docs/KAGGLE_SETUP.md) - GSS data setup

## Testing

```bash
# Backend tests
cd backend
pytest

# Run specific tests
python tests/test_juror_generation.py
python tests/test_data_collection.py
python tests/test_juror_visual.py

# Frontend tests
cd frontend-app
npm test
```

## Example Use Cases

1. **Legal Research**: Test how different jury compositions might respond to case arguments
2. **Case Strategy**: Understand potential biases and perspectives in specific counties
3. **Educational Tool**: Demonstrate jury psychology and deliberation dynamics
4. **Social Science**: Research demographic influences on legal decision-making

## Ethical Considerations

This system is designed for research and educational purposes only. Key considerations:

- Simulated jurors are based on statistical correlations, not deterministic stereotypes
- Real jury outcomes depend on countless factors beyond demographics
- This tool should complement, not replace, traditional legal research
- Generated deliberations are AI simulations and may not reflect real-world outcomes

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- U.S. Census Bureau for demographic data
- MIT Election Data + Science Lab for election results
- NORC at University of Chicago for General Social Survey data
- OpenPsychometrics for IPIP-FFM personality dataset
- Anthropic for Claude API access

## Contact

For questions or collaboration inquiries, please open an issue on GitHub.

---

**Note**: This is a research and educational tool. Always consult with qualified legal professionals for actual legal cases.

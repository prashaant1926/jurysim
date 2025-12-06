# Web Scrapers

This directory contains web scrapers for gathering trial documents and transcripts.

## Available Scrapers

### OJ Simpson Trial
- `scrape_oj_simpson.py` - Basic OJ Simpson trial scraper
- `scrape_oj_complete.py` - Comprehensive OJ Simpson document scraper
- `scrape_oj_transcripts.py` - Transcript-specific scraper

### George Zimmerman Trial
- `scrape_zimmerman_trial.py` - Basic Zimmerman trial scraper
- `scrape_zimmerman_complete.py` - Comprehensive Zimmerman document scraper with PDF support

## Usage

```bash
# Scrape OJ Simpson trial documents
python scripts/scrapers/scrape_oj_complete.py

# Scrape Zimmerman trial documents
python scripts/scrapers/scrape_zimmerman_complete.py
```

## Output

Scrapers save their output to the `data/case_files/` directory:
- JSON files with structured case data
- Text summaries
- Complete content archives
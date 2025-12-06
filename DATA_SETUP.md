# Data Setup and Access Guide

This repository uses **Git LFS (Large File Storage)** to manage large dataset files efficiently.

## What is Git LFS?

Git LFS is an extension for Git that allows you to store large files outside the main Git repository while keeping lightweight pointers in the repo. This makes cloning and pulling much faster while still giving you access to all the data.

## Files Stored with Git LFS

The following large datasets are tracked with Git LFS:

- **`backend/data/raw/gss_data.csv`** (1.9 GB)
  - General Social Survey cumulative data file (1972-2022)
  - Source: NORC at University of Chicago via Kaggle
  - Contains social attitudes, political views, and demographic data

- **`backend/data/raw/county_election_2020.csv`** (340 KB)
  - County-level 2020 U.S. presidential election results
  - Source: MIT Election Data + Science Lab

## Setup Instructions

### 1. Install Git LFS

Before cloning this repository, install Git LFS:

**macOS:**
```bash
brew install git-lfs
```

**Ubuntu/Debian:**
```bash
sudo apt-get install git-lfs
```

**Windows:**
Download from [git-lfs.github.com](https://git-lfs.github.com/)

**Verify installation:**
```bash
git lfs version
# Should output: git-lfs/3.x.x
```

### 2. Clone the Repository

```bash
# Clone with LFS support
git clone https://github.com/YOUR_USERNAME/FreudLaw.git
cd FreudLaw

# Initialize Git LFS (if not already done)
git lfs install

# Pull LFS files (should happen automatically during clone)
git lfs pull
```

### 3. Verify Data Files

Check that the large files were downloaded correctly:

```bash
# Check LFS-tracked files
git lfs ls-files

# Verify file sizes
ls -lh backend/data/raw/*.csv
```

You should see:
- `gss_data.csv` - approximately 1.9 GB
- `county_election_2020.csv` - approximately 340 KB

## Accessing the Data

### GSS Data (General Social Survey)

```python
import pandas as pd

# Load GSS data
gss_df = pd.read_csv('backend/data/raw/gss_data.csv')

print(f"GSS dataset shape: {gss_df.shape}")
print(f"Columns: {gss_df.columns.tolist()}")
```

Key GSS variables used in FreudLaw:
- `polviews` - Political views (1=Extremely liberal to 7=Extremely conservative)
- `trust` - Can people be trusted?
- `age`, `sex`, `race`, `educ` - Demographics
- `income` - Income level
- `year` - Survey year

### Election Data

```python
import pandas as pd

# Load election results
election_df = pd.read_csv('backend/data/raw/county_election_2020.csv')

# Example: Get results for a specific county
cook_county = election_df[
    (election_df['county_name'] == 'Cook County') &
    (election_df['state_name'] == 'Illinois')
]
```

## File Structure

```
backend/data/
├── raw/                          # Raw data files
│   ├── gss_data.csv             # [LFS] 1.9 GB - GSS cumulative file
│   ├── county_election_2020.csv # [LFS] 340 KB - Election results
│   ├── IPIP-FFM-data-8Nov2018/  # Personality data (excluded from repo)
│   └── census_cache/            # Census API cache (excluded)
├── case_files/                   # Legal case documents
│   ├── oj_simpson_*.json        # OJ Simpson trial documents
│   └── zimmerman_*.json         # George Zimmerman trial documents
└── processed/                    # Generated data (excluded)
```

## Troubleshooting

### Files Not Downloading

If large files didn't download during clone:

```bash
git lfs fetch --all
git lfs pull
```

### Check LFS Configuration

```bash
# View LFS tracking rules
cat .gitattributes

# Check LFS status
git lfs status
```

### Download Individual Files

```bash
# Pull specific file
git lfs pull --include="backend/data/raw/gss_data.csv"
```

### Disk Space Issues

The GSS dataset is large (1.9 GB). If you don't need it:

```bash
# Skip LFS files during clone
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/YOUR_USERNAME/FreudLaw.git

# Then download only what you need
cd FreudLaw
git lfs pull --include="backend/data/raw/county_election_2020.csv"
```

## Alternative: Download Data Manually

If you prefer not to use Git LFS, you can download datasets directly:

### GSS Data (via Kaggle)

```bash
cd backend
pip install kaggle

# Configure Kaggle API (requires kaggle.json credentials)
# See: https://github.com/Kaggle/kaggle-api#api-credentials

# Download GSS data
kaggle datasets download -d noaa/general-social-survey -p data/raw/
unzip data/raw/general-social-survey.zip -d data/raw/
```

### Election Data (via MIT Election Lab)

```bash
cd backend/scripts
python download_election_data.py
```

See [`backend/docs/KAGGLE_SETUP.md`](backend/docs/KAGGLE_SETUP.md) for detailed instructions.

## Data Licensing

- **GSS Data**: Public domain, provided by NORC
- **Election Data**: Public domain, provided by MIT Election Lab
- **Census Data**: Public domain, U.S. Census Bureau
- **Personality Data**: Academic use, OpenPsychometrics

## Storage Costs

Git LFS is free for public repositories on GitHub with the following limits:
- **Storage**: 1 GB free (GSS data uses 1.9 GB - may require paid plan)
- **Bandwidth**: 1 GB/month free

For larger projects, consider:
- GitHub paid plans (higher LFS limits)
- Self-hosted Git LFS server
- External data hosting (S3, Google Drive) with download scripts

## Need Help?

- Git LFS Documentation: https://git-lfs.github.com/
- FreudLaw Issues: https://github.com/YOUR_USERNAME/FreudLaw/issues
- Data Collection Guide: [`backend/docs/DATA_COLLECTION_SUMMARY.md`](backend/docs/DATA_COLLECTION_SUMMARY.md)

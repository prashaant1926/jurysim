# Kaggle Setup for GSS Data Download

## Quick Setup Steps

1. **Create Kaggle Account** (if you don't have one)
   - Go to https://www.kaggle.com
   - Sign up for free

2. **Generate API Token**
   - Go to https://www.kaggle.com/account
   - Scroll to "API" section
   - Click "Create New API Token"
   - This downloads `kaggle.json`

3. **Install Credentials**
   ```bash
   # Create kaggle directory
   mkdir -p ~/.kaggle
   
   # Move the downloaded kaggle.json to the directory
   mv ~/Downloads/kaggle.json ~/.kaggle/
   
   # Set permissions
   chmod 600 ~/.kaggle/kaggle.json
   ```

4. **Download GSS Data**
   ```bash
   # Run our download script
   python download_gss_data.py
   ```

## Alternative: Manual Download

If you prefer to download manually:

1. Visit: https://www.kaggle.com/datasets/norc/general-social-survey
2. Click "Download" (requires login)
3. Extract the ZIP file
4. Copy the CSV file to: `data/raw/gss_data.csv`

## Using Python Script

Once credentials are set up, you can also use:

```python
import kagglehub

# Download latest version
path = kagglehub.dataset_download("norc/general-social-survey")
print(f"Downloaded to: {path}")
```

## Troubleshooting

- **"kaggle: command not found"**: Add `~/.local/bin` to your PATH
- **Authentication errors**: Make sure kaggle.json has correct permissions (600)
- **Download fails**: Check internet connection and Kaggle API status
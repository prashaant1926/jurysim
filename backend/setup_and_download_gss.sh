#!/bin/bash
# Setup and download GSS data

echo "=== GSS Data Download Setup ==="
echo

# Step 1: Check for Kaggle credentials
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "❌ Kaggle credentials not found!"
    echo
    echo "Please follow these steps:"
    echo "1. Open your browser and go to: https://www.kaggle.com"
    echo "2. Sign in or create a free account"
    echo "3. Go to: https://www.kaggle.com/account"
    echo "4. Scroll down to 'API' section"
    echo "5. Click 'Create New API Token'"
    echo "6. This will download a file called 'kaggle.json'"
    echo
    echo "Once downloaded, press Enter to continue..."
    read
    
    # Create kaggle directory
    mkdir -p ~/.kaggle
    
    # Look for the downloaded file
    if [ -f ~/Downloads/kaggle.json ]; then
        echo "✓ Found kaggle.json in Downloads folder"
        cp ~/Downloads/kaggle.json ~/.kaggle/
        chmod 600 ~/.kaggle/kaggle.json
        echo "✓ Credentials installed!"
    else
        echo "Please move kaggle.json to ~/.kaggle/ manually:"
        echo "  mv ~/Downloads/kaggle.json ~/.kaggle/"
        echo "  chmod 600 ~/.kaggle/kaggle.json"
        echo
        echo "Then run this script again."
        exit 1
    fi
fi

echo "✓ Kaggle credentials found"
echo

# Step 2: Download GSS data
echo "Downloading GSS data..."
python download_gss_simple.py

echo
echo "Done! Check data/raw/gss_data.csv"
#!/usr/bin/env python3
"""
Download GSS data from Kaggle
"""
import os
import sys
import subprocess
from pathlib import Path
import shutil

def install_kaggle_dependencies():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "kaggle", "kagglehub"])
        print("✓ Packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def check_kaggle_auth():
    """Check if Kaggle credentials are set up"""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    
    if not kaggle_json.exists():
        print("\n❌ Kaggle credentials not found!")
        print("\nTo set up Kaggle authentication:")
        print("1. Go to https://www.kaggle.com/account")
        print("2. Click 'Create New API Token'")
        print("3. Save the downloaded kaggle.json to ~/.kaggle/")
        print("4. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    print("✓ Kaggle credentials found")
    return True

def download_gss_with_kagglehub():
    """Download GSS dataset using kagglehub"""
    try:
        import kagglehub
        
        print("\nDownloading GSS dataset using kagglehub...")
        path = kagglehub.dataset_download("norc/general-social-survey")
        print(f"✓ Dataset downloaded to: {path}")
        
        # Copy to our data directory
        dest_dir = Path("data/raw/gss")
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Find the CSV file in the downloaded path
        downloaded_path = Path(path)
        csv_files = list(downloaded_path.glob("*.csv"))
        
        if csv_files:
            # Copy the main GSS data file
            main_file = csv_files[0]  # Usually there's one main CSV
            dest_file = dest_dir / "gss_data.csv"
            shutil.copy2(main_file, dest_file)
            print(f"✓ Copied GSS data to: {dest_file}")
            
            # Also copy any other files
            for csv_file in csv_files[1:]:
                shutil.copy2(csv_file, dest_dir / csv_file.name)
                
            return dest_file
        else:
            print("❌ No CSV files found in downloaded dataset")
            return None
            
    except ImportError:
        print("❌ kagglehub not installed. Run: pip install kagglehub")
        return None
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        return None

def download_gss_with_cli():
    """Alternative: Download using Kaggle CLI"""
    try:
        print("\nDownloading GSS dataset using Kaggle CLI...")
        
        # Create destination directory
        dest_dir = Path("data/raw/gss")
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Download dataset
        subprocess.run([
            "kaggle", "datasets", "download", 
            "-d", "norc/general-social-survey",
            "-p", str(dest_dir),
            "--unzip"
        ], check=True)
        
        print(f"✓ Dataset downloaded to: {dest_dir}")
        
        # Find the main CSV file
        csv_files = list(dest_dir.glob("*.csv"))
        if csv_files:
            # Rename to standard name
            main_file = csv_files[0]
            dest_file = dest_dir / "gss_data.csv"
            if main_file != dest_file:
                main_file.rename(dest_file)
            return dest_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error with Kaggle CLI: {e}")
        print("Make sure 'kaggle' command is in your PATH")
        return None
    except FileNotFoundError:
        print("❌ Kaggle CLI not found. Make sure it's installed and in PATH")
        return None

def verify_gss_data(file_path):
    """Verify the downloaded GSS data"""
    try:
        import pandas as pd
        
        print(f"\nVerifying GSS data at: {file_path}")
        
        # Load a sample to check
        df = pd.read_csv(file_path, nrows=1000)
        
        print(f"✓ Successfully loaded GSS data")
        print(f"  Rows (sample): {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        
        # Check for key GSS variables
        key_vars = ['age', 'sex', 'race', 'educ', 'polviews', 'cappun', 'trust']
        found_vars = [var for var in key_vars if var in df.columns or var.upper() in df.columns]
        
        print(f"  Key variables found: {', '.join(found_vars)}")
        
        # Show some sample columns
        print(f"\n  Sample columns: {', '.join(df.columns[:10])}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        return False

def main():
    print("=== GSS DATA DOWNLOAD SCRIPT ===\n")
    
    # Step 1: Install dependencies
    if not install_kaggle_dependencies():
        return
    
    # Step 2: Check authentication
    if not check_kaggle_auth():
        print("\nPlease set up Kaggle authentication and run this script again.")
        return
    
    # Step 3: Try downloading with kagglehub first
    file_path = download_gss_with_kagglehub()
    
    # Step 4: If that fails, try CLI
    if not file_path:
        print("\nTrying alternative download method...")
        file_path = download_gss_with_cli()
    
    # Step 5: Verify the data
    if file_path and file_path.exists():
        if verify_gss_data(file_path):
            print("\n✅ GSS data successfully downloaded and verified!")
            print(f"📁 Location: {file_path}")
            
            # Update the GSS collector to use this path
            print("\nUpdating GSS data collector configuration...")
            config_file = Path("data/raw/gss_data.csv")
            if file_path != config_file:
                shutil.copy2(file_path, config_file)
                print(f"✓ Copied to expected location: {config_file}")
        else:
            print("\n❌ Data verification failed")
    else:
        print("\n❌ Download failed")
        print("\nManual download instructions:")
        print("1. Go to https://www.kaggle.com/datasets/norc/general-social-survey")
        print("2. Click 'Download' (requires Kaggle account)")
        print("3. Extract and place the CSV file at: data/raw/gss_data.csv")

if __name__ == "__main__":
    main()
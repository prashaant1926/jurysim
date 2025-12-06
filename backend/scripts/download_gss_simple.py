#!/usr/bin/env python3
"""
Simple GSS download using kagglehub
"""

def download_gss():
    try:
        import kagglehub
        import shutil
        from pathlib import Path
        
        print("Downloading GSS dataset...")
        
        # Download dataset
        path = kagglehub.dataset_download("norc/general-social-survey")
        
        print(f"Downloaded to: {path}")
        
        # Copy to our expected location
        source_path = Path(path)
        dest_path = Path("data/raw/gss_data.csv")
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Find CSV file
        csv_files = list(source_path.glob("*.csv"))
        if csv_files:
            shutil.copy2(csv_files[0], dest_path)
            print(f"Copied to: {dest_path}")
            
            # Quick preview
            import pandas as pd
            df = pd.read_csv(dest_path, nrows=5)
            print(f"\nDataset shape: {len(df)} rows (preview), {len(df.columns)} columns")
            print(f"Columns: {', '.join(df.columns[:10])}...")
            
            return dest_path
        else:
            print("No CSV files found in download")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Kaggle account")
        print("2. API token in ~/.kaggle/kaggle.json")
        print("3. Run: pip install kagglehub")

if __name__ == "__main__":
    download_gss()
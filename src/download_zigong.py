# Define libraries
import requests 
import zipfile
import io 
from pathlib import Path 

# Define URL to data download 
BASE_URL = "https://physionet.org/content/heart-failure-zigong/1.3/"

# Define specific files required
FILES = [
    "dat_icu.csv",
    "dat_md.csv",
    "variable_description.csv",
]

# Define save directory and make directory 
SAVE_DIR = Path("data/raw/zigong")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Define download function to request file and write file
def download_file(filename: str) -> None: 
    # Construct Url 
    url = BASE_URL + filename 
    print(f"Downloading {filename}...")
    
    response = requests.get(url, stream=True)
    
    if response.status_code == 200: 
        save_path = SAVE_DIR / filename
        with open(save_path, "wb") as f: 
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
            print(f" Saved to {save_path}")
    else:
        print(f" Failed: HTTP {response.status_code} for {url}")

def verify_downloads() -> None: 
    print(f" \nVerifying downloads...")
    for filename in FILES: 
        path = SAVE_DIR / filename
        if path.exists():
            size_kb = path.stat().st_size / 1024 
            print(f" {filename}: {size_kb: .1f} KB")
        else:
            print(f" MISSING: {filename}")

if __name__ == "__main__":
    # Download files
    print("=== Downloading Zigong Heart Failure Dataset ===\n")
    for f in FILES:
        download_file(f)
    # Verify downloads
    verify_downloads()
    print("\nDone")
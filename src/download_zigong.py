"""
download_zigong.py

Data source: PhysioNet — Zigong Heart Failure Dataset v1.3
https://physionet.org/content/heart-failure-zigong/1.3/

Download instructions:
    Requires a free PhysioNet account (physionet.org/register).
    Run the following in your terminal from data/raw/zigong/:

    wget -r -N -c -np --user <your_username> --ask-password \
        https://physionet.org/files/heart-failure-zigong/1.3/

Expected files after download:
    - dat_icu.csv         : main clinical table (2,008 patients, ~168 variables)
    - dat_md.csv          : medication table (multiple rows per patient)
    - variable_description.csv : data dictionary

Citation:
    Zhang Z et al. Electronic healthcare records and external outcome
    data for hospitalized patients with heart failure.
    Sci Data. 2021;8(1):46.
"""

# Define libraries
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment file and obtain required credentials
load_dotenv()

PHYSIONET_USER = os.getenv("PHYSIONET_USER")
PHYSIONET_PASSWORD = os.getenv("PHYSIONET_PASSWORD")
DOWNLOAD_URL = "https://physionet.org/files/heart-failure-zigong/1.3/"
SAVE_DIR = Path("data/raw/zigong")

# Define a function to check credentials
def check_credentials() -> bool:
    if not PHYSIONET_USER or not PHYSIONET_PASSWORD:
        print("ERROR: PHYSIONET_USER or PHYSIONET_PASSWORD not found in .env")
        print(" 1. Copy .env.example to .env")
        print(" 2. Fill in your PhysioNet credentials")
        return False
    return True

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
def download(filename: str) -> None: 
    # Make directory if it exists
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create command 
    command = [
        "wget",
        "-r", "-N", "-c", "-np",
        f"--user={PHYSIONET_USER}",
        f"--password={PHYSIONET_PASSWORD}"
        "-P", str(SAVE_DIR),
        DOWNLOAD_URL,
    ]
    
    print(f"Downloading Zigong dataset to {SAVE_DIR}...\n")
    subprocess.run(command, check=True)

def verify_downloads() -> None: 
    # Define expected files from download link
    expected = [
        "dat_icu.csv",
        "dat_md.csv", 
        "variable_description.csv"
    ]
    print(f" \nVerifying downloads...")
    all_present = True
    
    for filename in expected: 
        filepath = SAVE_DIR / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  OK  {filename} ({size_kb:.1f} KB)")
        else:
            print(f"  MISSING  {filename}")
            all_present = False

    if all_present:
        print("\nAll files present. Ready to proceed.")
    else:
        print("\nSome files missing. Check credentials and re-run.")

if __name__ == "__main__":
    # Download files
    print("=== Downloading Zigong Heart Failure Dataset ===\n")
    if check_credentials():
        download()
        verify_downloads()
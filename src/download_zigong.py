import os
import getpass
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_URL  = "https://physionet.org/protected/published-projects/heart-failure-zigong/1.3/"
LOGIN_URL = "https://physionet.org/login/"
SAVE_DIR  = Path("data/raw/zigong")

FILES = [
    "dat.csv",
    "dat_md.csv",
    "dataDictionary.csv",
    "LICENSE.txt",
    "SHA256SUMS.txt",
]


def get_credentials() -> tuple[str, str]:
    """
    Load credentials from .env if available.
    Falls back to interactive prompt so anyone can run this script
    without needing to set up a .env file first.
    """
    username = os.getenv("PHYSIONET_USER")
    password = os.getenv("PHYSIONET_PASSWORD")

    if not username:
        print("PHYSIONET_USER not found in .env")
        username = input("Enter your PhysioNet username: ").strip()

    if not password:
        print("PHYSIONET_PASSWORD not found in .env")
        password = getpass.getpass("Enter your PhysioNet password: ")

    return username, password


def create_session(username: str, password: str) -> requests.Session | None:
    """
    Log in to PhysioNet using a session so cookies are
    preserved across requests — same as a browser login.
    """
    session = requests.Session()

    # Step 1 — GET the login page to retrieve the CSRF token
    print("Connecting to PhysioNet...")
    response = session.get(LOGIN_URL)

    if response.status_code != 200:
        print(f"  ERROR: Could not reach login page (HTTP {response.status_code})")
        return None

    # Step 2 — Extract CSRF token from the login page
    csrf_token = None
    for line in response.text.splitlines():
        if "csrfmiddlewaretoken" in line:
            csrf_token = line.split('value="')[1].split('"')[0]
            break

    if not csrf_token:
        print("  ERROR: Could not find CSRF token on login page.")
        return None

    # Step 3 — POST login credentials with CSRF token
    login_payload = {
        "username":            username,
        "password":            password,
        "csrfmiddlewaretoken": csrf_token,
        "next":                "/",
    }

    headers = {
        "Referer": LOGIN_URL,
    }

    response = session.post(LOGIN_URL, data=login_payload, headers=headers)

    # Step 4 — Check login succeeded
    if "logout" in response.text.lower() or response.status_code == 200:
        print("  Logged in successfully.\n")
        return session
    else:
        print("  ERROR: Login failed. Check your credentials.")
        print("  Make sure your account is verified at https://physionet.org")
        return None


def download_file(filename: str, session: requests.Session) -> bool:
    url       = BASE_URL + filename
    save_path = SAVE_DIR / filename

    print(f"Downloading {filename}...")

    try:
        response = session.get(url, stream=True, timeout=60)

        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            size_kb = save_path.stat().st_size / 1024
            print(f"  OK  {filename} ({size_kb:.1f} KB)")
            return True

        elif response.status_code == 401:
            print("  ERROR: Not authorized.")
            print("  Make sure you accepted the DUA at:")
            print("  https://physionet.org/content/heart-failure-zigong/1.3/")
            return False

        elif response.status_code == 403:
            print("  ERROR: Access denied.")
            print("  Visit https://physionet.org/content/heart-failure-zigong/1.3/")
            print("  Log in and accept the data use agreement, then re-run.")
            return False

        elif response.status_code == 404:
            print(f"  ERROR: File not found at {url}")
            return False

        else:
            print(f"  ERROR: HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("  ERROR: No internet connection.")
        return False

    except requests.exceptions.Timeout:
        print("  ERROR: Request timed out. Try again.")
        return False


def verify_downloads() -> bool:
    print("\nVerifying downloads...")
    all_present = True

    # Only verify the core data files, not license/checksum
    expected = ["dat.csv", "dat_md.csv", "dataDictionary.csv"]

    for filename in expected:
        filepath = SAVE_DIR / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  OK      {filename} ({size_kb:.1f} KB)")
        else:
            print(f"  MISSING {filename}")
            all_present = False

    return all_present


if __name__ == "__main__":
    print("=" * 50)
    print("  Zigong Heart Failure Dataset Downloader")
    print("  Source: PhysioNet (free account required)")
    print("  https://physionet.org/register")
    print("=" * 50)
    print()

    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    username, password = get_credentials()
    print()

    session = create_session(username, password)
    if session is None:
        exit(1)

    all_ok = True
    for f in FILES:
        success = download_file(f, session)
        if not success:
            all_ok = False
            break

    if all_ok:
        verified = verify_downloads()
        if verified:
            print("\nDownload complete. You can now run the MySQL loader.")
        else:
            print("\nSomething went wrong. Re-run the script.")
    else:
        print("\nDownload aborted. Fix the error above and re-run.")
from pathlib import Path

# Base directory is the package directory; project data/ folder lives alongside package files
BASE_DIR = Path(__file__).resolve().parent

# Top-level data directory and raw data subdirectory
DATA_DIR = BASE_DIR / "data"
DATA_DIR_RAW = DATA_DIR / "raw"

# Ensure raw data directory exists when used from notebooks/scripts
DATA_DIR_RAW.mkdir(parents=True, exist_ok=True)

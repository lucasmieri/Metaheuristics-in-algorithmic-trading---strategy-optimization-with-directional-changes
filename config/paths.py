from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
print(PROJECT_ROOT)

DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_CACHE_DIR = DATA_DIR / "cache"

LOGS_DIR = PROJECT_ROOT / "logs"
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_EXPERIMENTS_DIR = RESULTS_DIR / "experiments"
RESULTS_FIGURES_DIR = RESULTS_DIR / "figures"
RESULTS_TABLES_DIR = RESULTS_DIR / "tables"

for directory in [DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_CACHE_DIR,
                  LOGS_DIR, RESULTS_EXPERIMENTS_DIR, RESULTS_FIGURES_DIR,
                  RESULTS_TABLES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
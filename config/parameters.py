from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).parent.parent


_end_date_str: str = "2025-12-31"
_end_date: date = date.fromisoformat(_end_date_str)
_lookback_years: int = 10
_start_date: date = _end_date.replace(year=_end_date.year - _lookback_years)
_start_date_str: str = _start_date.isoformat()


dict_input_parameters: dict = {
    "lookback_years": _lookback_years,
    "start_date": _start_date_str,
    "end_date": _end_date_str,
    "data_source": "yahoo",
    "interval": "1d",
    "min_valid_rows": 2000,
    "dc_thresholds": [0.005, 0.01, 0.02, 0.03, 0.05],
    "dc_default_threshold": 0.02,
    "b3_tickers": [
        # Financials
        "ITUB4.SA", "BBDC4.SA", "BBAS3.SA",
        # Commodities
        "VALE3.SA", "PETR4.SA", "SUZB3.SA", "EMBR3.SA",
        # Consumer
        "ABEV3.SA", "BRFS3.SA", "MRFG3.SA", "LREN3.SA",
        # Retail
        "MGLU3.SA",
        # Utilities
        "ELET3.SA", "CMIG4.SA", "ENBR3.SA", "TAEE11.SA",
        # Construction
        "MRVE3.SA", "CYRE3.SA",
        # Telecom
        "VIVT3.SA", "TIMS3.SA",
        # Healthcare
        "RDOR3.SA",
        # Industrial
        "WEG3.SA", "RENT3.SA", "RAIL3.SA",
    ],
}


dict_path_parameters: dict = {
    "project_root":             PROJECT_ROOT,
    "config_dir":               PROJECT_ROOT / "config",
    "data_dir":                 PROJECT_ROOT / "data",
    "data_raw_dir":             PROJECT_ROOT / "data" / "raw",
    "data_processed_dir":       PROJECT_ROOT / "data" / "processed",
    "data_cache_dir":           PROJECT_ROOT / "data" / "cache",
    "logs_dir":                 PROJECT_ROOT / "logs",
    "results_dir":              PROJECT_ROOT / "results",
    "results_experiments_dir":  PROJECT_ROOT / "results" / "experiments",
    "results_figures_dir":      PROJECT_ROOT / "results" / "figures",
    "results_tables_dir":       PROJECT_ROOT / "results" / "tables",
    "src_dir":                  PROJECT_ROOT / "src",
    "tests_dir":                PROJECT_ROOT / "tests",
}

for _path in dict_path_parameters.values():
    if isinstance(_path, Path):
        _path.mkdir(parents=True, exist_ok=True)
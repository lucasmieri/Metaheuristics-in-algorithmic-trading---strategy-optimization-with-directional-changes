from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

dict_input_parameters = {
    "lookback_years": 10,
    "end_date": "2025-12-31",
    "data_source": "yahoo",
    "interval": "1d",
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
            "WEG3.SA", "RENT3.SA", "RAIL3.SA"
    ]
}

dict_path_parameters = {
    "project_root": PROJECT_ROOT,
    "config_dir": PROJECT_ROOT / "config",
    "data_dir": PROJECT_ROOT / "data",
    "data_raw_dir": PROJECT_ROOT / "data" / "raw",
    "data_processed_dir": PROJECT_ROOT / "data" / "processed",
    "data_cache_dir": PROJECT_ROOT / "data" / "cache",
    "logs_dir": PROJECT_ROOT / "logs",
    "results_dir": PROJECT_ROOT / "results",
    "results_experiments_dir": PROJECT_ROOT / "results" / "experiments",
    "results_figures_dir": PROJECT_ROOT / "results" / "figures",
    "results_tables_dir": PROJECT_ROOT / "results" / "tables",
    "src_dir": PROJECT_ROOT / "src",
    "tests_dir": PROJECT_ROOT / "tests"
}

for path_value in dict_path_parameters.values():
    if isinstance(path_value, Path):
        path_value.mkdir(parents=True, exist_ok=True)
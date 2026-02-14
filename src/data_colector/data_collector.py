"""
Data Collector Module
Simple historical stock data collection with intelligent cache
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, Any


def collect_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    data_dir: Path,
    min_valid_rows: int = 2000,
    logger: Optional[Any] = None
) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Collect historical stock data with cache verification
    
    Args:
        ticker: Stock symbol (e.g., 'ITUB4.SA')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        data_dir: Directory to save data
        min_valid_rows: Minimum number of rows to consider data valid
        logger: Optional logger instance (if None, prints to console)
        
    Returns:
        Tuple containing:
            - File path (or None if failed)
            - Last available date (or None if failed)
            - Data quality boolean (True if valid)
    """
    
    def log_message(message: str, level: str = "info") -> None:
        """Helper function for logging or printing"""
        if logger is not None:
            if level == "info":
                logger.info(message)
            elif level == "warning":
                logger.warning(message)
            elif level == "error":
                logger.error(message)
        else:
            print(f"[{level.upper()}] {message}")
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    ticker_clean = ticker.replace('.SA', '').replace('.', '')
    filename = f"{ticker_clean}_{end_date}_{start_date}.gzip"
    filepath = data_dir / filename
    
    if filepath.exists():
        log_message(f"File found in cache: {filename}")
        
        try:
            df = pd.read_parquet(filepath)
            last_date = df.index.max().strftime('%Y-%m-%d')
            is_valid = len(df) >= min_valid_rows
            
            log_message(f"Valid cache - Last date: {last_date}, Rows: {len(df)}")
            return str(filepath), last_date, is_valid
            
        except Exception as e:
            log_message(f"Error reading cache: {e}", "error")
            log_message("Recollecting data...", "info")
    
    log_message(f"Collecting data for {ticker} from {start_date} to {end_date}")
    
    try:
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True
        )
        
        if data.empty:
            log_message(f"No data returned for {ticker}", "error")
            return None, None, False
        
        data = data.dropna()
        
        n_rows = len(data)
        is_valid = n_rows >= min_valid_rows
        
        if not is_valid:
            log_message(
                f"Insufficient data: {n_rows} rows (minimum: {min_valid_rows})",
                "warning"
            )
        
        last_date = data.index.max().strftime('%Y-%m-%d')

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.set_names([ticker_clean, 'Symbol'])
            data.columns = data.columns.get_level_values(0)

        
        data.to_parquet(filepath, compression='gzip')
        log_message(f"File saved: {filename} - Rows: {n_rows}")
        
        return str(filepath), last_date, is_valid
        
    except Exception as e:
        log_message(f"Error collecting data for {ticker}: {e}", "error")
        return None, None, False
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import sys
import pandas as pd
sys.path.append(str(Path(__file__).parent.parent))

from config.parameters import dict_input_parameters, dict_path_parameters
from src.utils.logger_setup import setup_logger
from src.data_colector.data_collector import collect_stock_data


class DCModelManager:
    
    def __init__(
        self,
        log_level: str = "INFO",
        log_format: str = "detailed",
        console_output: bool = True,
        file_output: bool = True
    ):
        self.current_ticker = None
        self.current_data = None

        self.run_timestamp = datetime.now()
        self.run_id = self.run_timestamp.strftime("%Y%m%d_%H%M%S")
        
        self.dict_input_parameters = dict_input_parameters
        self.dict_path_parameters = dict_path_parameters
        
        logger_name = f"DCModelManager_{self.run_id}"
        
        self.logger = setup_logger(
            name=logger_name,
            log_level=log_level,
            log_format=log_format,
            console_output=console_output,
            file_output=file_output,
            log_dir=self.dict_path_parameters["logs_dir"]
        )
        
        self.logger.info(f"DCModelManager initialized - Run ID: {self.run_id}")
        self.logger.info(f"Timestamp: {self.run_timestamp.isoformat()}")
        self.logger.info(f"Project root: {self.dict_path_parameters['project_root']}")
        self.logger.info(f"Total tickers: {len(self.dict_input_parameters['b3_tickers'])}")
        
    
    def load_ticker_data(
        self,
        ticker: str
    ) -> Optional[pd.DataFrame]:
        """
        Load ticker data into memory
        
        Args:
            ticker: Stock symbol (e.g., 'ITUB4.SA')
            
        Returns:
            DataFrame with loaded data (also stored in self.current_data)
        """
        filepath, last_date, is_valid = collect_stock_data(
                                        ticker=ticker,
                                        start_date=self.dict_input_parameters.get('start_date', '2015-12-31'),
                                        end_date=self.dict_input_parameters.get('end_date', '2025-12-31'),
                                        data_dir=self.dict_path_parameters['data_dir'],
                                        min_valid_rows=self.dict_input_parameters.get('min_valid_rows', 2000),
                                        logger=self.logger
                                    )
                                    
        
        try:
            self.df_hist_price = pd.read_parquet(filepath)
            self.current_ticker = ticker
        except Exception as e:
            self.current_ticker = None
            self.df_hist_price = None
            self.logger.error(f"Error loading data for ticker {ticker}: {e}")
            return None
from pathlib import Path
from typing import Optional
from datetime import datetime
import sys
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

from config.parameters import dict_input_parameters, dict_path_parameters
from src.utils.logger_setup import setup_logger
from src.data_colector.data_collector import collect_stock_data
from src.dc.dc_transformer import transform_to_dc_events


class DCModelManager:

    def __init__(
        self,
        log_level: str = "INFO",
        log_format: str = "detailed",
        console_output: bool = True,
        file_output: bool = True,
    ):
        self.run_timestamp: datetime = datetime.now()
        self.run_id: str = self.run_timestamp.strftime("%Y%m%d_%H%M%S")

        self.input_params: dict = dict_input_parameters
        self.path_params: dict = dict_path_parameters

        self.current_ticker: Optional[str] = None
        self.df_hist_price: Optional[pd.DataFrame] = None
        self.df_dc_events: Optional[pd.DataFrame] = None
        self.current_threshold: Optional[float] = None

        self.logger = setup_logger(
            name=f"DCModelManager_{self.run_id}",
            log_level=log_level,
            log_format=log_format,
            console_output=console_output,
            file_output=file_output,
            log_dir=self.path_params["logs_dir"],
        )

        self.logger.info(f"DCModelManager initialized - Run ID: {self.run_id}")
        self.logger.info(f"Timestamp: {self.run_timestamp.isoformat()}")
        self.logger.info(f"Project root: {self.path_params['project_root']}")
        self.logger.info(f"Date range: {self.input_params['start_date']} to {self.input_params['end_date']}")
        self.logger.info(f"Lookback years: {self.input_params['lookback_years']}")
        self.logger.info(f"Total tickers configured: {len(self.input_params['b3_tickers'])}")

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_ticker_data(self, ticker: str) -> pd.DataFrame:
        """
        Load historical price data for a single ticker.

        Checks for a cached file at data_raw_dir/TICKER_enddate_startdate.gzip
        before downloading. If download or file reading fails, raises RuntimeError.

        Args:
            ticker: Yahoo Finance ticker symbol (e.g., 'ITUB4.SA').

        Returns:
            DataFrame indexed by date with OHLCV columns.

        Raises:
            RuntimeError: If data collection or file loading fails.
        """
        self.logger.info(f"Loading data for ticker: {ticker}")

        filepath, last_date, is_valid = collect_stock_data(
            ticker=ticker,
            start_date=self.input_params["start_date"],
            end_date=self.input_params["end_date"],
            data_dir=self.path_params["data_raw_dir"],
            min_valid_rows=self.input_params["min_valid_rows"],
            logger=self.logger,
        )

        if filepath is None:
            raise RuntimeError(
                f"Data collection failed for ticker '{ticker}'. "
                "Check logs for details."
            )

        if not is_valid:
            raise RuntimeError(
                f"Insufficient data for ticker '{ticker}': "
                f"last available date {last_date}, "
                f"minimum rows required {self.input_params['min_valid_rows']}."
            )

        try:
            df: pd.DataFrame = pd.read_parquet(filepath)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to read parquet file for ticker '{ticker}': {filepath}. "
                f"Original error: {exc}"
            ) from exc

        self.current_ticker = ticker
        self.df_hist_price = df
        self.df_dc_events = None
        self.current_threshold = None

        self.logger.info(
            f"Data loaded for {ticker} - "
            f"Rows: {len(df)}, "
            f"From: {df.index.min().date()}, "
            f"To: {df.index.max().date()}"
        )

        return df

    # ------------------------------------------------------------------
    # DC transformation
    # ------------------------------------------------------------------

    def run_dc_transform(
        self,
        threshold: Optional[float] = None,
        price_column: str = "Close",
    ) -> pd.DataFrame:
        """
        Apply DC transformation to the currently loaded ticker data.

        Must be called after a successful load_ticker_data call.

        Args:
            threshold: DC threshold as decimal (e.g., 0.02 for 2%).
                       Defaults to dc_default_threshold from parameters.
            price_column: Column name used for DC event detection.

        Returns:
            DataFrame with original OHLCV columns plus DC event columns:
                event_type, extreme_price, change_pct, event_period.

        Raises:
            RuntimeError: If no ticker data is loaded.
        """
        if self.df_hist_price is None or self.current_ticker is None:
            raise RuntimeError(
                "No ticker data loaded. Call load_ticker_data before run_dc_transform."
            )

        effective_threshold: float = (
            threshold
            if threshold is not None
            else self.input_params["dc_default_threshold"]
        )

        self.logger.info(
            f"Running DC transformation for {self.current_ticker} "
            f"with threshold {effective_threshold:.2%}"
        )

        df_dc: pd.DataFrame = transform_to_dc_events(
            df_prices=self.df_hist_price,
            price_column=price_column,
            threshold=effective_threshold,
            logger=self.logger,
        )

        self.df_dc_events = df_dc
        self.current_threshold = effective_threshold

        n_up: int = (df_dc["event_type"] == "dc_up").sum()
        n_down: int = (df_dc["event_type"] == "dc_down").sum()

        self.logger.info(
            f"DC transformation complete for {self.current_ticker} - "
            f"Threshold: {effective_threshold:.2%}, "
            f"Up events: {n_up}, "
            f"Down events: {n_down}, "
            f"Total events: {n_up + n_down}"
        )

        return df_dc

    # ------------------------------------------------------------------
    # Cache utilities
    # ------------------------------------------------------------------

    def get_data_file_path(self, ticker: str) -> Path:
        """
        Return the standardised cache file path for a ticker.

        Filename convention: TICKER_enddate_startdate.gzip

        Args:
            ticker: Yahoo Finance ticker symbol.

        Returns:
            Full Path object pointing to the expected cache file.
        """
        clean_ticker: str = ticker.replace(".SA", "").replace(".", "")
        filename: str = (
            f"{clean_ticker}_"
            f"{self.input_params['end_date']}_"
            f"{self.input_params['start_date']}.gzip"
        )
        file_path: Path = self.path_params["data_raw_dir"] / filename

        self.logger.debug(f"Cache path for {ticker}: {file_path}")

        return file_path

    def check_cached_data(self, ticker: str) -> bool:
        """
        Check whether a cache file exists for a ticker.

        Args:
            ticker: Yahoo Finance ticker symbol.

        Returns:
            True if the file exists, False otherwise.
        """
        file_path: Path = self.get_data_file_path(ticker)
        exists: bool = file_path.exists()

        if exists:
            self.logger.info(f"Cache found for {ticker}: {file_path.name}")
        else:
            self.logger.info(f"Cache not found for {ticker}: {file_path.name}")

        return exists

    # ------------------------------------------------------------------
    # State inspection
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """
        Return a snapshot of the current manager state.

        Returns:
            Dictionary with run metadata, configuration, and current ticker state.
        """
        summary: dict = {
            "run_id": self.run_id,
            "timestamp": self.run_timestamp.isoformat(),
            "project_root": str(self.path_params["project_root"]),
            "date_range": {
                "start_date": self.input_params["start_date"],
                "end_date": self.input_params["end_date"],
                "lookback_years": self.input_params["lookback_years"],
            },
            "data_source": self.input_params["data_source"],
            "interval": self.input_params["interval"],
            "tickers_configured": len(self.input_params["b3_tickers"]),
            "current_state": {
                "ticker": self.current_ticker,
                "data_loaded": self.df_hist_price is not None,
                "dc_computed": self.df_dc_events is not None,
                "threshold": self.current_threshold,
                "rows": len(self.df_hist_price) if self.df_hist_price is not None else None,
            },
        }

        self.logger.info(
            f"Summary requested - Ticker: {self.current_ticker}, "
            f"Data loaded: {summary['current_state']['data_loaded']}, "
            f"DC computed: {summary['current_state']['dc_computed']}"
        )

        return summary

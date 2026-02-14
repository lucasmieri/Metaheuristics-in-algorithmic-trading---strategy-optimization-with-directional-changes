"""
Simple DC Strategy Module
Basic trading strategy based on Directional Changes events
"""

import pandas as pd
import numpy as np
from typing import Optional, Any


def generate_dc_signals(
    df_dc: pd.DataFrame,
    initial_position: str = 'cash',
    logger: Optional[Any] = None
) -> pd.DataFrame:
    """
    Generate trading signals based on DC events
    
    Strategy logic:
    - Buy on DC Down events (price dropped, buy the dip)
    - Sell on DC Up events (price rose, take profit)
    
    Args:
        df_dc: DataFrame with DC events
        initial_position: Initial position ('cash' or 'invested')
        logger: Optional logger instance
        
    Returns:
        DataFrame with signals and positions
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Generating DC trading signals")
    
    df_signals = df_dc.copy()
    
    # Initialize signal columns
    df_signals['signal'] = 'hold'
    df_signals['position'] = 0.0
    
    # Current position tracker
    position = 1.0 if initial_position == 'invested' else 0.0
    
    for i in range(len(df_signals)):
        event_type = df_signals.iloc[i]['event_type']
        
        if event_type == 'dc_up' and position == 0.0:
            # Buy signal
            df_signals.iloc[i, df_signals.columns.get_loc('signal')] = 'buy'
            position = 1.0
        
        elif event_type == 'dc_down' and position == 1.0:
            # Sell signal
            df_signals.iloc[i, df_signals.columns.get_loc('signal')] = 'sell'
            position = 0.0
        
        df_signals.iloc[i, df_signals.columns.get_loc('position')] = position
    
    n_buys = (df_signals['signal'] == 'buy').sum()
    n_sells = (df_signals['signal'] == 'sell').sum()
    
    log_message(f"Signals generated - Buys: {n_buys}, Sells: {n_sells}")
    
    return df_signals
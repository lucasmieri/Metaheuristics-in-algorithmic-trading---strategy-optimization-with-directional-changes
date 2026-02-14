"""
DC Transformer Module
Transform price series into Directional Changes events
"""

import pandas as pd
import numpy as np
from typing import Optional, Any


def transform_to_dc_events(
    df_prices: pd.DataFrame,
    price_column: str = 'Close',
    threshold: float = 0.02,
    logger: Optional[Any] = None
) -> pd.DataFrame:
    """
    Transform price series into Directional Changes events
    
    Args:
        df_prices: DataFrame with price data (indexed by datetime)
        price_column: Column name to use for DC detection (default: 'Close')
        threshold: DC threshold as decimal (e.g., 0.02 for 2%)
        logger: Optional logger instance
        
    Returns:
        DataFrame with all original columns plus DC columns:
            - event_type: 'dc_up', 'dc_down', or 'no_event'
            - extreme_price: reference extreme price (forward filled)
            - change_pct: percentage change from extreme (forward filled)
            - event_period: days since last DC event
    """
    
    def log_message(message: str, level: str = "info") -> None:
        if logger is not None:
            if level == "info":
                logger.info(message)
            elif level == "warning":
                logger.warning(message)
        else:
            print(f"[{level.upper()}] {message}")
    
    log_message(f"Starting DC transformation - Threshold: {threshold:.2%}")
    
    df_result = df_prices.copy()
    prices = df_prices[price_column].dropna()
    
    n_prices = len(prices)
    
    if n_prices < 2:
        log_message("Insufficient data for DC transformation", "warning")
        return df_result
    
    df_result['event_type'] = 'no_event'
    df_result['extreme_price'] = np.nan
    df_result['change_pct'] = np.nan
    
    #first price
    extreme_price = prices.iloc[0]
    mode = 'up'
    last_event_idx = 0
    
    for i, (timestamp, price) in enumerate(prices.items()):
        
        if mode == 'up':
            # Looking for upward DC
            if price >= extreme_price * (1 + threshold):
                # Upward DC confirmed
                df_result.loc[timestamp, 'event_type'] = 'dc_up'
                df_result.loc[timestamp, 'extreme_price'] = extreme_price
                df_result.loc[timestamp, 'change_pct'] = (price - extreme_price) / extreme_price
                
                extreme_price = price
                mode = 'down'
                last_event_idx = i
            
            elif price < extreme_price:
                # Update extreme (lowest point)
                extreme_price = price
        
        else:  
            # Looking for downward DC
            if price <= extreme_price * (1 - threshold):
                # Downward DC confirmed
                df_result.loc[timestamp, 'event_type'] = 'dc_down'
                df_result.loc[timestamp, 'extreme_price'] = extreme_price
                df_result.loc[timestamp, 'change_pct'] = (price - extreme_price) / extreme_price
                
                extreme_price = price
                mode = 'up'
                last_event_idx = i
            
            elif price > extreme_price:
                extreme_price = price
    
    df_result['extreme_price'] = df_result['extreme_price'].fillna(0)
    df_result['change_pct'] = df_result['change_pct'].fillna(0)
    
    event_indices = df_result[df_result['event_type'] != 'no_event'].index
    df_result['event_period'] = 0
    
    for i in range(len(df_result)):
        timestamp = df_result.index[i]
        
        previous_events = event_indices[event_indices <= timestamp]
        
        if len(previous_events) > 0:
            df_result.iloc[i, df_result.columns.get_loc('event_period')] = i - df_result.index.get_loc(previous_events[-1])
        else:
            df_result.iloc[i, df_result.columns.get_loc('event_period')] = i
    
    n_up = (df_result['event_type'] == 'dc_up').sum()
    n_down = (df_result['event_type'] == 'dc_down').sum()
    n_total_events = n_up + n_down
    
    log_message(
        f"DC transformation completed - "
        f"Total rows: {len(df_result)}, "
        f"Total events: {n_total_events} ({n_total_events/len(df_result):.1%}), "
        f"Up: {n_up}, Down: {n_down}"
    )
    
    return df_result
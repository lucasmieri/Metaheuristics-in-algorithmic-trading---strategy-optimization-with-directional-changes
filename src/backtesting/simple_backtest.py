"""
Simple Backtest Module
Basic backtesting engine for DC strategies
"""

import pandas as pd
import numpy as np
from typing import Optional, Any, Dict


def run_simple_backtest(
    df_signals: pd.DataFrame,
    price_column: str = 'Close',
    initial_capital: float = 10000.0,
    transaction_cost: float = 0.001,
    logger: Optional[Any] = None
) -> pd.DataFrame:
    """
    Run simple backtest with transaction costs
    
    Args:
        df_signals: DataFrame with signals and positions
        price_column: Column name for price
        initial_capital: Initial capital in currency
        transaction_cost: Transaction cost as decimal (0.001 = 0.1%)
        logger: Optional logger instance
        
    Returns:
        DataFrame with backtest results
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message(f"Running backtest - Initial capital: {initial_capital:.2f}")
    
    df_results = df_signals.copy()
    
    # Initialize backtest columns
    df_results['cash'] = initial_capital
    df_results['shares'] = 0.0
    df_results['portfolio_value'] = initial_capital
    df_results['trade_cost'] = 0.0
    
    cash = initial_capital
    shares = 0.0
    
    for i in range(len(df_results)):
        signal = df_results.iloc[i]['signal']
        price = df_results.iloc[i][price_column]
        
        if signal == 'buy' and cash > 0:
            # Buy shares with all cash
            cost = cash * transaction_cost
            shares_to_buy = (cash - cost) / price
            
            shares += shares_to_buy
            cash = 0.0
            
            df_results.iloc[i, df_results.columns.get_loc('trade_cost')] = cost
            
        elif signal == 'sell' and shares > 0:
            # Sell all shares
            proceeds = shares * price
            cost = proceeds * transaction_cost
            
            cash = proceeds - cost
            shares = 0.0
            
            df_results.iloc[i, df_results.columns.get_loc('trade_cost')] = cost
        
        # Update portfolio value
        portfolio_value = cash + (shares * price)
        
        df_results.iloc[i, df_results.columns.get_loc('cash')] = cash
        df_results.iloc[i, df_results.columns.get_loc('shares')] = shares
        df_results.iloc[i, df_results.columns.get_loc('portfolio_value')] = portfolio_value
    
    # Calculate returns
    df_results['strategy_returns'] = df_results['portfolio_value'].pct_change()
    
    total_costs = df_results['trade_cost'].sum()
    final_value = df_results['portfolio_value'].iloc[-1]
    total_return = (final_value - initial_capital) / initial_capital
    
    log_message(f"Backtest completed - Final value: {final_value:.2f}, Total costs: {total_costs:.2f}")
    
    return df_results


def run_buy_and_hold(
    df_prices: pd.DataFrame,
    price_column: str = 'Close',
    initial_capital: float = 10000.0,
    transaction_cost: float = 0.001,
    logger: Optional[Any] = None
) -> pd.DataFrame:
    """
    Run buy and hold benchmark strategy
    
    Args:
        df_prices: DataFrame with price data
        price_column: Column name for price
        initial_capital: Initial capital in currency
        transaction_cost: Transaction cost as decimal
        logger: Optional logger instance
        
    Returns:
        DataFrame with buy and hold results
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Running Buy & Hold benchmark")
    
    df_results = df_prices.copy()
    
    # Buy at first price
    first_price = df_results[price_column].iloc[0]
    cost = initial_capital * transaction_cost
    shares = (initial_capital - cost) / first_price
    
    # Hold until end
    df_results['portfolio_value'] = shares * df_results[price_column]
    df_results['bh_returns'] = df_results['portfolio_value'].pct_change()
    
    final_value = df_results['portfolio_value'].iloc[-1]
    total_return = (final_value - initial_capital) / initial_capital
    
    log_message(f"Buy & Hold completed - Final value: {final_value:.2f}, Return: {total_return:.2%}")
    
    return df_results
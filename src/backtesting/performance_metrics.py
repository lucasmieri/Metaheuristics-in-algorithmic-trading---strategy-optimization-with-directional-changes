"""
Performance Metrics Module
Calculate performance metrics with correct annualization
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def calculate_performance_metrics(
    df_results: pd.DataFrame,
    returns_column: str = 'strategy_returns',
    risk_free_rate: float = 0.0,
    logger: Optional[Any] = None
) -> Dict[str, float]:
    """
    Calculate performance metrics with calendar-based Sharpe Ratio
    
    Args:
        df_results: DataFrame with backtest results
        returns_column: Column name for returns
        risk_free_rate: Annual risk-free rate as decimal
        logger: Optional logger instance
        
    Returns:
        Dictionary with performance metrics
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Calculating performance metrics")
    
    returns = df_results[returns_column].dropna()
    
    # Total return
    initial_value = df_results['portfolio_value'].iloc[0]
    final_value = df_results['portfolio_value'].iloc[-1]
    total_return = (final_value - initial_value) / initial_value
    
    # Annualized return (geometric)
    n_days = len(df_results)
    n_years = n_days / 252
    annualized_return = (1 + total_return) ** (1 / n_years) - 1
    
    # Sharpe Ratio (calendar-based, correct method)
    daily_rf = (1 + risk_free_rate) ** (1/252) - 1
    excess_returns = returns - daily_rf
    
    sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252) if excess_returns.std() > 0 else 0
    
    # Maximum drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Win rate (for trades)
    if 'signal' in df_results.columns:
        trades = df_results[df_results['signal'].isin(['buy', 'sell'])]
        n_trades = len(trades) // 2
    else:
        n_trades = 0
    
    metrics = {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'volatility': returns.std() * np.sqrt(252),
        'n_days': n_days,
        'n_trades': n_trades
    }
    
    log_message(f"Metrics calculated - Sharpe: {sharpe_ratio:.2f}, Max DD: {max_drawdown:.2%}")
    
    return metrics
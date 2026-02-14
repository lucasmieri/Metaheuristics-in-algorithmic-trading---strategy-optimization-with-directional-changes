"""
DC Analyzer Module
Statistical analysis and diagnostics for Directional Changes events
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List


def calculate_basic_statistics(
    df_dc: pd.DataFrame,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Calculate basic statistics for DC events
    
    Args:
        df_dc: DataFrame with DC events (output from transform_to_dc_events)
        logger: Optional logger instance
        
    Returns:
        Dictionary with basic statistics
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Calculating basic DC statistics")
    
    total_rows = len(df_dc)
    dc_events = df_dc[df_dc['event_type'] != 'no_event']
    
    n_events = len(dc_events)
    n_up = (dc_events['event_type'] == 'dc_up').sum()
    n_down = (dc_events['event_type'] == 'dc_down').sum()
    
    event_periods = dc_events['event_period'].copy()
    event_periods = event_periods[event_periods > 0]
    
    change_pcts = dc_events['change_pct'].abs()
    
    stats = {
        'total_days': total_rows,
        'total_events': n_events,
        'events_percentage': n_events / total_rows,
        'up_events': n_up,
        'down_events': n_down,
        'up_down_ratio': n_up / n_down if n_down > 0 else np.nan,
        'mean_event_period': event_periods.mean() if len(event_periods) > 0 else 0,
        'median_event_period': event_periods.median() if len(event_periods) > 0 else 0,
        'std_event_period': event_periods.std() if len(event_periods) > 0 else 0,
        'min_event_period': event_periods.min() if len(event_periods) > 0 else 0,
        'max_event_period': event_periods.max() if len(event_periods) > 0 else 0,
        'mean_change_pct': change_pcts.mean(),
        'median_change_pct': change_pcts.median(),
        'std_change_pct': change_pcts.std(),
        'min_change_pct': change_pcts.min(),
        'max_change_pct': change_pcts.max()
    }
    
    log_message(f"Statistics calculated - Total events: {n_events}")
    
    return stats


def analyze_event_distribution(
    df_dc: pd.DataFrame,
    logger: Optional[Any] = None
) -> pd.DataFrame:
    """
    Analyze distribution of event periods
    
    Args:
        df_dc: DataFrame with DC events
        logger: Optional logger instance
        
    Returns:
        DataFrame with event period distribution
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Analyzing event period distribution")
    
    dc_events = df_dc[df_dc['event_type'] != 'no_event'].copy()
    
    bins = [0, 5, 10, 20, 50, 100, np.inf]
    labels = ['0-5', '6-10', '11-20', '21-50', '51-100', '100+']
    
    dc_events['period_bin'] = pd.cut(
        dc_events['event_period'],
        bins=bins,
        labels=labels,
        right=True
    )
    
    distribution = dc_events.groupby(['event_type', 'period_bin']).size().reset_index(name='count')
    distribution['percentage'] = distribution.groupby('event_type')['count'].transform(lambda x: x / x.sum())
    
    log_message("Event period distribution calculated")
    
    return distribution


def analyze_temporal_patterns(
    df_dc: pd.DataFrame,
    logger: Optional[Any] = None
) -> Dict[str, pd.DataFrame]:
    """
    Analyze temporal patterns in DC events
    
    Args:
        df_dc: DataFrame with DC events
        logger: Optional logger instance
        
    Returns:
        Dictionary with temporal analysis DataFrames
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Analyzing temporal patterns")
    
    dc_events = df_dc[df_dc['event_type'] != 'no_event'].copy()
    
    dc_events['year'] = dc_events.index.year
    by_year = dc_events.groupby(['year', 'event_type']).size().reset_index(name='count')
    by_year_pivot = by_year.pivot(index='year', columns='event_type', values='count').fillna(0)
    
    dc_events['month'] = dc_events.index.month
    by_month = dc_events.groupby(['month', 'event_type']).size().reset_index(name='count')
    by_month_pivot = by_month.pivot(index='month', columns='event_type', values='count').fillna(0)
    
    dc_events['quarter'] = dc_events.index.quarter
    by_quarter = dc_events.groupby(['quarter', 'event_type']).size().reset_index(name='count')
    by_quarter_pivot = by_quarter.pivot(index='quarter', columns='event_type', values='count').fillna(0)
    
    log_message("Temporal patterns analyzed")
    
    return {
        'by_year': by_year_pivot,
        'by_month': by_month_pivot,
        'by_quarter': by_quarter_pivot
    }


def analyze_threshold_sensitivity(
    df_prices: pd.DataFrame,
    thresholds: List[float],
    price_column: str = 'Close',
    logger: Optional[Any] = None
) -> pd.DataFrame:
    """
    Analyze sensitivity to different DC thresholds
    
    Args:
        df_prices: DataFrame with price data
        thresholds: List of thresholds to test (e.g., [0.01, 0.02, 0.05])
        price_column: Column name for price
        logger: Optional logger instance
        
    Returns:
        DataFrame with threshold sensitivity analysis
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message(f"Analyzing threshold sensitivity for {len(thresholds)} thresholds")
    
    from src.dc.dc_transformer import transform_to_dc_events
    
    results = []
    
    for threshold in thresholds:
        df_dc = transform_to_dc_events(
            df_prices=df_prices,
            price_column=price_column,
            threshold=threshold,
            logger=None
        )
        
        dc_events = df_dc[df_dc['event_type'] != 'no_event']
        n_events = len(dc_events)
        
        if n_events > 0:
            event_periods = dc_events[dc_events['event_period'] > 0]['event_period']
            change_pcts = dc_events['change_pct'].abs()
            
            results.append({
                'threshold': threshold,
                'threshold_pct': f"{threshold:.1%}",
                'total_events': n_events,
                'up_events': (dc_events['event_type'] == 'dc_up').sum(),
                'down_events': (dc_events['event_type'] == 'dc_down').sum(),
                'mean_event_period': event_periods.mean() if len(event_periods) > 0 else 0,
                'median_event_period': event_periods.median() if len(event_periods) > 0 else 0,
                'mean_change_pct': change_pcts.mean(),
                'median_change_pct': change_pcts.median()
            })
    
    df_sensitivity = pd.DataFrame(results)
    
    log_message("Threshold sensitivity analysis completed")
    
    return df_sensitivity


def analyze_regime_characteristics(
    df_dc: pd.DataFrame,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Analyze characteristics of market regimes (up vs down trends)
    
    Args:
        df_dc: DataFrame with DC events
        logger: Optional logger instance
        
    Returns:
        Dictionary with regime characteristics
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Analyzing regime characteristics")
    
    dc_events = df_dc[df_dc['event_type'] != 'no_event'].copy()
    
    up_events = dc_events[dc_events['event_type'] == 'dc_up']
    down_events = dc_events[dc_events['event_type'] == 'dc_down']
    
    up_periods = up_events[up_events['event_period'] > 0]['event_period']
    down_periods = down_events[down_events['event_period'] > 0]['event_period']
    
    regime_stats = {
        'up_regime': {
            'mean_period': up_periods.mean() if len(up_periods) > 0 else 0,
            'median_period': up_periods.median() if len(up_periods) > 0 else 0,
            'mean_change': up_events['change_pct'].mean(),
            'median_change': up_events['change_pct'].median(),
            'std_change': up_events['change_pct'].std()
        },
        'down_regime': {
            'mean_period': down_periods.mean() if len(down_periods) > 0 else 0,
            'median_period': down_periods.median() if len(down_periods) > 0 else 0,
            'mean_change': down_events['change_pct'].abs().mean(),
            'median_change': down_events['change_pct'].abs().median(),
            'std_change': down_events['change_pct'].std()
        }
    }
    
    up_mean = regime_stats['up_regime']['mean_period']
    down_mean = regime_stats['down_regime']['mean_period']
    up_change = regime_stats['up_regime']['mean_change']
    down_change = regime_stats['down_regime']['mean_change']
    
    regime_stats['symmetry'] = {
        'period_ratio': up_mean / down_mean if down_mean > 0 else np.nan,
        'change_ratio': up_change / down_change if down_change > 0 else np.nan
    }
    
    log_message("Regime characteristics analyzed")
    
    return regime_stats


def analyze_event_clustering(
    df_dc: pd.DataFrame,
    window_days: int = 30,
    logger: Optional[Any] = None
) -> pd.DataFrame:
    """
    Analyze clustering of DC events (high volatility periods)
    
    Args:
        df_dc: DataFrame with DC events
        window_days: Rolling window in days
        logger: Optional logger instance
        
    Returns:
        DataFrame with event density over time
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message(f"Analyzing event clustering with {window_days}-day window")
    
    df_result = df_dc.copy()
    df_result['is_event'] = (df_result['event_type'] != 'no_event').astype(int)
    
    df_result['event_density'] = df_result['is_event'].rolling(window=window_days, min_periods=1).sum()
    
    high_vol_threshold = df_result['event_density'].quantile(0.75)
    df_result['high_volatility_period'] = df_result['event_density'] >= high_vol_threshold
    
    log_message(f"Event clustering analyzed - High vol threshold: {high_vol_threshold:.1f} events/{window_days}days")
    
    return df_result


def analyze_overshoot(
    df_dc: pd.DataFrame,
    threshold: float,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Analyze overshoot beyond DC threshold
    
    Args:
        df_dc: DataFrame with DC events
        threshold: DC threshold used
        logger: Optional logger instance
        
    Returns:
        Dictionary with overshoot statistics
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Analyzing overshoot patterns")
    
    dc_events = df_dc[df_dc['event_type'] != 'no_event'].copy()
    
    dc_events['overshoot'] = dc_events['change_pct'].abs() - threshold
    dc_events['overshoot_pct'] = (dc_events['overshoot'] / threshold) * 100
    
    up_overshoot = dc_events[dc_events['event_type'] == 'dc_up']['overshoot']
    down_overshoot = dc_events[dc_events['event_type'] == 'dc_down']['overshoot']
    
    overshoot_stats = {
        'overall': {
            'mean_overshoot': dc_events['overshoot'].mean(),
            'median_overshoot': dc_events['overshoot'].median(),
            'std_overshoot': dc_events['overshoot'].std(),
            'max_overshoot': dc_events['overshoot'].max(),
            'min_overshoot': dc_events['overshoot'].min(),
            'mean_overshoot_pct': dc_events['overshoot_pct'].mean()
        },
        'up_events': {
            'mean_overshoot': up_overshoot.mean(),
            'median_overshoot': up_overshoot.median()
        },
        'down_events': {
            'mean_overshoot': down_overshoot.mean(),
            'median_overshoot': down_overshoot.median()
        }
    }
    
    log_message(f"Overshoot analysis completed - Mean: {overshoot_stats['overall']['mean_overshoot']:.4f}")
    
    return overshoot_stats


def analyze_consecutive_events(
    df_dc: pd.DataFrame,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Analyze patterns of consecutive short-period events
    
    Args:
        df_dc: DataFrame with DC events
        logger: Optional logger instance
        
    Returns:
        Dictionary with consecutive event statistics
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Analyzing consecutive event patterns")
    
    dc_events = df_dc[df_dc['event_type'] != 'no_event'].copy()
    
    dc_events['short_period'] = dc_events['event_period'] <= 3
    
    dc_events['consecutive_group'] = (dc_events['short_period'] != dc_events['short_period'].shift()).cumsum()
    
    consecutive_runs = dc_events[dc_events['short_period']].groupby('consecutive_group').size()
    
    stats = {
        'total_short_period_events': dc_events['short_period'].sum(),
        'pct_short_period': dc_events['short_period'].mean(),
        'max_consecutive_short': consecutive_runs.max() if len(consecutive_runs) > 0 else 0,
        'mean_consecutive_short': consecutive_runs.mean() if len(consecutive_runs) > 0 else 0,
        'total_runs': len(consecutive_runs)
    }
    
    log_message(f"Consecutive events analyzed - {stats['total_runs']} runs identified")
    
    return stats


def generate_summary_report(
    df_dc: pd.DataFrame,
    threshold: float,
    logger: Optional[Any] = None
) -> str:
    """
    Generate comprehensive summary report
    
    Args:
        df_dc: DataFrame with DC events
        threshold: Threshold used for DC transformation
        logger: Optional logger instance
        
    Returns:
        Formatted string report
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Generating summary report")
    
    stats = calculate_basic_statistics(df_dc, logger=None)
    regime = analyze_regime_characteristics(df_dc, logger=None)
    
    report = f"""
    ============================================
    DC ANALYSIS SUMMARY REPORT
    ============================================
    
    Threshold: {threshold:.2%}
    
    BASIC STATISTICS
    ----------------
    Total Days: {stats['total_days']:,}
    Total Events: {stats['total_events']}
    Event Frequency: {stats['events_percentage']:.2%}
    
    Up Events: {stats['up_events']}
    Down Events: {stats['down_events']}
    Up/Down Ratio: {stats['up_down_ratio']:.2f}
    
    EVENT PERIODS (days between events)
    -----------------------------------
    Mean: {stats['mean_event_period']:.1f}
    Median: {stats['median_event_period']:.1f}
    Std Dev: {stats['std_event_period']:.1f}
    Min: {stats['min_event_period']:.0f}
    Max: {stats['max_event_period']:.0f}
    
    CHANGE MAGNITUDES
    -----------------
    Mean: {stats['mean_change_pct']:.2%}
    Median: {stats['median_change_pct']:.2%}
    Std Dev: {stats['std_change_pct']:.2%}
    Min: {stats['min_change_pct']:.2%}
    Max: {stats['max_change_pct']:.2%}
    
    REGIME CHARACTERISTICS
    ----------------------
    Up Regime:
      Mean Period: {regime['up_regime']['mean_period']:.1f} days
      Mean Change: {regime['up_regime']['mean_change']:.2%}
      
    Down Regime:
      Mean Period: {regime['down_regime']['mean_period']:.1f} days
      Mean Change: {regime['down_regime']['mean_change']:.2%}
      
    Symmetry:
      Period Ratio (Up/Down): {regime['symmetry']['period_ratio']:.2f}
      Change Ratio (Up/Down): {regime['symmetry']['change_ratio']:.2f}
    
    ============================================
    """
    
    log_message("Summary report generated")
    
    return report
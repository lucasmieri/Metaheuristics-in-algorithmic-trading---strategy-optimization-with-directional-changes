"""
DC Graphs Module
Visualization functions for Directional Changes analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Any, List, Dict
from pathlib import Path


def setup_plot_style() -> None:
    """Setup consistent plot style"""
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10


def plot_price_with_dc_events(
    df_dc: pd.DataFrame,
    price_column: str = 'Close',
    figsize: tuple = (14, 7),
    save_path: Optional[Path] = None,
    logger: Optional[Any] = None
) -> None:
    """
    Plot price series with DC events marked
    
    Args:
        df_dc: DataFrame with DC events
        price_column: Column name for price
        figsize: Figure size
        save_path: Optional path to save figure
        logger: Optional logger instance
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Creating price chart with DC events")
    
    setup_plot_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.plot(df_dc.index, df_dc[price_column], label='Price', color='black', linewidth=1, alpha=0.7)
    
    dc_up = df_dc[df_dc['event_type'] == 'dc_up']
    dc_down = df_dc[df_dc['event_type'] == 'dc_down']
    
    ax.scatter(dc_up.index, dc_up[price_column], color='green', s=50, marker='^', 
               label=f'DC Up ({len(dc_up)})', zorder=5, alpha=0.8)
    ax.scatter(dc_down.index, dc_down[price_column], color='red', s=50, marker='v', 
               label=f'DC Down ({len(dc_down)})', zorder=5, alpha=0.8)
    
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title('Price Series with Directional Changes Events')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        log_message(f"Chart saved to {save_path}")
    
    plt.show()


def plot_event_period_distribution(
    df_dc: pd.DataFrame,
    bins: int = 30,
    figsize: tuple = (12, 6),
    save_path: Optional[Path] = None,
    logger: Optional[Any] = None
) -> None:
    """
    Plot distribution of event periods
    
    Args:
        df_dc: DataFrame with DC events
        bins: Number of histogram bins
        figsize: Figure size
        save_path: Optional path to save figure
        logger: Optional logger instance
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Creating event period distribution chart")
    
    setup_plot_style()
    
    dc_events = df_dc[df_dc['event_type'] != 'no_event']
    event_periods = dc_events[dc_events['event_period'] > 0]['event_period']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    ax1.hist(event_periods, bins=bins, color='steelblue', edgecolor='black', alpha=0.7)
    ax1.axvline(event_periods.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {event_periods.mean():.1f}')
    ax1.axvline(event_periods.median(), color='orange', linestyle='--', linewidth=2, label=f'Median: {event_periods.median():.1f}')
    ax1.set_xlabel('Days Between Events')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Event Period Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    up_periods = dc_events[(dc_events['event_type'] == 'dc_up') & (dc_events['event_period'] > 0)]['event_period']
    down_periods = dc_events[(dc_events['event_type'] == 'dc_down') & (dc_events['event_period'] > 0)]['event_period']
    
    data_box = [up_periods, down_periods]
    ax2.boxplot(data_box, labels=['DC Up', 'DC Down'], patch_artist=True,
                boxprops=dict(facecolor='lightblue', alpha=0.7),
                medianprops=dict(color='red', linewidth=2))
    ax2.set_ylabel('Days Between Events')
    ax2.set_title('Event Period by Type')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        log_message(f"Chart saved to {save_path}")
    
    plt.show()


def plot_threshold_sensitivity(
    df_sensitivity: pd.DataFrame,
    figsize: tuple = (14, 10),
    save_path: Optional[Path] = None,
    logger: Optional[Any] = None
) -> None:
    """
    Plot threshold sensitivity analysis
    
    Args:
        df_sensitivity: DataFrame from analyze_threshold_sensitivity
        figsize: Figure size
        save_path: Optional path to save figure
        logger: Optional logger instance
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Creating threshold sensitivity charts")
    
    setup_plot_style()
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    axes[0, 0].plot(df_sensitivity['threshold'] * 100, df_sensitivity['total_events'], 
                    marker='o', linewidth=2, markersize=8, color='steelblue')
    axes[0, 0].set_xlabel('Threshold (%)')
    axes[0, 0].set_ylabel('Total Events')
    axes[0, 0].set_title('Total DC Events vs Threshold')
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].plot(df_sensitivity['threshold'] * 100, df_sensitivity['mean_event_period'], 
                    marker='s', linewidth=2, markersize=8, color='green')
    axes[0, 1].set_xlabel('Threshold (%)')
    axes[0, 1].set_ylabel('Mean Days Between Events')
    axes[0, 1].set_title('Event Frequency vs Threshold')
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].plot(df_sensitivity['threshold'] * 100, df_sensitivity['mean_change_pct'] * 100, 
                    marker='^', linewidth=2, markersize=8, color='orange')
    axes[1, 0].set_xlabel('Threshold (%)')
    axes[1, 0].set_ylabel('Mean Change (%)')
    axes[1, 0].set_title('Mean Event Magnitude vs Threshold')
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].bar(df_sensitivity['threshold_pct'], df_sensitivity['up_events'], 
                   label='Up Events', alpha=0.7, color='green')
    axes[1, 1].bar(df_sensitivity['threshold_pct'], df_sensitivity['down_events'], 
                   bottom=df_sensitivity['up_events'], label='Down Events', alpha=0.7, color='red')
    axes[1, 1].set_xlabel('Threshold')
    axes[1, 1].set_ylabel('Number of Events')
    axes[1, 1].set_title('Event Type Balance vs Threshold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        log_message(f"Chart saved to {save_path}")
    
    plt.show()


def plot_temporal_patterns(
    temporal_data: Dict[str, pd.DataFrame],
    figsize: tuple = (14, 10),
    save_path: Optional[Path] = None,
    logger: Optional[Any] = None
) -> None:
    """
    Plot temporal patterns (yearly, monthly, quarterly)
    
    Args:
        temporal_data: Dictionary from analyze_temporal_patterns
        figsize: Figure size
        save_path: Optional path to save figure
        logger: Optional logger instance
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Creating temporal pattern charts")
    
    setup_plot_style()
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    if 'by_year' in temporal_data:
        df_year = temporal_data['by_year']
        df_year.plot(kind='bar', stacked=False, ax=axes[0, 0], color=['green', 'red'], alpha=0.7)
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Number of Events')
        axes[0, 0].set_title('DC Events by Year')
        axes[0, 0].legend(['DC Up', 'DC Down'])
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        axes[0, 0].tick_params(axis='x', rotation=45)
    
    if 'by_month' in temporal_data:
        df_month = temporal_data['by_month']
        df_month.plot(kind='bar', stacked=False, ax=axes[0, 1], color=['green', 'red'], alpha=0.7)
        axes[0, 1].set_xlabel('Month')
        axes[0, 1].set_ylabel('Number of Events')
        axes[0, 1].set_title('DC Events by Month')
        axes[0, 1].legend(['DC Up', 'DC Down'])
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        axes[0, 1].tick_params(axis='x', rotation=0)
    
    if 'by_quarter' in temporal_data:
        df_quarter = temporal_data['by_quarter']
        df_quarter.plot(kind='bar', stacked=False, ax=axes[1, 0], color=['green', 'red'], alpha=0.7)
        axes[1, 0].set_xlabel('Quarter')
        axes[1, 0].set_ylabel('Number of Events')
        axes[1, 0].set_title('DC Events by Quarter')
        axes[1, 0].legend(['DC Up', 'DC Down'])
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        axes[1, 0].tick_params(axis='x', rotation=0)
    
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        log_message(f"Chart saved to {save_path}")
    
    plt.show()


def plot_change_magnitude_analysis(
    df_dc: pd.DataFrame,
    bins: int = 30,
    figsize: tuple = (12, 6),
    save_path: Optional[Path] = None,
    logger: Optional[Any] = None
) -> None:
    """
    Plot change magnitude analysis
    
    Args:
        df_dc: DataFrame with DC events
        bins: Number of histogram bins
        figsize: Figure size
        save_path: Optional path to save figure
        logger: Optional logger instance
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Creating change magnitude analysis chart")
    
    setup_plot_style()
    
    dc_events = df_dc[df_dc['event_type'] != 'no_event']
    
    up_changes = dc_events[dc_events['event_type'] == 'dc_up']['change_pct'] * 100
    down_changes = dc_events[dc_events['event_type'] == 'dc_down']['change_pct'].abs() * 100
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    ax1.hist(up_changes, bins=bins, alpha=0.6, color='green', label='DC Up', edgecolor='black')
    ax1.hist(down_changes, bins=bins, alpha=0.6, color='red', label='DC Down', edgecolor='black')
    ax1.axvline(up_changes.mean(), color='darkgreen', linestyle='--', linewidth=2, label=f'Up Mean: {up_changes.mean():.2f}%')
    ax1.axvline(down_changes.mean(), color='darkred', linestyle='--', linewidth=2, label=f'Down Mean: {down_changes.mean():.2f}%')
    ax1.set_xlabel('Change Magnitude (%)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of Change Magnitudes')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    data_box = [up_changes, down_changes]
    bp = ax2.boxplot(data_box, labels=['DC Up', 'DC Down'], patch_artist=True,
                     boxprops=dict(alpha=0.7),
                     medianprops=dict(color='black', linewidth=2))
    bp['boxes'][0].set_facecolor('lightgreen')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax2.set_ylabel('Change Magnitude (%)')
    ax2.set_title('Change Magnitude Comparison')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        log_message(f"Chart saved to {save_path}")
    
    plt.show()


def plot_event_density_timeline(
    df_dc: pd.DataFrame,
    window_days: int = 30,
    figsize: tuple = (14, 6),
    save_path: Optional[Path] = None,
    logger: Optional[Any] = None
) -> None:
    """
    Plot event density over time to identify high volatility periods
    
    Args:
        df_dc: DataFrame with DC events
        window_days: Rolling window in days
        figsize: Figure size
        save_path: Optional path to save figure
        logger: Optional logger instance
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Creating event density timeline")
    
    from src.dc.dc_analyzer import analyze_event_clustering
    
    df_clustering = analyze_event_clustering(df_dc, window_days, logger=None)
    
    setup_plot_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.plot(df_clustering.index, df_clustering['event_density'], linewidth=2, color='steelblue', label='Event Density')
    ax.fill_between(df_clustering.index, df_clustering['event_density'], alpha=0.3, color='steelblue')
    
    high_vol = df_clustering[df_clustering['high_volatility_period']]
    if len(high_vol) > 0:
        ax.scatter(high_vol.index, high_vol['event_density'], color='red', s=20, alpha=0.5, label='High Volatility', zorder=5)
    
    ax.set_xlabel('Date')
    ax.set_ylabel(f'Events in {window_days}-day window')
    ax.set_title(f'DC Event Density Over Time ({window_days}-day rolling window)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        log_message(f"Chart saved to {save_path}")
    
    plt.show()


def plot_overshoot_analysis(
    df_dc: pd.DataFrame,
    threshold: float,
    bins: int = 30,
    figsize: tuple = (12, 6),
    save_path: Optional[Path] = None,
    logger: Optional[Any] = None
) -> None:
    """
    Plot overshoot analysis
    
    Args:
        df_dc: DataFrame with DC events
        threshold: DC threshold used
        bins: Number of histogram bins
        figsize: Figure size
        save_path: Optional path to save figure
        logger: Optional logger instance
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("Creating overshoot analysis chart")
    
    setup_plot_style()
    
    dc_events = df_dc[df_dc['event_type'] != 'no_event'].copy()
    dc_events['overshoot'] = (dc_events['change_pct'].abs() - threshold) * 100
    
    up_overshoot = dc_events[dc_events['event_type'] == 'dc_up']['overshoot']
    down_overshoot = dc_events[dc_events['event_type'] == 'dc_down']['overshoot']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    ax1.hist(dc_events['overshoot'], bins=bins, alpha=0.7, color='purple', edgecolor='black')
    ax1.axvline(dc_events['overshoot'].mean(), color='red', linestyle='--', linewidth=2, 
                label=f'Mean: {dc_events["overshoot"].mean():.2f}%')
    ax1.axvline(dc_events['overshoot'].median(), color='orange', linestyle='--', linewidth=2,
                label=f'Median: {dc_events["overshoot"].median():.2f}%')
    ax1.set_xlabel('Overshoot (%)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of Overshoot Beyond Threshold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    data_box = [up_overshoot, down_overshoot]
    bp = ax2.boxplot(data_box, labels=['DC Up', 'DC Down'], patch_artist=True,
                     boxprops=dict(alpha=0.7),
                     medianprops=dict(color='black', linewidth=2))
    bp['boxes'][0].set_facecolor('lightgreen')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax2.set_ylabel('Overshoot (%)')
    ax2.set_title('Overshoot by Event Type')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        log_message(f"Chart saved to {save_path}")
    
    plt.show()


def generate_complete_dc_analysis(
    df_dc: pd.DataFrame,
    threshold: float,
    output_dir: Path,
    thresholds_for_sensitivity: Optional[List[float]] = None,
    window_days: int = 30,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Generate complete DC analysis with all plots and statistics
    Master function to orchestrate all analysis
    
    Args:
        df_dc: DataFrame with DC events
        threshold: DC threshold used
        output_dir: Directory to save all outputs
        thresholds_for_sensitivity: List of thresholds for sensitivity analysis
        window_days: Rolling window for clustering analysis
        logger: Optional logger instance
        
    Returns:
        Dictionary with all analysis results
    """
    
    def log_message(message: str) -> None:
        if logger:
            logger.info(message)
        else:
            print(f"[INFO] {message}")
    
    log_message("="*60)
    log_message("STARTING COMPLETE DC ANALYSIS")
    log_message("="*60)
    
    output_dir = Path(output_dir)
    figures_dir = output_dir / 'figures'
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    log_message("\n[1/10] Calculating basic statistics...")
    from src.dc.dc_analyzer import calculate_basic_statistics
    results['basic_stats'] = calculate_basic_statistics(df_dc, logger=logger)
    
    log_message("[2/10] Analyzing event distribution...")
    from src.dc.dc_analyzer import analyze_event_distribution
    results['event_distribution'] = analyze_event_distribution(df_dc, logger=logger)
    
    log_message("[3/10] Analyzing temporal patterns...")
    from src.dc.dc_analyzer import analyze_temporal_patterns
    results['temporal_patterns'] = analyze_temporal_patterns(df_dc, logger=logger)
    
    if thresholds_for_sensitivity:
        log_message("[4/10] Analyzing threshold sensitivity...")
        from src.dc.dc_analyzer import analyze_threshold_sensitivity
        results['threshold_sensitivity'] = analyze_threshold_sensitivity(
            df_prices=df_dc,
            thresholds=thresholds_for_sensitivity,
            logger=logger
        )
    
    log_message("[5/10] Analyzing regime characteristics...")
    from src.dc.dc_analyzer import analyze_regime_characteristics
    results['regime_stats'] = analyze_regime_characteristics(df_dc, logger=logger)
    
    log_message("[6/10] Analyzing event clustering...")
    from src.dc.dc_analyzer import analyze_event_clustering
    results['clustering'] = analyze_event_clustering(df_dc, window_days=window_days, logger=logger)
    
    log_message("[7/10] Analyzing overshoot patterns...")
    from src.dc.dc_analyzer import analyze_overshoot
    results['overshoot'] = analyze_overshoot(df_dc, threshold=threshold, logger=logger)
    
    log_message("[8/10] Analyzing consecutive event patterns...")
    from src.dc.dc_analyzer import analyze_consecutive_events
    results['consecutive'] = analyze_consecutive_events(df_dc, logger=logger)
    
    log_message("\n[9/10] Generating visualizations...")
    
    log_message("  - Price with DC events...")
    plot_price_with_dc_events(
        df_dc=df_dc,
        save_path=figures_dir / 'price_with_dc_events.png',
        logger=None
    )
    
    log_message("  - Event period distribution...")
    plot_event_period_distribution(
        df_dc=df_dc,
        save_path=figures_dir / 'event_period_distribution.png',
        logger=None
    )
    
    if thresholds_for_sensitivity:
        log_message("  - Threshold sensitivity...")
        plot_threshold_sensitivity(
            df_sensitivity=results['threshold_sensitivity'],
            save_path=figures_dir / 'threshold_sensitivity.png',
            logger=None
        )
    
    log_message("  - Temporal patterns...")
    plot_temporal_patterns(
        temporal_data=results['temporal_patterns'],
        save_path=figures_dir / 'temporal_patterns.png',
        logger=None
    )
    
    log_message("  - Change magnitude analysis...")
    plot_change_magnitude_analysis(
        df_dc=df_dc,
        save_path=figures_dir / 'change_magnitude_analysis.png',
        logger=None
    )
    
    log_message("  - Event density timeline...")
    plot_event_density_timeline(
        df_dc=df_dc,
        window_days=window_days,
        save_path=figures_dir / 'event_density_timeline.png',
        logger=None
    )
    
    log_message("  - Overshoot analysis...")
    plot_overshoot_analysis(
        df_dc=df_dc,
        threshold=threshold,
        save_path=figures_dir / 'overshoot_analysis.png',
        logger=None
    )
    
    log_message("\n[10/10] Generating summary report...")
    from src.dc.dc_analyzer import generate_summary_report
    report = generate_summary_report(df_dc, threshold=threshold, logger=None)
    
    report_path = output_dir / 'dc_analysis_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    
    log_message(f"\nReport saved to: {report_path}")
    log_message(f"Figures saved to: {figures_dir}")
    
    log_message("\n" + "="*60)
    log_message("COMPLETE DC ANALYSIS FINISHED")
    log_message("="*60)
    
    print(report)
    
    return results
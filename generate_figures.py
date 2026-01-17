#!/usr/bin/env python3
"""
Generate publication-quality figures for Master's Thesis:
"Reliability-Aware Routing in 6G MANET"

Generates 3 figures:
1. PDR Stability Analysis (Box Plot with Swarm)
2. Trade-off Overview (Normalized Bar Chart)
3. Convergence Dynamics (Time Series Line Chart)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Try to import seaborn, but make it optional
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

# Set style for publication-quality plots
if HAS_SEABORN:
    plt.style.use('seaborn-v0_8-paper')
    sns.set_palette("husl")
else:
    # Use matplotlib's built-in style
    plt.style.use('seaborn-v0_8-whitegrid')

# Configuration
DPI = 300
FIG_SIZE = (6, 4.5)
FONT_SIZE = 11
TITLE_SIZE = 13

# Color scheme
BASELINE_COLOR = '#d62728'  # Red
PROPOSED_COLOR = '#2ca02c'  # Green

# Data paths
DATA_DIR = Path('ns3/campaign_results_20251217_210419')
RESULTS_CSV = DATA_DIR / 'results.csv'
TIME_SERIES_CSV = DATA_DIR / 'time_series.csv'

def load_results_data():
    """Load and process results.csv"""
    df = pd.read_csv(RESULTS_CSV)
    
    # Clean up whitespace in Mode column
    df['Mode'] = df['Mode'].astype(str).str.strip()
    
    # Convert Mode: 0 -> Baseline, 1 -> Proposed
    df['Mode'] = df['Mode'].replace({'0': 'Baseline', '1': 'Proposed'})
    
    # Clean numeric columns (remove whitespace)
    numeric_cols = ['PDR', 'Latency_ms', 'Hops', 'ReliabilityDrops']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors='coerce')
    
    return df

def load_time_series_data():
    """Load and process time_series.csv, separating Baseline and Proposed"""
    df = pd.read_csv(TIME_SERIES_CSV)
    
    # Clean numeric columns
    df['Time'] = pd.to_numeric(df['Time'].astype(str).str.strip(), errors='coerce')
    df['Tx'] = pd.to_numeric(df['Tx'].astype(str).str.strip(), errors='coerce')
    df['Rx'] = pd.to_numeric(df['Rx'].astype(str).str.strip(), errors='coerce')
    
    # Read results to determine which RunID belongs to which mode
    results_df = load_results_data()
    
    # The time_series.csv has RunID values that appear multiple times
    # We need to match them with results.csv to determine mode
    # Strategy: Group results by RunID and Mode, then match time series data
    
    baseline_data = []
    proposed_data = []
    
    # Process each row in results to find corresponding time series data
    # Since RunID appears twice (once for Baseline, once for Proposed),
    # we need to track which occurrence we're on
    baseline_processed = {}  # Track which RunIDs we've seen for Baseline
    proposed_processed = {}  # Track which RunIDs we've seen for Proposed
    
    for idx, row in results_df.iterrows():
        run_id = row['RunID']
        mode = row['Mode']
        
        # Get all time series entries for this RunID
        run_ts_data = df[df['RunID'] == run_id].copy()
        
        if mode == 'Baseline':
            # Check if we've already processed this RunID for Baseline
            if run_id not in baseline_processed:
                baseline_data.append(run_ts_data)
                baseline_processed[run_id] = True
        elif mode == 'Proposed':
            # Check if we've already processed this RunID for Proposed
            if run_id not in proposed_processed:
                proposed_data.append(run_ts_data)
                proposed_processed[run_id] = True
    
    baseline_df = pd.concat(baseline_data, ignore_index=True) if baseline_data else pd.DataFrame()
    proposed_df = pd.concat(proposed_data, ignore_index=True) if proposed_data else pd.DataFrame()
    
    return baseline_df, proposed_df

def calculate_cumulative_pdr(df):
    """Calculate cumulative PDR over time for a dataframe"""
    if df.empty:
        return pd.DataFrame()
    
    # Group by Time and calculate average Tx/Rx across all runs
    grouped = df.groupby('Time').agg({
        'Tx': 'mean',
        'Rx': 'mean'
    }).reset_index()
    
    # Calculate PDR
    grouped['PDR'] = (grouped['Rx'] / grouped['Tx'].replace(0, np.nan)) * 100
    grouped = grouped[grouped['Tx'] > 0]  # Remove rows with zero Tx
    
    return grouped

def figure1_pdr_boxplot(df):
    """Figure 1: PDR Stability Analysis (Box Plot with Swarm)"""
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    
    # Prepare data
    baseline_pdr = df[df['Mode'] == 'Baseline']['PDR'].values
    proposed_pdr = df[df['Mode'] == 'Proposed']['PDR'].values
    
    # Create box plot
    bp = ax.boxplot([baseline_pdr, proposed_pdr], 
                     tick_labels=['Baseline', 'Proposed'],
                     patch_artist=True,
                     widths=0.6,
                     showmeans=True,
                     meanline=True)
    
    # Color the boxes
    bp['boxes'][0].set_facecolor(BASELINE_COLOR)
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_facecolor(PROPOSED_COLOR)
    bp['boxes'][1].set_alpha(0.7)
    
    # Color the medians
    for median in bp['medians']:
        median.set_color('black')
        median.set_linewidth(1.5)
    
    # Add swarm plot (scatter overlay)
    x_baseline = np.random.normal(1, 0.04, size=len(baseline_pdr))
    x_proposed = np.random.normal(2, 0.04, size=len(proposed_pdr))
    
    ax.scatter(x_baseline, baseline_pdr, color=BASELINE_COLOR, 
               s=50, alpha=0.6, edgecolors='black', linewidth=0.5, zorder=3)
    ax.scatter(x_proposed, proposed_pdr, color=PROPOSED_COLOR, 
               s=50, alpha=0.6, edgecolors='black', linewidth=0.5, zorder=3)
    
    # Formatting
    ax.set_ylabel('Packet Delivery Ratio (%)', fontsize=FONT_SIZE)
    ax.set_xlabel('Routing Mode', fontsize=FONT_SIZE)
    ax.set_title('PDR Stability Analysis', fontsize=TITLE_SIZE, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim([0, 105])
    
    # Add statistics text
    baseline_mean = np.mean(baseline_pdr)
    proposed_mean = np.mean(proposed_pdr)
    baseline_std = np.std(baseline_pdr)
    proposed_std = np.std(proposed_pdr)
    
    stats_text = f'Baseline: μ={baseline_mean:.2f}%, σ={baseline_std:.2f}%\n'
    stats_text += f'Proposed: μ={proposed_mean:.2f}%, σ={proposed_std:.2f}%'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('fig1_pdr_box.png', dpi=DPI, bbox_inches='tight')
    print("✓ Saved: fig1_pdr_box.png")
    plt.close()

def figure2_tradeoff_barchart(df):
    """Figure 2: Trade-off Overview (Normalized Bar Chart)"""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), dpi=DPI)
    
    # Calculate means
    baseline_means = df[df['Mode'] == 'Baseline'][['PDR', 'Latency_ms', 'Hops']].mean()
    proposed_means = df[df['Mode'] == 'Proposed'][['PDR', 'Latency_ms', 'Hops']].mean()
    
    # Normalize relative to Baseline (Baseline = 1.0)
    pdr_norm = {
        'Baseline': 1.0,
        'Proposed': proposed_means['PDR'] / baseline_means['PDR']
    }
    
    latency_norm = {
        'Baseline': 1.0,
        'Proposed': proposed_means['Latency_ms'] / baseline_means['Latency_ms']
    }
    
    hops_norm = {
        'Baseline': 1.0,
        'Proposed': proposed_means['Hops'] / baseline_means['Hops']
    }
    
    # Plot 1: PDR (Higher is better)
    x = np.arange(2)
    width = 0.6
    axes[0].bar(x, [pdr_norm['Baseline'], pdr_norm['Proposed']], 
                width, color=[BASELINE_COLOR, PROPOSED_COLOR], alpha=0.7, edgecolor='black')
    axes[0].set_ylabel('Normalized Value (Baseline = 1.0)', fontsize=FONT_SIZE)
    axes[0].set_title('PDR (Higher is Better)', fontsize=TITLE_SIZE, fontweight='bold')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(['Baseline', 'Proposed'])
    axes[0].grid(True, alpha=0.3, linestyle='--', axis='y')
    axes[0].axhline(y=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add value labels
    axes[0].text(0, pdr_norm['Baseline'] + 0.02, f'{baseline_means["PDR"]:.2f}%',
                ha='center', va='bottom', fontsize=9)
    axes[0].text(1, pdr_norm['Proposed'] + 0.02, f'{proposed_means["PDR"]:.2f}%',
                ha='center', va='bottom', fontsize=9)
    
    # Plot 2: Latency (Lower is better)
    axes[1].bar(x, [latency_norm['Baseline'], latency_norm['Proposed']], 
                width, color=[BASELINE_COLOR, PROPOSED_COLOR], alpha=0.7, edgecolor='black')
    axes[1].set_ylabel('Normalized Value (Baseline = 1.0)', fontsize=FONT_SIZE)
    axes[1].set_title('Latency (Lower is Better)', fontsize=TITLE_SIZE, fontweight='bold')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(['Baseline', 'Proposed'])
    axes[1].grid(True, alpha=0.3, linestyle='--', axis='y')
    axes[1].axhline(y=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add value labels
    axes[1].text(0, latency_norm['Baseline'] + 0.01, f'{baseline_means["Latency_ms"]:.2f} ms',
                ha='center', va='bottom', fontsize=9)
    axes[1].text(1, latency_norm['Proposed'] + 0.01, f'{proposed_means["Latency_ms"]:.2f} ms',
                ha='center', va='bottom', fontsize=9)
    
    # Plot 3: Hops (Contextual)
    axes[2].bar(x, [hops_norm['Baseline'], hops_norm['Proposed']], 
                width, color=[BASELINE_COLOR, PROPOSED_COLOR], alpha=0.7, edgecolor='black')
    axes[2].set_ylabel('Normalized Value (Baseline = 1.0)', fontsize=FONT_SIZE)
    axes[2].set_title('Average Hops', fontsize=TITLE_SIZE, fontweight='bold')
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(['Baseline', 'Proposed'])
    axes[2].grid(True, alpha=0.3, linestyle='--', axis='y')
    axes[2].axhline(y=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add value labels
    axes[2].text(0, hops_norm['Baseline'] + 0.05, f'{baseline_means["Hops"]:.2f}',
                ha='center', va='bottom', fontsize=9)
    axes[2].text(1, hops_norm['Proposed'] + 0.05, f'{proposed_means["Hops"]:.2f}',
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('fig2_tradeoff.png', dpi=DPI, bbox_inches='tight')
    print("✓ Saved: fig2_tradeoff.png")
    plt.close()

def figure3_convergence_timeseries(baseline_df, proposed_df):
    """Figure 3: Convergence Dynamics (Time Series Line Chart)"""
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    
    # Calculate cumulative PDR for each mode
    baseline_pdr = calculate_cumulative_pdr(baseline_df)
    proposed_pdr = calculate_cumulative_pdr(proposed_df)
    
    # Plot lines
    if not baseline_pdr.empty:
        ax.plot(baseline_pdr['Time'], baseline_pdr['PDR'], 
                color=BASELINE_COLOR, linewidth=2, label='Baseline', marker='o', markersize=4, alpha=0.8)
    
    if not proposed_pdr.empty:
        ax.plot(proposed_pdr['Time'], proposed_pdr['PDR'], 
                color=PROPOSED_COLOR, linewidth=2, label='Proposed', marker='s', markersize=4, alpha=0.8)
    
    # Formatting
    ax.set_xlabel('Time (seconds)', fontsize=FONT_SIZE)
    ax.set_ylabel('Cumulative PDR (%)', fontsize=FONT_SIZE)
    ax.set_title('Convergence Dynamics', fontsize=TITLE_SIZE, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', fontsize=FONT_SIZE)
    ax.set_ylim([0, 105])
    
    # Add horizontal reference line at 95%
    ax.axhline(y=95, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='95% Reference')
    
    plt.tight_layout()
    plt.savefig('fig3_convergence.png', dpi=DPI, bbox_inches='tight')
    print("✓ Saved: fig3_convergence.png")
    plt.close()

def main():
    """Main function to generate all figures"""
    print("=" * 70)
    print("Generating Publication-Quality Figures for Master's Thesis")
    print("=" * 70)
    print()
    
    # Load data
    print("Loading data...")
    results_df = load_results_data()
    baseline_ts, proposed_ts = load_time_series_data()
    
    print(f"  Results: {len(results_df)} rows")
    print(f"  Baseline time series: {len(baseline_ts)} rows")
    print(f"  Proposed time series: {len(proposed_ts)} rows")
    print()
    
    # Generate figures
    print("Generating Figure 1: PDR Stability Analysis...")
    figure1_pdr_boxplot(results_df)
    
    print("Generating Figure 2: Trade-off Overview...")
    figure2_tradeoff_barchart(results_df)
    
    print("Generating Figure 3: Convergence Dynamics...")
    figure3_convergence_timeseries(baseline_ts, proposed_ts)
    
    print()
    print("=" * 70)
    print("All figures generated successfully!")
    print("=" * 70)
    print()
    print("Output files:")
    print("  - fig1_pdr_box.png")
    print("  - fig2_tradeoff.png")
    print("  - fig3_convergence.png")

if __name__ == '__main__':
    main()

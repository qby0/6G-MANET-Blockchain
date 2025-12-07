#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis and Visualization Script for Monte Carlo Simulation Results
Generates publication-quality graphs for thesis
"""

import sys
import os

# Check dependencies
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    print("="*70)
    print("ERROR: Required Python packages not installed!")
    print("="*70)
    print("Please install dependencies:")
    print("  pip3 install pandas matplotlib numpy seaborn")
    print("")
    print("Or use system package manager:")
    print("  sudo apt-get install python3-pandas python3-matplotlib python3-numpy")
    print("="*70)
    sys.exit(1)

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12

def load_data(csv_file):
    """Load simulation results from CSV"""
    try:
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} records from {csv_file}")
        return df
    except FileNotFoundError:
        print(f"ERROR: File {csv_file} not found!")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR loading data: {e}")
        sys.exit(1)

def calculate_statistics(df):
    """Calculate statistics for Baseline and Proposed modes"""
    baseline = df[df['Mode'] == 'Baseline']
    proposed = df[df['Mode'] == 'Proposed']
    
    stats = {
        'Baseline': {
            'PDR_mean': baseline['PDR'].mean(),
            'PDR_std': baseline['PDR'].std(),
            'PDR_min': baseline['PDR'].min(),
            'PDR_max': baseline['PDR'].max(),
            'Latency_mean': baseline[baseline['Latency'] > 0]['Latency'].mean() if len(baseline[baseline['Latency'] > 0]) > 0 else 0,
            'Latency_std': baseline[baseline['Latency'] > 0]['Latency'].std() if len(baseline[baseline['Latency'] > 0]) > 0 else 0,
            'AvgHops_mean': baseline['AvgHops'].mean() if 'AvgHops' in baseline.columns else 0,
            'AvgHops_std': baseline['AvgHops'].std() if 'AvgHops' in baseline.columns else 0,
            'MaliciousDrops_mean': baseline['MaliciousDrops'].mean() if 'MaliciousDrops' in baseline.columns else 0,
            'MaliciousDrops_std': baseline['MaliciousDrops'].std() if 'MaliciousDrops' in baseline.columns else 0,
        },
        'Proposed': {
            'PDR_mean': proposed['PDR'].mean(),
            'PDR_std': proposed['PDR'].std(),
            'PDR_min': proposed['PDR'].min(),
            'PDR_max': proposed['PDR'].max(),
            'Latency_mean': proposed[proposed['Latency'] > 0]['Latency'].mean() if len(proposed[proposed['Latency'] > 0]) > 0 else 0,
            'Latency_std': proposed[proposed['Latency'] > 0]['Latency'].std() if len(proposed[proposed['Latency'] > 0]) > 0 else 0,
            'AvgHops_mean': proposed['AvgHops'].mean() if 'AvgHops' in proposed.columns else 0,
            'AvgHops_std': proposed['AvgHops'].std() if 'AvgHops' in proposed.columns else 0,
            'MaliciousDrops_mean': proposed['MaliciousDrops'].mean() if 'MaliciousDrops' in proposed.columns else 0,
            'MaliciousDrops_std': proposed['MaliciousDrops'].std() if 'MaliciousDrops' in proposed.columns else 0,
        }
    }
    
    return stats, baseline, proposed

def plot_average_pdr(stats, output_file='average_pdr.png'):
    """Graph 1: Average PDR (Bar Chart)"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    modes = ['Baseline', 'Proposed']
    means = [stats['Baseline']['PDR_mean'], stats['Proposed']['PDR_mean']]
    stds = [stats['Baseline']['PDR_std'], stats['Proposed']['PDR_std']]
    colors = ['#d62728', '#2ca02c']  # Red for Baseline, Green for Proposed
    
    bars = ax.bar(modes, means, yerr=stds, capsize=10, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (mean, std) in enumerate(zip(means, stds)):
        ax.text(i, mean + std + 2, f'{mean:.2f}%', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('Packet Delivery Ratio (PDR) [%]', fontsize=14, fontweight='bold')
    ax.set_title('Average Packet Delivery Ratio: Baseline vs Proposed', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add improvement annotation
    improvement = stats['Proposed']['PDR_mean'] - stats['Baseline']['PDR_mean']
    ax.annotate(f'Improvement: +{improvement:.2f}%', 
                xy=(1, stats['Proposed']['PDR_mean']), 
                xytext=(0.5, stats['Proposed']['PDR_mean'] + 15),
                arrowprops=dict(arrowstyle='->', color='green', lw=2),
                fontsize=12, fontweight='bold', color='green',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def plot_pdr_distribution(baseline, proposed, output_file='pdr_distribution.png'):
    """Graph 2: PDR Distribution (Box Plot)"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = [baseline['PDR'].values, proposed['PDR'].values]
    labels = ['Baseline', 'Proposed']
    colors = ['#d62728', '#2ca02c']
    
    bp = ax.boxplot(data, labels=labels, patch_artist=True, 
                    widths=0.6, showmeans=True, meanline=True,
                    medianprops=dict(color='black', linewidth=2),
                    meanprops=dict(color='blue', linewidth=2, linestyle='--'))
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Packet Delivery Ratio (PDR) [%]', fontsize=14, fontweight='bold')
    ax.set_title('PDR Distribution: Baseline vs Proposed (Box Plot)', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add statistics text
    stats_text = f"Baseline: μ={baseline['PDR'].mean():.2f}%, σ={baseline['PDR'].std():.2f}%\n"
    stats_text += f"Proposed: μ={proposed['PDR'].mean():.2f}%, σ={proposed['PDR'].std():.2f}%"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def plot_latency_comparison(baseline, proposed, output_file='latency_comparison.png'):
    """Graph 3: Latency Comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Filter out zero latency values
    baseline_latency = baseline[baseline['Latency'] > 0]['Latency'].values
    proposed_latency = proposed[proposed['Latency'] > 0]['Latency'].values
    
    if len(baseline_latency) == 0:
        baseline_latency = np.array([0])
    if len(proposed_latency) == 0:
        proposed_latency = np.array([0])
    
    data = [baseline_latency, proposed_latency]
    labels = ['Baseline', 'Proposed']
    colors = ['#d62728', '#2ca02c']
    
    bp = ax.boxplot(data, labels=labels, patch_artist=True,
                    widths=0.6, showmeans=True, meanline=True,
                    medianprops=dict(color='black', linewidth=2),
                    meanprops=dict(color='blue', linewidth=2, linestyle='--'))
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Average Latency [ms]', fontsize=14, fontweight='bold')
    ax.set_title('End-to-End Latency: Baseline vs Proposed', fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add statistics
    if len(baseline_latency) > 0 and len(proposed_latency) > 0:
        stats_text = f"Baseline: μ={np.mean(baseline_latency):.2f}ms, σ={np.std(baseline_latency):.2f}ms\n"
        stats_text += f"Proposed: μ={np.mean(proposed_latency):.2f}ms, σ={np.std(proposed_latency):.2f}ms"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def plot_malicious_drops(stats, output_file='malicious_drops.png'):
    """Graph 4: Malicious Drops Comparison (Bar Chart)"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    modes = ['Baseline', 'Proposed']
    means = [stats['Baseline']['MaliciousDrops_mean'], stats['Proposed']['MaliciousDrops_mean']]
    stds = [stats['Baseline']['MaliciousDrops_std'], stats['Proposed']['MaliciousDrops_std']]
    colors = ['#d62728', '#2ca02c']  # Red for Baseline, Green for Proposed
    
    bars = ax.bar(modes, means, yerr=stds, capsize=10, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (mean, std) in enumerate(zip(means, stds)):
        ax.text(i, mean + std + max(means) * 0.05, f'{mean:.0f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('Malicious Drops (Count)', fontsize=14, fontweight='bold')
    ax.set_title('Malicious Packet Drops: Baseline vs Proposed', fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add reduction annotation if Proposed has fewer drops
    if means[1] < means[0]:
        reduction = means[0] - means[1]
        reduction_pct = (reduction / means[0]) * 100 if means[0] > 0 else 0
        ax.annotate(f'Reduction: -{reduction:.0f} ({reduction_pct:.1f}%)', 
                    xy=(1, means[1]), 
                    xytext=(0.5, means[1] + max(means) * 0.2),
                    arrowprops=dict(arrowstyle='->', color='green', lw=2),
                    fontsize=12, fontweight='bold', color='green',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def print_statistics(stats):
    """Print detailed statistics"""
    print("\n" + "="*70)
    print("DETAILED STATISTICS")
    print("="*70)
    
    for mode in ['Baseline', 'Proposed']:
        print(f"\n{mode} Mode:")
        print(f"  PDR:")
        print(f"    Mean:   {stats[mode]['PDR_mean']:.2f}%")
        print(f"    Std:    {stats[mode]['PDR_std']:.2f}%")
        print(f"    Min:    {stats[mode]['PDR_min']:.2f}%")
        print(f"    Max:    {stats[mode]['PDR_max']:.2f}%")
        print(f"  Latency:")
        print(f"    Mean:   {stats[mode]['Latency_mean']:.2f} ms")
        print(f"    Std:    {stats[mode]['Latency_std']:.2f} ms")
        if 'AvgHops_mean' in stats[mode]:
            print(f"  Avg Hops:")
            print(f"    Mean:   {stats[mode]['AvgHops_mean']:.2f}")
            print(f"    Std:    {stats[mode]['AvgHops_std']:.2f}")
        if 'MaliciousDrops_mean' in stats[mode]:
            print(f"  Malicious Drops:")
            print(f"    Mean:   {stats[mode]['MaliciousDrops_mean']:.0f}")
            print(f"    Std:    {stats[mode]['MaliciousDrops_std']:.0f}")
    
    print("\n" + "="*70)
    print("IMPROVEMENT ANALYSIS")
    print("="*70)
    pdr_improvement = stats['Proposed']['PDR_mean'] - stats['Baseline']['PDR_mean']
    pdr_improvement_pct = (pdr_improvement / stats['Baseline']['PDR_mean']) * 100 if stats['Baseline']['PDR_mean'] > 0 else 0
    
    print(f"PDR Improvement: {pdr_improvement:.2f}% (absolute)")
    print(f"PDR Improvement: {pdr_improvement_pct:.2f}% (relative)")
    
    if stats['Proposed']['PDR_std'] < stats['Baseline']['PDR_std']:
        stability_improvement = ((stats['Baseline']['PDR_std'] - stats['Proposed']['PDR_std']) / stats['Baseline']['PDR_std']) * 100
        print(f"Stability Improvement: {stability_improvement:.2f}% reduction in variance")
    
    if 'MaliciousDrops_mean' in stats['Baseline'] and 'MaliciousDrops_mean' in stats['Proposed']:
        drops_reduction = stats['Baseline']['MaliciousDrops_mean'] - stats['Proposed']['MaliciousDrops_mean']
        drops_reduction_pct = (drops_reduction / stats['Baseline']['MaliciousDrops_mean']) * 100 if stats['Baseline']['MaliciousDrops_mean'] > 0 else 0
        print(f"Malicious Drops Reduction: {drops_reduction:.0f} (absolute)")
        print(f"Malicious Drops Reduction: {drops_reduction_pct:.2f}% (relative)")
    
    print("="*70 + "\n")

def main():
    csv_file = 'final_results.csv'
    
    if not os.path.exists(csv_file):
        print(f"ERROR: {csv_file} not found!")
        print("Please run the simulation campaign first:")
        print("  ./run_campaign.sh 30 3 2 60.0 150.0 20.0 1 50")
        sys.exit(1)
    
    print("="*70)
    print("Monte Carlo Simulation Results Analysis")
    print("="*70)
    
    # Load data
    df = load_data(csv_file)
    
    # Calculate statistics
    stats, baseline, proposed = calculate_statistics(df)
    
    # Print statistics
    print_statistics(stats)
    
    # Generate plots
    print("Generating plots...")
    plot_average_pdr(stats, 'average_pdr.png')
    plot_pdr_distribution(baseline, proposed, 'pdr_distribution.png')
    plot_latency_comparison(baseline, proposed, 'latency_comparison.png')
    
    # Generate malicious drops plot if data is available
    if 'MaliciousDrops' in df.columns:
        plot_malicious_drops(stats, 'malicious_drops.png')
    
    print("\n" + "="*70)
    print("Analysis Complete!")
    print("="*70)
    print("Generated files:")
    print("  - average_pdr.png (Graph 1: Average PDR Bar Chart)")
    print("  - pdr_distribution.png (Graph 2: PDR Distribution Box Plot)")
    print("  - latency_comparison.png (Graph 3: Latency Comparison)")
    if 'MaliciousDrops' in df.columns:
        print("  - malicious_drops.png (Graph 4: Malicious Drops Comparison)")
    print("="*70)

if __name__ == '__main__':
    main()


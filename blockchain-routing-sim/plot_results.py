#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Results visualization script
"""

import json
import os
import sys
import argparse
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List


def load_metrics(filename: str) -> Dict:
    """
    Loads metrics from JSON file.
    
    Args:
        filename: Filename
        
    Returns:
        Dictionary with metrics
    """
    with open(filename, 'r') as f:
        return json.load(f)


def plot_pdr_comparison(baseline_file: str, proposed_file: str, output_file: str = None):
    """
    Creates PDR comparison plot between Baseline and Proposed methods.
    
    Args:
        baseline_file: Baseline metrics file
        proposed_file: Proposed metrics file
        output_file: Output filename (if None, shows plot)
    """
    baseline_data = load_metrics(baseline_file)
    proposed_data = load_metrics(proposed_file)
    
    baseline_pdr = baseline_data.get("summary", {}).get("pdr_percent", 0.0)
    proposed_pdr = proposed_data.get("summary", {}).get("pdr_percent", 0.0)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    methods = ["Baseline\n(Shortest Path)", "Proposed\n(Blockchain-assisted)"]
    pdr_values = [baseline_pdr, proposed_pdr]
    colors = ['#ff6b6b', '#51cf66']
    
    bars = ax.bar(methods, pdr_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add values on bars
    for bar, value in zip(bars, pdr_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{value:.2f}%',
               ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Packet Delivery Ratio (%)', fontsize=12, fontweight='bold')
    ax.set_title('PDR Comparison: Baseline vs Proposed Routing', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 100])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"PDR comparison saved to {output_file}")
    else:
        plt.show()
    
    plt.close()


def plot_latency_comparison(baseline_file: str, proposed_file: str, output_file: str = None):
    """
    Creates Latency comparison plot between Baseline and Proposed methods.
    
    Args:
        baseline_file: Baseline metrics file
        proposed_file: Proposed metrics file
        output_file: Output filename (if None, shows plot)
    """
    baseline_data = load_metrics(baseline_file)
    proposed_data = load_metrics(proposed_file)
    
    baseline_latency = baseline_data.get("summary", {}).get("average_latency_ms", 0.0)
    proposed_latency = proposed_data.get("summary", {}).get("average_latency_ms", 0.0)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    methods = ["Baseline\n(Shortest Path)", "Proposed\n(Blockchain-assisted)"]
    latency_values = [baseline_latency, proposed_latency]
    colors = ['#ff6b6b', '#51cf66']
    
    bars = ax.bar(methods, latency_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add values on bars
    for bar, value in zip(bars, latency_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{value:.2f} ms',
               ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Average Latency (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Latency Comparison: Baseline vs Proposed Routing', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Latency comparison saved to {output_file}")
    else:
        plt.show()
    
    plt.close()


def plot_combined_comparison(baseline_file: str, proposed_file: str, output_file: str = None):
    """
    Creates combined comparison plot of PDR and Latency.
    
    Args:
        baseline_file: Baseline metrics file
        proposed_file: Proposed metrics file
        output_file: Output filename (if None, shows plot)
    """
    baseline_data = load_metrics(baseline_file)
    proposed_data = load_metrics(proposed_file)
    
    baseline_pdr = baseline_data.get("summary", {}).get("pdr_percent", 0.0)
    proposed_pdr = proposed_data.get("summary", {}).get("pdr_percent", 0.0)
    baseline_latency = baseline_data.get("summary", {}).get("average_latency_ms", 0.0)
    proposed_latency = proposed_data.get("summary", {}).get("average_latency_ms", 0.0)
    
    # Create two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    methods = ["Baseline\n(Shortest Path)", "Proposed\n(Blockchain-assisted)"]
    colors = ['#ff6b6b', '#51cf66']
    
    # PDR plot
    pdr_values = [baseline_pdr, proposed_pdr]
    bars1 = ax1.bar(methods, pdr_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    for bar, value in zip(bars1, pdr_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Packet Delivery Ratio (%)', fontsize=11, fontweight='bold')
    ax1.set_title('PDR Comparison', fontsize=12, fontweight='bold')
    ax1.set_ylim([0, 100])
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Latency plot
    latency_values = [baseline_latency, proposed_latency]
    bars2 = ax2.bar(methods, latency_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    for bar, value in zip(bars2, latency_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f} ms',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Average Latency (ms)', fontsize=11, fontweight='bold')
    ax2.set_title('Latency Comparison', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.suptitle('6G MANET Routing Performance Comparison', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Combined comparison saved to {output_file}")
    else:
        plt.show()
    
    plt.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Visualize simulation results")
    parser.add_argument("--baseline", type=str, required=True,
                       help="Baseline metrics JSON file")
    parser.add_argument("--proposed", type=str, required=True,
                       help="Proposed metrics JSON file")
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Output directory for plots")
    parser.add_argument("--plot-type", type=str, default="combined",
                       choices=["pdr", "latency", "combined"],
                       help="Type of plot to generate")
    
    args = parser.parse_args()
    
    # Check file existence
    if not os.path.exists(args.baseline):
        print(f"Error: Baseline file not found: {args.baseline}")
        sys.exit(1)
    
    if not os.path.exists(args.proposed):
        print(f"Error: Proposed file not found: {args.proposed}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate plots
    if args.plot_type == "pdr":
        output_file = os.path.join(args.output_dir, "pdr_comparison.png")
        plot_pdr_comparison(args.baseline, args.proposed, output_file)
    elif args.plot_type == "latency":
        output_file = os.path.join(args.output_dir, "latency_comparison.png")
        plot_latency_comparison(args.baseline, args.proposed, output_file)
    else:  # combined
        output_file = os.path.join(args.output_dir, "combined_comparison.png")
        plot_combined_comparison(args.baseline, args.proposed, output_file)
    
    print("Visualization complete!")


if __name__ == "__main__":
    main()


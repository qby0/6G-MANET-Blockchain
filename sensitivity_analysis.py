#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

# Sensitivity Sweep Data: PDR vs Beta
beta_values = [1.0, 100, 500, 1000]
pdr_values = [98.61, 98.62, 97.52, 98.56]  # Updated with actual results

# Ablation Study Data: PDR vs Trust Floor
floor_values = [0.1, 0.2, 0.3]
floor_pdr_values = [95.77, 98.61, 93.65]  # Floor=0.2 from Beta=1.0 test

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Sensitivity Sweep - PDR vs Beta
ax1.plot(beta_values, pdr_values, 'o-', linewidth=2.5, markersize=10, color='#2E86AB', markerfacecolor='#06A77D')
ax1.set_xlabel('Beta Coefficient', fontsize=12, fontweight='bold')
ax1.set_ylabel('Packet Delivery Ratio (PDR) [%]', fontsize=12, fontweight='bold')
ax1.set_title('Sensitivity Analysis: PDR vs Beta', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_xscale('log')
ax1.set_ylim([97, 99])
ax1.set_xticks([1, 100, 500, 1000])
ax1.set_xticklabels(['1', '100', '500', '1000'])

# Add value labels
for i, (beta, pdr) in enumerate(zip(beta_values, pdr_values)):
    ax1.annotate(f'{pdr:.2f}%', (beta, pdr), 
                textcoords="offset points", xytext=(0,12), ha='center', fontsize=10, fontweight='bold')

# Calculate and display range
pdr_range = max(pdr_values) - min(pdr_values)
ax1.text(0.5, 0.02, f'PDR Range: {pdr_range:.2f}% (97.52% - 98.62%)', 
         transform=ax1.transAxes, ha='center', fontsize=10, 
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Plot 2: Ablation Study - PDR vs Trust Floor
ax2.plot(floor_values, floor_pdr_values, 's-', linewidth=2.5, markersize=10, color='#A23B72', markerfacecolor='#F18F01')
ax2.set_xlabel('Trust Floor Value', fontsize=12, fontweight='bold')
ax2.set_ylabel('Packet Delivery Ratio (PDR) [%]', fontsize=12, fontweight='bold')
ax2.set_title('Ablation Study: PDR vs Trust Floor', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.set_ylim([92, 99])
ax2.set_xticks([0.1, 0.2, 0.3])
ax2.set_xticklabels(['0.1', '0.2', '0.3'])

# Add value labels
for i, (floor, pdr) in enumerate(zip(floor_values, floor_pdr_values)):
    ax2.annotate(f'{pdr:.2f}%', (floor, pdr), 
                textcoords="offset points", xytext=(0,12), ha='center', fontsize=10, fontweight='bold')

# Highlight optimal floor
ax2.axvline(x=0.2, color='green', linestyle='--', alpha=0.5, linewidth=2)
ax2.text(0.2, 98.5, 'Optimal\n(Floor=0.2)', ha='center', fontsize=9, 
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

plt.tight_layout()
plt.savefig('sensitivity_analysis.png', dpi=300, bbox_inches='tight')
print("Graph saved as sensitivity_analysis.png")

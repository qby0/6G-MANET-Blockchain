#!/bin/bash

# Advanced Realistic Cross-Zone Blockchain Simulation Runner
# This script sets up the environment and runs the comprehensive simulation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Check if pip is available
    if ! command_exists pip3; then
        print_error "pip3 not found. Please install Python3 and pip3."
        exit 1
    fi
    
    # Install required packages
    pip3 install --user matplotlib seaborn numpy pandas scipy networkx || {
        print_warning "Failed to install with --user flag, trying without..."
        pip3 install matplotlib seaborn numpy pandas scipy networkx
    }
    
    print_success "Dependencies installed successfully"
}

# Function to setup simulation environment
setup_environment() {
    print_info "Setting up simulation environment..."
    
    # Create results directory
    mkdir -p results
    mkdir -p results/plots
    mkdir -p results/detailed
    
    # Check if config exists
    if [ ! -f "config/realistic_device_config.json" ]; then
        print_error "Realistic device configuration not found!"
        print_info "Please run the device parameter tests first: python3 scripts/test_realistic_devices.py"
        exit 1
    fi
    
    # Check if realistic device manager exists
    if [ ! -f "models/realistic_device_manager.py" ]; then
        print_error "Realistic device manager not found!"
        exit 1
    fi
    
    print_success "Environment setup complete"
}

# Function to run the simulation
run_simulation() {
    local scenario=${1:-"medium_district"}
    local duration=${2:-600}
    
    print_header "🚀 STARTING ADVANCED REALISTIC CROSS-ZONE BLOCKCHAIN SIMULATION"
    echo "================================================================="
    print_info "Scenario: $scenario"
    print_info "Duration: $duration seconds ($(($duration / 60)) minutes)"
    print_info "Output: results/"
    echo

    # Set PYTHONPATH to include current directory
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    
    # Run the simulation
    python3 advanced_realistic_simulation.py \
        --scenario "$scenario" \
        --duration "$duration" \
        --output-dir results/ || {
        print_error "Simulation failed!"
        exit 1
    }
}

# Function to create enhanced visualization script
create_enhanced_visualization() {
    print_info "Creating enhanced visualization capabilities..."
    
    cat > "visualize_results.py" << 'EOF'
#!/usr/bin/env python3
"""
Enhanced Visualization Script for Simulation Results
"""

import matplotlib.pyplot as plt
import seaborn as sns
import json
import sys
from pathlib import Path

def create_presentation_plots(results_dir):
    """Create presentation-ready plots"""
    results_path = Path(results_dir)
    
    # Load summary data
    summary_file = results_path / "simulation_summary.json"
    if not summary_file.exists():
        print("No summary file found!")
        return
    
    with open(summary_file) as f:
        summary = json.load(f)
    
    # Create presentation figure
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Energy consumption by device type
    ax1 = axes[0, 0]
    device_types = list(summary['device_statistics']['by_type'].keys())
    energies = [summary['device_statistics']['by_type'][dt]['total_energy'] 
               for dt in device_types]
    
    bars = ax1.bar(device_types, energies, color=sns.color_palette("husl", len(device_types)))
    ax1.set_title('Total Energy Consumption by Device Type', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Energy (mJ)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Battery levels
    ax2 = axes[0, 1] 
    battery_data = [summary['device_statistics']['by_type'][dt]['avg_battery'] 
                   for dt in device_types if 'avg_battery' in summary['device_statistics']['by_type'][dt]]
    device_types_with_battery = [dt for dt in device_types 
                               if 'avg_battery' in summary['device_statistics']['by_type'][dt]]
    
    if battery_data:
        bars = ax2.bar(device_types_with_battery, battery_data, 
                      color=['#FF6B6B', '#4ECDC4', '#45B7D1'][:len(battery_data)])
        ax2.set_title('Average Battery Levels', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Battery Level (%)')
        ax2.tick_params(axis='x', rotation=45)
    
    # Network statistics
    ax3 = axes[1, 0]
    metrics = ['Total Transactions', 'Confirmed Transactions', 'Total Blocks']
    values = [summary['simulation_overview']['total_transactions'],
              summary['simulation_overview']['confirmed_transactions'],
              summary['simulation_overview']['total_blocks']]
    
    bars = ax3.bar(metrics, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax3.set_title('Network Activity Summary', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Count')
    
    # Performance metrics
    ax4 = axes[1, 1]
    perf_metrics = ['Energy/Tx (mJ)', 'Consensus Efficiency', 'Device Uptime (%)']
    perf_values = [summary['performance_metrics']['energy_per_transaction'],
                   summary['performance_metrics']['consensus_efficiency'] * 100,
                   summary['performance_metrics']['device_uptime']]
    
    bars = ax4.bar(perf_metrics, perf_values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax4.set_title('Performance Metrics', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Value')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.suptitle('Cross-Zone Blockchain Simulation Results', fontsize=16, y=0.98)
    
    # Save presentation plot
    plt.savefig(results_path / "presentation_summary.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Presentation plots saved to {results_path}/presentation_summary.png")

if __name__ == "__main__":
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    create_presentation_plots(results_dir)
EOF

    chmod +x visualize_results.py
    print_success "Enhanced visualization script created"
}

# Function to display results
display_results() {
    print_header "📊 SIMULATION RESULTS"
    echo "====================="
    
    if [ -f "results/simulation_summary.json" ]; then
        print_info "Summary statistics generated: results/simulation_summary.json"
        
        # Extract key metrics using jq if available
        if command_exists jq; then
            total_devices=$(jq -r '.simulation_overview.total_devices' results/simulation_summary.json)
            total_transactions=$(jq -r '.simulation_overview.total_transactions' results/simulation_summary.json)
            confirmed_transactions=$(jq -r '.simulation_overview.confirmed_transactions' results/simulation_summary.json)
            total_blocks=$(jq -r '.simulation_overview.total_blocks' results/simulation_summary.json)
            energy_per_tx=$(jq -r '.performance_metrics.energy_per_transaction' results/simulation_summary.json)
            device_uptime=$(jq -r '.performance_metrics.device_uptime' results/simulation_summary.json)
            
            echo
            print_info "📈 Key Metrics:"
            echo "   Devices: $total_devices"
            echo "   Total Transactions: $total_transactions"
            echo "   Confirmed Transactions: $confirmed_transactions"
            echo "   Blocks Generated: $total_blocks"
            echo "   Energy per Transaction: ${energy_per_tx} mJ"
            echo "   Device Uptime: ${device_uptime}%"
        fi
    fi
    
    echo
    print_info "📁 Generated Files:"
    find results/ -name "*.png" -o -name "*.json" | sort | while read file; do
        echo "   $file"
    done
    
    echo
    print_success "🎉 Simulation completed successfully!"
    print_info "📊 Main dashboard: results/simulation_dashboard.png"
    print_info "📈 Detailed plots: results/*_detailed.png"
    print_info "📋 Raw data: results/simulation_summary.json"
}

# Function to open results (if GUI available)
open_results() {
    if command_exists xdg-open; then
        print_info "Opening results in default image viewer..."
        xdg-open results/simulation_dashboard.png 2>/dev/null &
    elif command_exists open; then  # macOS
        print_info "Opening results in default image viewer..."
        open results/simulation_dashboard.png 2>/dev/null &
    else
        print_info "GUI not available. Results saved to results/ directory."
    fi
}

# Main function
main() {
    local scenario=${1:-"medium_district"}
    local duration=${2:-600}
    local skip_deps=${3:-false}
    
    print_header "🔬 ADVANCED REALISTIC CROSS-ZONE BLOCKCHAIN SIMULATION"
    print_header "======================================================="
    echo
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Install dependencies unless skipped
    if [ "$skip_deps" != "true" ]; then
        install_dependencies
        echo
    fi
    
    # Setup environment
    setup_environment
    echo
    
    # Create enhanced visualization
    create_enhanced_visualization
    echo
    
    # Run simulation
    run_simulation "$scenario" "$duration"
    echo
    
    # Create presentation plots
    print_info "Creating presentation plots..."
    python3 visualize_results.py results/
    echo
    
    # Display results
    display_results
    echo
    
    # Optionally open results
    if [ "${DISPLAY:-}" ] || [ "$(uname)" = "Darwin" ]; then
        read -p "Open results in image viewer? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open_results
        fi
    fi
}

# Help function
show_help() {
    echo "Advanced Realistic Cross-Zone Blockchain Simulation"
    echo
    echo "Usage: $0 [scenario] [duration] [skip_deps]"
    echo
    echo "Parameters:"
    echo "  scenario   : Simulation scenario (default: medium_district)"
    echo "               Options: small_campus, medium_district, large_city"
    echo "  duration   : Simulation duration in seconds (default: 600)"
    echo "  skip_deps  : Skip dependency installation (true/false, default: false)"
    echo
    echo "Examples:"
    echo "  $0                                    # Run with defaults"
    echo "  $0 large_city 1200                   # Large city, 20 minutes"
    echo "  $0 small_campus 300 true             # Small campus, 5 min, skip deps"
    echo
    echo "Output:"
    echo "  All results will be saved to the 'results/' directory"
    echo "  - simulation_dashboard.png          : Main dashboard"
    echo "  - *_detailed.png                    : Detailed analysis plots"
    echo "  - simulation_summary.json           : Raw statistics"
    echo "  - presentation_summary.png          : Presentation-ready summary"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help|help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac 
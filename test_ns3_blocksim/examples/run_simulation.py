#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive Cross-Zone Blockchain Simulation Runner

This script orchestrates the entire simulation pipeline including:
- Advanced realistic device simulation
- Beautiful statistical visualizations
- Interactive dashboards
- Publication-ready reports
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Optional

# Import our simulation modules
try:
    # Add parent directory to path to access src modules
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    sys.path.insert(0, str(project_root))
    
    from src.simulation.advanced_realistic_simulation import AdvancedRealisticSimulation
    from src.visualization.enhanced_visualization import EnhancedVisualization
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required modules are available")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimulationRunner:
    """
    Comprehensive simulation runner with enhanced visualization
    """
    
    def __init__(self, args):
        """Initialize the simulation runner"""
        self.args = args
        self.simulation: Optional[AdvancedRealisticSimulation] = None
        self.visualization: Optional[EnhancedVisualization] = None
        
        # Ensure output directory exists
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    def run_complete_simulation(self):
        """Run the complete simulation pipeline"""
        print("🚀 Starting Comprehensive Cross-Zone Blockchain Simulation")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # Phase 1: Initialize and run simulation
            self._run_simulation_phase()
            
            # Phase 2: Generate enhanced visualizations
            self._generate_visualizations_phase()
            
            # Phase 3: Create comprehensive report
            self._create_comprehensive_report()
            
            # Phase 4: Display results summary
            self._display_results_summary()
            
            total_time = time.time() - start_time
            print(f"\n✅ Complete simulation pipeline finished in {total_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Simulation pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
    
    def _run_simulation_phase(self):
        """Phase 1: Run the advanced realistic simulation"""
        print("\n📊 Phase 1: Running Advanced Realistic Simulation")
        print("-" * 50)
        
        # Initialize simulation
        self.simulation = AdvancedRealisticSimulation(self.args.scenario)
        
        print(f"📋 Scenario: {self.args.scenario}")
        print(f"⏱️  Duration: {self.args.duration} seconds ({self.args.duration//60}:{self.args.duration%60:02d})")
        print(f"🔧 Devices: {len(self.simulation.devices)}")
        print(f"📍 Area: {self.simulation.scenario['area_km2']} km²")
        print(f"📁 Output: {self.args.output_dir}/")
        
        # Run simulation
        print("\n🔄 Running simulation...")
        self.simulation.run_simulation(self.args.duration)
        
        # Generate basic report
        print("📈 Generating basic simulation report...")
        report_path = self.simulation.generate_comprehensive_report(self.args.output_dir)
        print(f"✅ Basic report saved to: {report_path}")
    
    def _generate_visualizations_phase(self):
        """Phase 2: Generate enhanced visualizations"""
        print("\n🎨 Phase 2: Generating Enhanced Visualizations")
        print("-" * 50)
        
        # Initialize visualization
        self.visualization = EnhancedVisualization(self.args.output_dir)
        
        if self.args.executive_dashboard:
            print("📊 Creating executive dashboard...")
            dashboard_path = self.visualization.create_executive_dashboard()
            print(f"✅ Executive dashboard: {dashboard_path}")
        
        if self.args.interactive_plots:
            print("🎯 Creating interactive dashboard...")
            interactive_path = self.visualization.create_interactive_dashboard()
            print(f"✅ Interactive dashboard: {interactive_path}")
        
        if self.args.publication_plots:
            print("📝 Creating publication-ready plots...")
            plot_paths = self.visualization.create_publication_plots()
            print(f"✅ Publication plots: {len(plot_paths)} files created")
    
    def _create_comprehensive_report(self):
        """Phase 3: Create comprehensive text report"""
        print("\n📋 Phase 3: Creating Comprehensive Report")
        print("-" * 50)
        
        report_path = Path(self.args.output_dir) / "comprehensive_report.md"
        
        with open(report_path, 'w') as f:
            f.write(self._generate_markdown_report())
        
        print(f"✅ Comprehensive report: {report_path}")
    
    def _generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report"""
        if not self.simulation:
            return "No simulation data available"
        
        # Calculate statistics
        total_energy = sum(state.total_energy_consumed for state in self.simulation.device_states.values())
        confirmed_txs = len([tx for tx in self.simulation.transactions if tx.status == 'confirmed'])
        online_devices = len([s for s in self.simulation.device_states.values() if s.online])
        
        # Device type breakdown
        device_type_counts = {}
        for device in self.simulation.devices.values():
            device_type = device.device_type
            device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
        
        # Zone distribution
        zone_counts = {}
        for state in self.simulation.device_states.values():
            if state.online:
                zone_counts[state.current_zone] = zone_counts.get(state.current_zone, 0) + 1
        
        report = f"""# Cross-Zone Blockchain Simulation Report

## Executive Summary

This report presents the results of an advanced realistic cross-zone blockchain simulation 
that models real-world device parameters, energy consumption, and network dynamics.

### Key Findings

- **Total Devices**: {len(self.simulation.devices):,}
- **Simulation Duration**: {self.simulation.current_time:.0f} seconds ({self.simulation.current_time/60:.1f} minutes)
- **Total Transactions**: {len(self.simulation.transactions):,}
- **Confirmed Transactions**: {confirmed_txs:,}
- **Success Rate**: {(confirmed_txs/max(1, len(self.simulation.transactions))*100):.1f}%
- **Total Blocks**: {len(self.simulation.blocks):,}
- **Device Uptime**: {(online_devices/len(self.simulation.devices)*100):.1f}%

## Energy Analysis

### Overall Energy Consumption
- **Total Energy Consumed**: {total_energy:.1f} mJ
- **Energy per Transaction**: {total_energy/max(1, confirmed_txs):.1f} mJ
- **Energy per Block**: {total_energy/max(1, len(self.simulation.blocks)):.1f} mJ

### Device Type Energy Breakdown
"""
        
        for device_type, count in device_type_counts.items():
            type_energy = sum(state.total_energy_consumed 
                            for device_id, state in self.simulation.device_states.items()
                            if self.simulation.devices[device_id].device_type == device_type)
            online_count = sum(1 for device_id, state in self.simulation.device_states.items() 
                             if self.simulation.devices[device_id].device_type == device_type and state.online)
            
            report += f"- **{device_type.replace('_', ' ').title()}**: {type_energy:.1f} mJ across {online_count}/{count} devices\n"
        
        report += f"""
## Network Performance

### Zone Distribution
"""
        
        for zone, count in zone_counts.items():
            percentage = (count / online_devices) * 100
            report += f"- **{zone.upper()} Zone**: {count} devices ({percentage:.1f}%)\n"
        
        report += f"""
### Transaction Performance
- **Transaction Rate**: {len(self.simulation.transactions) / self.simulation.current_time * 60:.1f} tx/min
- **Confirmed Rate**: {confirmed_txs / self.simulation.current_time * 60:.1f} tx/min
- **Block Rate**: {len(self.simulation.blocks) / self.simulation.current_time * 60:.1f} blocks/min

### Consensus Performance
"""
        
        if self.simulation.stats['consensus_latency']:
            avg_consensus = sum(self.simulation.stats['consensus_latency']) / len(self.simulation.stats['consensus_latency'])
            report += f"- **Average Consensus Time**: {avg_consensus:.2f} seconds\n"
            report += f"- **Total Consensus Rounds**: {len(self.simulation.stats['consensus_latency'])}\n"
        
        report += f"""
## Device Performance Analysis

### Mobile Device Battery Analysis
"""
        
        mobile_devices = ['smartphone', 'iot_sensor']
        for device_type in mobile_devices:
            battery_levels = [state.battery_level for device_id, state in self.simulation.device_states.items()
                             if self.simulation.devices[device_id].device_type == device_type]
            if battery_levels:
                avg_battery = sum(battery_levels) / len(battery_levels)
                min_battery = min(battery_levels)
                report += f"- **{device_type.replace('_', ' ').title()}**: Avg {avg_battery:.1f}%, Min {min_battery:.1f}%\n"
        
        report += f"""
### Zone Transition Analysis
"""
        
        for transition, count in self.simulation.stats['zone_transitions'].items():
            report += f"- **{transition.replace('_', ' → ').upper()}**: {count} transitions\n"
        
        report += f"""
## Methodology

### Simulation Parameters
- **Scenario**: {self.simulation.scenario.get('name', 'Custom')}
- **Area**: {self.simulation.scenario['area_km2']} km²
- **Time Step**: 1 second
- **Consensus Interval**: 5 seconds
- **Maximum Block Size**: 50 transactions

### Device Models
The simulation uses realistic device parameters based on current technology:
"""
        
        for device_type, count in device_type_counts.items():
            sample_device = next(device for device in self.simulation.devices.values() 
                                if device.device_type == device_type)
            report += f"""
#### {device_type.replace('_', ' ').title()}
- **Count**: {count}
- **CPU Performance**: {sample_device.cpu_performance} GFLOPS
- **Memory**: {sample_device.ram_gb} GB
- **Mobility**: {sample_device.mobility_type}
"""
        
        report += f"""
## Conclusions

1. **Energy Efficiency**: The system achieved {total_energy/max(1, confirmed_txs):.1f} mJ per confirmed transaction
2. **Network Stability**: {(online_devices/len(self.simulation.devices)*100):.1f}% device uptime demonstrates robust network operation
3. **Transaction Throughput**: {confirmed_txs / self.simulation.current_time * 60:.1f} confirmed transactions per minute
4. **Consensus Performance**: Average consensus time of {sum(self.simulation.stats['consensus_latency'])/max(1, len(self.simulation.stats['consensus_latency'])):.2f} seconds

## Recommendations

1. **Energy Optimization**: Focus on optimizing {max(device_type_counts, key=device_type_counts.get)} devices for better energy efficiency
2. **Zone Balancing**: Consider load balancing strategies for zone distribution
3. **Consensus Tuning**: Evaluate consensus parameters for optimal performance vs. security trade-offs

---
*Report generated on {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def _display_results_summary(self):
        """Phase 4: Display final results summary"""
        print("\n📊 Phase 4: Results Summary")
        print("-" * 50)
        
        if not self.simulation:
            print("❌ No simulation data available")
            return
        
        # Calculate key metrics
        total_energy = sum(state.total_energy_consumed for state in self.simulation.device_states.values())
        confirmed_txs = len([tx for tx in self.simulation.transactions if tx.status == 'confirmed'])
        online_devices = len([s for s in self.simulation.device_states.values() if s.online])
        
        print(f"📈 Simulation Results:")
        print(f"   ├── Total Transactions: {len(self.simulation.transactions):,}")
        print(f"   ├── Confirmed Transactions: {confirmed_txs:,}")
        print(f"   ├── Total Blocks: {len(self.simulation.blocks):,}")
        print(f"   ├── Total Energy: {total_energy:.1f} mJ")
        print(f"   ├── Energy/Transaction: {total_energy/max(1, confirmed_txs):.1f} mJ")
        print(f"   ├── Active Devices: {online_devices}/{len(self.simulation.devices)}")
        print(f"   └── Success Rate: {(confirmed_txs/max(1, len(self.simulation.transactions))*100):.1f}%")
        
        print(f"\n📁 Generated Files:")
        output_dir = Path(self.args.output_dir)
        files = list(output_dir.glob("*.png")) + list(output_dir.glob("*.html")) + list(output_dir.glob("*.json")) + list(output_dir.glob("*.md"))
        for file_path in sorted(files):
            print(f"   ├── {file_path.name}")
        
        print(f"\n🎯 Key Visualizations:")
        if (output_dir / "simulation_dashboard.png").exists():
            print(f"   ├── 📊 Main Dashboard: simulation_dashboard.png")
        if (output_dir / "executive_dashboard.png").exists():
            print(f"   ├── 👔 Executive Dashboard: executive_dashboard.png")
        if (output_dir / "interactive_dashboard.html").exists():
            print(f"   ├── 🎯 Interactive Dashboard: interactive_dashboard.html")
        if (output_dir / "comprehensive_report.md").exists():
            print(f"   └── 📋 Comprehensive Report: comprehensive_report.md")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Comprehensive Cross-Zone Blockchain Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --scenario medium_district --duration 600
  %(prog)s --scenario large_city --duration 1200 --all-visualizations
  %(prog)s --help
        """
    )
    
    # Basic simulation parameters
    parser.add_argument('--scenario', type=str, default='medium_district',
                        choices=['small_campus', 'medium_district', 'large_city'],
                        help='Simulation scenario')
    parser.add_argument('--duration', type=int, default=600,
                        help='Simulation duration in seconds')
    parser.add_argument('--output-dir', type=str, default='results',
                        help='Output directory for results')
    
    # Visualization options
    parser.add_argument('--executive-dashboard', action='store_true',
                        help='Generate executive dashboard')
    parser.add_argument('--interactive-plots', action='store_true',
                        help='Generate interactive Plotly dashboard')
    parser.add_argument('--publication-plots', action='store_true',
                        help='Generate publication-ready plots')
    parser.add_argument('--all-visualizations', action='store_true',
                        help='Generate all visualization types')
    
    # Debug options
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--quick-test', action='store_true',
                        help='Run quick test (60 seconds)')
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Enable all visualizations if requested
    if args.all_visualizations:
        args.executive_dashboard = True
        args.interactive_plots = True
        args.publication_plots = True
    
    # Quick test mode
    if args.quick_test:
        args.duration = 60
        args.scenario = 'small_campus'
        print("🚀 Quick test mode: 60 seconds, small campus scenario")
    
    # Create and run simulation
    runner = SimulationRunner(args)
    success = runner.run_complete_simulation()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 
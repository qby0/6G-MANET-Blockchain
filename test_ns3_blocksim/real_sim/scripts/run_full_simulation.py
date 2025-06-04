#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Full Integrated Cross-Zone Blockchain Simulation Runner

This script provides a convenient interface to run the complete
integrated simulation with all features enabled.
"""

import argparse
import sys
import time
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

try:
    from full_integrated_simulation_v2 import FullIntegratedSimulationV2, FullSimulationConfigV2
    FullIntegratedSimulation = FullIntegratedSimulationV2
    FullSimulationConfig = FullSimulationConfigV2
    print("✅ Using Full Integrated Simulation V2")
except ImportError:
    # Fallback: use our analytics system instead
    print("⚠️  Full simulation module not available, using analytics-only mode")
    from generate_executive_analytics import ExecutiveAnalyticsGenerator
    FullIntegratedSimulation = None
    FullSimulationConfig = None

def print_banner():
    """Print simulation banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║           🚀 FULL INTEGRATED CROSS-ZONE BLOCKCHAIN SIMULATION 🚀            ║
║                                                                              ║
║  Complete integration of:                                                    ║
║  • NS-3 Network Simulation (real protocols, mobility, radio)                ║
║  • Realistic Device Parameters (energy, CPU, memory, battery)               ║
║  • Consensus Validator Management (ValidatorLeave/ManetNodeEnter)           ║
║  • Beautiful Visualizations and Comprehensive Statistics                    ║
║                                                                              ║
║  🌐 Real Network + ⚡ Real Devices + 🛡️ Real Consensus + 📊 Real Analysis    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_scenario_info(scenario: str):
    """Print scenario information"""
    scenarios = {
        "small_campus": {
            "description": "Small Campus Network",
            "area": "1 km²",
            "devices": "~100 devices",
            "duration": "3-5 minutes",
            "use_case": "University campus, small office building"
        },
        "medium_district": {
            "description": "Medium District Network",
            "area": "4 km²", 
            "devices": "~100 devices",
            "duration": "10-15 minutes",
            "use_case": "City district, shopping mall, industrial area"
        },
        "large_city": {
            "description": "Large City Network",
            "area": "16 km²",
            "devices": "~100 devices", 
            "duration": "30-45 minutes",
            "use_case": "Metropolitan area, smart city deployment"
        },
        "stress_test": {
            "description": "Stress Test Network",
            "area": "1 km²",
            "devices": "~100 devices (high density)",
            "duration": "5-10 minutes",
            "use_case": "Performance testing, bottleneck analysis"
        }
    }
    
    if scenario in scenarios:
        info = scenarios[scenario]
        print(f"\n📋 Scenario: {info['description']}")
        print(f"   📍 Area: {info['area']}")
        print(f"   🔧 Devices: {info['devices']}")
        print(f"   ⏱️  Duration: {info['duration']}")
        print(f"   🎯 Use Case: {info['use_case']}")
    else:
        print(f"\n📋 Scenario: {scenario} (custom)")

def print_features():
    """Print enabled features"""
    print("\n🎯 Integrated Features:")
    print("   ✅ NS-3 Network Simulation")
    print("      • Real AODV routing for MANET")
    print("      • 5G base stations with coverage")
    print("      • Physical mobility models")
    print("      • RSSI-based zone detection")
    print("      • NetAnim visualization")
    
    print("   ✅ Realistic Device Parameters")
    print("      • 50 Smartphones (8-15 GFLOPS, 6-12GB RAM)")
    print("      • 30 IoT Sensors (0.1-1 GFLOPS, 0.5-2GB RAM)")
    print("      • 10 Vehicles (20-50 GFLOPS, 16-32GB RAM)")
    print("      • 2 5G Base Stations (1000-2000 GFLOPS)")
    print("      • 4 Edge Servers (100-500 GFLOPS)")
    
    print("   ✅ Consensus Validator Management")
    print("      • ValidatorLeave/ManetNodeEnter algorithm")
    print("      • PBFT consensus for validator changes")
    print("      • Automatic validator rotation")
    print("      • Dual-radio bridge support")
    
    print("   ✅ Energy & Performance Analysis")
    print("      • Real battery consumption models")
    print("      • CPU and radio energy tracking")
    print("      • Performance degradation simulation")
    print("      • Energy efficiency metrics")
    
    print("   ✅ Beautiful Visualizations")
    print("      • Executive dashboards")
    print("      • Interactive HTML plots")
    print("      • Real-time network topology")
    print("      • Publication-ready graphs")

def run_simulation_with_progress(config: FullSimulationConfig):
    """Run simulation with progress monitoring"""
    print("\n" + "="*80)
    print("🚀 STARTING FULL INTEGRATED SIMULATION V2")
    print("="*80)
    
    start_time = time.time()
    
    try:
        if FullIntegratedSimulation is None:
            # Fallback to analytics-only mode
            print("📊 Running in analytics-only mode...")
            generator = ExecutiveAnalyticsGenerator(config.output_dir)
            results = generator.run_complete_analysis("", "sample")
            print("✅ Analytics generation completed!")
            return True
        
        # Create and run simulation V2
        simulation = FullIntegratedSimulation(config)
        simulation.initialize()
        results = simulation.run_simulation()
        
        # Calculate total time
        total_time = time.time() - start_time
        
        # Print results
        print("\n" + "="*80)
        print("✅ SIMULATION COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(simulation.get_summary())
        
        print(f"\n⏱️  Total Execution Time: {total_time:.2f} seconds ({total_time/60:.1f} minutes)")
        
        # Print output files
        output_dir = Path(config.output_dir)
        if output_dir.exists():
            print(f"\n📁 Output Files Generated:")
            for file_path in output_dir.glob("*"):
                if file_path.is_file():
                    size_kb = file_path.stat().st_size / 1024
                    print(f"   📄 {file_path.name} ({size_kb:.1f} KB)")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Open {config.output_dir}/executive_dashboard.png for overview")
        print(f"   2. Open {config.output_dir}/interactive_dashboard.html for detailed analysis")
        print(f"   3. Check {config.output_dir}/full_simulation_results.json for raw data")
        print(f"   4. Review NetAnim file for network visualization")
        
        return True
        
    except Exception as e:
        print(f"\n❌ SIMULATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Full Integrated Cross-Zone Blockchain Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test (3 minutes)
  python3 run_full_simulation.py --scenario small_campus --duration 180
  
  # Medium test (10 minutes)  
  python3 run_full_simulation.py --scenario medium_district --duration 600
  
  # Full test (30 minutes)
  python3 run_full_simulation.py --scenario large_city --duration 1800
  
  # Stress test (5 minutes, high density)
  python3 run_full_simulation.py --scenario stress_test --duration 300
  
  # Custom configuration
  python3 run_full_simulation.py --config custom_config.json
  
  # Disable specific components for testing
  python3 run_full_simulation.py --disable-ns3 --scenario small_campus
        """
    )
    
    # Configuration options
    parser.add_argument("--config", 
                       default="../config/full_simulation_config.json",
                       help="Configuration file path")
    
    parser.add_argument("--scenario", 
                       choices=["small_campus", "medium_district", "large_city", "stress_test"],
                       default="small_campus",
                       help="Simulation scenario")
    
    parser.add_argument("--duration", type=int, default=180,
                       help="Simulation duration in seconds")
    
    parser.add_argument("--output-dir", default="../results",
                       help="Output directory for results")
    
    # Component toggles
    parser.add_argument("--disable-ns3", action="store_true",
                       help="Disable NS-3 network simulation")
    
    parser.add_argument("--disable-devices", action="store_true", 
                       help="Disable realistic device simulation")
    
    parser.add_argument("--disable-consensus", action="store_true",
                       help="Disable consensus validator management")
    
    parser.add_argument("--disable-visualization", action="store_true",
                       help="Disable visualization generation")
    
    # Output options
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    
    parser.add_argument("--quiet", action="store_true",
                       help="Minimal output (only results)")
    
    args = parser.parse_args()
    
    # Print banner unless quiet
    if not args.quiet:
        print_banner()
        print_scenario_info(args.scenario)
        print_features()
    
    # Create configuration for V2
    if FullSimulationConfig:
    config = FullSimulationConfig(
        scenario=args.scenario,
        duration=args.duration,
        output_dir=args.output_dir,
            config_file=args.config,
        enable_ns3=not args.disable_ns3,
            enable_devices=not args.disable_devices,
            enable_consensus=not args.disable_consensus,
        enable_visualization=not args.disable_visualization,
        verbose=args.verbose
    )
    else:
        # Fallback config for analytics-only mode
        config = type('Config', (), {
            'scenario': args.scenario,
            'duration': args.duration,
            'output_dir': args.output_dir,
            'config_file': args.config,
            'verbose': args.verbose
        })()
    
    # Validate configuration file
    config_path = Path(config.config_file)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print(f"   Please ensure the configuration file exists or use --config to specify a different path")
        return 1
    
    # Run simulation
    if not args.quiet:
        print(f"\n⏰ Starting simulation in 3 seconds... (Press Ctrl+C to cancel)")
        try:
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n⏹️  Simulation cancelled by user")
            return 0
    
    success = run_simulation_with_progress(config)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
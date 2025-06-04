#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Executive Analytics Generator for Cross-Zone Blockchain Network Simulation

This script integrates the analytics engine and visualization components
to generate comprehensive executive-level reports and dashboards for the
real_sim blockchain simulation.

Features:
- Comprehensive statistical analysis
- Professional executive dashboards
- Interactive HTML visualizations
- Energy consumption analysis
- Network topology visualization
- Performance recommendations

Usage:
    python3 generate_executive_analytics.py --data-dir ../results
    python3 generate_executive_analytics.py --simulation-data sample_data.json
    python3 generate_executive_analytics.py --live-analysis

Author: Advanced Blockchain Research Team
Version: 1.0.0
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

# Add parent directories to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "src"))

# Import our custom modules
try:
    from executive_dashboard_analyzer import ExecutiveDashboardAnalyzer, load_simulation_data
    from dashboard_visualizer import DashboardVisualizer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExecutiveAnalyticsGenerator:
    """
    Main class for generating executive analytics and dashboards
    """
    
    def __init__(self, output_dir: str = "results"):
        """Initialize the analytics generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.analyzer: Optional[ExecutiveDashboardAnalyzer] = None
        self.visualizer: Optional[DashboardVisualizer] = None
        
        logger.info(f"Executive Analytics Generator initialized with output: {self.output_dir}")
    
    def load_data_from_directory(self, data_dir: str) -> Dict[str, Any]:
        """Load simulation data from directory"""
        logger.info(f"Loading simulation data from: {data_dir}")
        
        try:
            simulation_data = load_simulation_data(data_dir)
            
            if not simulation_data:
                logger.warning("No simulation data found, generating sample data")
                simulation_data = self._generate_sample_data()
            
            logger.info(f"Loaded data with {len(simulation_data)} datasets")
            return simulation_data
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            logger.info("Generating sample data for demonstration")
            return self._generate_sample_data()
    
    def load_data_from_file(self, data_file: str) -> Dict[str, Any]:
        """Load simulation data from JSON file"""
        logger.info(f"Loading simulation data from file: {data_file}")
        
        try:
            with open(data_file, 'r') as f:
                simulation_data = json.load(f)
            
            logger.info("Successfully loaded simulation data from file")
            return simulation_data
            
        except Exception as e:
            logger.error(f"Failed to load data from file: {e}")
            logger.info("Generating sample data for demonstration")
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate realistic sample data for demonstration"""
        logger.info("Generating realistic sample simulation data...")
        
        np.random.seed(42)  # For reproducible results
        
        # Generate device data based on correct network architecture
        device_types = ['smartphone', 'iot_sensor', 'vehicle', 'base_station_6g', 'edge_server']
        
        # Обновленная конфигурация зон с новыми названиями
        zone_config = {
            '5G_Zone': {'count': 15, 'validator_ratio': 0.53},      # 8 out of 15 are validators
            'Bridge_Zone': {'count': 20, 'validator_ratio': 0.0},   # No validators outside 5G zone
            'MANET_Zone': {'count': 33, 'validator_ratio': 0.0}     # No validators in MANET zone
        }
        
        devices_list = []  # Изменяем на список для совместимости с новым анализатором
        device_id = 0
        
        for zone, config in zone_config.items():
            for i in range(config['count']):
                # Select device type based on zone characteristics
                if zone == '5G_Zone':
                    # 5G zone has more powerful devices and base stations
                    device_type = device_types[np.random.choice([2, 3, 4], p=[0.4, 0.3, 0.3])]  # vehicles, base_stations, edge_servers
                elif zone == 'Bridge_Zone':
                    # Bridge zone has mixed devices
                    device_type = device_types[np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2])]  # smartphones, iot, vehicles
                else:  # MANET_Zone
                    # MANET zone has mostly mobile devices
                    device_type = device_types[np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])]  # mostly smartphones and iot
                
                # Determine if device is validator (only in 5G zone)
                is_validator = (zone == '5G_Zone' and i < int(config['count'] * config['validator_ratio']))
                
                # Realistic device parameters based on type and zone
                if device_type == 'smartphone':
                    battery_level = np.random.uniform(30, 95)
                    energy_consumed = np.random.uniform(50, 200)
                    transactions = np.random.randint(5, 25)
                    blocks = np.random.randint(0, 3) if is_validator else 0
                elif device_type == 'iot_sensor':
                    battery_level = np.random.uniform(60, 100)
                    energy_consumed = np.random.uniform(10, 50)
                    transactions = np.random.randint(1, 10)
                    blocks = np.random.randint(0, 1) if is_validator else 0
                elif device_type == 'vehicle':
                    battery_level = np.random.uniform(70, 100)
                    energy_consumed = np.random.uniform(100, 400)
                    transactions = np.random.randint(10, 40)
                    blocks = np.random.randint(1, 8) if is_validator else 0
                elif device_type == 'base_station_6g':
                    battery_level = 100  # Grid connected
                    energy_consumed = np.random.uniform(500, 1500)
                    transactions = np.random.randint(20, 60)
                    blocks = np.random.randint(3, 15) if is_validator else 0
                else:  # edge_server
                    battery_level = 100  # Grid connected
                    energy_consumed = np.random.uniform(300, 800)
                    transactions = np.random.randint(15, 45)
                    blocks = np.random.randint(2, 10) if is_validator else 0
                
                # Boost validator performance
                if is_validator:
                    transactions = int(transactions * 1.5)  # Validators handle more transactions
                    energy_consumed *= 1.3  # Validators consume more energy
                
                device_info = {
                    'device_id': f'device_{device_id}',
                    'device_type': device_type,
                    'current_zone': zone,
                    'battery_level': battery_level,
                    'energy_consumed': energy_consumed,
                    'is_validator': is_validator,
                    'performance_score': np.random.uniform(0.7, 1.0) if is_validator else np.random.uniform(0.5, 0.9),
                    'transactions_sent': transactions,
                    'blocks_validated': blocks,
                    'memory_usage': np.random.uniform(0.3, 0.8),
                    'distance_from_tower': self._calculate_distance_from_tower(zone, i, config['count'])
                }
                
                devices_list.append(device_info)
                device_id += 1
        
        # Generate simulation results
        total_transactions = sum(d['transactions_sent'] for d in devices_list)
        total_blocks = sum(d['blocks_validated'] for d in devices_list)
        total_validators = sum(1 for d in devices_list if d['is_validator'])
        total_energy = sum(d['energy_consumed'] for d in devices_list)
        
        simulation_config = {
            'simulation_duration': 300,  # 5 minutes
            'simulation_time': 300,
            'duration': 300,
            'total_devices': len(devices_list),
            'total_transactions': total_transactions,
            'total_blocks': total_blocks,
            'total_validators': total_validators,
            'total_energy_consumed': total_energy,
            'average_battery': np.mean([d['battery_level'] for d in devices_list]),
            'zone_transitions': np.random.randint(50, 150)  # Realistic zone transitions
        }
        
        # Структура данных совместимая с новым анализатором
        return {
            'devices': devices_list,  # Список устройств
            'simulation_config': simulation_config,
            'network_topology': [],  # Пустой список для совместимости
            'blockchain_metrics': {},  # Пустой словарь для совместимости
            'energy_consumption': []  # Пустой список для совместимости
        }
    
    def _calculate_distance_from_tower(self, zone: str, device_index: int, zone_device_count: int) -> float:
        """Calculate realistic distance from central tower based on zone"""
        # Distance ranges for each zone (in relative units)
        zone_distances = {
            '5G_Zone': (0.02, 0.15),      # Close to tower
            'Bridge_Zone': (0.15, 0.25),  # Medium distance
            'MANET_Zone': (0.25, 0.45)    # Far from tower
        }
        
        min_dist, max_dist = zone_distances.get(zone, (0.1, 0.3))
        
        # Add some randomness but ensure proper distribution
        base_distance = min_dist + (max_dist - min_dist) * (device_index / zone_device_count)
        noise = np.random.uniform(-0.02, 0.02)
        
        return max(min_dist, min(max_dist, base_distance + noise))
    
    def generate_comprehensive_analytics(self, simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analytics from simulation data"""
        logger.info("🔍 Generating comprehensive analytics...")
        
        # Initialize analyzer
        self.analyzer = ExecutiveDashboardAnalyzer(simulation_data)
        
        # Generate complete analytics
        analytics_summary = self.analyzer.generate_executive_summary()
        
        # Save analytics to file
        analytics_file = self.output_dir / "executive_analytics_summary.json"
        with open(analytics_file, 'w') as f:
            json.dump(analytics_summary, f, indent=2, default=str)
        
        logger.info(f"📊 Analytics summary saved: {analytics_file}")
        return analytics_summary
    
    def generate_visualizations(self, analytics_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate all visualizations"""
        logger.info("🎨 Generating comprehensive visualizations...")
        
        # Initialize visualizer
        self.visualizer = DashboardVisualizer(str(self.output_dir))
        
        # Generate all visualizations
        visualization_paths = {}
        
        try:
            # Executive Dashboard
            executive_dashboard = self.visualizer.create_executive_dashboard(analytics_data)
            visualization_paths['executive_dashboard'] = executive_dashboard
            
            # Interactive Dashboard
            interactive_dashboard = self.visualizer.create_interactive_dashboard(analytics_data)
            visualization_paths['interactive_dashboard'] = interactive_dashboard
            
            # Network Topology
            network_topology = self.visualizer.create_network_topology_visualization(analytics_data)
            visualization_paths['network_topology'] = network_topology
            
            logger.info("✅ All visualizations generated successfully")
            
        except Exception as e:
            logger.error(f"Visualization generation failed: {e}")
            import traceback
            traceback.print_exc()
        
        return visualization_paths
    
    def generate_executive_report(self, analytics_data: Dict[str, Any]) -> str:
        """Generate executive text report"""
        logger.info("📝 Generating executive report...")
        
        # Extract key metrics
        overview = analytics_data['simulation_overview']
        kpis = analytics_data['key_performance_indicators']
        network_health = analytics_data['network_health']
        energy_efficiency = analytics_data['energy_efficiency']
        recommendations = analytics_data['recommendations']
        
        # Generate report
        report = f"""
# Cross-Zone Blockchain Network Executive Report

## Executive Summary
- **Total Devices**: {overview['total_devices']}
- **Simulation Duration**: {overview['simulation_duration']} seconds
- **Overall Performance Rating**: {overview['overall_performance_rating']}
- **Network Health Score**: {network_health['score']:.1f}/100
- **Energy Efficiency**: {energy_efficiency['efficiency_percentage']:.1f}%

## Key Performance Indicators

### Device Metrics
- **Total Devices**: {kpis['devices']['total']}
- **Active Devices**: {kpis['devices']['active']}
- **Device Utilization**: {kpis['devices']['utilization_rate']:.1f}%

### Transaction Metrics
- **Total Transactions**: {kpis['transactions']['total']}
- **Confirmed Transactions**: {kpis['transactions']['confirmed']}
- **Success Rate**: {kpis['transactions']['success_rate']:.1f}%
- **Throughput**: {kpis['transactions']['throughput_per_minute']:.1f} tx/min

### Block Metrics
- **Total Blocks**: {kpis['blocks']['total']}
- **Average Block Time**: {kpis['blocks']['average_block_time']:.2f} seconds
- **Block Rate**: {kpis['blocks']['blocks_per_minute']:.1f} blocks/min

## Network Health Analysis
- **Network Health Score**: {network_health['score']:.1f}/100
- **Network Uptime**: {network_health['uptime']:.1f}%
- **Zone Connectivity**: {network_health['zone_connectivity']:.1f}%
- **Validator Availability**: {network_health['validator_availability']:.1f}%

## Energy Efficiency Analysis
- **Energy Efficiency Score**: {energy_efficiency['efficiency_percentage']:.1f}%
- **Total Energy Consumption**: {energy_efficiency['total_consumption_mj']:.1f} mJ
- **Energy per Transaction**: {energy_efficiency['energy_per_transaction']:.2f} mJ
- **Battery Efficiency**: {energy_efficiency['battery_efficiency']:.1f}%

## Recommendations
"""
        
        for i, recommendation in enumerate(recommendations, 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""
## Technical Details
- **Consensus Algorithm**: PBFT with ValidatorLeave/ManetNodeEnter
- **Network Zones**: 5G, MANET, Bridge
- **Device Types**: Smartphones, IoT Sensors, Vehicles, Base Stations, Edge Servers
- **Simulation Framework**: NS-3 + Realistic Device Models

---
*Report generated by Cross-Zone Blockchain Network Executive Analytics*
*Timestamp: {analytics_data.get('timestamp', 'N/A')}*
"""
        
        # Save report
        report_file = self.output_dir / "executive_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"📄 Executive report saved: {report_file}")
        return str(report_file)
    
    def run_complete_analysis(self, data_source: str, source_type: str = "directory") -> Dict[str, Any]:
        """Run complete analytics pipeline"""
        logger.info("🚀 Starting complete executive analytics pipeline...")
        
        # Load data
        if source_type == "directory":
            simulation_data = self.load_data_from_directory(data_source)
        elif source_type == "file":
            simulation_data = self.load_data_from_file(data_source)
        else:
            simulation_data = self._generate_sample_data()
        
        # Generate analytics
        analytics_data = self.generate_comprehensive_analytics(simulation_data)
        
        # Generate visualizations
        visualization_paths = self.generate_visualizations(analytics_data)
        
        # Generate executive report
        report_path = self.generate_executive_report(analytics_data)
        
        # Create summary
        results = {
            'analytics_data': analytics_data,
            'visualization_paths': visualization_paths,
            'report_path': report_path,
            'output_directory': str(self.output_dir)
        }
        
        # Print summary
        self._print_completion_summary(results)
        
        return results
    
    def _print_completion_summary(self, results: Dict[str, Any]):
        """Print completion summary"""
        print("\n" + "="*80)
        print("🎉 EXECUTIVE ANALYTICS GENERATION COMPLETED")
        print("="*80)
        
        analytics = results['analytics_data']['simulation_overview']
        print(f"📊 Network Health Score: {results['analytics_data']['network_health']['score']:.1f}/100")
        print(f"⚡ Energy Efficiency: {results['analytics_data']['energy_efficiency']['efficiency_percentage']:.1f}%")
        print(f"🎯 Overall Rating: {analytics['overall_performance_rating']}")
        
        print(f"\n📁 Output Directory: {results['output_directory']}")
        print(f"📄 Executive Report: {results['report_path']}")
        
        print(f"\n🎨 Generated Visualizations:")
        for viz_type, path in results['visualization_paths'].items():
            print(f"   • {viz_type.replace('_', ' ').title()}: {Path(path).name}")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Review executive report: {Path(results['report_path']).name}")
        print(f"   2. Open executive dashboard: {Path(results['visualization_paths'].get('executive_dashboard', '')).name}")
        print(f"   3. Explore interactive dashboard: {Path(results['visualization_paths'].get('interactive_dashboard', '')).name}")
        print(f"   4. Analyze energy consumption: {Path(results['visualization_paths'].get('energy_heatmap', '')).name}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generate Executive Analytics for Cross-Zone Blockchain Network Simulation"
    )
    
    parser.add_argument("--data-dir", type=str, default="../results",
                       help="Directory containing simulation data files")
    
    parser.add_argument("--data-file", type=str,
                       help="Specific JSON file containing simulation data")
    
    parser.add_argument("--output-dir", type=str, default="../results/executive_analytics",
                       help="Output directory for analytics and visualizations")
    
    parser.add_argument("--sample-data", action="store_true",
                       help="Generate analytics using sample data")
    
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print banner
    print("🚀 Cross-Zone Blockchain Network Executive Analytics Generator")
    print("=" * 70)
    
    try:
        # Initialize generator
        generator = ExecutiveAnalyticsGenerator(args.output_dir)
        
        # Determine data source
        if args.sample_data:
            results = generator.run_complete_analysis("", "sample")
        elif args.data_file:
            results = generator.run_complete_analysis(args.data_file, "file")
        else:
            results = generator.run_complete_analysis(args.data_dir, "directory")
        
        return 0
        
    except Exception as e:
        logger.error(f"Analytics generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 
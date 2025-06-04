#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for realistic device parameters demonstration

This script shows how to use the realistic device manager and demonstrates
various device capabilities and simulation scenarios.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.realistic_device_manager import RealisticDeviceManager, DeviceCapabilities, NetworkConditions

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_device_creation():
    """Test creating devices with realistic parameters"""
    print("\n" + "="*60)
    print("🔧 TESTING DEVICE CREATION")
    print("="*60)
    
    device_manager = RealisticDeviceManager()
    
    # Create different types of devices
    device_types = ["smartphone", "iot_sensor", "vehicle", "base_station_5g", "edge_server"]
    devices = []
    
    for device_type in device_types:
        device = device_manager.create_device(device_type)
        devices.append(device)
        
        print(f"\n📱 {device_type.upper()}: {device.device_id}")
        print(f"   CPU: {device.cpu_performance:.1f} GFLOPS")
        print(f"   RAM: {device.ram_gb:.1f} GB")
        print(f"   Battery: {device.battery_mah:,} mAh")
        print(f"   Signatures/sec: {device.signatures_per_sec:,}")
        print(f"   Stake Weight: {device.stake_weight}")
        print(f"   Max Speed: {device.max_speed_kmh} km/h")
        print(f"   Interfaces: {', '.join(device.network_interfaces)}")
    
    return devices

def test_energy_consumption(device_manager, devices):
    """Test energy consumption calculations"""
    print("\n" + "="*60)
    print("⚡ TESTING ENERGY CONSUMPTION")
    print("="*60)
    
    operations = ["idle", "cpu_active", "wifi_tx", "5g_tx", "consensus"]
    duration = 60.0  # 60 seconds
    
    for device in devices[:3]:  # Test first 3 devices
        print(f"\n🔋 Energy consumption for {device.device_id}:")
        total_energy = 0
        
        for operation in operations:
            energy = device_manager.calculate_energy_consumption(
                device.device_id, operation, duration
            )
            print(f"   {operation:12}: {energy:8.1f} mJ/min")
            total_energy += energy
        
        print(f"   {'TOTAL':12}: {total_energy:8.1f} mJ/min")

def test_battery_lifetime(device_manager, devices):
    """Test battery lifetime estimation"""
    print("\n" + "="*60)
    print("🔋 TESTING BATTERY LIFETIME")
    print("="*60)
    
    # Different usage patterns
    usage_patterns = {
        "light_user": {"idle": 0.9, "cpu_active": 0.05, "wifi_tx": 0.05},
        "normal_user": {"idle": 0.7, "cpu_active": 0.2, "wifi_tx": 0.1},
        "heavy_user": {"idle": 0.5, "cpu_active": 0.3, "wifi_tx": 0.15, "5g_tx": 0.05},
        "validator": {"idle": 0.4, "cpu_active": 0.4, "wifi_tx": 0.15, "consensus": 0.05}
    }
    
    for device in devices[:3]:  # Test mobile devices
        if device.device_type in ["smartphone", "iot_sensor"]:
            print(f"\n📱 Battery lifetime for {device.device_id}:")
            for pattern_name, pattern in usage_patterns.items():
                lifetime = device_manager.estimate_battery_lifetime(device.device_id, pattern)
                print(f"   {pattern_name:12}: {lifetime:6.1f} hours")

def test_consensus_participation(device_manager, devices):
    """Test consensus participation capabilities"""
    print("\n" + "="*60)
    print("🤝 TESTING CONSENSUS PARTICIPATION")
    print("="*60)
    
    consensus_rounds = [1, 50, 99]  # Different consensus complexity levels
    
    for round_num in consensus_rounds:
        print(f"\n🔄 Consensus Round {round_num}:")
        print("-" * 40)
        
        for device in devices:
            requirements = device_manager.get_consensus_requirements(device.device_id, round_num)
            
            if requirements:
                can_participate = requirements["capabilities"]["can_participate"]
                score = requirements["participation_score"]
                energy_cost = requirements["requirements"]["energy_cost_mj"]
                
                status = "✅ YES" if can_participate else "❌ NO"
                print(f"   {device.device_id:20} {status} Score:{score:5.1f} Energy:{energy_cost:6.1f}mJ")

def test_zone_transitions(device_manager, devices):
    """Test zone transition costs"""
    print("\n" + "="*60)
    print("🌐 TESTING ZONE TRANSITIONS")
    print("="*60)
    
    transitions = [
        ("manet", "bridge"),
        ("bridge", "5g"),
        ("5g", "manet")
    ]
    
    for device in devices[:4]:  # Test different device types
        print(f"\n📡 Zone transitions for {device.device_id}:")
        for from_zone, to_zone in transitions:
            cost = device_manager.get_zone_transition_cost(device.device_id, from_zone, to_zone)
            print(f"   {from_zone:6} → {to_zone:6}: "
                  f"Energy:{cost['energy_mj']:5.1f}mJ "
                  f"Latency:{cost['latency_ms']:5.1f}ms "
                  f"Success:{cost['success_probability']:.2f}")

def test_performance_scaling(device_manager):
    """Test performance scaling under load"""
    print("\n" + "="*60)
    print("📈 TESTING PERFORMANCE SCALING")
    print("="*60)
    
    device_types = ["smartphone", "iot_sensor", "base_station_5g"]
    metrics = ["throughput", "latency", "energy"]
    load_levels = [0.0, 0.3, 0.6, 0.9, 1.0]
    
    for device_type in device_types:
        print(f"\n📊 Performance scaling for {device_type}:")
        print("   Load:    " + "".join(f"{load:8.1f}" for load in load_levels))
        
        for metric in metrics:
            print(f"   {metric:8}: ", end="")
            for load in load_levels:
                scaling = device_manager.get_performance_scaling(device_type, metric, load)
                print(f"{scaling:8.2f}", end="")
            print()

def test_simulation_scenarios(device_manager):
    """Test predefined simulation scenarios"""
    print("\n" + "="*60)
    print("🎯 TESTING SIMULATION SCENARIOS")
    print("="*60)
    
    scenarios = ["small_campus", "medium_district", "large_city"]
    
    for scenario_name in scenarios:
        scenario = device_manager.generate_simulation_scenario(scenario_name)
        
        print(f"\n📍 Scenario: {scenario_name}")
        print(f"   Area: {scenario['area_km2']} km²")
        print(f"   Duration: {scenario['simulation_time_sec']} seconds")
        print(f"   Environment: {scenario['environment']}")
        print(f"   Total devices: {scenario['total_devices']}")
        
        # Show device distribution
        device_counts = {}
        for device_info in scenario['devices']:
            device_type = device_info['device_type']
            device_counts[device_type] = device_counts.get(device_type, 0) + 1
        
        print("   Device distribution:")
        for device_type, count in device_counts.items():
            print(f"     {device_type:15}: {count:3d}")

def test_environment_conditions(device_manager):
    """Test environment conditions"""
    print("\n" + "="*60)
    print("🌍 TESTING ENVIRONMENT CONDITIONS")
    print("="*60)
    
    environments = ["urban_dense", "urban_normal", "suburban", "rural"]
    
    for env_type in environments:
        conditions = device_manager.get_environment_conditions(env_type)
        
        print(f"\n🏙️  {env_type}:")
        print(f"   Interference: {conditions.interference_level:.1f} dBm")
        print(f"   Path Loss Exp: {conditions.path_loss_exponent:.1f}")
        print(f"   Node Density: {conditions.node_density:,}/km²")
        print(f"   Signal Strength: {conditions.signal_strength:.1f} dBm")

def display_device_stats(device_manager):
    """Display overall device statistics"""
    print("\n" + "="*60)
    print("📊 DEVICE STATISTICS SUMMARY")
    print("="*60)
    
    stats = device_manager.get_device_stats()
    
    print(f"\n📈 Total devices created: {stats['total_devices']}")
    print(f"📈 Total compute power: {stats['total_compute_gflops']:.1f} GFLOPS")
    print(f"📈 Total signature capacity: {stats['total_signatures_per_sec']:,}/sec")
    print(f"📈 Average battery: {stats['avg_battery_mah']:.0f} mAh")
    
    print("\n📊 Device distribution:")
    for device_type, count in stats['by_type'].items():
        print(f"   {device_type:15}: {count:3d}")

def save_sample_config():
    """Save a sample configuration for reference"""
    print("\n" + "="*60)
    print("💾 SAVING SAMPLE CONFIGURATION")
    print("="*60)
    
    device_manager = RealisticDeviceManager()
    scenario = device_manager.generate_simulation_scenario("medium_district")
    
    output_path = Path(__file__).parent.parent / "results" / "sample_realistic_scenario.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(scenario, f, indent=2, default=str)
    
    print(f"✅ Sample scenario saved to: {output_path}")

def main():
    """Main test function"""
    print("🚀 REALISTIC DEVICE PARAMETERS TEST")
    print("🎯 Testing Cross-Zone Blockchain Device Capabilities")
    
    try:
        # Create device manager
        device_manager = RealisticDeviceManager()
        
        # Run tests
        devices = test_device_creation()
        test_energy_consumption(device_manager, devices)
        test_battery_lifetime(device_manager, devices)
        test_consensus_participation(device_manager, devices)
        test_zone_transitions(device_manager, devices)
        test_performance_scaling(device_manager)
        test_simulation_scenarios(device_manager)
        test_environment_conditions(device_manager)
        display_device_stats(device_manager)
        save_sample_config()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎉 Realistic device parameters are working correctly!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logger.exception("Test failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Test for Full Integrated Cross-Zone Blockchain Simulation

This script performs a quick test to verify that all components
of the integrated simulation are working correctly.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import numpy as np
        print("   ✅ numpy")
    except ImportError:
        print("   ❌ numpy - install with: pip3 install numpy")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("   ✅ matplotlib")
    except ImportError:
        print("   ❌ matplotlib - install with: pip3 install matplotlib")
        return False
    
    try:
        import pandas as pd
        print("   ✅ pandas")
    except ImportError:
        print("   ❌ pandas - install with: pip3 install pandas")
        return False
    
    try:
        from test_ns3_blocksim.real_sim.src.old_full_integrated_simulation import FullIntegratedSimulation, FullSimulationConfig
        print("   ✅ full_integrated_simulation")
    except ImportError as e:
        print(f"   ❌ full_integrated_simulation - {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    config_file = project_root / "config" / "full_simulation_config.json"
    if not config_file.exists():
        print(f"   ❌ Configuration file not found: {config_file}")
        return False
    
    try:
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        print("   ✅ Configuration file loaded successfully")
        print(f"   📋 Simulation: {config['simulation_name']}")
        return True
    except Exception as e:
        print(f"   ❌ Configuration loading failed: {e}")
        return False

def test_device_manager():
    """Test realistic device manager"""
    print("\n⚡ Testing device manager...")
    
    try:
        # Import from parent project
        sys.path.insert(0, str(project_root.parent))
        from models.realistic_device_manager import RealisticDeviceManager
        
        device_manager = RealisticDeviceManager()
        print("   ✅ Device manager created")
        
        # Test device creation with proper parameters
        custom_params = {
            "hardware": {
                "cpu_performance_gflops": 10.0,
                "ram_gb": 8
            },
            "power": {
                "battery_mah": 4000
            },
            "blockchain": {
                "signatures_per_sec": 100,
                "stake_weight": 1.0
            }
        }
        
        device_capabilities = device_manager.create_device("smartphone", custom_params)
        print("   ✅ Test device created")
        print(f"   📱 Device ID: {device_capabilities.device_id}")
        print(f"   ⚡ CPU: {device_capabilities.cpu_performance} GFLOPS")
        print(f"   🔋 Battery: {device_capabilities.battery_mah} mAh")
        
        return True
    except Exception as e:
        print(f"   ❌ Device manager test failed: {e}")
        return False

def test_ns3_path():
    """Test NS-3 path"""
    print("\n🌐 Testing NS-3 path...")
    
    ns3_path = project_root.parent / "external" / "ns-3"
    if not ns3_path.exists():
        print(f"   ❌ NS-3 directory not found: {ns3_path}")
        print("   💡 Please ensure NS-3 is installed in external/ns-3")
        return False
    
    ns3_script = ns3_path / "ns3"
    if not ns3_script.exists():
        print(f"   ❌ NS-3 script not found: {ns3_script}")
        print("   💡 Please build NS-3 first")
        return False
    
    print("   ✅ NS-3 directory found")
    print("   ✅ NS-3 script found")
    return True

def test_simulation_creation():
    """Test simulation object creation"""
    print("\n🚀 Testing simulation creation...")
    
    try:
        from test_ns3_blocksim.real_sim.src.old_full_integrated_simulation import FullIntegratedSimulation, FullSimulationConfig
        
        config = FullSimulationConfig(
            config_file="../config/full_simulation_config.json",
            scenario="small_campus",
            duration=60,  # 1 minute test
            output_dir="../results/quick_test",
            enable_ns3=False,  # Disable NS-3 for quick test
            enable_realistic_devices=True,
            enable_consensus_validators=False,  # Disable consensus for quick test
            enable_visualization=False,  # Disable visualization for quick test
            verbose=True
        )
        
        simulation = FullIntegratedSimulation(config)
        print("   ✅ Simulation object created")
        
        return True
    except Exception as e:
        print(f"   ❌ Simulation creation failed: {e}")
        return False

def run_mini_simulation():
    """Run a minimal simulation test"""
    print("\n🎯 Running mini simulation test...")
    
    try:
        from test_ns3_blocksim.real_sim.src.old_full_integrated_simulation import FullIntegratedSimulation, FullSimulationConfig
        
        # Create minimal configuration
        config = FullSimulationConfig(
            config_file="../config/full_simulation_config.json",
            scenario="small_campus",
            duration=30,  # 30 seconds
            output_dir="../results/mini_test",
            enable_ns3=False,  # Disable NS-3
            enable_realistic_devices=True,
            enable_consensus_validators=False,  # Disable consensus
            enable_visualization=False,  # Disable visualization
            verbose=False
        )
        
        print("   🔄 Starting mini simulation (30 seconds)...")
        start_time = time.time()
        
        simulation = FullIntegratedSimulation(config)
        results = simulation.run_simulation()
        
        duration = time.time() - start_time
        print(f"   ✅ Mini simulation completed in {duration:.2f} seconds")
        
        if results:
            print(f"   📊 Results: {results.total_devices} devices, {results.total_transactions} transactions")
        
        return True
    except Exception as e:
        print(f"   ❌ Mini simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Full Integrated Simulation - Quick Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Device Manager Test", test_device_manager),
        ("NS-3 Path Test", test_ns3_path),
        ("Simulation Creation Test", test_simulation_creation),
        ("Mini Simulation Test", run_mini_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The simulation is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Run: python3 run_full_simulation.py --scenario small_campus --duration 180")
        print("   2. Check results in ../results/ directory")
        print("   3. Open generated dashboards and visualizations")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the full simulation.")
        print("\n🔧 Common fixes:")
        print("   1. Install missing dependencies: pip3 install -r requirements.txt")
        print("   2. Ensure NS-3 is built: cd ../external/ns-3 && python3 ns3 build")
        print("   3. Check configuration file exists: config/full_simulation_config.json")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
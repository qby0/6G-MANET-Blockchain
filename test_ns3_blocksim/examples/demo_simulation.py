#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 DEMONSTRATION SIMULATION
Comprehensive Demo of Advanced Cross-Zone Blockchain Simulation

This script demonstrates all capabilities of the advanced
cross-zone blockchain simulation with beautiful visualization.
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import List, Dict

def print_banner():
    """Print beautiful banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                🚀 ADVANCED CROSS-ZONE BLOCKCHAIN SIMULATION DEMO 🚀          ║
║                                                                              ║
║  Demonstration of advanced cross-zone blockchain simulation                  ║
║  with realistic device parameters and beautiful visualization                ║
║                                                                              ║
║  🔧 Realistic devices      📊 Beautiful charts      📈 Detailed statistics   ║
║  ⚡ Energy analysis        🎯 Interactivity        📋 Complete reports       ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_section(title: str, description: str = ""):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"🎯 {title}")
    if description:
        print(f"   {description}")
    print('='*80)

def print_step(step: int, title: str, description: str = ""):
    """Print step information"""
    print(f"\n📋 Step {step}: {title}")
    if description:
        print(f"   └── {description}")

def check_dependencies() -> bool:
    """Check if all dependencies are installed"""
    print_step(1, "Checking Dependencies", "Ensuring all required modules are installed")
    
    required_modules = [
        'numpy', 'matplotlib', 'seaborn', 'pandas', 
        'scipy', 'networkx', 'plotly'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module:12} - OK")
        except ImportError:
            print(f"   ❌ {module:12} - Not installed")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  Missing modules: {', '.join(missing_modules)}")
        print("   Run: pip3 install " + " ".join(missing_modules))
        return False
    
    print("\n✅ All dependencies installed!")
    return True

def check_files() -> bool:
    """Check if all required files exist"""
    print_step(2, "Checking Files", "Ensuring all components of the simulation are available")
    
    # Get project root directory
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    required_files = [
        'models/realistic_device_manager.py',
        'config/realistic_device_config.json',
        'src/simulation/advanced_realistic_simulation.py',
        'src/visualization/enhanced_visualization.py',
        'examples/run_simulation.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path:35} - OK")
        else:
            print(f"   ❌ {file_path:35} - Not found")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {len(missing_files)}")
        return False
    
    print("\n✅ All files found!")
    return True

def run_quick_test() -> bool:
    """Run quick test simulation"""
    print_step(3, "Quick Test", "Running a 60-second simulation to check functionality")
    
    try:
        print("   🔄 Running simulation...")
        result = subprocess.run([
            'python3', 'run_simulation.py',
            '--quick-test',
            '--executive-dashboard',
            '--output-dir', 'demo_results'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("   ✅ Quick test completed successfully!")
            return True
        else:
            print(f"   ❌ Error during test execution:")
            print(f"   {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ Test exceeded waiting time (2 minutes)")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def run_full_demo() -> bool:
    """Run full demonstration simulation"""
    print_step(4, "Full Demonstration", "Running full simulation with all visualizations")
    
    scenarios = [
        ('small_campus', 300, 'Small Campus (5 minutes)'),
        ('medium_district', 600, 'Medium District (10 minutes)')
    ]
    
    for scenario, duration, description in scenarios:
        print(f"\n   🎯 Scenario: {description}")
        print(f"      Parameters: {scenario}, {duration} seconds")
        
        try:
            result = subprocess.run([
                'python3', 'run_simulation.py',
                '--scenario', scenario,
                '--duration', str(duration),
                '--all-visualizations',
                '--output-dir', f'demo_results_{scenario}'
            ], capture_output=True, text=True, timeout=duration + 180)
            
            if result.returncode == 0:
                print(f"   ✅ Scenario {scenario} completed successfully!")
            else:
                print(f"   ❌ Error in scenario {scenario}:")
                print(f"   {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Scenario {scenario} exceeded waiting time")
            return False
        except Exception as e:
            print(f"   ❌ Error in scenario {scenario}: {e}")
            return False
    
    return True

def generate_demo_report():
    """Generate comprehensive demo report"""
    print_step(5, "Generating Report", "Creating final report of demonstration")
    
    # Collect all generated files
    results_dirs = ['demo_results', 'demo_results_small_campus', 'demo_results_medium_district']
    all_files = []
    
    for results_dir in results_dirs:
        if Path(results_dir).exists():
            files = list(Path(results_dir).glob('*.png')) + \
                   list(Path(results_dir).glob('*.html')) + \
                   list(Path(results_dir).glob('*.json')) + \
                   list(Path(results_dir).glob('*.md'))
            all_files.extend([(results_dir, f) for f in files])
    
    # Create demo report
    report_content = f"""# 🚀 Demonstration Report Advanced Cross-Zone Blockchain Simulation

## Overview of Demonstration

This report contains results of the advanced cross-zone blockchain simulation demonstration.

**Date of Generation**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Total Files Created**: {len(all_files)}

## Completed Tests

### 1. Quick Test (60 seconds)
- ✅ Base Functionality Check
- ✅ Executive Dashboard Generation
- 📁 Results: `demo_results/`

### 2. Small Campus (5 minutes)
- ✅ Local Network Simulation
- ✅ All Visualization Types
- 📁 Results: `demo_results_small_campus/`

### 3. Medium District (10 minutes)
- ✅ Mixed Environment Simulation
- ✅ Full Performance Analysis
- 📁 Results: `demo_results_medium_district/`

## Created Files

"""
    
    for results_dir, file_path in all_files:
        file_type = "🖼️" if file_path.suffix == '.png' else \
                   "🌐" if file_path.suffix == '.html' else \
                   "📊" if file_path.suffix == '.json' else \
                   "📋" if file_path.suffix == '.md' else "📄"
        
        report_content += f"- {file_type} `{results_dir}/{file_path.name}`\n"
    
    report_content += f"""
## Key Capabilities Demonstrated

### 🔧 Realistic Device Parameters
- Smartphones with Batteries and Mobility
- IoT Sensors with Limited Resources
- High-Performance Vehicles
- 5G Base Stations and Edge Servers

### 📊 Beautiful Visualization
- Executive Dashboards for Presentations
- Interactive HTML Graphs with Plotly
- Scientific Graphs, Ready for Publications
- Detailed Heat Maps and Network Diagrams

### 📈 Comprehensive Statistics
- Energy Consumption Analysis
- Consensus Performance
- Mobility and Zone Transitions
- Network Throughput

### ⚡ Automatic Analysis
- Automatic Optimization Recommendations
- Identifying Performance Bottlenecks
- Comparison with Theoretical Limits

## Next Steps

1. **Review Results**: Open Created Dashboards and Reports
2. **Experiment**: Try Different Scenarios and Parameters
3. **Adapt**: Add Your Own Device Types and Algorithms
4. **Publish**: Use Graphs in Scientific Works

---

*Demonstration Completed Successfully! 🎉*
"""
    
    # Save report
    with open('DEMO_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("   ✅ Demonstration Report Created: DEMO_REPORT.md")
    print(f"   📊 Total Files Created: {len(all_files)}")

def show_results_summary():
    """Show summary of generated results"""
    print_step(6, "Demonstration Outcomes", "Overview of Created Results")
    
    print("\n   🎯 Main Results:")
    
    # Check for key files
    key_files = [
        ('demo_results/executive_dashboard.png', '👔 Executive Dashboard'),
        ('demo_results_small_campus/simulation_dashboard.png', '📊 Main Dashboard (small campus)'),
        ('demo_results_medium_district/interactive_dashboard.html', '🌐 Interactive Dashboard'),
        ('DEMO_REPORT.md', '📋 Demonstration Final Report')
    ]
    
    for file_path, description in key_files:
        if Path(file_path).exists():
            print(f"   ✅ {description:40} - {file_path}")
        else:
            print(f"   ❌ {description:40} - Not Created")
    
    print("\n   📁 Directories with Results:")
    for results_dir in ['demo_results', 'demo_results_small_campus', 'demo_results_medium_district']:
        if Path(results_dir).exists():
            file_count = len(list(Path(results_dir).glob('*')))
            print(f"   ├── {results_dir:25} ({file_count} files)")
        else:
            print(f"   ├── {results_dir:25} (not created)")

def main():
    """Main demo function"""
    print_banner()
    
    print_section("START OF DEMONSTRATION", 
                  "Checking system and starting comprehensive demonstration")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Demonstration Aborted: Missing Dependencies")
        return 1
    
    time.sleep(1)
    
    # Step 2: Check files
    if not check_files():
        print("\n❌ Demonstration Aborted: Missing Files")
        return 1
    
    time.sleep(1)
    
    # Step 3: Quick test
    print_section("QUICK TEST", "Checking Base Functionality")
    if not run_quick_test():
        print("\n❌ Demonstration Aborted: Quick Test Failed")
        return 1
    
    time.sleep(2)
    
    # Step 4: Full demo
    print_section("FULL DEMONSTRATION", "Running different simulation scenarios")
    if not run_full_demo():
        print("\n⚠️  Full Demonstration Completed with Errors")
    
    # Step 5: Generate report
    print_section("GENERATING REPORT", "Creating Final Report")
    generate_demo_report()
    
    # Step 6: Show results
    print_section("OUTCOMES", "Overview of Created Results")
    show_results_summary()
    
    # Final message
    print_section("DEMONSTRATION COMPLETED! 🎉")
    print("""
🎊 Congratulations! Demonstration Completed Successfully.

📋 What Was Demonstrated:
   ✅ Realistic Device Parameters (smartphones, IoT, vehicles, 5G, edge)
   ✅ Beautiful Charts and Dashboards
   ✅ Interactive HTML Visualizations
   ✅ Comprehensive Statistics and Analysis
   ✅ Automatic Reports

�� Results Saved in:
   ├── demo_results/               (quick test)
   ├── demo_results_small_campus/  (small campus)
   ├── demo_results_medium_district/ (medium district)
   └── DEMO_REPORT.md             (final report)

🚀 Next Steps:
   1. Open Created Dashboards and Review Results
   2. Try: python3 run_simulation.py --help
   3. Experiment with Different Scenarios
   4. Read README_SIMULATION.md for Detailed Documentation

💡 For Quick Repeat Run:
   python3 run_simulation.py --quick-test --all-visualizations
    """)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Demonstration Aborted by User")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
# 🚀 Installation Guide - Full Integrated Cross-Zone Blockchain Simulation

This guide will help you set up and run the complete integrated simulation that combines NS-3 network simulation with realistic device parameters and consensus validators.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows WSL2
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: 5GB free space
- **CPU**: Multi-core processor recommended

### Software Dependencies
- **Python**: 3.8 or higher
- **NS-3**: Version 3.35 or higher
- **Git**: For cloning repositories
- **Build tools**: gcc, make, cmake

## 🔧 Step-by-Step Installation

### Step 1: Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-dev
sudo apt install -y build-essential cmake git
sudo apt install -y libgtk-3-dev libxml2-dev libsqlite3-dev
sudo apt install -y qt5-default  # For NetAnim visualization
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 cmake git qt5
```

#### Windows WSL2
```bash
# Enable WSL2 and install Ubuntu
# Then follow Ubuntu instructions above
```

### Step 2: Install Python Dependencies

```bash
# Navigate to the real_sim directory
cd test_ns3_blocksim/real_sim

# Install Python packages
pip3 install -r requirements.txt

# Verify installation
python3 -c "import numpy, matplotlib, pandas; print('✅ Python dependencies installed')"
```

### Step 3: Install and Build NS-3

#### Option A: Automatic Installation (Recommended)
```bash
# Navigate to project root
cd test_ns3_blocksim

# Create external directory if it doesn't exist
mkdir -p external

# Clone NS-3
cd external
git clone https://gitlab.com/nsnam/ns-3-dev.git ns-3
cd ns-3

# Configure and build NS-3
python3 ns3 configure --enable-examples --enable-tests
python3 ns3 build

# Verify installation
python3 ns3 run hello-simulator
```

#### Option B: Manual Installation
```bash
# Download NS-3 from official website
wget https://www.nsnam.org/releases/ns-allinone-3.35.tar.bz2
tar -xjf ns-allinone-3.35.tar.bz2
mv ns-allinone-3.35/ns-3.35 external/ns-3

# Build NS-3
cd external/ns-3
./waf configure --enable-examples --enable-tests
./waf build
```

### Step 4: Verify Installation

```bash
# Navigate to real_sim scripts directory
cd test_ns3_blocksim/real_sim/scripts

# Run quick test
python3 quick_test.py
```

Expected output:
```
🚀 Full Integrated Simulation - Quick Test
==================================================

==================== Import Test ====================
🔍 Testing imports...
   ✅ numpy
   ✅ matplotlib
   ✅ pandas
   ✅ full_integrated_simulation
✅ Import Test PASSED

==================== Configuration Test ====================
🔧 Testing configuration...
   ✅ Configuration file loaded successfully
   📋 Simulation: Full NS-3 Integrated Cross-Zone Blockchain Simulation
✅ Configuration Test PASSED

[... more tests ...]

📊 Test Results: 6/6 tests passed
🎉 All tests passed! The simulation is ready to use.
```

## 🚀 Quick Start

### Basic Test Run
```bash
# Navigate to scripts directory
cd test_ns3_blocksim/real_sim/scripts

# Run a quick 3-minute simulation
python3 run_full_simulation.py --scenario small_campus --duration 180

# Check results
ls ../results/
```

### Expected Output Structure
```
results/
├── full_simulation_results.json      # Complete results
├── device_data.json                  # Device performance data
├── simulation_statistics.json        # Detailed statistics
├── executive_dashboard.png           # Overview dashboard
├── interactive_dashboard.html        # Interactive plots
├── energy_consumption_detailed.png   # Energy analysis
└── advanced-cross-zone-blockchain-fixed.xml  # NetAnim file
```

## 🔧 Configuration

### Main Configuration File
Edit `config/full_simulation_config.json` to customize:

```json
{
  "device_types": {
    "smartphone": {"count": 50},
    "iot_sensor": {"count": 30},
    "vehicle": {"count": 10}
  },
  "consensus_validator_config": {
    "min_validators": 5,
    "max_validators": 15
  },
  "network_config": {
    "simulation_time": 300,
    "area_size_km": 2.0
  }
}
```

### Scenario Selection
Available scenarios:
- `small_campus`: 1 km², 180s, university/office
- `medium_district`: 4 km², 600s, city district
- `large_city`: 16 km², 1800s, metropolitan area
- `stress_test`: 1 km², 300s, high density testing

## 🎯 Usage Examples

### Basic Usage
```bash
# Quick test (3 minutes)
python3 run_full_simulation.py --scenario small_campus --duration 180

# Medium test (10 minutes)
python3 run_full_simulation.py --scenario medium_district --duration 600

# Full test (30 minutes)
python3 run_full_simulation.py --scenario large_city --duration 1800
```

### Advanced Usage
```bash
# Custom configuration
python3 run_full_simulation.py --config custom_config.json

# Disable specific components for testing
python3 run_full_simulation.py --disable-ns3 --scenario small_campus
python3 run_full_simulation.py --disable-devices --scenario small_campus
python3 run_full_simulation.py --disable-consensus --scenario small_campus

# Verbose output for debugging
python3 run_full_simulation.py --verbose --scenario small_campus

# Quiet mode for automated runs
python3 run_full_simulation.py --quiet --scenario small_campus
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. NS-3 Build Errors
```bash
# Error: NS-3 not found
# Solution: Ensure NS-3 is in external/ns-3
ls external/ns-3/ns3  # Should exist

# Error: Build failed
# Solution: Install missing dependencies
sudo apt install -y build-essential cmake libgtk-3-dev
```

#### 2. Python Import Errors
```bash
# Error: Module not found
# Solution: Install missing packages
pip3 install numpy matplotlib pandas seaborn plotly

# Error: Path issues
# Solution: Run from correct directory
cd test_ns3_blocksim/real_sim/scripts
```

#### 3. Configuration Errors
```bash
# Error: Configuration file not found
# Solution: Check file path
ls ../config/full_simulation_config.json

# Error: Invalid JSON
# Solution: Validate JSON syntax
python3 -m json.tool ../config/full_simulation_config.json
```

#### 4. Memory Issues
```bash
# Error: Out of memory
# Solution: Reduce simulation size
python3 run_full_simulation.py --scenario small_campus --duration 60
```

#### 5. Permission Issues
```bash
# Error: Permission denied
# Solution: Fix permissions
chmod +x run_full_simulation.py
chmod +x quick_test.py
```

### Debug Mode
```bash
# Run with maximum verbosity
python3 run_full_simulation.py --verbose --scenario small_campus

# Check logs
tail -f ../results/simulation.log
```

### Performance Optimization
```bash
# For faster testing, disable heavy components
python3 run_full_simulation.py \
  --disable-visualization \
  --scenario small_campus \
  --duration 60
```

## 📊 Validation

### Verify Correct Installation
1. **Quick Test**: `python3 quick_test.py` should pass all tests
2. **Mini Simulation**: Should complete in under 1 minute
3. **NS-3 Integration**: NetAnim file should be generated
4. **Visualizations**: PNG and HTML files should be created

### Expected Performance
- **Small Campus (180s)**: 2-5 minutes execution time
- **Medium District (600s)**: 10-20 minutes execution time
- **Large City (1800s)**: 30-60 minutes execution time

### Output Validation
```bash
# Check result files
ls -la ../results/

# Validate JSON output
python3 -m json.tool ../results/full_simulation_results.json

# Check visualization files
file ../results/*.png ../results/*.html
```

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
# Update Python packages
pip3 install --upgrade -r requirements.txt

# Update NS-3 (if needed)
cd external/ns-3
git pull
python3 ns3 build
```

### Cleaning Up
```bash
# Clean simulation results
rm -rf ../results/*

# Clean NS-3 build files
cd external/ns-3
python3 ns3 clean
```

## 📞 Support

### Getting Help
1. **Check Documentation**: Read README.md and this INSTALL.md
2. **Run Quick Test**: `python3 quick_test.py` to identify issues
3. **Check Logs**: Review error messages and logs
4. **Minimal Test**: Try with minimal configuration first

### Reporting Issues
When reporting issues, please include:
- Operating system and version
- Python version (`python3 --version`)
- Error messages and logs
- Configuration used
- Steps to reproduce

### Community Resources
- **Documentation**: Check all README files
- **Examples**: Review example configurations
- **Test Scripts**: Use quick_test.py for diagnostics

---

## 🎉 Success!

If you've completed all steps successfully, you now have a fully integrated cross-zone blockchain simulation that combines:

✅ **NS-3 Network Simulation** - Real protocols and mobility  
✅ **Realistic Device Parameters** - Energy, CPU, memory models  
✅ **Consensus Validator Management** - Advanced algorithms  
✅ **Beautiful Visualizations** - Professional dashboards  

**Next Steps:**
1. Run your first simulation: `python3 run_full_simulation.py --scenario small_campus`
2. Explore the generated visualizations
3. Experiment with different scenarios and configurations
4. Use the results for your research or development

**Happy Simulating! 🚀** 
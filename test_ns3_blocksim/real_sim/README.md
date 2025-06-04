# 🚀 Full Integrated Cross-Zone Blockchain Simulation

**Complete integration of NS-3 network simulation with realistic device parameters and consensus validators**

## 🎯 Overview

This simulation combines the best of all worlds:

- **🌐 NS-3 Network Simulation**: Real protocols (AODV, 5G), physical mobility, RSSI-based zone detection
- **⚡ Realistic Device Parameters**: Energy consumption, CPU performance, memory usage, battery models
- **🛡️ Consensus Validator Management**: ValidatorLeave/ManetNodeEnter algorithm with PBFT consensus
- **📊 Beautiful Visualizations**: Executive dashboards, interactive plots, publication-ready graphs

## 🏗️ Architecture

```
Full Integrated Simulation
├── NS-3 Network Layer
│   ├── AODV Routing (MANET)
│   ├── 5G Base Stations
│   ├── Physical Mobility Models
│   └── RSSI-based Zone Detection
├── Realistic Device Layer
│   ├── Energy Consumption Models
│   ├── CPU Performance Simulation
│   ├── Battery Drain Calculation
│   └── Performance Degradation
├── Consensus Validator Layer
│   ├── ValidatorLeave Algorithm
│   ├── ManetNodeEnter Algorithm
│   ├── PBFT Consensus Voting
│   └── Automatic Validator Rotation
└── Visualization Layer
    ├── Executive Dashboards
    ├── Interactive HTML Plots
    ├── NetAnim Network Visualization
    └── Real-time Statistics
```

## 🔧 Device Types & Specifications

### 📱 Smartphones (50 devices)
- **CPU**: 8-15 GFLOPS
- **Memory**: 6-12 GB RAM
- **Battery**: 3000-5000 mAh
- **Mobility**: Pedestrian (1-3 m/s)
- **Applications**: Blockchain client, transaction generator

### 🔗 IoT Sensors (30 devices)
- **CPU**: 0.1-1 GFLOPS
- **Memory**: 0.5-2 GB RAM
- **Battery**: 500-2000 mAh
- **Mobility**: Static
- **Applications**: Sensor data, lightweight blockchain

### 🚗 Vehicles (10 devices)
- **CPU**: 20-50 GFLOPS
- **Memory**: 16-32 GB RAM
- **Battery**: 50000-100000 mAh
- **Mobility**: Vehicular (10-30 m/s)
- **Applications**: Blockchain validator, edge computing

### 📡 5G Base Stations (2 devices)
- **CPU**: 1000-2000 GFLOPS
- **Memory**: 64-128 GB RAM
- **Power**: Grid connected
- **Coverage**: 150m radius
- **Applications**: Blockchain core, consensus coordinator

### 🖥️ Edge Servers (4 devices)
- **CPU**: 100-500 GFLOPS
- **Memory**: 32-64 GB RAM
- **Power**: Grid connected
- **Applications**: Blockchain validator, data processing

## 🌐 Network Zones

### 5G Zone
- **Coverage**: 150m radius per base station
- **Frequency**: 28 GHz
- **Bandwidth**: 100 MHz
- **Devices**: Smartphones, base stations

### MANET Zone
- **Routing**: AODV protocol
- **Range**: 50m per device
- **Frequency**: 2.4 GHz
- **Data Rate**: 11 Mbps
- **Devices**: IoT sensors, mobile devices

### Bridge Zone
- **Dual Radio**: 5G + MANET
- **Handover**: RSSI-based (-80 dBm threshold)
- **Devices**: Vehicles, edge servers

## 🛡️ Consensus Features

### ValidatorLeave/ManetNodeEnter Algorithm
1. **RSSI Monitoring**: Continuous signal strength monitoring
2. **Leave Detection**: Automatic detection of weak signals
3. **Leave Transaction**: Broadcast validator leave intention
4. **Candidate Selection**: Identify eligible replacement nodes
5. **Join Transaction**: New candidate requests validator role
6. **PBFT Voting**: Consensus voting on validator changes
7. **Automatic Promotion**: Successful candidates become validators
8. **Dual Radio Activation**: Bridge validators activate relay duties

### Consensus Parameters
- **Min Validators**: 5
- **Max Validators**: 15
- **Rotation Interval**: 30 seconds
- **RSSI Threshold**: -85 dBm
- **Battery Threshold**: 20%
- **Consensus Threshold**: 67%

## 📊 Scenarios

### Small Campus (180s)
- **Area**: 1 km²
- **Density**: Medium
- **Use Case**: University campus, office building
- **Duration**: 3-5 minutes

### Medium District (600s)
- **Area**: 4 km²
- **Density**: High
- **Use Case**: City district, shopping mall
- **Duration**: 10-15 minutes

### Large City (1800s)
- **Area**: 16 km²
- **Density**: Very high
- **Use Case**: Metropolitan area, smart city
- **Duration**: 30-45 minutes

### Stress Test (300s)
- **Area**: 1 km²
- **Density**: Extreme
- **Use Case**: Performance testing, bottleneck analysis
- **Duration**: 5-10 minutes

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies
pip3 install numpy matplotlib seaborn pandas scipy networkx plotly

# Ensure NS-3 is built
cd ../external/ns-3
python3 ns3 configure --enable-examples --enable-tests
python3 ns3 build
```

### Basic Usage
```bash
# Quick test (3 minutes)
cd real_sim/scripts
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

# Disable specific components
python3 run_full_simulation.py --disable-ns3 --scenario small_campus
python3 run_full_simulation.py --disable-devices --scenario small_campus
python3 run_full_simulation.py --disable-consensus --scenario small_campus

# Verbose output
python3 run_full_simulation.py --verbose --scenario small_campus

# Quiet mode (minimal output)
python3 run_full_simulation.py --quiet --scenario small_campus
```

## 📁 Output Files

After simulation completion, the following files are generated:

### Results
- `full_simulation_results.json` - Complete simulation results
- `device_data.json` - Individual device performance data
- `simulation_statistics.json` - Detailed statistics

### Visualizations
- `executive_dashboard.png` - High-level overview dashboard
- `interactive_dashboard.html` - Interactive analysis plots
- `energy_consumption_detailed.png` - Energy analysis
- `zone_distribution_detailed.png` - Zone transition analysis

### NS-3 Output
- `advanced-cross-zone-blockchain-fixed.xml` - NetAnim visualization
- `*.pcap` - Network packet captures (if enabled)
- `*.tr` - ASCII trace files (if enabled)

## 📈 Key Metrics

### Network Performance
- **Zone Transitions**: Dynamic movement between zones
- **Validator Rotations**: Automatic validator management
- **Cross-zone Transactions**: Inter-zone communication
- **Network Throughput**: Transactions per minute
- **Consensus Latency**: Time for validator consensus

### Energy Analysis
- **Total Energy Consumption**: System-wide energy usage
- **Energy per Transaction**: Efficiency metric
- **Battery Levels**: Device battery status over time
- **Energy per Device Type**: Breakdown by device category

### Consensus Performance
- **Validator Success Rate**: Successful validator changes
- **PBFT Consensus Time**: Time for consensus decisions
- **Leave/Join Transactions**: Validator management activity
- **Dual Radio Performance**: Bridge validator efficiency

## 🔧 Configuration

### Main Configuration File
`config/full_simulation_config.json` contains all simulation parameters:

```json
{
  "simulation_name": "Full NS-3 Integrated Cross-Zone Blockchain Simulation",
  "ns3_config": {
    "ns3_path": "../external/ns-3",
    "enable_netanim": true,
    "enable_pcap": true
  },
  "device_types": {
    "smartphone": {"count": 50, "cpu_gflops": "8.0:15.0"},
    "iot_sensor": {"count": 30, "cpu_gflops": "0.1:1.0"},
    "vehicle": {"count": 10, "cpu_gflops": "20.0:50.0"}
  },
  "consensus_validator_config": {
    "min_validators": 5,
    "max_validators": 15,
    "rssi_threshold": -85
  }
}
```

### Customization
- Modify device counts and specifications
- Adjust consensus parameters
- Change network zone configurations
- Enable/disable specific features

## 🎯 Integration Features

### ✅ What's Integrated
- **Real Network Simulation**: NS-3 provides actual network protocols
- **Real Device Parameters**: Energy, CPU, memory from real devices
- **Real Consensus Algorithm**: PBFT with ValidatorLeave/ManetNodeEnter
- **Real Mobility**: Physical movement models with RSSI
- **Real Visualizations**: Professional dashboards and plots

### 🔄 Data Flow
1. **NS-3** simulates network layer (protocols, mobility, radio)
2. **Device Manager** simulates realistic device behavior
3. **Consensus Manager** handles validator selection and rotation
4. **Statistics Collector** gathers comprehensive metrics
5. **Visualization Engine** creates beautiful outputs

## 🚀 Advanced Features

### Multi-threaded Execution
- NS-3 simulation runs in background thread
- Device simulation runs in parallel
- Real-time statistics collection
- Synchronized data aggregation

### Real-time Monitoring
- Live progress updates
- Error detection and handling
- Resource usage monitoring
- Performance optimization

### Extensible Architecture
- Modular component design
- Easy to add new device types
- Configurable consensus algorithms
- Pluggable visualization modules

## 📚 Research Applications

### Academic Research
- **Network Protocol Evaluation**: Test new routing algorithms
- **Energy Efficiency Studies**: Analyze power consumption patterns
- **Consensus Algorithm Research**: Evaluate validator selection methods
- **Mobility Impact Analysis**: Study movement effects on blockchain

### Industry Applications
- **Smart City Planning**: Optimize infrastructure deployment
- **IoT Network Design**: Plan sensor network topologies
- **5G Blockchain Integration**: Test 5G + blockchain scenarios
- **Edge Computing Optimization**: Analyze edge server placement

## 🤝 Contributing

### Adding New Device Types
1. Update `config/full_simulation_config.json`
2. Add device specifications to realistic device manager
3. Update zone assignment logic
4. Test with different scenarios

### Adding New Consensus Algorithms
1. Implement algorithm in consensus validator manager
2. Add configuration parameters
3. Update visualization components
4. Document algorithm behavior

### Adding New Visualizations
1. Extend visualization engine
2. Add new plot types
3. Update dashboard layouts
4. Test with different data sets

## 📞 Support

For questions, issues, or contributions:
- Check existing documentation
- Review configuration examples
- Test with small scenarios first
- Report issues with detailed logs

---

**🎉 Enjoy exploring the full integrated cross-zone blockchain simulation!**

*This simulation represents the state-of-the-art in blockchain network research, combining real network protocols, realistic device parameters, and advanced consensus algorithms in a single comprehensive platform.* 
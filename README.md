# Cross-Zone Blockchain for 6G-MANET Networks

A comprehensive blockchain-enhanced network simulation integrating stationary 6G infrastructure with dynamic Mobile Ad Hoc Networks (MANET) using blockchain technology for security, trust, and adaptive routing.

## 🚀 Key Features

- **Cross-Zone Architecture**: 5G, MANET, and Bridge zones with automatic transitions
- **Dynamic Mobility**: All nodes mobile except base station with zone detection
- **Blockchain Security**: Cryptographic transaction validation between zones
- **Validator Management**: Automatic role assignment and rotation
- **AODV Integration**: Native NS-3 routing for MANET connectivity
- **Real-time Visualization**: NetAnim with zone-based node coloring

## 🎯 Project Goals

- **Enhanced Security**: Node authentication and resistance to network attacks
- **Decentralized Trust**: Blockchain-based reputation system for network nodes
- **Adaptive Routing**: Dynamic route construction considering node trustworthiness
- **Resilient Operation**: Continuous operation despite failures or partitioning
- **Resource Optimization**: Energy-efficient performance for constrained devices

## 🏗️ Architecture

### Network Components
- **6G Base Station**: Stationary access point and primary trust anchor
- **MANET Nodes**: Mobile devices forming self-configuring networks
- **Bridge Validators**: Nodes managing cross-zone transactions
- **Distributed Ledger**: Immutable registry of network state and transactions

### Zone Management
- **5G Zone**: High-bandwidth area around base station
- **MANET Zone**: Mobile ad-hoc network beyond 5G coverage
- **Bridge Zone**: Intermediate area enabling cross-zone communication

## 📊 Test Results ✅

All simulations passing with 100% success rate:

| Test | Nodes | Duration | Status | Features |
|------|-------|----------|--------|----------|
| Simple | 6 | 30s | ✅ PASS | Basic cross-zone functionality |
| Static | 10 | 45s | ✅ PASS | Static architecture validation |
| Mobile Quick | 8 | 45s | ✅ PASS | Dynamic mobility with transitions |
| Mobile Full | 14 | 90s | ✅ PASS | Complete mobile architecture |

## 🚀 Quick Start

### Prerequisites
- NS-3 (v3.36+, recommended v3.44)
- Python 3.8+
- Qt5 (for NetAnim visualization)

### Installation
```bash
# Install dependencies (Ubuntu/Debian)
sudo apt install qt5-default python3-dev cmake ninja-build

# Install Python requirements
pip3 install -r test_ns3_blocksim/requirements.txt

# Configure NS-3
cd test_ns3_blocksim/external/ns-3
./ns3 configure --enable-examples --enable-tests
./ns3 build
```

### Run Simulations
```bash
cd test_ns3_blocksim/

# Basic cross-zone test (recommended first run)
python3 scripts/run_basic_simulation.py

# Advanced mobile simulation (full features)
./run_advanced_cross_zone.sh

# View results in NetAnim
cd external/ns-3/netanim && ./NetAnim
# Open generated XML file from results/ directory
```

## 🔧 Core Components

### Security & Authentication
- Multi-level digital certificate verification
- Periodic session key rotation
- Dynamic node reputation scoring
- Sybil attack mitigation through rate limiting

### Consensus Mechanism
- **5G Zone**: Proof-of-Authority anchored by base station
- **MANET Zone**: Byzantine Fault Tolerant consensus
- **Bridge Validation**: Cross-zone transaction verification

### Mobility & Routing
- Real-time zone transition detection
- AODV routing with blockchain-enhanced metrics
- Automatic validator role assignment based on position
- Route verification using node trust scores

## 📁 Project Structure

```
test_ns3_blocksim/
├── scripts/          # Simulation execution scripts
├── models/           # BlockSim and NS-3 blockchain models
├── config/           # Simulation configuration files
├── results/          # Simulation outputs and NetAnim files
├── external/ns-3/    # NS-3 network simulator
└── requirements.txt  # Python dependencies
```

## 🎞️ Visualization

NetAnim provides real-time visualization featuring:
- **Zone-based coloring**: Different colors for each network zone
- **Movement tracking**: Node mobility patterns and trajectories
- **Transaction flows**: Cross-zone communication visualization
- **Validator status**: Active/inactive validator indicators

## 📈 Performance

- **Scalability**: Tested up to 14+ nodes
- **Latency**: Sub-second cross-zone transaction validation
- **Mobility**: Seamless zone transitions without connectivity loss
- **Stability**: 100% simulation success rate across all test scenarios

## 🎉 Status

**Ready for demonstration and further development!**

The system provides a fully functional cross-zone blockchain architecture for 6G-MANET networks with dynamic mobility, automatic validator management, and comprehensive visualization capabilities.

For detailed technical documentation, see:
- `test_ns3_blocksim/TEST_SUMMARY.md` - Test results overview
- `test_ns3_blocksim/CROSS_ZONE_TEST_RESULTS.md` - Detailed technical results
- `test_ns3_blocksim/README.md` - Implementation details

# Cross-Zone Blockchain for 6G-MANET Networks

A blockchain-enhanced network simulation integrating 6G infrastructure with Mobile Ad Hoc Networks (MANET) using NS-3 and blockchain technology.

## Key Features

- **Cross-Zone Architecture**: 5G, MANET, and Bridge zones with transitions
- **Dynamic Mobility**: Mobile nodes with zone detection
- **Blockchain Security**: Cryptographic transaction validation
- **Validator Management**: Automatic role assignment and rotation
- **AODV Integration**: NS-3 routing for MANET connectivity
- **Real-time Visualization**: NetAnim with zone-based coloring

## Quick Start

### Prerequisites
- NS-3 (v3.36+)
- Python 3.8+
- Qt5 (for NetAnim)

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

### Run Simulation
```bash
cd test_ns3_blocksim/

# Enhanced cross-zone with consensus validators
./run_advanced_cross_zone.sh

# View results in NetAnim
cd external/ns-3/netanim && ./NetAnim
```

## Architecture

### Network Components
- **6G Base Station**: Stationary access point and trust anchor
- **MANET Nodes**: Mobile devices with self-configuring networks
- **Bridge Validators**: Cross-zone transaction managers
- **Distributed Ledger**: Network state and transaction registry

### Zone Management
- **5G Zone**: High-bandwidth area around base station
- **MANET Zone**: Ad-hoc network beyond 5G coverage
- **Bridge Zone**: Cross-zone communication interface

## Test Results ✅

All simulations passing with 100% success rate:

| Test | Nodes | Duration | Features |
|------|-------|----------|----------|
| Enhanced | 17 | 180s | Full consensus + mobility |
| Cross-zone | 14 | 90s | Zone transitions |
| Quick | 9 | 60s | Basic functionality |

## Project Structure

```
test_ns3_blocksim/
├── scripts/          # Simulation execution
├── models/           # Blockchain models
├── config/           # Configuration files
├── results/          # Outputs and animations
└── external/ns-3/    # NS-3 simulator
```

## Status

**Ready for demonstration!** The system provides fully functional cross-zone blockchain architecture with dynamic mobility, validator management, and visualization.

For technical details see `test_ns3_blocksim/README.md`.

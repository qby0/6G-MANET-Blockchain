# Cross-Zone Blockchain Simulation for 6G-MANET Networks

Cross-zone blockchain simulation with consensus-based validator management for hybrid 6G-MANET networks, featuring the ValidatorLeave/ManetNodeEnter algorithm with mobility support and PBFT consensus.

## Key Features

### Cross-Zone Architecture
- **Three-Zone Network**: 5G, MANET, and Bridge zones with automatic transitions
- **Dynamic Mobility**: All nodes mobile except base station
- **RSSI-Based Detection**: Automatic zone transitions based on signal strength
- **Cross-Zone Validation**: Cryptographic transaction validation between zones

### Consensus-Based Validator Management
- **ValidatorLeave/ManetNodeEnter Algorithm**: Automatic validator rotation with mobility
- **PBFT Consensus**: Byzantine fault-tolerant voting for validator changes
- **Performance-Based Selection**: Scoring system for candidate validators
- **Battery Level Monitoring**: Automatic rotation on low battery
- **Dual-Radio Gateway Preference**: Bridge nodes preferred as validators

### Network Simulation
- **NS-3 Integration**: Native simulation with C++ performance
- **AODV Routing**: Real ad-hoc routing for MANET zone
- **NetAnim Visualization**: Real-time network visualization with zone coloring
- **BlockSim Integration**: Blockchain consensus and transaction processing

## Quick Start

### Installation
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt install qt5-default python3-dev cmake ninja-build ccache

# Install Python dependencies
pip3 install -r requirements.txt

# Configure and build NS-3
cd external/ns-3
./ns3 configure --enable-examples --enable-tests --enable-python-bindings
./ns3 build
```

### Run Simulations

#### Main Simulation Controller (Recommended)
```bash
# Enhanced cross-zone with consensus validators
python3 main_sim.py enhanced

# Custom parameters
python3 main_sim.py enhanced --time 300 --min-validators 4 --max-validators 8

# List all simulation types
python3 main_sim.py --list
```

#### Shell Script Interface
```bash
# Enhanced simulation with consensus validators
./run_advanced_cross_zone.sh

# Quick test mode
./run_advanced_cross_zone.sh enhanced quick --verbose

# Large network demonstration
./run_advanced_cross_zone.sh enhanced large
```

### View Results
```bash
# Open NetAnim for visualization
cd external/ns-3/netanim
./NetAnim
# Load generated XML file: advanced-cross-zone-blockchain-fixed.xml
```

## Simulation Types

| Type | Description | Features |
|------|-------------|----------|
| **enhanced** | Enhanced cross-zone with consensus validators | Full ValidatorLeave/ManetNodeEnter + PBFT |
| **cross-zone** | Basic cross-zone without consensus | Zone transitions + basic validation |
| **consensus** | Standalone consensus validator system | Pure consensus algorithm testing |

## Simulation Modes

| Mode | Duration | Nodes | Purpose |
|------|----------|-------|---------|
| **quick** | 60s | 9 (4M+3G+2B) | Quick testing |
| **standard** | 180s | 17 (8M+6G+3B) | Standard demo |
| **large** | 300s | 27 (12M+10G+5B) | Scalability test |

## Consensus Validator Features

### ValidatorLeave/ManetNodeEnter Algorithm
```
1. RSSI threshold detection (< -80dBm triggers leave)
2. PBFT consensus voting for validator changes
3. Battery level monitoring (< 20% triggers rotation)
4. Mobility-aware candidate promotion
5. Automatic shortage handling
```

### Zone-Based Distribution
- **5G Zone** (0-100m): Strong signal validators
- **Bridge Zone** (100-150m): Dual-radio gateway validators
- **MANET Zone** (150-400m): Ad-hoc connectivity only

## Test Results

All enhanced simulations passing with 100% success rate:

| Test Type | Nodes | Duration | Consensus Features | Status |
|-----------|-------|----------|-------------------|---------|
| Enhanced Quick | 9 | 60s | 2-4 validators | ✅ PASS |
| Enhanced Standard | 17 | 180s | 3-7 validators | ✅ PASS |
| Enhanced Large | 27 | 300s | 4-10 validators | ✅ PASS |

## Configuration Options

### Network Parameters
```bash
--manet-nodes N      # MANET zone nodes (default: 8)
--5g-nodes N         # 5G zone nodes (default: 6)
--bridge-nodes N     # Bridge validators (default: 3)
--time T             # Simulation time (default: 180s)
```

### Consensus Parameters
```bash
--min-validators N   # Minimum validators (default: 3)
--max-validators N   # Maximum validators (default: 7)
--disable-consensus  # Disable consensus management
```

## Project Structure

```
test_ns3_blocksim/
├── main_sim.py                     # Main simulation controller
├── run_advanced_cross_zone.sh      # Enhanced shell script
├── scripts/                        # Simulation execution scripts
├── models/                         # BlockSim models and NS-3 extensions
│   └── blockchain/
│       ├── consensus_validator_manager.py     # Consensus validator system
│       ├── blocksim_bridge.py              # BlockSim integration
│       └── transaction_handler.py          # Cross-zone transactions
├── config/                         # Configuration files
├── results/                        # Simulation outputs and logs
├── external/ns-3/                 # NS-3 simulator installation
└── CONSENSUS_VALIDATOR_DOCUMENTATION.md  # Detailed documentation
```

## Documentation

- `CONSENSUS_VALIDATOR_DOCUMENTATION.md` - Complete consensus system documentation
- `TEST_SUMMARY.md` - Test results and performance metrics
- `CROSS_ZONE_TEST_RESULTS.md` - Detailed cross-zone test results

## Status

**Ready for demonstration and further development!** 

Enhanced Cross-Zone Blockchain with Consensus Validators represents a successful implementation of next-generation blockchain architecture for mobile networks with 100% pass rate across all test scenarios.

For detailed consensus validator documentation, see [`CONSENSUS_VALIDATOR_DOCUMENTATION.md`](CONSENSUS_VALIDATOR_DOCUMENTATION.md).
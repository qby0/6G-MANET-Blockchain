# Blockchain-Assisted QoS Routing in 6G MANET (WiGig Edition)

Research project implementing a blockchain-assisted routing mechanism for 6G Mobile Ad-hoc Networks (MANETs) operating in the 60 GHz band (WiGig).

## Overview

This project proposes a lightweight blockchain-based trust management system for QoS-aware routing in dynamic MANET environments. The system uses a distributed ledger to track link quality metrics (SNR, trust scores) and dynamically routes packets around unreliable nodes.

## Key Features

- **Blockchain-Assisted Routing**: Distributed ledger stores link metrics (SNR, trust) for QoS-aware path selection
- **Dynamic Blackhole Detection**: Timeout-based detection mechanism identifies unreliable nodes
- **Asymmetric Trust Dynamics**: Fast penalty (×0.5) on packet drops, slow recovery (+0.005) requiring ~200 successful packets
- **Balanced Cost Function**: Trust and SNR penalties are mathematically balanced (Beta=500)
- **NS-3 Simulation**: Full network simulation with WiGig (802.11a @ 60 GHz) physical layer

## Project Structure

```
├── ns3/ns-3-dev/scratch/sixg-wigig-sim.cc  # Main NS-3 simulation code
├── sensitivity_analysis.py                 # Sensitivity analysis script
├── thesis_technical_sections.md           # Technical documentation
├── blockchain-rounting-c++/                # Legacy C++ implementation
└── blockchain-routing-sim/                 # Python simulation framework
```

## Simulation Parameters

- **Network**: 30 nodes, 10 flows, 7 blackhole nodes (23%)
- **Area**: 300×300m (dense network)
- **Radio Range**: 150m
- **Simulation Time**: 60 seconds
- **Routing Cost**: `cost = α·(1/snr²) + β·(1/trust²)` where α=1.0, β=500.0
- **Trust Floor**: 0.2 (configurable)

## Results

The proposed blockchain-assisted routing demonstrates:
- Improved Packet Delivery Ratio (PDR) compared to baseline hop-count routing
- Resilience to blackhole attacks through dynamic trust management
- Acceptable latency overhead for enhanced reliability

## Technologies

- **NS-3 Network Simulator** (v3.46)
- **C++** (simulation core)
- **Python** (analysis scripts)

## Usage

### Running the Simulation

```bash
cd ns3/ns-3-dev
./ns3 build scratch/sixg-wigig-sim
./build/scratch/ns3.46-sixg-wigig-sim-default \
  --numNodes=30 \
  --numFlows=10 \
  --numBlackholes=7 \
  --simTime=60.0 \
  --useBlockchain=true \
  --beta=500.0 \
  --trustFloor=0.2 \
  --sideLength=300.0 \
  --RngSeed=1 \
  --RngRun=1
```

### Sensitivity Analysis

```bash
python3 sensitivity_analysis.py
```

## Documentation

- `thesis_technical_sections.md` - Detailed technical documentation

## License

Academic research project.
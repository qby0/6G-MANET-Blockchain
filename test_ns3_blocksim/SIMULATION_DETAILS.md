# NS-3 and BlockSim Integration for Blockchain Simulation

## Overview
This project demonstrates the integration of NS-3 (Network Simulator 3) with BlockSim to simulate blockchain operations in Mobile Ad-hoc Networks (MANET) and 6G environments. The simulation platform enables researchers and developers to analyze blockchain performance, consensus mechanisms, and network behavior in complex wireless environments.

## Key Features
- Integration of network simulation (NS-3) with blockchain simulation (BlockSim)
- Support for various consensus mechanisms (PoA, PoW, PoS)
- Mobile node simulation with realistic movement patterns
- Transaction processing and block creation
- Network topology configuration with various node types (validators, regular nodes, base stations)
- Visualization of network topology and packet flows using NetAnim
- Detailed performance metrics and statistics

## Simulation Components

### Network Layer (NS-3)
- Simulates physical network topology and connectivity
- Models wireless communication with signal propagation
- Implements node mobility patterns
- Handles packet routing and transmission delays
- Provides realistic network metrics (latency, packet loss, throughput)

### Blockchain Layer (BlockSim)
- Models different consensus algorithms
- Manages transaction pools and block creation
- Tracks blockchain state and node participation
- Calculates resource utilization and performance
- Evaluates security metrics and attack resistance

### Integration Interface
- Synchronizes time between both simulators
- Translates network events to blockchain events and vice versa
- Manages shared state and data consistency
- Routes transactions through the simulated network
- Captures combined metrics and analytics

## Simulation Scenarios
1. **Base Scenario**: Static network with fixed nodes
2. **Mobile Scenario**: Nodes with RandomWalk mobility model
3. **Urban Scenario**: Realistic urban environment with buildings and obstacles
4. **Mixed Infrastructure**: Combined 6G base stations with MANET nodes
5. **Attack Scenarios**: Simulations of various attack vectors (Sybil, Eclipse, etc.)

## Recent Simulation Results
The most recent simulation (timestamp: 20250318-083723) produced the following results:
- Simulation duration: 100.0 seconds
- Number of nodes: 14 (1 base station, 3 validators, 10 regular nodes)
- Transactions processed: 50
- Blocks created: 11
- Network connections: 79

## Visualization
Network activity can be visualized using NetAnim. Key visualization features include:
- Node movement trajectories
- Data flow between nodes
- Color-coded node types (validators in red, regular nodes in blue)
- Transaction propagation patterns

## Future Work
- Implementation of more complex consensus mechanisms
- Integration with real blockchain implementations
- Support for larger-scale simulations
- Advanced attack and security testing
- Machine learning-based prediction for network and blockchain behavior

## How to Run a Simulation
```bash
# Activate the virtual environment
source venv/bin/activate

# Run a basic simulation
python scripts/run_basic_simulation.py

# Run with animation enabled
python scripts/run_basic_simulation.py --animation

# Run with custom parameters
python scripts/run_basic_simulation.py --duration 200 --time-step 0.5 --config config/urban.json
```

## Visualizing Results
```bash
# Launch NetAnim
cd external/netanim/build/bin && ./netanim

# In NetAnim, open the animation file from the results directory
# Example: results/simulation_20250318-083723/animation_20250318-083723.xml
``` 
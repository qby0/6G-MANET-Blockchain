# Single Base Station MANET Simulation with AODV Routing

## Overview
This simulation models a Mobile Ad-hoc Network (MANET) operating with a single fixed base station and multiple mobile nodes. The unique feature of this simulation is that nodes move freely in and out of the base station's coverage area, with AODV (Ad hoc On-Demand Distance Vector) routing enabling communication between out-of-coverage nodes and the base station through multi-hop paths.

## Simulation Features

### Network Topology
- **Single Base Station**: Fixed position in the center of the simulation area with a defined coverage radius
- **Mobile Nodes**: Nodes that move randomly within the simulation area
- **Validators**: Subset of mobile nodes (10%) that can validate blockchain transactions
- **Coverage Zone**: Only nodes within the coverage radius can directly communicate with the base station
- **Inter-Node Connections**: Nodes can form connections with each other when within range (100m by default)

### Routing Mechanism
- **AODV Protocol**: Enables dynamic, on-demand routing between nodes
- **Multi-hop Paths**: Nodes outside base station coverage can still communicate by routing messages through intermediate nodes
- **Dynamic Path Discovery**: As nodes move, new routing paths are established based on current node positions
- **Path Optimization**: AODV automatically finds the shortest available path

### Node Mobility
- **Random Walk Model**: Nodes move in random directions at configurable speeds
- **Boundary Reflection**: Nodes change direction when they reach the simulation area boundaries
- **Dynamic Connectivity**: Network topology changes continuously as nodes move
- **Coverage Transitions**: Tracks when nodes enter or leave base station coverage

## How It Works

### Network Layer (NS-3)
1. The simulation area is created with a single base station at the center
2. Mobile nodes are placed randomly within the area
3. Direct connections are established between:
   - Base station and nodes within its coverage radius
   - Between nodes that are within range of each other
4. As nodes move, these connections are periodically updated
5. AODV routing protocol enables multi-hop communication for out-of-coverage nodes

### Blockchain Layer (BlockSim)
1. Transactions are generated from mobile nodes to the base station
2. Nodes outside coverage rely on the routing path established by AODV
3. Successfully routed messages are processed by the blockchain
4. The base station (acting as the main validator) creates blocks with validated transactions

## Simulation Parameters
The simulation is highly configurable through command-line arguments or a configuration file:

- `--coverage-radius`: Base station coverage radius in meters (default: 200.0)
- `--node-count`: Number of mobile nodes in the simulation (default: 30)
- `--movement-speed`: Node movement speed in m/s (default: 5.0)
- `--area-size`: Simulation area size in meters (default: 500.0)
- `--duration`: Simulation duration in seconds (default: 300.0)

## Running the Simulation

```bash
# Run with default parameters
python scripts/run_single_basestation_simulation.py

# Run with custom parameters
python scripts/run_single_basestation_simulation.py --node-count 50 --coverage-radius 150 --movement-speed 3.0

# Enable animation visualization
python scripts/run_single_basestation_simulation.py --animation

# Run with configuration file
python scripts/run_single_basestation_simulation.py --config config/basestation.json
```

## Simulation Outputs

### Data Files
- Network state (positions and connections at each time step)
- Blockchain state (blocks and transactions)
- Coverage changes (tracks when nodes enter/exit coverage)
- Transaction routes (shows routing paths used for each transaction)

### Visualization
If animation is enabled, the simulation produces an animation file viewable with NetAnim, showing:
- Color-coded nodes (base station, validators, regular nodes)
- Coverage area of the base station
- Node movement trajectories
- Message routing paths
- Packet flows between nodes

## Analysis Possibilities
This simulation enables study of:
1. Effectiveness of AODV routing in mobile blockchain networks
2. Impact of base station coverage radius on network performance
3. Relationship between node density and successful routing
4. Blockchain transaction success rates based on node position
5. Effectiveness of multi-hop communication for blockchain operations

## Example Scenarios

### High Mobility Scenario
Increase movement speed to simulate fast-moving nodes, testing AODV's ability to maintain routing paths under rapidly changing network topology.

```bash
python scripts/run_single_basestation_simulation.py --movement-speed 10.0 --duration 500
```

### Limited Coverage Scenario
Reduce the base station coverage to force more multi-hop routing through the network.

```bash
python scripts/run_single_basestation_simulation.py --coverage-radius 100.0 --node-count 40
```

### Dense Network Scenario
Increase node count in the same area to create more routing options and potential network congestion.

```bash
python scripts/run_single_basestation_simulation.py --node-count 80 --area-size 400.0
```

## Performance Considerations
- Higher node counts will increase simulation complexity and runtime
- Animation generation can significantly slow down simulation execution
- For large-scale simulations, consider disabling interim result saving 
# Integration of NS-3 and BlockSim for Blockchain System Simulation in 6G/MANET Networks
## Overview
This project demonstrates the integration of NS-3 (Network Simulator 3) and BlockSim for simulating a blockchain system in a hybrid network infrastructure of 6G and MANET.

## Project Structure
- `config/` - configuration files for various simulation scenarios
- `models/` - models for BlockSim and additional classes for NS-3
- `scripts/` - scripts for running different simulations
- `visualization/` - tools for visualizing simulation results
- `results/` - directory for saving simulation results

## Requirements
- NS-3 (version 3.36 or higher recommended)
- Python 3.8+
- Dependencies from requirements.txt
- Qt5 (for NetAnim)
- ccache (for faster builds)

## Quick Installation and Build

1. Install system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt install ccache qt5-default python3-dev cmake ninja-build
   
   # Fedora
   sudo dnf install ccache qt5-devel python3-devel cmake ninja-build
   ```

2. Install Python dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Configure and build NS-3 with optimizations:
   ```bash
   cd external/ns-3
   
   # Configure ccache for faster rebuilds
   export CCACHE_DIR=$(pwd)/.ccache
   export CCACHE_MAXSIZE=50G
   
   # Configuration with optimizations
   ./ns3 configure --enable-examples --enable-tests \
                  --enable-python-bindings \
                  --enable-modules='netanim' \
                  --build-profile=optimized \
                  --enable-ccache \
                  --enable-ninja
   
   # Parallel build (using all available cores)
   ./ns3 build -j$(nproc)
   ```

4. Set environment variables:
   ```bash
   export NS3_DIR=$(pwd)
   cd ../..
   ```

## Running Simulation with Visualization
1. Basic simulation:
   ```bash
   python scripts/run_basic_simulation.py
   ```

2. Launch NetAnim for visualization:
   ```bash
   cd $NS3_DIR/netanim
   ./NetAnim
   ```
   Then open the generated XML file from the results directory.

## Simulation Scenarios
1. **baseline_scenario** - basic simulation with fixed nodes
2. **mobility_scenario** - scenario with mobile nodes using the RandomWalk model
3. **urban_scenario** - urban environment scenario with realistic node movement

## Visualizing Results
```bash
python visualization/plot_results.py --input results/simulation_output.json
```

## Examples
The `examples/` directory contains detailed examples of using the system for different scenarios.

## Performance Tips
- Use ccache to speed up repeated builds
- Only include necessary modules when configuring NS-3
- Use optimized build profile
- Use debug profile only when necessary during development
- Use ninja instead of make for faster builds

## Integration Architecture
The integration of NS-3 and BlockSim is implemented through an intermediate interface that synchronizes events between the two simulators and ensures data consistency.
# Simulation Scripts

Collection of simulation execution scripts for cross-zone blockchain experiments.

## Main Scripts

### Core Simulations
- `run_advanced_cross_zone_simulation.py` - Enhanced cross-zone with consensus validators
- `run_consensus_validator_simulation.py` - Standalone consensus validator system
- `run_basic_simulation.py` - Basic cross-zone functionality
- `run_5g_basestation_simulation.py` - 5G base station with MANET integration
- `run_single_basestation_simulation.py` - Single base station simulation

### Integration Scripts
- `run_simple_ns3_blocksim_integration.py` - Simple NS-3/BlockSim integration
- `run_5g_simulation.sh` - Shell wrapper for 5G simulation

### Utility Scripts
- `check_ns3.py` - NS-3 availability and functionality check
- `view_animation_stats.py` - NetAnim animation analysis
- `setup_netanim.sh` - NetAnim installation and setup

## Usage

For main simulation controller, use:
```bash
cd .. && python3 main_sim.py enhanced
```

For direct script execution:
```bash
python3 run_advanced_cross_zone_simulation.py --help
```

## Parameters

Common parameters across scripts:
- `--time T` - Simulation duration (seconds)
- `--nodes N` - Number of nodes
- `--output-dir DIR` - Results directory
- `--verbose` - Detailed logging

See individual script help for specific options 
# 6G MANET Blockchain-assisted Routing Simulation

Python-based simulation using ns-3 with nr module to validate Master's Thesis hypothesis about Blockchain-assisted routing in 6G MANET environments.

## Setup

1. Ensure ns-3 is built with Python bindings
2. Install Python dependencies: `pip install -r requirements.txt`
3. Set PYTHONPATH to include ns-3 bindings:
   ```bash
   export PYTHONPATH=/home/katae/study/dp/ns3/ns-3-dev/build/bindings/python:$PYTHONPATH
   ```

## Usage

Run simulation with baseline routing:
```bash
python src/sim/main_sim.py --mode baseline
```

Run simulation with proposed blockchain-assisted routing:
```bash
python src/sim/main_sim.py --mode proposed
```

## Project Structure

- `src/sim/main_sim.py` - Main simulation script
- `src/core/ledger.py` - BlockchainLedger implementation
- `src/core/routing.py` - RoutingEngine implementation
- `src/core/link_state.py` - LinkStateBuffer implementation
- `src/utils/metrics.py` - Metrics collection
- `tests/test_logic.py` - Unit tests
- `plot_results.py` - Results visualization


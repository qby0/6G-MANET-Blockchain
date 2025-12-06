# Installation and Setup Guide

## Prerequisites

1. **ns-3 with Python bindings**: Ensure ns-3 is built with Python bindings enabled
   - Path: `/home/katae/study/dp/ns3/ns-3-dev`
   - Python bindings should be in: `build/bindings/python`

2. **Python 3**: Python 3.6 or higher

3. **Python dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

## Setup Steps

1. **Set PYTHONPATH**:
   ```bash
   export PYTHONPATH=/home/katae/study/dp/ns3/ns-3-dev/build/bindings/python:$PYTHONPATH
   ```
   
   Or add to your `~/.bashrc`:
   ```bash
   echo 'export PYTHONPATH=/home/katae/study/dp/ns3/ns-3-dev/build/bindings/python:$PYTHONPATH' >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Verify ns-3 Python bindings**:
   ```bash
   cd /home/katae/study/dp/ns3/ns-3-dev
   python3 -c "import sys; sys.path.insert(0, 'build/bindings/python'); from ns import ns; print('NS-3 loaded:', hasattr(ns, 'NodeContainer'))"
   ```

3. **Run unit tests** (optional):
   ```bash
   cd /home/katae/study/dp/blockchain-routing-sim
   python3 -m pytest tests/test_logic.py -v
   ```

## Running Simulations

### Single Experiment

**Baseline routing**:
```bash
python3 src/sim/main_sim.py --mode baseline --num-nodes 25 --sim-time 10.0
```

**Proposed routing**:
```bash
python3 src/sim/main_sim.py --mode proposed --num-nodes 25 --sim-time 10.0
```

### Run Both Experiments

```bash
./run_experiments.sh
```

This will:
1. Run baseline experiment
2. Run proposed experiment  
3. Generate comparison plots

### Visualization

After running experiments, generate plots:
```bash
python3 plot_results.py \
    --baseline results/baseline_metrics.json \
    --proposed results/proposed_metrics.json \
    --output-dir results \
    --plot-type combined
```

## Configuration

Key parameters in `main_sim.py`:
- `--num-nodes`: Number of nodes (default: 25)
- `--sim-time`: Simulation time in seconds (default: 10.0)
- `--num-flows`: Number of UDP flows (default: 5)
- `--area-size`: Area size in meters (default: 500.0)
- `--seed`: Random seed (default: 1)

## Troubleshooting

1. **ModuleNotFoundError: No module named 'ns'**
   - Check PYTHONPATH is set correctly
   - Verify ns-3 Python bindings are built

2. **Import errors for project modules**
   - Ensure you're running from project root directory
   - Check that `src/` directory structure is correct

3. **NR module not found**
   - Verify nr module is enabled in ns-3 build
   - Check that `contrib/nr` exists in ns-3 directory


# 🎯 Usage Examples

This section contains ready-to-run simulation examples.

## 📋 Available Examples

### [`run_simulation.py`](run_simulation.py)
Main simulation runner script with multiple options.

**Usage:**
```bash
# Quick test
python3 run_simulation.py --quick-test --all-visualizations

# Standard simulation
python3 run_simulation.py --scenario medium_district --duration 600

# Full simulation with reports
python3 run_simulation.py --scenario large_city --duration 1200 --all-visualizations
```

**Options:**
- `--scenario` - scenario type (small_campus, medium_district, large_city)
- `--duration` - duration in seconds
- `--all-visualizations` - all visualization types
- `--quick-test` - quick test (60 seconds)

### [`demo_simulation.py`](demo_simulation.py)
Complete demonstration of all system capabilities.

**Usage:**
```bash
python3 demo_simulation.py
```

**What it does:**
1. Checks dependencies
2. Verifies files
3. Runs quick test
4. Executes full demonstration
5. Creates report

## 🚀 Quick Start

```bash
# Navigate to examples folder
cd examples

# Run demonstration
python3 demo_simulation.py
```

## 📊 Results

All results are saved to folders:
- `demo_results/` - quick test
- `demo_results_small_campus/` - small campus
- `demo_results_medium_district/` - medium district
- `results/` - latest simulation

## 🔧 Configuration

To modify simulation parameters, edit:
- [`../config/realistic_device_config.json`](../config/realistic_device_config.json) - device configuration
- Command line arguments in scripts

## 📚 Documentation

- [Main documentation](../docs/README_SIMULATION.md)
- [Device parameters](../docs/DEVICE_PARAMETERS.md)
- [Statistics analysis](../docs/STATISTICS_ANALYSIS.md) 
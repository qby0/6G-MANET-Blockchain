# 🚀 Advanced Cross-Zone Blockchain Simulation

Advanced cross-zone blockchain simulation with realistic device parameters and beautiful visualization.

## 📁 Project Structure

```
test_ns3_blocksim/
├── 📚 docs/                         # Documentation
│   ├── README_SIMULATION.md         # Simulation guide
│   ├── DEVICE_PARAMETERS.md         # Device parameters
│   ├── STATISTICS_ANALYSIS.md       # Statistics analysis
│   └── DEMO_REPORT.md              # Demo report
├── 🎯 examples/                     # Usage examples
│   ├── demo_simulation.py           # Complete demonstration
│   └── run_simulation.py           # Simulation runner
├── 💻 src/                         # Main source code
│   ├── simulation/                  # Simulation modules
│   │   └── advanced_realistic_simulation.py
│   ├── visualization/               # Visualization modules
│   │   └── enhanced_visualization.py
│   └── utils/                      # Utilities (empty)
├── 🔧 models/                      # Data models
│   └── realistic_device_manager.py
├── ⚙️ config/                       # Configuration files
│   └── realistic_device_config.json
├── 📊 scripts/                     # Executable scripts
│   ├── run_advanced_realistic_simulation.sh
│   ├── generate_all_animations.sh
│   ├── run_consensus_validator_test.sh
│   ├── run_advanced_cross_zone.sh
│   └── main_sim.py
├── 🧪 tests/                       # Tests
├── 📈 results/                     # Simulation results
├── 🎨 visualization/               # Static visualization
├── 🎬 animations/                  # Animations
├── 🔗 integration/                 # Integration modules
├── 📦 external/                    # External dependencies
└── 🗂️ temp/                        # Temporary files
    └── demo_archive/               # Demo archive
```

## 🚀 Quick Start

### 1. Install Dependencies
   ```bash
pip install -r requirements.txt
   ```

### 2. Quick Test
   ```bash
cd examples
python3 run_simulation.py --quick-test --all-visualizations
   ```

### 3. Full Demonstration
   ```bash
cd examples
python3 demo_simulation.py
   ```

## 📖 Key Features

### 🔧 Realistic Devices
- **Smartphones**: 10 GFLOPS, 8GB RAM, 4000mAh, mobile
- **IoT Sensors**: 0.5 GFLOPS, 512MB RAM, 2000mAh, static
- **Vehicles**: 30 GFLOPS, 8GB RAM, unlimited power
- **5G Base Stations**: 1200 GFLOPS, 64GB RAM
- **Edge Servers**: 2500 GFLOPS, 256GB RAM

### 📊 Visualization
- 12-panel dashboards
- Executive reports
- Interactive HTML charts
- Publication-ready plots

### 📈 Statistics
- Energy consumption by device
- Network performance
- Consensus and validation
- Mobility and zone transitions

## 🎯 Usage

### Example Commands

```bash
# Quick test (60 seconds)
python3 examples/run_simulation.py --quick-test --all-visualizations

# Medium district (10 minutes)
python3 examples/run_simulation.py --scenario medium_district --duration 600

# Large city with full reports
python3 examples/run_simulation.py --scenario large_city --duration 1200 --all-visualizations

# Complete demonstration of all scenarios
python3 examples/demo_simulation.py
```

### Available Scenarios
- `small_campus` - Small campus (68 devices, 1 km²)
- `medium_district` - Medium district (344 devices, 9 km²)
- `large_city` - Large city (1000+ devices, 25 km²)

## 📊 Results

All results are saved in the `results/` directory:
- 📊 `simulation_dashboard.png` - Main dashboard
- 👔 `executive_dashboard.png` - Executive report  
- 🌐 `interactive_dashboard.html` - Interactive charts
- 📋 `comprehensive_report.md` - Detailed report
- 📈 `simulation_summary.json` - JSON statistics

## 🔧 Configuration

### Device Parameters
Configured in `config/realistic_device_config.json`:
- CPU Performance
- Memory capacity
- Battery capacity
- Network interfaces
- Mobility models

### Simulation Scenarios
Defined in the same configuration file:
- Device distribution
- Area size
- Environmental conditions

## 🧪 Testing

```bash
# Run tests
python3 -m pytest tests/

# Integration tests
python3 tests/test_integration.py
```

## 📚 Documentation

- 📖 [`docs/README_SIMULATION.md`](docs/README_SIMULATION.md) - Detailed guide
- 🔧 [`docs/DEVICE_PARAMETERS.md`](docs/DEVICE_PARAMETERS.md) - Device parameters
- 📊 [`docs/STATISTICS_ANALYSIS.md`](docs/STATISTICS_ANALYSIS.md) - Data analysis
- 🧭 [`NAVIGATION.md`](NAVIGATION.md) - Project navigation
- 📂 [`STRUCTURE.md`](STRUCTURE.md) - Project structure
- 🌍 [`TRANSLATION_SUMMARY.md`](TRANSLATION_SUMMARY.md) - English translation notes

## 🤝 Development

### Adding New Devices
1. Update `config/realistic_device_config.json`
2. Add tests in `tests/`
3. Update documentation

### Adding New Visualizations
1. Extend `src/visualization/enhanced_visualization.py`
2. Add examples in `examples/`

## 📄 License

MIT License - see LICENSE file

## 👥 Authors

- Simulation Development: Advanced Blockchain Research Team
- Realistic Device Models: IoT Performance Lab
- Visualization: Data Science Visualization Group

---

*For help: `python3 examples/run_simulation.py --help`* 
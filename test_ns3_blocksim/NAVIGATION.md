# 🧭 Project Navigation

Quick navigation guide for the structured Advanced Cross-Zone Blockchain Simulation project.

## 🚀 Quick Access

### Running Simulations
```bash
# Demonstration
cd examples && python3 demo_simulation.py

# Quick test
cd examples && python3 run_simulation.py --quick-test --all-visualizations

# Full simulation
cd examples && python3 run_simulation.py --scenario medium_district --duration 600 --all-visualizations
```

### Main Files
- 📊 **Main Simulation**: [`src/simulation/advanced_realistic_simulation.py`](src/simulation/advanced_realistic_simulation.py)
- 🎨 **Visualization**: [`src/visualization/enhanced_visualization.py`](src/visualization/enhanced_visualization.py)
- 🔧 **Device Model**: [`models/realistic_device_manager.py`](models/realistic_device_manager.py)
- ⚙️ **Configuration**: [`config/realistic_device_config.json`](config/realistic_device_config.json)

## 📁 Directory Structure

### 📚 [`docs/`](docs/) - Documentation
| File | Description |
|------|-------------|
| [`README_SIMULATION.md`](docs/README_SIMULATION.md) | Detailed simulation guide |
| [`DEVICE_PARAMETERS.md`](docs/DEVICE_PARAMETERS.md) | Device parameters and characteristics |
| [`STATISTICS_ANALYSIS.md`](docs/STATISTICS_ANALYSIS.md) | Statistics and metrics analysis |
| [`DEMO_REPORT.md`](docs/DEMO_REPORT.md) | Demonstration report |

### 🎯 [`examples/`](examples/) - Usage Examples
| File | Description |
|------|-------------|
| [`demo_simulation.py`](examples/demo_simulation.py) | Complete demonstration of all features |
| [`run_simulation.py`](examples/run_simulation.py) | Main simulation runner script |

### 💻 [`src/`](src/) - Source Code
| Directory | Description |
|-----------|-------------|
| [`simulation/`](src/simulation/) | Core simulation modules |
| [`visualization/`](src/visualization/) | Data visualization modules |
| [`utils/`](src/utils/) | Utilities and helper functions |

### 🔧 [`models/`](models/) - Data Models
- [`realistic_device_manager.py`](models/realistic_device_manager.py) - Realistic device manager

### ⚙️ [`config/`](config/) - Configuration
- [`realistic_device_config.json`](config/realistic_device_config.json) - Device and scenario configuration

### 📊 [`scripts/`](scripts/) - Executable Scripts
| File | Description |
|------|-------------|
| [`main_sim.py`](scripts/main_sim.py) | Main simulation controller |
| [`run_advanced_realistic_simulation.sh`](scripts/run_advanced_realistic_simulation.sh) | Advanced simulation bash script |
| [`generate_all_animations.sh`](scripts/generate_all_animations.sh) | Animation generation |

### 📈 Results and Temporary Files
| Directory | Description |
|-----------|-------------|
| [`results/`](results/) | Current simulation results |
| [`temp/demo_archive/`](temp/demo_archive/) | Demo results archive |
| [`animations/`](animations/) | Generated animations |
| [`visualization/`](visualization/) | Static visualizations |

## 🎯 Workflows

### For Researchers
1. 📖 Read [`docs/README_SIMULATION.md`](docs/README_SIMULATION.md)
2. 🔧 Study [`docs/DEVICE_PARAMETERS.md`](docs/DEVICE_PARAMETERS.md)
3. 🚀 Run [`examples/demo_simulation.py`](examples/demo_simulation.py)
4. 📊 Analyze results in [`results/`](results/)

### For Developers
1. 💻 Study [`src/simulation/`](src/simulation/) and [`src/visualization/`](src/visualization/)
2. 🔧 Modify [`models/realistic_device_manager.py`](models/realistic_device_manager.py)
3. ⚙️ Update [`config/realistic_device_config.json`](config/realistic_device_config.json)
4. 🧪 Add tests in [`tests/`](tests/)

### For Teachers/Students
1. 🎯 Start with [`examples/run_simulation.py`](examples/run_simulation.py) `--help`
2. 📚 Study [`docs/STATISTICS_ANALYSIS.md`](docs/STATISTICS_ANALYSIS.md)
3. 🎨 View visualizations in [`results/`](results/)
4. 📋 Read reports in [`docs/DEMO_REPORT.md`](docs/DEMO_REPORT.md)

## 🔍 Finding Specific Components

### Energy Consumption
- **Calculation**: [`models/realistic_device_manager.py`](models/realistic_device_manager.py) → `calculate_energy_consumption()`
- **Analysis**: [`src/visualization/enhanced_visualization.py`](src/visualization/enhanced_visualization.py)
- **Configuration**: [`config/realistic_device_config.json`](config/realistic_device_config.json) → `power.consumption_mw`

### Consensus and Validation
- **Algorithm**: [`src/simulation/advanced_realistic_simulation.py`](src/simulation/advanced_realistic_simulation.py) → `_run_consensus_round()`
- **Requirements**: [`models/realistic_device_manager.py`](models/realistic_device_manager.py) → `get_consensus_requirements()`

### Mobility and Zones
- **Mobility Model**: [`src/simulation/advanced_realistic_simulation.py`](src/simulation/advanced_realistic_simulation.py) → `_update_device_mobility()`
- **Zone Transitions**: [`src/simulation/advanced_realistic_simulation.py`](src/simulation/advanced_realistic_simulation.py) → `_handle_zone_transition()`

### Visualization
- **Dashboards**: [`src/visualization/enhanced_visualization.py`](src/visualization/enhanced_visualization.py) → `create_executive_dashboard()`
- **Interactive Charts**: [`src/visualization/enhanced_visualization.py`](src/visualization/enhanced_visualization.py) → `create_interactive_dashboard()`

## 📞 Contact and Support

- 🐛 **Bugs**: Create an issue in the repository
- 💡 **Suggestions**: Discussion in discussions
- 📧 **Direct Contact**: Contacts in main README.md

---

*Use this file as a map to navigate the project!* 
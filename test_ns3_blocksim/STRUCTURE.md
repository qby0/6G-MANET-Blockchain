# 📂 Advanced Cross-Zone Blockchain Simulation Project Structure

## 🎯 Reorganization Overview

The project has been completely restructured to improve code organization, facilitate navigation, and simplify development.

## 📁 New Structure

```
test_ns3_blocksim/
├── 📖 README.md                     # Main project documentation
├── 🧭 NAVIGATION.md                 # Project navigation guide
├── 📂 STRUCTURE.md                  # This file - structure description
├── 📦 requirements.txt              # Python dependencies
├── 🚫 .gitignore                    # Git exclusions
│
├── 📚 docs/                         # 📚 DOCUMENTATION
│   ├── README_SIMULATION.md         # Detailed simulation guide
│   ├── DEVICE_PARAMETERS.md         # Device parameters and characteristics
│   ├── STATISTICS_ANALYSIS.md       # Statistics and metrics analysis
│   └── DEMO_REPORT.md              # Demonstration report
│
├── 🎯 examples/                     # 🎯 USAGE EXAMPLES
│   ├── README.md                    # Examples documentation
│   ├── demo_simulation.py           # Complete system demonstration
│   └── run_simulation.py           # Main runner script
│
├── 💻 src/                         # 💻 SOURCE CODE
│   ├── __init__.py
│   ├── simulation/                  # Simulation modules
│   │   ├── __init__.py
│   │   └── advanced_realistic_simulation.py
│   ├── visualization/               # Visualization modules
│   │   ├── __init__.py
│   │   └── enhanced_visualization.py
│   └── utils/                      # Utilities (for future expansion)
│       └── __init__.py
│
├── 🔧 models/                      # 🔧 DATA MODELS
│   └── realistic_device_manager.py # Realistic device manager
│
├── ⚙️ config/                       # ⚙️ CONFIGURATIONS
│   └── realistic_device_config.json # Device and scenario configuration
│
├── 📊 scripts/                     # 📊 EXECUTABLE SCRIPTS
│   ├── main_sim.py                 # Main simulation controller
│   ├── run_advanced_realistic_simulation.sh
│   ├── generate_all_animations.sh
│   ├── run_consensus_validator_test.sh
│   ├── run_advanced_cross_zone.sh
│   └── test_real_blocksim_integration.py
│
├── 🧪 tests/                       # 🧪 TESTING
│   └── [test modules]
│
├── 📈 results/                     # 📈 RESULTS
│   └── [simulation result files]
│
├── 🗂️ temp/                        # 🗂️ TEMPORARY FILES
│   ├── demo_archive/               # Demo archive
│   ├── env_paths.json             # Environment paths
│   └── __pycache__/               # Python cache
│
├── 🎨 visualization/               # 🎨 STATIC VISUALIZATION
│   └── [static visualizations]
│
├── 🎬 animations/                  # 🎬 ANIMATIONS
│   └── [generated animations]
│
├── 🔗 integration/                 # 🔗 INTEGRATION
│   └── [integration modules]
│
├── 📦 external/                    # 📦 EXTERNAL DEPENDENCIES
│   └── [external libraries]
│
├── 🌐 netanim/                     # 🌐 NETANIM
│   └── [NetAnim files]
│
├── 📡 test_ipc/                    # 📡 IPC TESTING
│   └── [inter-process communication]
│
└── 🐍 venv/                        # 🐍 VIRTUAL ENVIRONMENT
    └── [Python virtual environment]
```

## 🎯 Organization Principles

### 1. **Separation by Purpose**
- `src/` - main source code
- `examples/` - ready-to-use examples
- `docs/` - all documentation
- `config/` - configuration files
- `results/` - simulation results

### 2. **Modularity**
- Each module has clear responsibility
- Proper imports through Python packages
- `__init__.py` files for packages

### 3. **Usability**
- Examples in `examples/` ready to run
- Navigation through `NAVIGATION.md`
- README files in each important folder

### 4. **Cleanliness**
- Temporary files in `temp/`
- Results are archived
- Clear separation of code and data

## 🚀 Quick Access

### Running Simulations
```bash
cd examples
python3 demo_simulation.py                    # Complete demonstration
python3 run_simulation.py --quick-test        # Quick test
```

### Main Files
- **Simulation**: [`src/simulation/advanced_realistic_simulation.py`](src/simulation/advanced_realistic_simulation.py)
- **Visualization**: [`src/visualization/enhanced_visualization.py`](src/visualization/enhanced_visualization.py)
- **Devices**: [`models/realistic_device_manager.py`](models/realistic_device_manager.py)
- **Configuration**: [`config/realistic_device_config.json`](config/realistic_device_config.json)

## 📚 Documentation

| File | Description |
|------|-------------|
| [`README.md`](README.md) | Main documentation |
| [`NAVIGATION.md`](NAVIGATION.md) | Project navigation |
| [`docs/README_SIMULATION.md`](docs/README_SIMULATION.md) | Detailed guide |
| [`examples/README.md`](examples/README.md) | Usage examples |

## 🔄 Migration (What Changed)

### Before (pre-reorganization):
```
test_ns3_blocksim/
├── advanced_realistic_simulation.py
├── enhanced_visualization.py
├── demo_simulation.py
├── run_simulation.py
├── *.md files
├── *.sh scripts
└── many files in root
```

### After (post-reorganization):
```
test_ns3_blocksim/
├── src/simulation/advanced_realistic_simulation.py
├── src/visualization/enhanced_visualization.py
├── examples/demo_simulation.py
├── examples/run_simulation.py
├── docs/*.md
├── scripts/*.sh
└── clear folder structure
```

### Updated Imports:
```python
# Old way
from advanced_realistic_simulation import AdvancedRealisticSimulation

# New way
from src.simulation.advanced_realistic_simulation import AdvancedRealisticSimulation
```

## ✅ Benefits of New Structure

1. **📁 Organization**: Logical file separation by purpose
2. **🔍 Navigation**: Easy to find needed components
3. **🧪 Development**: Convenient to add new modules
4. **📚 Documentation**: All documentation in one place
5. **🎯 Examples**: Ready examples for quick start
6. **🔧 Scalability**: Easy to expand the project

## 🛠️ For Developers

### Adding New Modules:
1. **Simulation**: add to `src/simulation/`
2. **Visualization**: add to `src/visualization/`
3. **Utilities**: add to `src/utils/`
4. **Examples**: add to `examples/`
5. **Tests**: add to `tests/`

### Updating Documentation:
1. General documentation → `docs/`
2. Examples → `examples/README.md`
3. Modules → code comments

---

*Structure created for maximum convenience in using and developing the project* 🎯 
# 6G Mobility Model for MANET Simulations

This module implements an advanced mobility model suitable for 6G networks, combining elements of Gauss-Markov, Random Waypoint, and correlated mobility patterns with realistic parameters for 6G environments.

## Features

- **High-frequency position updates** suitable for mmWave/THz 6G environments
- **Correlated velocities** between nodes (drone swarms, vehicle platoons)
- **Dynamic clustering behavior** (nodes tend to form and dissolve groups)
- **Realistic acceleration/deceleration** patterns
- **Variable speed zones** with context-aware behavior
- **Support for 3D movement** (ground, aerial, building penetration)
- **Real-time visualization** with 2D/3D options

## Usage

### Basic Usage

```python
from test_ns3_blocksim.models.manet.mobility import SixGMobilityModel

# Create model with default parameters
model = SixGMobilityModel()

# Simulate 10 seconds of movement with 0.1s increments
for step in range(100):
    positions = model.update_positions(0.1)
    # Do something with the updated positions
```

### With Custom Configuration

```python
config = {
    "area_size": [1000, 1000, 100],  # x, y, z dimensions in meters
    "node_count": 50,
    "update_interval": 0.01,  # 10ms updates
    "min_speed": 0.5,         # m/s
    "max_speed": 30.0,        # m/s
    "alpha": 0.85,            # Memory level for Gauss-Markov
    "clustering_factor": 0.7, # How strongly nodes tend to cluster
    "3d_enabled": True        # Enable full 3D movement
}

model = SixGMobilityModel(config)
```

### Visualization

```python
from test_ns3_blocksim.models.manet.mobility.visualization import MobilityVisualizer

# Create visualizer
visualizer = MobilityVisualizer(model)

# Run animation
visualizer.animate(num_frames=200, interval=50)

# Create a heatmap of node density
visualizer.plot_trajectory_heatmap("mobility_heatmap.png")
```

## Running the Simulation Demo

A demo script is provided to showcase the mobility model:

```bash
# Activate the virtual environment
source test_ns3_blocksim/venv-mobility/bin/activate

# Run the demo with default settings
python test_ns3_blocksim/scripts/run_mobility_simulation.py

# Run with custom options
python test_ns3_blocksim/scripts/run_mobility_simulation.py --frames 300 --interval 20 --video --heatmap
```

## Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `area_size` | Simulation area dimensions (x, y, z) | [1000, 1000, 100] |
| `node_count` | Number of nodes in the simulation | 50 |
| `update_interval` | Time between position updates (seconds) | 0.01 |
| `min_speed` | Minimum node speed (m/s) | 0.5 |
| `max_speed` | Maximum node speed (m/s) | 30.0 |
| `alpha` | Memory factor for Gauss-Markov (0-1) | 0.85 |
| `clustering_factor` | Tendency of nodes to form clusters (0-1) | 0.7 |
| `speed_std_dev` | Standard deviation for speed changes | 1.5 |
| `direction_std_dev` | Standard deviation for direction changes | 0.2 |
| `pause_probability` | Probability of pausing at waypoint | 0.05 |
| `max_pause_time` | Maximum pause duration (seconds) | 5.0 |
| `3d_enabled` | Enable 3D movement | true |
| `context_zones` | Areas with special mobility behavior | [] |
| `correlated_nodes` | Groups of nodes with correlated movement | [] |

## Implementation Details

The 6G mobility model combines several mobility models to create realistic movement patterns:

1. **Gauss-Markov Process**: Provides smooth, temporally correlated movements
2. **Clustering Behavior**: Nodes tend to move toward each other and form groups
3. **Context-Aware Zones**: Areas where nodes change their behavior (e.g., slow down)
4. **Correlated Group Movement**: Groups of nodes can move in a coordinated way

## Visualization Options

The visualization tool provides several options:

- 2D or 3D views of node movement
- Node trails showing recent movement history
- Velocity vectors showing direction and speed
- Density heatmaps showing node concentration
- Video generation for presentations
- Customizable colors and appearance

## Integration with NS-3

This mobility model is designed to work with NS-3 for network simulations through the NS3Adapter. 
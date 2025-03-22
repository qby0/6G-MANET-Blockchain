#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced 6G Mobility Model for MANET simulations
This model implements an advanced mobility pattern suitable for 6G networks,
combining elements of Gauss-Markov, Random Waypoint, and correlated mobility
patterns with realistic parameters for 6G environments.
"""

import logging
import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union

logger = logging.getLogger(__name__)

class SixGMobilityModel:
    """
    Advanced 6G Mobility Model that simulates realistic movement patterns
    in high-density, high-speed 6G environments with dynamic clustering behavior.
    
    Features:
    - High-frequency position updates suitable for mmWave/THz 6G environments
    - Correlated velocities between nodes (drone swarms, vehicle platoons)
    - Dynamic clustering behavior (nodes tend to form and dissolve groups)
    - Realistic acceleration/deceleration patterns
    - Variable speed zones with context-aware behavior
    - Support for 3D movement (ground, aerial, building penetration)
    - Random jump modeling to simulate connection loss or signal interference
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the 6G Mobility Model.
        
        Args:
            config: Configuration dictionary for the mobility model
        """
        self.logger = logging.getLogger("SixGMobilityModel")
        
        # Default configuration suitable for 6G simulations
        default_config = {
            "area_size": [1000, 1000, 100],  # x, y, z dimensions in meters
            "node_count": 50,
            "update_interval": 0.1,  # Increased from 0.01 to 0.1 seconds for more visible movement
            "min_speed": 5.0,         # Increased from 0.5 to 5.0 m/s
            "max_speed": 50.0,        # Increased from 30.0 to 50.0 m/s
            "alpha": 0.85,            # Memory level for Gauss-Markov
            "clustering_factor": 0.7, # How strongly nodes tend to cluster
            "speed_std_dev": 2.5,     # Increased from 1.5 to 2.5
            "direction_std_dev": 0.3, # Increased from 0.2 to 0.3
            "pause_probability": 0.01, # Decreased from 0.05 to 0.01
            "max_pause_time": 2.0,    # Decreased from 5.0 to 2.0 seconds
            "context_zones": [        # Special areas with different mobility behaviors
                {
                    "center": [500, 500, 0],
                    "radius": 100,
                    "speed_factor": 0.5,
                    "clustering_factor": 0.9
                }
            ],
            "3d_enabled": True,       # Enable full 3D movement
            "building_penetration": True, # Allow movement through buildings (with signal attenuation)
            "correlated_nodes": [],    # Groups of node IDs whose movements are correlated
            "random_jump_probability": 0.03, # Increased from 0.01 to 0.03
            "max_jump_distance": 200.0  # Maximum distance a node can jump (in meters)
        }
        
        # Merge provided config with defaults
        self.config = default_config.copy()
        if config:
            self.config.update(config)
            
        self.logger.info("Initialized 6G Mobility Model with %d nodes", self.config["node_count"])
        
        # Initialize node positions, velocities, and states
        self.node_positions = np.zeros((self.config["node_count"], 3))
        self.node_velocities = np.zeros((self.config["node_count"], 3))
        self.node_targets = np.zeros((self.config["node_count"], 3))
        self.node_states = ["moving"] * self.config["node_count"]
        self.node_pause_times = np.zeros(self.config["node_count"])
        
        # Initialize with random positions and velocities
        self._initialize_nodes()
        
        # Mobility history for trajectory analysis
        self.position_history = []
        
        # Connection status tracking
        self.connection_status = np.ones(self.config["node_count"], dtype=bool)
        
    def _initialize_nodes(self):
        """Initialize node positions and velocities with realistic distributions"""
        # Random initial positions within area
        self.node_positions = np.random.rand(self.config["node_count"], 3)
        self.node_positions[:, 0] *= self.config["area_size"][0]
        self.node_positions[:, 1] *= self.config["area_size"][1]
        
        if self.config["3d_enabled"]:
            self.node_positions[:, 2] *= self.config["area_size"][2]
        else:
            self.node_positions[:, 2] = 0.0
            
        # Initialize with random velocities
        for i in range(self.config["node_count"]):
            self._assign_random_velocity(i)
            
        # Set random target positions
        self._update_targets()
        
        self.logger.debug("Nodes initialized with random positions and velocities")
        
    def _assign_random_velocity(self, node_id: int):
        """Assign a random velocity to a node within the configured bounds"""
        speed = np.random.uniform(self.config["min_speed"], self.config["max_speed"])
        
        # Random direction
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.random.uniform(0, np.pi) if self.config["3d_enabled"] else np.pi/2
        
        # Convert spherical to cartesian coordinates
        self.node_velocities[node_id, 0] = speed * np.sin(phi) * np.cos(theta)
        self.node_velocities[node_id, 1] = speed * np.sin(phi) * np.sin(theta)
        self.node_velocities[node_id, 2] = speed * np.cos(phi) if self.config["3d_enabled"] else 0.0
        
    def _update_targets(self):
        """Update target destinations for all nodes"""
        for i in range(self.config["node_count"]):
            if self.node_states[i] == "moving" and np.all(np.isclose(self.node_positions[i], self.node_targets[i], atol=1.0)):
                # Node reached target, decide whether to pause
                if np.random.random() < self.config["pause_probability"]:
                    self.node_states[i] = "paused"
                    self.node_pause_times[i] = np.random.uniform(0, self.config["max_pause_time"])
                    self.node_velocities[i] = np.zeros(3)
                else:
                    # Set new target
                    self._set_new_target(i)
            elif self.node_states[i] == "paused":
                # Check if pause time is over
                self.node_pause_times[i] -= self.config["update_interval"]
                if self.node_pause_times[i] <= 0:
                    self.node_states[i] = "moving"
                    self._set_new_target(i)
    
    def _set_new_target(self, node_id: int):
        """Set a new target position for a specific node, with clustering behavior"""
        # With some probability, target moves toward a cluster center
        if np.random.random() < self.config["clustering_factor"]:
            # Find a random other node to move toward
            other_node = np.random.randint(0, self.config["node_count"])
            if other_node != node_id:
                # Target is halfway between current position and other node
                self.node_targets[node_id] = 0.5 * (self.node_positions[node_id] + self.node_positions[other_node])
                # Add some randomness
                self.node_targets[node_id] += np.random.normal(0, 50, 3)
        else:
            # Random waypoint within bounds
            self.node_targets[node_id, 0] = np.random.uniform(0, self.config["area_size"][0])
            self.node_targets[node_id, 1] = np.random.uniform(0, self.config["area_size"][1])
            if self.config["3d_enabled"]:
                self.node_targets[node_id, 2] = np.random.uniform(0, self.config["area_size"][2])
            else:
                self.node_targets[node_id, 2] = 0.0
                
        # Calculate new velocity vector toward target
        direction = self.node_targets[node_id] - self.node_positions[node_id]
        distance = np.linalg.norm(direction)
        if distance > 0:
            direction = direction / distance
            speed = np.random.uniform(self.config["min_speed"], self.config["max_speed"])
            self.node_velocities[node_id] = direction * speed
    
    def _apply_random_jumps(self):
        """Apply random jumps to simulate connection loss or radio interference"""
        for i in range(self.config["node_count"]):
            # Only apply to moving nodes with some probability
            if self.node_states[i] == "moving" and np.random.random() < self.config.get("random_jump_probability", 0.01):
                # Generate a random jump vector
                jump_distance = np.random.uniform(0, self.config.get("max_jump_distance", 200.0))
                
                # Random direction in 3D or 2D space
                theta = np.random.uniform(0, 2 * np.pi)
                if self.config["3d_enabled"]:
                    phi = np.random.uniform(0, np.pi)
                    jump_vector = np.array([
                        jump_distance * np.sin(phi) * np.cos(theta),
                        jump_distance * np.sin(phi) * np.sin(theta),
                        jump_distance * np.cos(phi)
                    ])
                else:
                    jump_vector = np.array([
                        jump_distance * np.cos(theta),
                        jump_distance * np.sin(theta),
                        0.0
                    ])
                
                # Apply the jump
                self.node_positions[i] += jump_vector
                
                # Ensure we're still within bounds
                for d in range(3):
                    if d == 2 and not self.config["3d_enabled"]:
                        self.node_positions[i, d] = 0.0
                    else:
                        self.node_positions[i, d] = np.clip(
                            self.node_positions[i, d],
                            0,
                            self.config["area_size"][d]
                        )
                
                # Update connection status to simulate temporary disconnection
                self.connection_status[i] = False
                
                self.logger.debug(f"Node {i} performed a random jump of {jump_distance:.2f}m")
            else:
                # Reset connection status (node reconnects after a jump)
                self.connection_status[i] = True
    
    def update_positions(self, time_delta: float = None):
        """
        Update node positions based on their velocities and the mobility model.
        
        Args:
            time_delta: Time step in seconds, defaults to update_interval if None
        """
        if time_delta is None:
            time_delta = self.config["update_interval"]
            
        # Update positions based on Gauss-Markov process
        for i in range(self.config["node_count"]):
            if self.node_states[i] == "moving":
                # Get current velocity
                current_vel = self.node_velocities[i].copy()
                current_speed = np.linalg.norm(current_vel)
                
                if current_speed > 0:
                    current_direction = current_vel / current_speed
                else:
                    # If speed is zero, assign a random direction
                    theta = np.random.uniform(0, 2 * np.pi)
                    phi = np.random.uniform(0, np.pi) if self.config["3d_enabled"] else np.pi/2
                    current_direction = np.array([
                        np.sin(phi) * np.cos(theta),
                        np.sin(phi) * np.sin(theta),
                        np.cos(phi) if self.config["3d_enabled"] else 0.0
                    ])
                
                # Gauss-Markov mobility model
                alpha = self.config["alpha"]
                
                # Calculate new speed with Gauss-Markov process
                mean_speed = (self.config["min_speed"] + self.config["max_speed"]) / 2
                new_speed = (alpha * current_speed + 
                             (1 - alpha) * mean_speed + 
                             np.sqrt(1 - alpha**2) * np.random.normal(0, self.config["speed_std_dev"]))
                
                # Ensure speed is within bounds
                new_speed = np.clip(new_speed, self.config["min_speed"], self.config["max_speed"])
                
                # Calculate new direction with Gauss-Markov process
                # Add small Gaussian noise to each direction component
                new_direction = np.zeros(3)
                for d in range(3):
                    if d == 2 and not self.config["3d_enabled"]:
                        new_direction[d] = 0.0
                    else:
                        new_direction[d] = (alpha * current_direction[d] + 
                                           np.sqrt(1 - alpha**2) * np.random.normal(0, self.config["direction_std_dev"]))
                
                # Normalize new direction
                direction_norm = np.linalg.norm(new_direction)
                if direction_norm > 0:
                    new_direction = new_direction / direction_norm
                
                # Calculate new velocity vector
                self.node_velocities[i] = new_direction * new_speed
                
                # Apply the velocity to update the node's position
                self.node_positions[i] += self.node_velocities[i] * time_delta
                
                # Check if we need to adjust for boundaries
                for d in range(3):
                    if d == 2 and not self.config["3d_enabled"]:
                        continue
                        
                    # If node hits a boundary, reflect the direction
                    if self.node_positions[i, d] < 0:
                        self.node_positions[i, d] = 0
                        self.node_velocities[i, d] = -self.node_velocities[i, d]
                    elif self.node_positions[i, d] > self.config["area_size"][d]:
                        self.node_positions[i, d] = self.config["area_size"][d]
                        self.node_velocities[i, d] = -self.node_velocities[i, d]
                        
        # Store position history
        self.position_history.append(self.node_positions.copy())
        if len(self.position_history) > 1000:  # Limit history size
            self.position_history.pop(0)
            
        # Apply random jumps
        self._apply_random_jumps()
        
        # Update targets
        self._update_targets()
        
        # Apply correlations between nodes
        self._apply_node_correlation()
        
        return self.get_positions()
    
    def _apply_node_correlation(self):
        """Apply correlation between movements of specified node groups"""
        for group in self.config["correlated_nodes"]:
            if not group or len(group) < 2:
                continue
                
            # Calculate average velocity for the group
            avg_velocity = np.zeros(3)
            for node_id in group:
                if node_id < self.config["node_count"] and self.node_states[node_id] == "moving":
                    avg_velocity += self.node_velocities[node_id]
            
            avg_velocity /= len(group)
            
            # Apply correlation by adjusting velocities toward the average
            correlation_strength = 0.5  # How strongly to correlate movements
            for node_id in group:
                if node_id < self.config["node_count"] and self.node_states[node_id] == "moving":
                    self.node_velocities[node_id] = (1 - correlation_strength) * self.node_velocities[node_id] + \
                                                  correlation_strength * avg_velocity
    
    def get_positions(self) -> np.ndarray:
        """Get current positions of all nodes"""
        return self.node_positions.copy()
    
    def get_velocities(self) -> np.ndarray:
        """Get current velocities of all nodes"""
        return self.node_velocities.copy()
    
    def get_connection_status(self) -> np.ndarray:
        """Get connection status for all nodes (True = connected, False = disconnected)"""
        return self.connection_status.copy()
        
    def get_trajectory_data(self) -> Dict[str, Any]:
        """Get trajectory data for visualization and analysis"""
        return {
            "position_history": self.position_history.copy(),
            "current_positions": self.node_positions.copy(),
            "current_velocities": self.node_velocities.copy(),
            "node_states": self.node_states.copy(),
            "connection_status": self.connection_status.copy()
        }
        
    def __str__(self) -> str:
        """String representation of the model"""
        return f"SixGMobilityModel(nodes={self.config['node_count']}, area={self.config['area_size']})"


# For testing the model
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create model with default parameters
    model = SixGMobilityModel()
    
    # Simulate 10 seconds of movement
    for step in range(100):
        positions = model.update_positions(0.1)
        logger.info(f"Step {step}: Updated {len(positions)} node positions")
        
    logger.info("Simulation complete") 
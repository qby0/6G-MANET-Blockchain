#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Blockchain Mobility Visualization
This module extends mobility visualization with blockchain status
"""

import logging
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from typing import Dict, Any, List, Optional

from models.manet.mobility.visualization import MobilityVisualizer
from models.manet.blockchain.blockchain_integration import BlockchainMobilityIntegration

logger = logging.getLogger(__name__)

class BlockchainMobilityVisualizer(MobilityVisualizer):
    """
    Enhanced visualizer showing both mobility and blockchain status
    """
    
    def __init__(self, blockchain_integration: BlockchainMobilityIntegration, config: Dict[str, Any] = None):
        """
        Initialize the blockchain-mobility visualizer.
        
        Args:
            blockchain_integration: The blockchain-mobility integration to visualize
            config: Optional visualization configuration
        """
        # Initialize parent with mobility model
        super().__init__(blockchain_integration.mobility_model, config)
        
        self.blockchain_integration = blockchain_integration
        self.logger = logging.getLogger("BlockchainMobilityVisualizer")
        
        # Add blockchain-specific visualization elements
        self._setup_blockchain_visualization()
        
    def _setup_blockchain_visualization(self):
        """Set up visualization elements for blockchain"""
        # Create subplot for blockchain metrics
        self.blockchain_ax = self.fig.add_axes([0.75, 0.75, 0.2, 0.2])
        self.blockchain_ax.set_title("Blockchain Status")
        self.blockchain_ax.axis('off')
        
        # Text for blockchain metrics
        self.blockchain_text = self.blockchain_ax.text(
            0.05, 0.95, "Initializing...", 
            transform=self.blockchain_ax.transAxes,
            verticalalignment='top'
        )
        
        # Modify node colors to show validators
        self.validator_nodes = self.blockchain_integration.validators
        self._update_node_colors()
        
        # Add connection lines between nodes
        self.connections = []
    
    def _update_node_colors(self):
        """Update node colors based on validator status"""
        colors = []
        for i in range(self.mobility_model.config["node_count"]):
            if i in self.validator_nodes:
                colors.append(self.config["validator_color"])
            else:
                colors.append(self.config["node_color"])
                
        self.scatter.set_color(colors)
    
    def _update_blockchain_text(self):
        """Update the blockchain status text"""
        state = self.blockchain_integration.network_state
        
        if not state:
            return
            
        text = (
            f"Time: {state['time']:.1f}s\n"
            f"Blocks: {state['block_count']}\n"
            f"Trans: {state['total_transactions']}\n"
            f"Connect: {state['avg_connections']:.1f}\n"
            f"Validators: {state['validator_count']}"
        )
        
        self.blockchain_text.set_text(text)
    
    def _draw_connections(self):
        """Draw connection lines between connected nodes"""
        # Remove old connections
        for conn in self.connections:
            conn.remove()
        self.connections = []
        
        # Get current node positions and connectivity matrix
        positions = self.mobility_model.get_positions()
        connectivity = self.blockchain_integration.connectivity_matrix
        
        # Plot connections (limit to avoid overplotting)
        max_connections = 100  # Limit to avoid too many lines
        count = 0
        
        for i in range(connectivity.shape[0]):
            for j in range(i+1, connectivity.shape[1]):
                if connectivity[i, j] and count < max_connections:
                    if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
                        line = self.ax.plot3D(
                            [positions[i, 0], positions[j, 0]],
                            [positions[i, 1], positions[j, 1]],
                            [positions[i, 2], positions[j, 2]],
                            color='white', alpha=0.1, linewidth=0.5
                        )[0]
                    else:
                        line = self.ax.plot(
                            [positions[i, 0], positions[j, 0]],
                            [positions[i, 1], positions[j, 1]],
                            color='white', alpha=0.1, linewidth=0.5
                        )[0]
                    
                    self.connections.append(line)
                    count += 1
    
    def update(self, frame_num: int):
        """
        Update both mobility and blockchain visualizations.
        
        Args:
            frame_num: The frame number
            
        Returns:
            List of updated artists
        """
        # Update blockchain integration
        self.blockchain_integration.update(self.config["update_interval"])
        
        # Call parent update (updates mobility model)
        artists = super().update(frame_num)
        
        # Update blockchain visualization elements
        self._update_blockchain_text()
        self._draw_connections()
        
        # Add blockchain-specific artists to return list
        artists.append(self.blockchain_text)
        artists.extend(self.connections)
        
        return artists
    
    def create_blockchain_heatmap(self, output_file: Optional[str] = None):
        """
        Create a heatmap showing blockchain connectivity density.
        
        Args:
            output_file: Path to save the heatmap image
        """
        plt.figure(figsize=(12, 10))
        
        # Create a grid to store node density with connection info
        area_size = self.mobility_model.config["area_size"]
        grid_size = 50
        
        # Initialize grid for connection density
        connectivity_grid = np.zeros((grid_size, grid_size))
        
        # Get all positions from history and connectivity matrices
        history = self.mobility_model.position_history
        
        if not history:
            self.logger.warning("No position history available for heatmap")
            return
            
        # For each timestep
        for step_idx, positions in enumerate(history):
            # Map positions to grid cells
            for node_idx, pos in enumerate(positions):
                # Get grid indices
                x_idx = min(grid_size-1, int(pos[0] / area_size[0] * grid_size))
                y_idx = min(grid_size-1, int(pos[1] / area_size[1] * grid_size))
                
                # Increment grid by connection count
                connection_count = np.sum(self.blockchain_integration.connectivity_matrix[node_idx])
                connectivity_grid[y_idx, x_idx] += connection_count
        
        # Normalize the grid
        if np.max(connectivity_grid) > 0:
            connectivity_grid = connectivity_grid / np.max(connectivity_grid)
        
        # Plot connection density heatmap
        plt.subplot(121)
        plt.imshow(
            connectivity_grid,
            origin='lower',
            extent=[0, area_size[0], 0, area_size[1]],
            aspect='auto',
            cmap='plasma'
        )
        plt.colorbar(label='Normalized Connection Density')
        plt.title('Blockchain Connection Density')
        plt.xlabel('X (meters)')
        plt.ylabel('Y (meters)')
        
        # Plot regular node density heatmap for comparison
        plt.subplot(122)
        
        # Flatten all positions into a single array
        all_positions = np.vstack([pos for pos in history])
        
        # Create 2D histogram
        node_heatmap, xedges, yedges = np.histogram2d(
            all_positions[:, 0], 
            all_positions[:, 1], 
            bins=grid_size, 
            range=[[0, area_size[0]], [0, area_size[1]]]
        )
        
        plt.imshow(
            node_heatmap.T,
            origin='lower',
            extent=[0, area_size[0], 0, area_size[1]],
            aspect='auto',
            cmap='viridis'
        )
        plt.colorbar(label='Node Count')
        plt.title('Node Density')
        plt.xlabel('X (meters)')
        plt.ylabel('Y (meters)')
        
        plt.tight_layout()
        
        # Show or save
        if output_file:
            plt.savefig(output_file, dpi=150)
            self.logger.info("Blockchain heatmap saved to: %s", output_file)
        else:
            plt.show() 
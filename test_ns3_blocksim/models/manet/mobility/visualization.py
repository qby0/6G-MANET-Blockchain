#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
6G Mobility Model Visualization Tool
This module provides visualization capabilities for the 6G mobility model,
allowing for real-time and post-simulation analysis of node movements.
"""

import logging
import os
import time
import random
from typing import Dict, List, Tuple, Optional, Any, Union

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

# Import the mobility model
from models.manet.mobility.sixg_mobility_model import SixGMobilityModel

logger = logging.getLogger(__name__)

# Define a 3D arrow class for packet transmission visualization
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)
        
    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return min(zs)

class MobilityVisualizer:
    """
    Visualization tool for 6G mobility model simulation results.
    Provides real-time and post-simulation visualization of node movements.
    """
    
    def __init__(self, mobility_model: SixGMobilityModel, config: Dict[str, Any] = None):
        """
        Initialize the visualizer with a mobility model.
        
        Args:
            mobility_model: The 6G mobility model to visualize
            config: Optional configuration for the visualization
        """
        self.logger = logging.getLogger("MobilityVisualizer")
        self.mobility_model = mobility_model
        
        # Default visualization configuration
        default_config = {
            "update_interval": 0.1,  # Update interval in seconds
            "trail_length": 20,     # Number of history points to show in trail
            "node_size": 50,        # Size of node markers
            "validator_color": "red", # Color for validator nodes
            "node_color": "blue",    # Color for regular nodes
            "disconnected_color": "gray", # Color for disconnected nodes
            "background_color": "#f0f0f0",  # Light gray background
            "show_velocity": True,   # Whether to show velocity vectors
            "velocity_scale": 1.0,   # Scale factor for velocity vectors
            "show_grid": True,       # Show grid on the plot
            "node_alpha": 0.7,       # Transparency for nodes
            "title": "6G Network Mobility Simulation",
            "show_3d": True,         # Show 3D visualization if model is 3D
            "save_frames": False,    # Save frames as images
            "frames_dir": "mobility_frames",  # Directory to save frames
            "frame_format": "png",   # Format for saved frames
            "validators": [],        # List of validator node IDs
            "zone_alpha": 0.2,       # Transparency for context zones
            "trail_fade": True,      # Fade trail colors from dark to light
            "show_packets": True,    # Show packet transmissions
            "packet_rate": 0.1,      # Probability of packet transmission per node per frame
            "connection_range": 120, # Maximum distance for node communication
            "packet_color": "green", # Color of packet transmission visualization
            "packet_width": 1.5,     # Width of packet transmission lines
            "packet_alpha": 0.8      # Transparency of packet transmissions
        }
        
        # Merge provided config with defaults
        self.config = default_config.copy()
        if config:
            self.config.update(config)
            
        # If validators not provided, use 20% of nodes as validators
        if not self.config["validators"]:
            node_count = self.mobility_model.config["node_count"]
            validator_count = int(node_count * 0.2)
            self.config["validators"] = list(range(validator_count))
            
        # Initialize figure and plot
        plt.style.use('dark_background' if self.config["background_color"] == "black" else "default")
        
        # Create 3D or 2D figure based on configuration
        if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
            self.fig = plt.figure(figsize=(10, 8))
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.fig = plt.figure(figsize=(10, 8))
            self.ax = self.fig.add_subplot(111)
            
        # Set background color
        self.fig.patch.set_facecolor(self.config["background_color"])
        self.ax.set_facecolor(self.config["background_color"])
        
        # Setup plot limits and labels
        self._setup_plot()
        
        # Prepare node scatter plot
        positions = self.mobility_model.get_positions()
        colors = self._get_node_colors()
        
        if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
            self.scatter = self.ax.scatter(
                positions[:, 0], 
                positions[:, 1], 
                positions[:, 2],
                c=colors, 
                s=self.config["node_size"],
                alpha=self.config["node_alpha"]
            )
        else:
            self.scatter = self.ax.scatter(
                positions[:, 0], 
                positions[:, 1], 
                c=colors, 
                s=self.config["node_size"],
                alpha=self.config["node_alpha"]
            )
            
        # Prepare velocity quiver plot if enabled
        if self.config["show_velocity"]:
            velocities = self.mobility_model.get_velocities()
            if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
                self.quiver = self.ax.quiver(
                    positions[:, 0], 
                    positions[:, 1], 
                    positions[:, 2],
                    velocities[:, 0], 
                    velocities[:, 1], 
                    velocities[:, 2],
                    color='white', 
                    alpha=0.5,
                    length=self.config["velocity_scale"] * 10
                )
            else:
                self.quiver = self.ax.quiver(
                    positions[:, 0], 
                    positions[:, 1], 
                    velocities[:, 0], 
                    velocities[:, 1],
                    color='white', 
                    alpha=0.5,
                    scale=self.config["velocity_scale"] * 10
                )
        else:
            self.quiver = None
            
        # Prepare trails (node movement history)
        self.trails = []
        
        # Initialize packet transmission visualization
        self.packet_arrows = []
        
        # Initialize legend
        self._setup_legend()
        
        # For saving frames
        if self.config["save_frames"]:
            os.makedirs(self.config["frames_dir"], exist_ok=True)
            self.frame_count = 0
            
        self.logger.info("Mobility visualizer initialized")
        
    def _setup_plot(self):
        """Configure the plot with correct limits, labels, etc."""
        area_size = self.mobility_model.config["area_size"]
        
        # Set labels
        self.ax.set_xlabel('X (meters)')
        self.ax.set_ylabel('Y (meters)')
        if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
            self.ax.set_zlabel('Z (meters)')
            
        # Set limits
        self.ax.set_xlim(0, area_size[0])
        self.ax.set_ylim(0, area_size[1])
        if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
            self.ax.set_zlim(0, area_size[2])
            
        # Grid
        if self.config["show_grid"]:
            self.ax.grid(True, alpha=0.3)
            
        # Title
        self.ax.set_title(self.config["title"])
        
        # Show context zones if any
        for zone in self.mobility_model.config["context_zones"]:
            center = zone["center"]
            radius = zone["radius"]
            
            # Draw a circle for the zone (or sphere in 3D)
            if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
                # Create a wireframe sphere (simplified)
                u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
                x = center[0] + radius * np.cos(u) * np.sin(v)
                y = center[1] + radius * np.sin(u) * np.sin(v)
                z = center[2] + radius * np.cos(v)
                self.ax.plot_wireframe(x, y, z, color='yellow', alpha=self.config["zone_alpha"])
            else:
                # Create a circle
                circle = plt.Circle(
                    (center[0], center[1]), 
                    radius, 
                    color='yellow', 
                    fill=True, 
                    alpha=self.config["zone_alpha"]
                )
                self.ax.add_patch(circle)
    
    def _get_node_colors(self) -> List[str]:
        """Determine colors for nodes based on their role and connection status"""
        colors = []
        connection_status = self.mobility_model.get_connection_status()
        
        for i in range(self.mobility_model.config["node_count"]):
            if not connection_status[i]:
                colors.append(self.config["disconnected_color"])
            elif i in self.config["validators"]:
                colors.append(self.config["validator_color"])
            else:
                colors.append(self.config["node_color"])
        return colors
    
    def _setup_legend(self):
        """Add a legend to the plot"""
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor=self.config["node_color"],
                   markersize=10, label='Regular Node'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=self.config["validator_color"],
                   markersize=10, label='Validator Node'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=self.config["disconnected_color"],
                   markersize=10, label='Disconnected Node')
        ]
        
        # Add packet transmission to legend
        if self.config["show_packets"]:
            legend_elements.append(
                Line2D([0], [0], color=self.config["packet_color"], linestyle='-',
                       markersize=10, label='Packet Transmission')
            )
        
        # Add context zone to legend if any exist
        if self.mobility_model.config["context_zones"]:
            legend_elements.append(
                Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow',
                       markersize=10, alpha=self.config["zone_alpha"], label='Context Zone')
            )
            
        self.ax.legend(handles=legend_elements, loc='upper right')
    
    def _generate_packet_transmissions(self, positions):
        """Generate random packet transmissions between nodes that are within range"""
        # Remove previous packet arrows
        for arrow in self.packet_arrows:
            arrow.remove()
        self.packet_arrows = []
        
        # Get connection status
        connection_status = self.mobility_model.get_connection_status()
        
        # For each node, randomly decide if it will transmit packets
        for i in range(self.mobility_model.config["node_count"]):
            # Skip disconnected nodes
            if not connection_status[i]:
                continue
                
            # Randomly decide to transmit a packet with configured probability
            if np.random.random() < self.config["packet_rate"]:
                # Find all nodes within connection range
                for j in range(self.mobility_model.config["node_count"]):
                    # Skip self or disconnected receivers
                    if i == j or not connection_status[j]:
                        continue
                        
                    # Calculate distance between nodes
                    distance = np.linalg.norm(positions[i] - positions[j])
                    
                    # If within connection range, create a packet transmission visualization
                    if distance <= self.config["connection_range"]:
                        if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
                            # 3D arrow
                            arrow = Arrow3D(
                                [positions[i, 0], positions[j, 0]],
                                [positions[i, 1], positions[j, 1]],
                                [positions[i, 2], positions[j, 2]],
                                mutation_scale=10,
                                lw=self.config["packet_width"],
                                arrowstyle="-|>",
                                color=self.config["packet_color"],
                                alpha=self.config["packet_alpha"]
                            )
                            self.ax.add_artist(arrow)
                        else:
                            # 2D arrow
                            arrow = self.ax.arrow(
                                positions[i, 0],
                                positions[i, 1],
                                positions[j, 0] - positions[i, 0],
                                positions[j, 1] - positions[i, 1],
                                head_width=10,
                                head_length=10,
                                fc=self.config["packet_color"],
                                ec=self.config["packet_color"],
                                alpha=self.config["packet_alpha"],
                                width=self.config["packet_width"]
                            )
                        
                        self.packet_arrows.append(arrow)
                        
                        # Only generate one packet per node to avoid cluttering
                        break
                        
        return self.packet_arrows
    
    def update(self, frame_num: int):
        """
        Update the visualization for animation.
        
        Args:
            frame_num: The current frame number
        
        Returns:
            List of artists that were updated
        """
        # Update node positions in the model - ensure time_delta is used
        positions = self.mobility_model.update_positions(time_delta=self.config["update_interval"])
        
        # Log position changes for debugging
        if frame_num % 10 == 0:  # Log every 10 frames to avoid spam
            self.logger.debug(f"Frame {frame_num}: Position of node 0: {positions[0]}")
            velocities = self.mobility_model.get_velocities()
            self.logger.debug(f"Frame {frame_num}: Velocity of node 0: {velocities[0]}")
        
        # Update node colors based on connection status
        colors = self._get_node_colors()
        self.scatter.set_color(colors)
        
        # Clear previous scatter plot and create a new one with updated positions
        self.scatter.remove()
        if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
            self.scatter = self.ax.scatter(
                positions[:, 0], 
                positions[:, 1], 
                positions[:, 2],
                c=colors, 
                s=self.config["node_size"],
                alpha=self.config["node_alpha"]
            )
        else:
            self.scatter = self.ax.scatter(
                positions[:, 0], 
                positions[:, 1], 
                c=colors, 
                s=self.config["node_size"],
                alpha=self.config["node_alpha"]
            )
            
        # Update velocity vectors if enabled
        if self.config["show_velocity"]:
            velocities = self.mobility_model.get_velocities()
            if self.quiver:
                self.quiver.remove()
            
            if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
                self.quiver = self.ax.quiver(
                    positions[:, 0], 
                    positions[:, 1], 
                    positions[:, 2],
                    velocities[:, 0], 
                    velocities[:, 1], 
                    velocities[:, 2],
                    color='white', 
                    alpha=0.5,
                    length=self.config["velocity_scale"] * 10
                )
            else:
                self.quiver = self.ax.quiver(
                    positions[:, 0], 
                    positions[:, 1], 
                    velocities[:, 0], 
                    velocities[:, 1],
                    color='white', 
                    alpha=0.5,
                    scale=self.config["velocity_scale"] * 10
                )
        
        # Generate packet transmissions if enabled
        if self.config["show_packets"]:
            self._generate_packet_transmissions(positions)
                
        # Update node trails
        if len(self.trails) > 0:
            for trail in self.trails:
                trail.remove()
        
        self.trails = []
        
        # Get position history for trails
        history = self.mobility_model.position_history
        if len(history) > 2:
            # Only show the last N positions in the trail
            trail_length = min(self.config["trail_length"], len(history))
            trail_history = history[-trail_length:]
            
            # For each node, draw a line connecting its recent positions
            for node_idx in range(self.mobility_model.config["node_count"]):
                node_positions = np.array([pos[node_idx] for pos in trail_history])
                
                # Set color based on node type
                if node_idx in self.config["validators"]:
                    color = self.config["validator_color"]
                else:
                    color = self.config["node_color"]
                
                # If node is disconnected, use disconnected color for trail
                if not self.mobility_model.get_connection_status()[node_idx]:
                    color = self.config["disconnected_color"]
                
                # Draw the trail
                if self.mobility_model.config["3d_enabled"] and self.config["show_3d"]:
                    if self.config["trail_fade"]:
                        # Create fading effect
                        for i in range(1, len(node_positions)):
                            alpha = 0.7 * (i / len(node_positions))
                            trail = self.ax.plot3D(
                                node_positions[i-1:i+1, 0],
                                node_positions[i-1:i+1, 1],
                                node_positions[i-1:i+1, 2],
                                color=color,
                                alpha=alpha,
                                linewidth=1
                            )[0]
                            self.trails.append(trail)
                    else:
                        trail = self.ax.plot3D(
                            node_positions[:, 0],
                            node_positions[:, 1],
                            node_positions[:, 2],
                            color=color,
                            alpha=0.5,
                            linewidth=1
                        )[0]
                        self.trails.append(trail)
                else:
                    if self.config["trail_fade"]:
                        # Create fading effect
                        for i in range(1, len(node_positions)):
                            alpha = 0.7 * (i / len(node_positions))
                            trail = self.ax.plot(
                                node_positions[i-1:i+1, 0],
                                node_positions[i-1:i+1, 1],
                                color=color,
                                alpha=alpha,
                                linewidth=1
                            )[0]
                            self.trails.append(trail)
                    else:
                        trail = self.ax.plot(
                            node_positions[:, 0],
                            node_positions[:, 1],
                            color=color,
                            alpha=0.5,
                            linewidth=1
                        )[0]
                        self.trails.append(trail)
        
        # Update title with simulation time
        frame_time = frame_num * self.config["update_interval"]
        self.ax.set_title(f"{self.config['title']} - Time: {frame_time:.1f}s")
        
        # Save frame if enabled
        if self.config["save_frames"]:
            filename = os.path.join(
                self.config["frames_dir"],
                f"frame_{self.frame_count:04d}.{self.config['frame_format']}"
            )
            self.fig.savefig(filename, dpi=100)
            self.frame_count += 1
            
        # Collect all updated artists
        artists = [self.scatter]
        if self.quiver:
            artists.append(self.quiver)
        artists.extend(self.trails)
        artists.extend(self.packet_arrows)
            
        return artists
    
    def animate(self, num_frames: int = 100, interval: int = 100):
        """
        Create and show an animation of the mobility model.
        
        Args:
            num_frames: Number of frames to animate
            interval: Interval between frames in milliseconds
        """
        self.logger.info("Starting animation with %d frames", num_frames)
        
        # Create animation with lower interval for more fluid movement
        ani = animation.FuncAnimation(
            self.fig, 
            self.update, 
            frames=num_frames,
            interval=interval, 
            blit=True,
            repeat=True,  # Repeat the animation when it reaches the end
            cache_frame_data=False  # Don't cache frame data to allow dynamic updates
        )
        
        # Display the animation
        plt.tight_layout()
        plt.show()
        
        return ani
    
    def create_video(self, output_file: str = "mobility_animation.mp4", fps: int = 10, num_frames: int = 100):
        """
        Create a video file of the mobility animation.
        
        Args:
            output_file: Path to the output video file
            fps: Frames per second in the video
            num_frames: Number of frames to include
        """
        self.logger.info("Creating video with %d frames at %d FPS", num_frames, fps)
        
        # Get output directory
        output_dir = os.path.dirname(output_file)
        if not output_dir:
            output_dir = "."
            
        # Create frames directory next to output file
        frames_dir = os.path.join(output_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        # Generate frames
        for frame in range(num_frames):
            self.update(frame)
            self.fig.savefig(os.path.join(frames_dir, f"frame_{frame:04d}.png"), dpi=100)
            if frame % 10 == 0:
                self.logger.info("Generated frame %d/%d", frame, num_frames)
                
        # Use ffmpeg to create video
        try:
            import subprocess
            cmd = [
                'ffmpeg', '-y', '-framerate', str(fps), 
                '-i', os.path.join(frames_dir, 'frame_%04d.png'),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                output_file
            ]
            subprocess.run(cmd, check=True)
            self.logger.info("Video saved to: %s", output_file)
        except Exception as e:
            self.logger.error("Error creating video: %s", e)
            
        # Keep the frames directory for manual video creation if ffmpeg fails
            
    def plot_trajectory_heatmap(self, output_file: Optional[str] = None):
        """
        Create a heatmap showing node density over the simulation area.
        
        Args:
            output_file: If provided, save the heatmap to this file
        """
        # Create a new figure for the heatmap
        plt.figure(figsize=(10, 8))
        
        # Get all positions from history
        history = self.mobility_model.position_history
        if not history:
            self.logger.warning("No position history available for heatmap")
            return
            
        # Flatten all positions into a single array
        all_positions = np.vstack([pos for pos in history])
        
        # Create 2D histogram
        heatmap, xedges, yedges = np.histogram2d(
            all_positions[:, 0], 
            all_positions[:, 1], 
            bins=50, 
            range=[[0, self.mobility_model.config["area_size"][0]], 
                  [0, self.mobility_model.config["area_size"][1]]]
        )
        
        # Plot heatmap
        plt.imshow(
            heatmap.T, 
            origin='lower', 
            extent=[0, self.mobility_model.config["area_size"][0], 
                   0, self.mobility_model.config["area_size"][1]],
            aspect='auto',
            cmap='viridis'
        )
        
        plt.colorbar(label='Node Count')
        plt.title('Node Density Heatmap')
        plt.xlabel('X (meters)')
        plt.ylabel('Y (meters)')
        
        # Show or save
        if output_file:
            plt.savefig(output_file, dpi=100)
            self.logger.info("Heatmap saved to: %s", output_file)
        else:
            plt.show()
            
    def __str__(self) -> str:
        """String representation of the visualizer"""
        return f"MobilityVisualizer({self.mobility_model})"


# For testing the visualizer
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create mobility model
    model = SixGMobilityModel()
    
    # Create visualizer
    visualizer = MobilityVisualizer(model)
    
    # Run animation
    visualizer.animate(num_frames=200, interval=50)
    
    # Create a heatmap
    visualizer.plot_trajectory_heatmap("mobility_heatmap.png") 
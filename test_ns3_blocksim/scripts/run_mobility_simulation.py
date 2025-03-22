#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
6G MANET Mobility Simulation Demo Script
This script demonstrates the 6G mobility model by running a simulation and visualizing
the movement patterns of nodes in a MANET environment.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, Any

# Add project root to path to allow imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

# Import the mobility model and visualizer
from models.manet.mobility.sixg_mobility_model import SixGMobilityModel
from models.manet.mobility.visualization import MobilityVisualizer


def setup_logging(debug: bool = False):
    """Set up logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )


def load_config(config_file: str) -> Dict[str, Any]:
    """Load simulation configuration from file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Error loading config file: {e}")
        return {}


def save_results(results: Dict[str, Any], output_file: str):
    """Save simulation results to a file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        logging.info(f"Results saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving results: {e}")


def main():
    """Main function to run the mobility simulation"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run 6G MANET mobility simulation')
    parser.add_argument('--config', type=str, default='../config/mobility_simulation.json',
                        help='Path to simulation configuration file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--frames', type=int, default=200, help='Number of animation frames')
    parser.add_argument('--interval', type=int, default=50, help='Animation interval (ms)')
    parser.add_argument('--output', type=str, default='../results/mobility_simulation',
                        help='Output directory for results and visualizations')
    parser.add_argument('--video', action='store_true',
                        help='Create video of the simulation')
    parser.add_argument('--no-display', action='store_true',
                        help='Run without displaying the animation window (useful for servers)')
    parser.add_argument('--video-filename', type=str, default='mobility_animation.mp4',
                        help='Filename for the output video')
    parser.add_argument('--heatmap', action='store_true', help='Generate node density heatmap')
    parser.add_argument('--simulation-time', type=float, default=20.0, 
                        help='Total simulation time in seconds')
    parser.add_argument('--3d', dest='enable_3d', action='store_true', 
                        help='Enable 3D visualization')
    parser.set_defaults(enable_3d=True)
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    logging.info("Starting 6G MANET mobility simulation")
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Load configuration
    config = {}
    if os.path.exists(args.config):
        config = load_config(args.config)
        logging.info(f"Loaded configuration from {args.config}")
    else:
        logging.warning(f"Config file {args.config} not found. Using default settings.")
    
    # Create mobility model with configuration
    mobility_model = SixGMobilityModel(config)
    logging.info(f"Created mobility model with {mobility_model.config['node_count']} nodes")
    
    # Configure visualization
    viz_config = {
        "show_3d": args.enable_3d,
        "title": "6G Network Mobility Simulation",
        "node_color": "deepskyblue",
        "validator_color": "crimson",
        "background_color": "black",
        "trail_length": 50,
        "save_frames": args.video,
        "frames_dir": os.path.join(args.output, "frames"),
        "update_interval": 0.05,
        "node_size": 80,
        "trail_fade": True,
        "show_velocity": False,
        "velocity_scale": 0.5,
        "node_alpha": 0.9,
    }
    
    # Create visualizer
    visualizer = MobilityVisualizer(mobility_model, viz_config)
    logging.info("Created mobility visualizer")
    
    # Run animation
    logging.info(f"Running animation with {args.frames} frames at {args.interval}ms interval")
    
    if args.no_display:
        # Run simulation without displaying animation
        logging.info("Running in headless mode (no display)")
        # Just update frames without displaying
        for frame in range(args.frames):
            visualizer.update(frame)
            if frame % 20 == 0:
                logging.info(f"Processed frame {frame}/{args.frames}")
        
        # Automatically create video in no-display mode
        video_file = os.path.join(args.output, args.video_filename)
        logging.info(f"Creating video in headless mode: {video_file}")
        visualizer.create_video(video_file, fps=20, num_frames=args.frames)
    else:
        # Display animation
        ani = visualizer.animate(num_frames=args.frames, interval=args.interval)
    
    # Generate heatmap if requested
    if args.heatmap:
        heatmap_file = os.path.join(args.output, "mobility_heatmap.png")
        logging.info(f"Generating node density heatmap: {heatmap_file}")
        visualizer.plot_trajectory_heatmap(heatmap_file)
    
    # Create video if requested
    if args.video:
        video_file = os.path.join(args.output, args.video_filename)
        logging.info(f"Creating video of the simulation: {video_file}")
        visualizer.create_video(video_file, fps=20, num_frames=args.frames)
    
    # Save trajectory data
    trajectory_data = mobility_model.get_trajectory_data()
    trajectory_file = os.path.join(args.output, "trajectory_data.json")
    
    # Don't save position history to JSON as it's too large
    # Just save metadata
    trajectory_summary = {
        "simulation_time": args.simulation_time,
        "node_count": mobility_model.config["node_count"],
        "area_size": mobility_model.config["area_size"],
        "mobility_model": str(mobility_model),
        "config": mobility_model.config
    }
    
    save_results(trajectory_summary, trajectory_file)
    
    logging.info("Simulation completed successfully")


if __name__ == "__main__":
    main() 
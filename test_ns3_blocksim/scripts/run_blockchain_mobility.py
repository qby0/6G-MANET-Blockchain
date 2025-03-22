#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to run blockchain integration with 6G mobility model.
This demonstrates the integration of 6G MANET with blockchain components.
"""

import os
import sys
import json
import argparse
import logging
import numpy as np
from pathlib import Path

# Add the project directory to the path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from models.manet.mobility.sixg_mobility_model import SixGMobilityModel
from models.manet.blockchain_integration import BlockchainIntegration

# Setup logging
def setup_logging(debug=False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s:%(name)s:%(message)s"
    )

# Load configuration
def load_config(config_path):
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)

# Save simulation results
def save_results(results, output_dir):
    """Save simulation results to disk"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "simulation_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    logging.info(f"Results saved to {output_path}")

def main():
    """Main function to run the simulation"""
    parser = argparse.ArgumentParser(description="Run 6G MANET Blockchain Mobility Simulation")
    parser.add_argument("--config", type=str, default="test_ns3_blocksim/config/mobility_simulation.json",
                       help="Path to mobility configuration file")
    parser.add_argument("--blockchain-config", type=str, default="test_ns3_blocksim/config/blockchain_config.json",
                       help="Path to blockchain configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--frames", type=int, default=100, help="Number of frames to simulate")
    parser.add_argument("--interval", type=int, default=100, help="Interval between frames in milliseconds")
    parser.add_argument("--no-visual", action="store_true", help="Disable visualization")
    parser.add_argument("--heatmap", action="store_true", help="Generate heatmap of node density")
    parser.add_argument("--create-video", action="store_true", help="Create video of the simulation")
    parser.add_argument("--output-dir", type=str, default="results/blockchain_mobility",
                       help="Directory to save results")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    # Print banner
    logging.info("=" * 50)
    logging.info("6G MANET Blockchain Mobility Simulation")
    logging.info("=" * 50)
    
    # Create output directories
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    blockchain_data_dir = output_dir / "blockchain_data"
    blockchain_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Load configurations
    logging.info(f"Loading mobility configuration from {args.config}")
    mobility_config = load_config(args.config)
    
    logging.info(f"Loading blockchain configuration from {args.blockchain_config}")
    blockchain_config = load_config(args.blockchain_config)
    
    # Initialize models
    mobility_model = SixGMobilityModel(config=mobility_config)
    
    blockchain_integration = BlockchainIntegration(
        mobility_model=mobility_model,
        config=blockchain_config,
        blockchain_data_dir=blockchain_data_dir
    )
    
    # Set up visualization if needed
    if not args.no_visual:
        try:
            from models.manet.mobility.visualization import MobilityVisualizer
            visualizer = MobilityVisualizer(mobility_model)
        except ImportError as e:
            logging.warning(f"Visualization not available: {e}")
            args.no_visual = True
    
    # Run simulation
    results = {
        "frames": [],
        "blockchain": {},
        "configuration": {
            "mobility": mobility_config,
            "blockchain": blockchain_config,
            "frames": args.frames,
            "interval": args.interval
        }
    }
    
    logging.info(f"Starting simulation with {args.frames} frames")
    
    for frame in range(args.frames):
        # Update mobility model
        mobility_model.update_positions(args.interval / 1000.0)
        
        # Update blockchain integration
        blockchain_integration.update(frame)
        
        # Collect frame data
        frame_data = {
            "frame_number": frame,
            "timestamp": frame * args.interval / 1000.0,  # Convert to seconds
            "node_count": mobility_model.config["node_count"]
        }
        
        results["frames"].append(frame_data)
        
        # Update visualization
        if not args.no_visual:
            visualizer.update(frame)
            
        # Log progress
        if frame % 10 == 0 or frame == args.frames - 1:
            logging.info(f"Processed frame {frame+1}/{args.frames}")
    
    # Save blockchain results
    blockchain_integration.save_results(blockchain_data_dir)
    
    # Generate heatmap if requested
    if args.heatmap and not args.no_visual:
        try:
            visualizer.create_heatmap(output_dir / "node_density_heatmap.png")
            logging.info(f"Heatmap saved to {output_dir / 'node_density_heatmap.png'}")
        except Exception as e:
            logging.error(f"Failed to create heatmap: {e}")
    
    # Create video if requested
    if args.create_video and not args.no_visual:
        try:
            video_path = output_dir / "simulation_video.mp4"
            visualizer.create_video(str(video_path))
            logging.info(f"Video saved to {video_path}")
        except Exception as e:
            logging.error(f"Failed to create video: {e}")
    
    # Save overall results
    save_results(results, output_dir)
    
    logging.info("Simulation complete")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to run an integrated NS-3 and distributed blockchain simulation.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.ns3_adapter import NS3Adapter
from models.paths_manager import get_config_dir, get_ns3_dir, get_path, get_results_dir

# Setup logging - use paths_manager for log directory
log_dir = get_results_dir()
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(
                log_dir,
                f"integrated_sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            )
        ),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("integrated_sim")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run integrated blockchain simulation with NS-3"
    )

    # NS3 path can be set in paths_manager, environment, or command line
    parser.add_argument(
        "--ns3-path",
        help="Path to NS-3 installation (if not set in paths_manager or NS3_DIR environment variable)",
    )

    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output-dir", help="Output directory for simulation results")
    parser.add_argument(
        "--simulation-time", type=float, help="Simulation time in seconds"
    )
    parser.add_argument(
        "--node-count", type=int, help="Number of nodes in the simulation"
    )
    parser.add_argument(
        "--validator-percentage",
        type=float,
        help="Percentage of nodes that are validators",
    )
    parser.add_argument(
        "--animation", action="store_true", help="Generate NS-3 animation"
    )

    return parser.parse_args()


def get_ns3_path(args):
    """Get NS-3 path from command line, paths_manager, or environment."""
    # First try command line argument
    if args.ns3_path and os.path.exists(args.ns3_path):
        logger.info(
            "Using NS-3 path from command line: %s", args.ns3_path,
        )
        return args.ns3_path

    # Then try paths_manager
    ns3_path = get_ns3_dir()
    if ns3_path and os.path.exists(ns3_path):
        logger.info(
            "Using NS-3 path from paths_manager: %s", ns3_path
        )
        return ns3_path

    # Finally try environment variable
    ns3_path = os.environ.get("NS3_DIR")
    if ns3_path and os.path.exists(ns3_path):
        logger.info(
            "Using NS-3 path from environment variable: %s", ns3_path,
        )
        return ns3_path

    logger.error(
        "NS-3 path not found. Please set it in paths_manager, NS3_DIR environment variable, or command line."
    )
    return None


def load_config(args):
    """Load configuration from file or command line arguments."""
    config = {}

    # If config file specified, load it
    if args.config:
        config_path = args.config
    else:
        # Use default config file from config directory
        config_path = os.path.join(get_config_dir(), "integrated.json")

    logger.info(
        "Loading configuration from: %s", config_path
    )

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        logger.warning(
            "Configuration file not found: %s", config_path
        )
        logger.info("Using default configuration with command line overrides")

    # Override with command line arguments if provided
    if args.simulation_time:
        config["simulation_time"] = args.simulation_time

    if args.node_count:
        if "network" not in config:
            config["network"] = {}
        config["network"]["node_count"] = args.node_count

    if args.validator_percentage:
        if "network" not in config:
            config["network"] = {}
        config["network"]["validator_percentage"] = args.validator_percentage

    if args.animation:
        if "visualization" not in config:
            config["visualization"] = {}
        config["visualization"]["generate_animation"] = True

    if args.output_dir:
        if "output" not in config:
            config["output"] = {}
        config["output"]["save_path"] = args.output_dir
    else:
        # Use paths_manager for output directory
        if "output" not in config:
            config["output"] = {}
        if "save_path" not in config["output"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config["output"]["save_path"] = os.path.join(
                get_results_dir(), f"integrated_sim_{timestamp}"
            )

    return config


def run_simulation(config_path, ns3_path):
    """
    Run the integrated NS-3 and blockchain simulation.

    Args:
        config_path (str): Path to configuration file
        ns3_path (str): Path to NS-3 directory

    Returns:
        dict: Simulation results
    """
    logger.info("=== Starting Integrated NS-3 and Blockchain Simulation ===")

    # Log configuration details
    if config_path:
        logger.info(
            "Using configuration from: %s", config_path
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                logger.info(
                    "Configuration: %(json.dumps(config, indent=2))s",
                    {json.dumps(config, indent=2): json.dumps(config, indent=2)},
                )
        except Exception as e:
            logger.warning("Could not read config file: %s", e)
    else:
        logger.info("Using default configuration")

    logger.info("NS-3 path: %s", ns3_path)

    # Create simulation adapter
    start_time = time.time()
    logger.info("Initializing NS-3 Blockchain Adapter")

    try:
        adapter = NS3Adapter(ns3_path, config_path)

        # Run the simulation
        logger.info("Running integrated simulation")
        results = adapter.run_integrated_simulation()

        # Calculate duration
        end_time = time.time()
        duration = end_time - start_time

        # Log results summary
        logger.info("=== Simulation Completed ===")
        logger.info("Duration: %(duration).2f seconds", {duration: duration})
        logger.info(
            "Transactions: %(results['blockchain']['transactions'])s",
            {
                results["blockchain"]["transactions"]: results["blockchain"][
                    "transactions"
                ]
            },
        )
        logger.info(
            "Blocks: %(results['blockchain']['blocks'])s",
            {results["blockchain"]["blocks"]: results["blockchain"]["blocks"]},
        )

        if "final_status" in results["blockchain"]:
            network_status = results["blockchain"]["final_status"]
            logger.info(
                f"Network status: {network_status['total_nodes']} nodes, "
                f"max height: {network_status['max_blockchain_height']}, "
                f"consistency: {network_status['blockchain_consistency']}"
            )

        logger.info(
            "Results saved to: %(results['output_dir'])s",
            {results["output_dir"]: results["output_dir"]},
        )

        # Save results summary to a more accessible location
        summary_file = os.path.join(
            get_results_dir(), f"summary_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        )

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "duration": duration,
                    "transactions": results["blockchain"]["transactions"],
                    "blocks": results["blockchain"]["blocks"],
                    "node_count": results["node_count"],
                    "simulation_time": results["simulation_time"],
                    "output_dir": results["output_dir"],
                    "timestamp": end_time,
                },
                f,
                indent=4,
            )

        logger.info("Summary saved to: %s", summary_file)

        return results

    except Exception as e:
        logger.error(f"Error during simulation: {e}", exc_info=True)
        return {"error": str(e)}


def main():
    """Main function to run the integrated simulation."""
    # Parse command line arguments
    args = parse_arguments()

    # Get NS-3 path
    ns3_path = get_ns3_path(args)
    if not ns3_path:
        return 1

    # Load configuration
    config = load_config(args)

    # Import NS3Adapter here to avoid circular imports
    from models.ns3_adapter import NS3Adapter

    try:
        # Create adapter
        logger.info("Creating NS3Adapter...")
        adapter = NS3Adapter(config_file=args.config, ns3_path=ns3_path)

        # Run simulation
        logger.info("Starting integrated simulation...")
        results = adapter.run_integrated_simulation()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = os.path.join(get_results_dir(), f"summary_{timestamp}.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        logger.info(
            "Simulation completed. Results saved to: %s", summary_file,
        )
        return 0

    except Exception as e:
        logger.error(f"Error running simulation: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

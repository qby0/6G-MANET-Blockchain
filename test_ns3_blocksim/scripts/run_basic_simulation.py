#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for running integrated NS-3 and BlockSim simulation.
"""
import argparse
import json
import logging
import os
import random
import secrets
import sys
import time
from typing import Any, Dict, Optional

import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add models directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.blocksim_adapter import BlockSimAdapter
from models.integration_interface import IntegrationInterface
from models.ns3_adapter import NS3Adapter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("simulation.log"), logging.StreamHandler()],
)
logger = logging.getLogger("Simulation")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Integrated simulation of NS-3 and BlockSim"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="../config/default.json",
        help="Path to simulation configuration file",
    )
    parser.add_argument(
        "--duration", type=float, default=100.0, help="Simulation duration in seconds"
    )
    parser.add_argument(
        "--time-step", type=float, default=1.0, help="Simulation time step in seconds"
    )
    parser.add_argument(
        "--output-dir", type=str, default="../results", help="Directory to save results"
    )
    parser.add_argument(
        "--ns3-path",
        type=str,
        default=os.getenv("NS3_DIR"),
        help="Path to NS-3 installation",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with more detailed logging",
    )
    parser.add_argument(
        "--animation",
        action="store_true",
        help="Enable NS-3 animation for visualization",
    )
    parser.add_argument(
        "--save-interim", action="store_true", help="Save interim simulation results"
    )
    parser.add_argument(
        "--rebuild", action="store_true", help="Rebuild NS-3 before running"
    )
    return parser.parse_args()


def load_config(config_path):
    """Load configuration file."""
    try:
        # Check if file exists
        if not os.path.exists(config_path):
            logger.error(
                f"Configuration file {config_path} not found. Using default values."
            )
            return {}

        # Check read permissions
        if not os.access(config_path, os.R_OK):
            logger.error(
                f"Read permission error: no read permissions for file {config_path}"
            )
            logger.error("Please check read permissions for the configuration file")
            return {}

        # Try to open file and read data
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(
            f"Configuration file {config_path} not found. Using default values."
        )
        return {}
    except PermissionError:
        logger.error(
            "Read permission error: cannot read file %(config_path)s",
            {config_path: config_path},
        )
        logger.error("Please check read permissions for the configuration file")
        return {}
    except json.JSONDecodeError:
        logger.error(
            f"JSON decoding error in file {config_path}. Using default values."
        )
        return {}
    except Exception as e:
        logger.error("Unexpected error reading configuration file: %(e)s", {e: e})
        return {}


def setup_environment(config, ns3_path: Optional[Any] = None):
    """Setup environment for simulation."""
    # Create results directory if it doesn't exist
    os.makedirs(config.get("output_dir", "../results"), exist_ok=True)

    # Setup NS-3
    if ns3_path:
        os.environ["NS3_DIR"] = ns3_path

    # Other environment setup can be added here

    logger.info("Environment setup complete")


def create_network_topology(interface, config):
    """Create network topology based on configuration."""
    # Register base station
    interface.register_node(
        "base_station_1",
        (0.0, 0.0, 10.0),
        "base_station",
        {"computational_power": 100, "storage": 1000, "battery": None},
    )

    # Register validators
    for i in range(config.get("num_validators", 3)):
        interface.register_node(
            f"validator_{i+1}",
            (50.0 * (i + 1), 50.0 * (i + 1), 1.5),
            "validator",
            {"computational_power": 20, "storage": 100, "battery": 0.8},
        )

    # Register regular nodes
    for i in range(config.get("num_regular_nodes", 10)):
        interface.register_node(
            f"node_{i+1}",
            (100.0 + 20.0 * (i % 5), 100.0 + 20.0 * (i // 5), 1.5),
            "regular",
            {"computational_power": 10, "storage": 50, "battery": 0.9},
        )

    # Connect nodes
    # First, connect base station to validators
    for i in range(config.get("num_validators", 3)):
        interface.register_connection("base_station_1", f"validator_{i+1}", 0.9, 100.0)

    # Connect validators between each other
    for i in range(config.get("num_validators", 3)):
        for j in range(i + 1, config.get("num_validators", 3)):
            interface.register_connection(
                f"validator_{i+1}", f"validator_{j+1}", 0.8, 50.0
            )

    # Connect regular nodes to nearest validators and between each other
    for i in range(config.get("num_regular_nodes", 10)):
        # Connect to nearest validator
        validator_idx = (i % config.get("num_validators", 3)) + 1
        interface.register_connection(
            f"node_{i+1}", f"validator_{validator_idx}", 0.7, 10.0
        )

        # Connect to several neighboring nodes
        for j in range(1, 4):  # Connect to 3 neighboring nodes
            neighbor_idx = (i + j) % config.get("num_regular_nodes", 10) + 1
            interface.register_connection(
                f"node_{i+1}", f"node_{neighbor_idx}", 0.6, 5.0
            )

    logger.info("Network topology created")


def run_simulation(args, config):
    """Run simulation."""
    # Create integration interface
    interface = IntegrationInterface()

    # Create NS-3 and BlockSim adapters
    try:
        ns3_adapter = NS3Adapter(args.ns3_path)

        # If rebuild flag is specified, rebuild NS-3
        if args.rebuild:
            logger.info("Starting NS-3 rebuild with optimizations...")
            if ns3_adapter.configure_and_build():
                logger.info("NS-3 successfully rebuilt")
            else:
                logger.error("NS-3 build error")
                return None

        # Create script for MANET simulation with blockchain support
        script_path = ns3_adapter.create_ns3_manet_script()

        # Compile script
        script_name = os.path.basename(script_path).replace(".cc", "")
        if ns3_adapter.compile_ns3_script(script_name):
            logger.info(
                "Script %(script_name)s successfully compiled",
                {script_name: script_name},
            )
        else:
            logger.warning(
                f"Failed to compile script {script_name}. Using existing scripts."
            )

        logger.info("NS-3 adapter successfully initialized")
    except Exception as e:
        logger.warning("Failed to initialize NS-3 adapter: %(e)s", {e: e})
        logger.warning("NS-3 emulation will be used")
        ns3_adapter = None

    blocksim_adapter = BlockSimAdapter()
    logger.info("BlockSim adapter initialized")

    # Create network topology
    create_network_topology(interface, config)

    # Initialize blockchain
    consensus_type = config.get("consensus_type", "PoA")
    num_validators = config.get("num_validators", 3)
    block_interval = config.get("block_interval", 5.0)

    blocksim_adapter.initialize_blockchain(
        consensus_type, num_validators, block_interval
    )

    # Synchronize nodes between interface and BlockSim
    for node_id, node_info in interface.nodes.items():
        node_type = "validator" if node_info["type"] == "validator" else "regular"
        if node_info["type"] == "base_station":
            node_type = "validator"  # Base station is considered a validator

        resources = {
            "computational_power": node_info["capabilities"].get(
                "computational_power", 10
            ),
            "storage": node_info["capabilities"].get("storage", 50),
        }
        blocksim_adapter.register_node(node_id, node_type, resources)

    # Simulation scenario
    total_time = args.duration
    time_step = args.time_step
    current_time = 0.0

    # Create output directory with timestamp for current run
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = os.path.join(args.output_dir, f"simulation_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    # Generate scenario file for NS-3 (if NS-3 is available)
    network_params = {
        "simulation_time": total_time,
        "time_step": time_step,
        "wifi_standard": "80211g",
        "propagation_model": "friis",
        "routing_protocol": "aodv",
    }

    if ns3_adapter:
        scenario_file = ns3_adapter.create_scenario_file(
            interface.nodes, interface.links, network_params
        )

        # Start NS-3 simulation in background mode
        logger.info("Starting NS-3 simulation...")
        ns3_results = ns3_adapter.run_simulation(
            scenario_file, total_time, time_step, output_dir
        )

    # Main simulation loop
    logger.info(
        f"Starting simulation. Duration: {total_time} seconds, step: {time_step} seconds"
    )
    node_positions = {}  # For storing current node positions

    # Initialize initial positions
    for node_id, node_info in interface.nodes.items():
        node_positions[node_id] = list(node_info["position"])

    while current_time < total_time:
        # Update current time
        interface.advance_time(time_step)
        blocksim_adapter.advance_time(time_step)
        current_time += time_step

        # Simulate mobile node movement (excluding base station)
        for node_id, position in node_positions.items():
            if "base_station" not in node_id:  # Don't move base station
                # Random movement within a small radius
                dx = (
                    (-5) + (secrets.randbelow(int((5 - -5) * 1000)) / 1000.0)
                ) * time_step
                dy = (
                    (-5) + (secrets.randbelow(int((5 - -5) * 1000)) / 1000.0)
                ) * time_step
                dz = 0  # Default, movement only in XY plane

                # Limit movement within reasonable area
                new_x = max(0, min(500, position[0] + dx))
                new_y = max(0, min(500, position[1] + dy))
                new_z = position[2]  # Height doesn't change

                # Update position
                new_position = [new_x, new_y, new_z]
                node_positions[node_id] = new_position
                interface.update_node_position(node_id, tuple(new_position))

                # Update connection quality based on distance
                for other_id, other_pos in node_positions.items():
                    if node_id != other_id:
                        # Calculate distance between nodes
                        distance = np.sqrt(
                            (new_x - other_pos[0]) ** 2
                            + (new_y - other_pos[1]) ** 2
                            + (new_z - other_pos[2]) ** 2
                        )

                        # Connection quality inversely proportional to distance
                        # Maximum distance for connection - 100 units
                        if distance <= 100:
                            quality = max(0.1, 1.0 - distance / 100.0)
                            # Bandwidth depends on connection quality
                            bandwidth = 50.0 * quality

                            # Update connection between nodes
                            connection_ids = [
                                f"{min(node_id, other_id)}_{max(node_id, other_id)}"
                            ]
                            interface.register_connection(
                                node_id, other_id, quality, bandwidth
                            )

        # Generate node activity every 10 seconds
        if (
            int(current_time * 10) % 100 == 0
        ):  # Every 10 seconds (considering simulation step)
            # Create several transactions
            for _ in range(5):
                # Select random nodes for transaction
                all_node_ids = list(interface.nodes.keys())
                if len(all_node_ids) >= 2:
                    source_id = secrets.choice(all_node_ids)
                    target_id = random.choice(
                        [n for n in all_node_ids if n != source_id]
                    )

                    # Create transaction through interface
                    tx_data = {
                        "type": "data_transfer",
                        "content": f"Transaction at time {current_time:.2f}",
                        "size": secrets.randbelow((1000) - (1) + 1) + (1),
                        "priority": secrets.choice(["low", "medium", "high"]),
                    }
                    tx_id = interface.send_transaction(source_id, target_id, tx_data)

                    # Create corresponding transaction in BlockSim
                    if tx_id:
                        blocksim_adapter.create_transaction(
                            source_id, target_id, tx_data
                        )

            # Process pending transactions
            processed = interface.process_pending_transactions()
            if processed > 0:
                logger.debug(
                    "Processed %(processed)s transactions in interface",
                    {processed: processed},
                )

            processed_blockchain = blocksim_adapter.process_pending_transactions()
            if processed_blockchain > 0:
                logger.debug(
                    f"Processed {processed_blockchain} transactions in blockchain"
                )
                # Create block with processed transactions
                block = blocksim_adapter.create_block()
                if block:
                    logger.info(
                        f"New block {block['index']} created by validator {block['validator']}"
                    )

        # Output current state every 20 seconds
        if int(current_time * 10) % 200 == 0 or current_time >= total_time - time_step:
            net_state = interface.get_network_state()
            blockchain_state = blocksim_adapter.get_blockchain_state()

            logger.info(
                "Simulation time: %(current_time).2f/%(total_time)s",
                {current_time: current_time, total_time: total_time},
            )
            logger.info(
                "Nodes in network: %(len(net_state['nodes']))s",
                {len(net_state["nodes"]): len(net_state["nodes"])},
            )
            logger.info(
                "Connections in network: %(len(net_state['links']))s",
                {len(net_state["links"]): len(net_state["links"])},
            )
            logger.info(
                "Transactions in network: %(len(net_state['transactions']))s",
                {len(net_state["transactions"]): len(net_state["transactions"])},
            )
            logger.info(
                "Blocks in blockchain: %(blockchain_state['blocks_count'])s",
                {blockchain_state["blocks_count"]: blockchain_state["blocks_count"]},
            )
            logger.info(
                f"Pending transactions: {blockchain_state['pending_transactions']}"
            )
            logger.info(
                f"Confirmed transactions: {blockchain_state['confirmed_transactions']}"
            )

            # Save interim results
            if args.save_interim:
                interim_output = os.path.join(
                    output_dir, f"interim_{int(current_time)}"
                )
                os.makedirs(interim_output, exist_ok=True)
                interface.save_state(os.path.join(interim_output, "network_state.json"))
                blocksim_adapter.save_state(
                    os.path.join(interim_output, "blockchain_state.json")
                )

    logger.info("Simulation completed")

    # Save results
    network_state_file = os.path.join(output_dir, f"network_state_{timestamp}.json")
    interface.save_state(network_state_file)

    # Save blockchain state
    blockchain_state_file = os.path.join(
        output_dir, f"blockchain_state_{timestamp}.json"
    )
    blocksim_adapter.save_state(blockchain_state_file)

    # If animation is enabled, check animation file
    animation_file = None
    if args.animation and ns3_adapter:
        animation_file = os.path.join(output_dir, f"animation_{timestamp}.xml")
        logger.info(
            "Animation file will be saved as: %(animation_file)s",
            {animation_file: animation_file},
        )
        logger.info("To view animation, start NetAnim and open the file")

    # Save summary information about simulation
    summary = {
        "timestamp": timestamp,
        "duration": total_time,
        "time_step": time_step,
        "nodes_count": len(interface.nodes),
        "transactions_processed": len(
            [
                tx
                for tx in interface.transactions
                if tx["status"] in ["processed", "included"]
            ]
        ),
        "blocks_created": blocksim_adapter.get_blockchain_state()["blocks_count"],
        "network_state_file": network_state_file,
        "blockchain_state_file": blockchain_state_file,
        "animation_file": animation_file,
    }

    with open(
        os.path.join(output_dir, f"summary_{timestamp}.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(summary, f, indent=2)

    return {
        "network_state": interface.get_network_state(),
        "blockchain_state": blocksim_adapter.get_detailed_state(),
        "timestamp": timestamp,
        "animation_file": animation_file,
    }


def main():
    """Main function."""
    # Parse command line arguments
    args = parse_arguments()

    # Setup logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = load_config(args.config)

    # Add command line arguments to configuration
    config["duration"] = args.duration
    config["time_step"] = args.time_step
    config["output_dir"] = args.output_dir
    config["animation_enabled"] = args.animation

    # Setup environment
    setup_environment(config, args.ns3_path)

    # Run simulation
    results = run_simulation(args, config)

    if results:
        logger.info(
            "Simulation results saved to %(args.output_dir)s",
            {args.output_dir: args.output_dir},
        )
        logger.info(
            "Simulation results timestamp: %(results['timestamp'])s",
            {results["timestamp"]: results["timestamp"]},
        )
        if results.get("animation_file"):
            logger.info(
                "Animation file: %(results['animation_file'])s",
                {results["animation_file"]: results["animation_file"]},
            )
    else:
        logger.error("Simulation ended with error")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

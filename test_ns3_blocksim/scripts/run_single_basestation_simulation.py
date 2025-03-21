#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for running simulation with a single base station and mobile nodes using AODV routing.
Nodes that are outside of base station coverage communicate through nodes within coverage.
"""
import argparse
import json
import logging
import os
import random
import secrets
import sys
import time
from typing import Any, Dict, List, Tuple

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
logger = logging.getLogger("BasestationSimulation")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Single Base Station Simulation with AODV Routing"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="../config/basestation.json",
        help="Path to simulation configuration file",
    )
    parser.add_argument(
        "--duration", type=float, default=300.0, help="Simulation duration in seconds"
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
        "--coverage-radius",
        type=float,
        default=200.0,
        help="Base station coverage radius in meters",
    )
    parser.add_argument(
        "--node-count", type=int, default=30, help="Number of mobile nodes"
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
        "--movement-speed", type=float, default=5.0, help="Node movement speed in m/s"
    )
    parser.add_argument(
        "--area-size",
        type=float,
        default=500.0,
        help="Simulation area size (creates a square area)",
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

        # Try to open file and read data
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Error reading configuration file: %s", e)
        return {}


def is_in_coverage(
    position: Tuple[float, float, float],
    base_station_pos: Tuple[float, float, float],
    coverage_radius: float,
) -> bool:
    """
    Check if a node is within the coverage radius of the base station.

    Args:
        position: Node position as (x, y, z)
        base_station_pos: Base station position as (x, y, z)
        coverage_radius: Coverage radius in meters

    Returns:
        bool: True if node is within coverage
    """
    distance = np.sqrt(
        (position[0] - base_station_pos[0]) ** 2
        + (position[1] - base_station_pos[1]) ** 2
    )
    return distance <= coverage_radius


def create_network_topology(interface, config, args):
    """Create network topology with one base station and mobile nodes."""
    # Simulation area parameters
    area_size = args.area_size
    node_count = args.node_count
    coverage_radius = args.coverage_radius

    # Base station position (center of the area)
    base_station_pos = (
        area_size / 2,
        area_size / 2,
        20.0,
    )  # Higher elevation for the base station

    # Register base station
    interface.register_node(
        "base_station_1",
        base_station_pos,
        "base_station",
        {
            "computational_power": 100,
            "storage": 1000,
            "battery": None,
            "coverage_radius": coverage_radius,
        },
    )

    # Register mobile nodes with random initial positions
    nodes_in_coverage = 0
    nodes_outside_coverage = 0

    for i in range(node_count):
        # Random position within the area
        x = (0) + (secrets.randbelow(int((area_size - 0) * 1000)) / 1000.0)
        y = (0) + (secrets.randbelow(int((area_size - 0) * 1000)) / 1000.0)
        z = 1.5  # Fixed height for mobile nodes

        position = (x, y, z)

        # Determine if the node should be a validator (10% chance)
        is_validator = secrets.randbelow(100) < int(0.1 * 100)

        # Register the node
        node_id = f"validator_{i+1}" if is_validator else f"node_{i+1}"
        node_type = "validator" if is_validator else "regular"

        interface.register_node(
            node_id,
            position,
            node_type,
            {
                "computational_power": 20 if is_validator else 10,
                "storage": 100 if is_validator else 50,
                "battery": 0.8 if is_validator else 0.7,
            },
        )

        # Count nodes in/out of coverage
        if is_in_coverage(position, base_station_pos, coverage_radius):
            nodes_in_coverage += 1
        else:
            nodes_outside_coverage += 1

    logger.info(
        "Created network topology with 1 base station and %s nodes", node_count,
    )
    logger.info(
        "Initial nodes in coverage: %s", nodes_in_coverage,
    )
    logger.info(
        "Initial nodes outside coverage: %s", nodes_outside_coverage,
    )

    # Create initial connections based on distance
    update_connections(interface, base_station_pos, coverage_radius)

    return base_station_pos


def update_connections(
    interface, base_station_pos, coverage_radius, max_node_range=100.0
):
    """Update connections between nodes based on their positions."""
    # Clear existing connections
    interface.links = {}

    # Connect base station to nodes within coverage
    for node_id, node_info in interface.nodes.items():
        if node_id == "base_station_1":
            continue

        position = node_info["position"]

        # Check if node is in base station coverage
        if is_in_coverage(position, base_station_pos, coverage_radius):
            # Connect to base station with good quality
            quality = max(
                0.5,
                1.0
                - np.sqrt(
                    (position[0] - base_station_pos[0]) ** 2
                    + (position[1] - base_station_pos[1]) ** 2
                )
                / coverage_radius,
            )
            bandwidth = 100.0 * quality
            interface.register_connection("base_station_1", node_id, quality, bandwidth)

    # Connect nodes to each other if they are close enough
    node_ids = list(interface.nodes.keys())
    for i, node1_id in enumerate(node_ids):
        if node1_id == "base_station_1":
            continue

        node1_pos = interface.nodes[node1_id]["position"]

        for node2_id in node_ids[i + 1 :]:
            if node2_id == "base_station_1":
                continue

            node2_pos = interface.nodes[node2_id]["position"]

            # Calculate distance between nodes
            distance = np.sqrt(
                (node1_pos[0] - node2_pos[0]) ** 2 + (node1_pos[1] - node2_pos[1]) ** 2
            )

            # Connect if within range
            if distance <= max_node_range:
                quality = max(0.1, 1.0 - distance / max_node_range)
                bandwidth = 50.0 * quality
                interface.register_connection(node1_id, node2_id, quality, bandwidth)

    # For nodes that are not directly connected to the base station,
    # AODV routing will find paths through intermediate nodes.
    # No need to manually establish these connections as AODV will handle routing.

    logger.debug(
        "Total connections in network: %(len(interface.links))s",
        {len(interface.links): len(interface.links)},
    )


def run_simulation(args, config):
    """Run the single base station simulation."""
    # Create integration interface
    interface = IntegrationInterface()

    # Create network topology
    base_station_pos = create_network_topology(interface, config, args)

    # Create NS-3 and BlockSim adapters
    try:
        ns3_adapter = NS3Adapter(args.ns3_path)

        # Create script for simulation with coverage visualization
        script_path = ns3_adapter.create_ns3_manet_script()

        # Compile script
        script_name = os.path.basename(script_path).replace(".cc", "")
        ns3_adapter.compile_ns3_script(script_name)
        logger.info("NS-3 adapter initialized")
    except Exception as e:
        logger.warning("Failed to initialize NS-3 adapter: %s", e)
        logger.warning("NS-3 emulation will be used")
        ns3_adapter = None

    # Initialize BlockSim
    blocksim_adapter = BlockSimAdapter()

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

    # Simulation parameters
    total_time = args.duration
    time_step = args.time_step
    current_time = 0.0

    # Create output directory with timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = os.path.join(args.output_dir, f"basestation_sim_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    # Network parameters for NS-3
    network_params = {
        "simulation_time": total_time,
        "time_step": time_step,
        "wifi_standard": "80211g",
        "propagation_model": "friis",
        "routing_protocol": "aodv",
        "coverage_radius": args.coverage_radius,
        "node_movement_speed": args.movement_speed,
    }

    # Create scenario file for NS-3 if available
    if ns3_adapter:
        scenario_file = ns3_adapter.create_scenario_file(
            interface.nodes, interface.links, network_params
        )

        # Start NS-3 simulation
        logger.info("Starting NS-3 simulation...")
        ns3_adapter.run_simulation(scenario_file, total_time, time_step, output_dir)

    # Store node positions
    node_positions = {}
    for node_id, node_info in interface.nodes.items():
        node_positions[node_id] = list(node_info["position"])

    # Initialize movement directions for each node
    node_directions = {}
    for node_id in interface.nodes:
        if node_id != "base_station_1":  # Base station doesn't move
            # Random angle in radians
            angle = (0) + (secrets.randbelow(int((2 * np.pi - 0) * 1000)) / 1000.0)
            node_directions[node_id] = (np.cos(angle), np.sin(angle))

    # Tracking metrics
    coverage_changes = []
    transaction_hops = []

    # Main simulation loop
    logger.info(
        f"Starting simulation. Duration: {total_time} seconds, step: {time_step} seconds"
    )

    while current_time < total_time:
        # Advance time
        interface.advance_time(time_step)
        blocksim_adapter.advance_time(time_step)
        current_time += time_step

        # Move nodes
        for node_id, position in list(node_positions.items()):
            if node_id == "base_station_1":
                continue  # Skip base station

            # Current direction
            direction = node_directions[node_id]

            # Random chance to change direction (5% per step)
            if secrets.randbelow(100) < int(0.05 * 100):
                angle = (0) + (secrets.randbelow(int((2 * np.pi - 0) * 1000)) / 1000.0)
                direction = (np.cos(angle), np.sin(angle))
                node_directions[node_id] = direction

            # Calculate new position
            speed = args.movement_speed * time_step
            dx = direction[0] * speed
            dy = direction[1] * speed

            # Update position with boundary checking
            new_x = max(0, min(args.area_size, position[0] + dx))
            new_y = max(0, min(args.area_size, position[1] + dy))

            # If hitting boundary, reflect the direction
            if new_x <= 0 or new_x >= args.area_size:
                node_directions[node_id] = (-direction[0], direction[1])
            if new_y <= 0 or new_y >= args.area_size:
                node_directions[node_id] = (direction[0], -direction[1])

            # Check if node is entering or leaving coverage area
            was_in_coverage = is_in_coverage(
                position, base_station_pos, args.coverage_radius
            )
            is_in_coverage_now = is_in_coverage(
                (new_x, new_y, position[2]), base_station_pos, args.coverage_radius
            )

            if was_in_coverage != is_in_coverage_now:
                status = "entered coverage" if is_in_coverage_now else "left coverage"
                logger.debug(
                    "Node %s %s at time %(current_time).2f", (node_id, status),
                )
                coverage_changes.append(
                    {"time": current_time, "node_id": node_id, "status": status}
                )

            # Update position
            new_position = [new_x, new_y, position[2]]
            node_positions[node_id] = new_position
            interface.update_node_position(node_id, tuple(new_position))

        # Update connections based on new positions
        if int(current_time * 10) % 50 == 0:  # Update every 5 seconds
            update_connections(interface, base_station_pos, args.coverage_radius)

        # Create transactions
        if int(current_time * 10) % 100 == 0:  # Every 10 seconds
            # Create transactions from random nodes to base station
            nodes_communicating = min(
                3, len(interface.nodes) - 1
            )  # Max 3 nodes communicate at once

            # Prefer nodes outside coverage for interesting routing paths
            outside_nodes = [
                node_id
                for node_id, pos in node_positions.items()
                if node_id != "base_station_1"
                and not is_in_coverage(pos, base_station_pos, args.coverage_radius)
            ]

            # If we have nodes outside coverage, use them
            communicating_nodes = []
            if outside_nodes:
                # Include at least one node outside coverage if available
                communicating_nodes.append(secrets.choice(outside_nodes))
                nodes_communicating -= 1

            # Add random nodes for remaining slots
            available_nodes = [
                n
                for n in interface.nodes.keys()
                if n != "base_station_1" and n not in communicating_nodes
            ]

            communicating_nodes.extend(
                random.sample(
                    available_nodes, min(nodes_communicating, len(available_nodes))
                )
            )

            # Create transactions to base station
            for node_id in communicating_nodes:
                tx_data = {
                    "type": "data_transfer",
                    "content": f"Data from {node_id} at {current_time:.2f}",
                    "size": secrets.randbelow((1000) - (100) + 1) + (100),
                    "priority": secrets.choice(["low", "medium", "high"]),
                }

                # Determine if direct path exists or routing is needed
                direct_path = False
                for link_id in interface.links:
                    nodes = interface.links[link_id].get("nodes", [])
                    if "base_station_1" in nodes and node_id in nodes:
                        direct_path = True
                        break

                logger.debug(
                    f"Transaction from {node_id} to base_station_1 - Direct path: {direct_path}"
                )

                # Record routing information
                transaction_hops.append(
                    {
                        "time": current_time,
                        "source": node_id,
                        "direct_path": direct_path,
                        "distance_to_bs": np.sqrt(
                            (node_positions[node_id][0] - base_station_pos[0]) ** 2
                            + (node_positions[node_id][1] - base_station_pos[1]) ** 2
                        ),
                    }
                )

                # Send transaction
                tx_id = interface.send_transaction(node_id, "base_station_1", tx_data)
                if tx_id:
                    blocksim_adapter.create_transaction(
                        node_id, "base_station_1", tx_data
                    )

            # Process transactions
            interface.process_pending_transactions()
            processed = blocksim_adapter.process_pending_transactions()

            # Create blocks
            if processed > 0:
                block = blocksim_adapter.create_block()
                if block:
                    logger.info(
                        "New block %(block['index'])s created by base station",
                        {block["index"]: block["index"]},
                    )

        # Output status periodically
        if int(current_time * 10) % 200 == 0 or current_time >= total_time - time_step:
            net_state = interface.get_network_state()
            blockchain_state = blocksim_adapter.get_blockchain_state()

            # Count nodes in and out of coverage
            nodes_in_coverage = 0
            nodes_outside_coverage = 0

            for node_id, position in node_positions.items():
                if node_id == "base_station_1":
                    continue

                if is_in_coverage(position, base_station_pos, args.coverage_radius):
                    nodes_in_coverage += 1
                else:
                    nodes_outside_coverage += 1

            logger.info(
                "Simulation time: %(current_time).2f/%s", total_time,
            )
            logger.info(
                f"Nodes in coverage: {nodes_in_coverage}, outside: {nodes_outside_coverage}"
            )
            logger.info(
                "Total connections: %(len(net_state['links']))s",
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

            # Save interim results
            if args.save_interim and int(current_time * 10) % 500 == 0:
                interim_output = os.path.join(
                    output_dir, f"interim_{int(current_time)}"
                )
                os.makedirs(interim_output, exist_ok=True)

                # Save network state
                interface.save_state(os.path.join(interim_output, "network_state.json"))

                # Save blockchain state
                blocksim_adapter.save_state(
                    os.path.join(interim_output, "blockchain_state.json")
                )

                # Save coverage data
                with open(
                    os.path.join(interim_output, "coverage_changes.json"), "w"
                ) as f:
                    json.dump(coverage_changes, f, indent=2)

                # Save routing data
                with open(
                    os.path.join(interim_output, "transaction_routes.json"), "w"
                ) as f:
                    json.dump(transaction_hops, f, indent=2)

    logger.info("Simulation completed")

    # Save final results
    network_state_file = os.path.join(output_dir, f"network_state_{timestamp}.json")
    interface.save_state(network_state_file)

    blockchain_state_file = os.path.join(
        output_dir, f"blockchain_state_{timestamp}.json"
    )
    blocksim_adapter.save_state(blockchain_state_file)

    # Save coverage and routing data
    with open(
        os.path.join(output_dir, f"coverage_changes_{timestamp}.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(coverage_changes, f, indent=2)

    with open(
        os.path.join(output_dir, f"transaction_routes_{timestamp}.json"), "w"
    ) as f:
        json.dump(transaction_hops, f, indent=2)

    # Animation file
    animation_file = None
    if args.animation and ns3_adapter:
        animation_file = os.path.join(output_dir, f"animation_{timestamp}.xml")

    # Save summary
    summary = {
        "timestamp": timestamp,
        "duration": total_time,
        "time_step": time_step,
        "coverage_radius": args.coverage_radius,
        "total_nodes": len(interface.nodes),
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
        "coverage_changes_file": os.path.join(
            output_dir, f"coverage_changes_{timestamp}.json"
        ),
        "transaction_routes_file": os.path.join(
            output_dir, f"transaction_routes_{timestamp}.json"
        ),
        "animation_file": animation_file,
    }

    with open(
        os.path.join(output_dir, f"summary_{timestamp}.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(summary, f, indent=2)

    return summary


def main():
    """Main function."""
    # Parse command line arguments
    args = parse_arguments()

    # Setup logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = load_config(args.config)

    # Merge config with command line arguments
    for key, value in vars(args).items():
        config[key] = value

    # Run simulation
    results = run_simulation(args, config)

    if results:
        logger.info(
            "Simulation results saved to %s", args.output_dir,
        )
        logger.info(
            "Simulation results timestamp: %(results['timestamp'])s",
            {results["timestamp"]: results["timestamp"]},
        )
    else:
        logger.error("Simulation failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

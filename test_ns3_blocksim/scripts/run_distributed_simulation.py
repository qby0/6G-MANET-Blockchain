#!/usr/bin/env python3

import argparse
import json
import logging
import os
import random
import secrets
import sys
import time
from datetime import datetime
from typing import Any, Optional

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.blockchain.network.node import Node
from models.integration.distributed_blockchain_manager import (
    DistributedBlockchainManager,
)
from models.ns3_adapter import NS3Adapter
from models.paths_manager import get_config_dir, get_ns3_dir, get_results_dir


def setup_logging(config):
    """Set up logging based on configuration"""
    level_str = config.get("logging", {}).get("level", "INFO")
    level = getattr(logging, level_str)

    # Use paths_manager for log directory
    log_dir = get_results_dir()
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir, f"distributed_simulation_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
    )

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

    return logging.getLogger("distributed_simulation")


def load_config(config_file):
    """Load configuration from file"""
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def create_nodes(config, blockchain_manager):
    """Create nodes based on configuration"""
    logger = logging.getLogger("create_nodes")

    node_count = config["network"]["node_count"]
    validator_percentage = config["network"]["validator_percentage"]
    area_size = config["network"]["area_size"]

    regular_props = config["node_properties"]["regular"]
    validator_props = config["node_properties"]["validator"]

    # Calculate number of validators
    validator_count = int(node_count * validator_percentage)
    regular_count = node_count - validator_count

    logger.info(
        f"Creating {validator_count} validators and {regular_count} regular nodes"
    )

    nodes = []

    # Create validators
    for i in range(validator_count):
        node_id = f"validator_{i}"
        position = (
            ((0) + (secrets.randbelow(int((area_size[0] - 0) * 1000)) / 1000.0)),
            ((0) + (secrets.randbelow(int((area_size[1] - 0) * 1000)) / 1000.0)),
            0,
        )

        blockchain_manager.register_node(
            node_id=node_id,
            node_type="validator",
            position=position,
            coverage_radius=validator_props["coverage_radius"],
        )

        nodes.append(node_id)

    # Create regular nodes
    for i in range(regular_count):
        node_id = f"regular_{i}"
        position = (
            ((0) + (secrets.randbelow(int((area_size[0] - 0) * 1000)) / 1000.0)),
            ((0) + (secrets.randbelow(int((area_size[1] - 0) * 1000)) / 1000.0)),
            0,
        )

        blockchain_manager.register_node(
            node_id=node_id,
            node_type="regular",
            position=position,
            coverage_radius=regular_props["coverage_radius"],
        )

        nodes.append(node_id)

    logger.info("Created %s nodes", len(nodes))
    return nodes


def update_node_positions(
    config, blockchain_manager, nodes, time_step, ns3_adapter: Optional[Any] = None
):
    """Update node positions based on mobility model"""
    area_size = config["network"]["area_size"]
    speed = config["network"]["speed"]

    # If NS3 adapter is provided, we'll use its position data instead
    if ns3_adapter and ns3_adapter.simulation_running:
        # We would fetch positions from NS-3 here
        # For now, use simple movement model
        pass

    for node_id in nodes:
        if secrets.randbelow(100) < int(
            0.8 * 100
        ):  # 80% chance of movement in each step
            # Get current position
            if node_id in blockchain_manager.nodes:
                current_pos = blockchain_manager.nodes[node_id].position
                x, y, z = current_pos

                # Simple random walk
                dx = (
                    (
                        min(
                            1.0,
                            max(
                                -1.0, -1.0 + secrets.randbelow(int(2.0 * 1000)) / 1000.0
                            ),
                        )
                    )
                    * speed
                    * time_step
                )
                dy = (
                    (
                        min(
                            1.0,
                            max(
                                -1.0, -1.0 + secrets.randbelow(int(2.0 * 1000)) / 1000.0
                            ),
                        )
                    )
                    * speed
                    * time_step
                )

                # Ensure node stays within boundaries
                new_x = max(0, min(area_size[0], x + dx))
                new_y = max(0, min(area_size[1], y + dy))

                # Update position
                blockchain_manager.update_node_position(node_id, (new_x, new_y, z))


def generate_transactions(config, blockchain_manager, nodes, current_time):
    """Generate random transactions from nodes"""
    transaction_count = 0

    for node_id in nodes:
        if node_id not in blockchain_manager.nodes:
            continue

        node = blockchain_manager.nodes[node_id]
        generation_rate = config["node_properties"][node.node_type][
            "transaction_generation_rate"
        ]

        if random.random() < generation_rate:
            # Create a simple transaction
            data = {
                "timestamp": current_time,
                "message": f"Transaction from {node_id} at {current_time:.2f}",
                "value": (
                    min(
                        100.0,
                        max(1.0, 1.0 + secrets.randbelow(int(99.0 * 1000)) / 1000.0),
                    )
                ),
            }

            transaction = blockchain_manager.create_transaction(node_id, data)
            if transaction:
                transaction_count += 1

                # Propagate to neighbors
                received_nodes = blockchain_manager.propagate_transaction(transaction)
                logging.debug(
                    f"Transaction from {node_id} propagated to {len(received_nodes)} nodes"
                )

    return transaction_count


def create_blocks(config, blockchain_manager, nodes, current_time):
    """Create blocks from pending transactions"""
    block_time = config["blockchain"]["block_time"]
    block_count = 0

    # Only validator nodes can create blocks
    validator_nodes = [
        node_id
        for node_id in nodes
        if node_id in blockchain_manager.nodes
        and blockchain_manager.nodes[node_id].node_type == "validator"
    ]

    # Check if it's time to create a block (approximately every block_time seconds)
    if current_time % block_time < 1.0:
        # Select a random validator to create a block
        if validator_nodes:
            selected_validator = secrets.choice(validator_nodes)

            # Create a block
            new_block = blockchain_manager.create_block(selected_validator)
            if new_block:
                block_count += 1
                logging.info(f"Block {new_block.index} created by {selected_validator}")

                # Propagate the block
                received_nodes = blockchain_manager.propagate_block(
                    selected_validator, new_block
                )
                logging.info(f"Block propagated to {len(received_nodes)} nodes")

    return block_count


def save_simulation_state(config, blockchain_manager, current_time):
    """Save current simulation state"""
    save_interval = config["logging"].get("save_state_interval", 30.0)

    # Save state approximately every save_interval seconds
    if current_time % save_interval < 1.0:
        save_dir = os.path.join(
            config["output"]["save_path"], f"state_{int(current_time)}"
        )
        os.makedirs(save_dir, exist_ok=True)

        success = blockchain_manager.save_state(save_dir)
        if success:
            logging.info(f"Simulation state saved at t={current_time:.2f}")


def log_metrics(config, blockchain_manager, metrics, current_time):
    """Log metrics about the simulation"""
    metrics["time"].append(current_time)

    # Get network status
    status = blockchain_manager.get_network_status()

    # Log blockchain height
    if "blockchain_height" in config["logging"]["metrics"]:
        metrics["max_blockchain_height"].append(status["max_blockchain_height"])
        metrics["min_blockchain_height"].append(status["min_blockchain_height"])
        metrics["avg_blockchain_height"].append(status["avg_blockchain_height"])

    # Log connectivity
    if "connectivity" in config["logging"]["metrics"]:
        # Calculate average neighbor count
        avg_neighbors = 0
        if blockchain_manager.nodes:
            neighbor_counts = [
                len(node.neighbors) for node in blockchain_manager.nodes.values()
            ]
            avg_neighbors = sum(neighbor_counts) / len(neighbor_counts)

        metrics["avg_neighbors"].append(avg_neighbors)

    return metrics


def save_metrics(config, metrics):
    """Save metrics to output file"""
    output_path = os.path.join(
        config["output"]["save_path"],
        f"metrics_{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

    logging.info(f"Metrics saved to {output_path}")


def run_simulation(config, ns3_path: Optional[Any] = None):
    """Run the distributed blockchain simulation"""
    logger = setup_logging(config)
    logger.info(
        f"Starting distributed blockchain simulation: {config['simulation_name']}"
    )

    # Set random seed for reproducibility
    random.seed(config["random_seed"])

    # Initialize NS3Adapter if path is provided
    ns3_adapter = None
    if ns3_path:
        try:
            logger.info("Initializing NS3Adapter with path: %s", ns3_path)
            ns3_adapter = NS3Adapter(
                config_file=os.path.join(get_config_dir(), "distributed.json"),
                ns3_path=ns3_path,
            )
            logger.info("NS3Adapter initialized successfully")
        except Exception as e:
            logger.error("Error initializing NS3Adapter: %s", str(e))
            logger.warning("Continuing simulation without NS-3 integration")

    # Create blockchain manager
    config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "config", "distributed.json")
    )
    blockchain_manager = DistributedBlockchainManager(config_path)

    # Create nodes
    nodes = create_nodes(config, blockchain_manager)

    # Initialize blockchain in a distributed way
    logger.info("Initializing blockchain network...")
    success = blockchain_manager.initialize_blockchain_network()

    if not success:
        logger.error("Failed to initialize blockchain network")
        return False

    logger.info("Blockchain network initialized")

    # Initialize metrics
    metrics = {
        "time": [],
        "max_blockchain_height": [],
        "min_blockchain_height": [],
        "avg_blockchain_height": [],
        "avg_neighbors": [],
        "transactions_created": [],
        "blocks_created": [],
    }

    # Start NS-3 simulation if adapter is available
    if ns3_adapter:
        logger.info("Setting up NS-3 simulation script")
        ns3_adapter.setup_ns3_script()
        logger.info("Starting NS-3 integrated simulation")
        ns3_adapter.simulation_running = True

    # Main simulation loop
    time_step = 1.0  # Update every second
    simulation_time = config["simulation_time"]
    current_time = 0.0

    transaction_count = 0
    block_count = 0

    logger.info(
        "Running simulation for %s seconds",
        simulation_time,
    )

    simulation_start = time.time()

    while current_time < simulation_time:
        # Update node positions
        update_node_positions(config, blockchain_manager, nodes, time_step, ns3_adapter)

        # Update network topology
        blockchain_manager.update_topology()

        # Generate transactions
        new_transactions = generate_transactions(
            config, blockchain_manager, nodes, current_time
        )
        transaction_count += new_transactions

        # Create blocks
        new_blocks = create_blocks(config, blockchain_manager, nodes, current_time)
        block_count += new_blocks

        # Save simulation state periodically
        save_simulation_state(config, blockchain_manager, current_time)

        # Log metrics
        metrics["transactions_created"].append(new_transactions)
        metrics["blocks_created"].append(new_blocks)
        metrics = log_metrics(config, blockchain_manager, metrics, current_time)

        # Progress update
        if int(current_time) % 10 == 0 and current_time > 0:
            progress = (current_time / simulation_time) * 100
            elapsed = time.time() - simulation_start
            remaining = (
                (elapsed / current_time) * (simulation_time - current_time)
                if current_time > 0
                else 0
            )

            logger.info(
                f"Simulation progress: {progress:.1f}% (Time: {current_time:.1f}s, "
                f"Transactions: {transaction_count}, Blocks: {block_count})"
            )
            logger.info("Estimated time remaining: %.1fs", remaining)

        # Increment time
        current_time += time_step

    # Stop NS-3 simulation if running
    if ns3_adapter and ns3_adapter.simulation_running:
        logger.info("Stopping NS-3 simulation")
        ns3_adapter.simulation_running = False
        # Save NS-3 results
        ns3_results = ns3_adapter.get_simulation_state()
        ns3_output_path = os.path.join(
            config["output"]["save_path"],
            f"ns3_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
        )
        ns3_adapter.save_results(ns3_results, os.path.basename(ns3_output_path))

    simulation_end = time.time()
    simulation_duration = simulation_end - simulation_start

    logger.info(
        "Simulation completed in %.2f seconds",
        simulation_duration,
    )
    logger.info("Total transactions: %s", transaction_count)
    logger.info("Total blocks: %s", block_count)

    # Final network status
    status = blockchain_manager.get_network_status()
    logger.info("Final network status: %s", status)

    # Save metrics
    save_metrics(config, metrics)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Run distributed blockchain simulation"
    )

    # Change default path to be relative to the script location
    default_config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "config", "distributed.json")
    )
    parser.add_argument(
        "-c", "--config", default=default_config_path, help="Path to config file"
    )
    # Add NS-3 path argument
    parser.add_argument(
        "--ns3-path", help="Path to NS-3 installation (optional for NS-3 integration)"
    )
    args = parser.parse_args()

    # Get absolute path of the config file
    config_path = os.path.abspath(args.config)

    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        print(f"Make sure the file exists or provide correct path with -c option")
        return 1

    # Get NS-3 path
    ns3_path = None
    if args.ns3_path:
        ns3_path = args.ns3_path
    else:
        # Try to get NS-3 path from paths_manager
        ns3_path = get_ns3_dir()
        if ns3_path:
            print(f"Using NS-3 path from paths_manager: {ns3_path}")
        else:
            print("NS-3 path not provided and not found in paths_manager")
            print("Continuing without NS-3 integration")

    config = load_config(config_path)

    # Ensure output directory exists
    os.makedirs(config["output"]["save_path"], exist_ok=True)

    try:
        success = run_simulation(config, ns3_path)
        return 0 if success else 1
    except Exception as e:
        logging.exception(f"Error running simulation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

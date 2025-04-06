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
from typing import Any, Dict, List, Optional, Tuple, Union

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
    level = getattr(logging, level_str, logging.INFO)

    # Use paths_manager for log directory
    log_dir = get_results_dir()
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir, f"distributed_simulation_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
    )

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Return a specific logger for this module
    return logging.getLogger("distributed_simulation_script")


def load_config(config_file):
    """Load configuration from file"""
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.getLogger("load_config").error(
            f"Configuration file not found: {config_file}"
        )
        raise
    except json.JSONDecodeError as e:
        logging.getLogger("load_config").error(
            f"Error decoding JSON from {config_file}: {e}"
        )
        raise
    except Exception as e:
        logging.getLogger("load_config").error(
            f"Error loading configuration from {config_file}: {e}", exc_info=True
        )
        raise


def create_nodes(config, blockchain_manager):
    """Create nodes based on configuration and register them"""
    logger = logging.getLogger("create_nodes")

    node_count = config["network"]["node_count"]
    validator_percentage = config["network"]["validator_percentage"]
    area_size = config["network"]["area_size"]

    # Handle different property structures
    node_props = config.get("node_properties", {})
    regular_props = node_props.get("regular", {"coverage_radius": 150.0})
    validator_props = node_props.get("validator", {"coverage_radius": 200.0})

    # Calculate number of validators
    validator_count = max(1, int(node_count * validator_percentage))
    regular_count = node_count - validator_count

    logger.info(
        f"Creating {validator_count} validators and {regular_count} regular nodes"
    )

    nodes_created = []

    # Use consistent naming scheme expected by NS3Adapter position reader ('node_0', 'node_1', ...)
    node_index = 0

    # Create validators
    for _ in range(validator_count):
        node_id = f"node_{node_index}"
        position = (
            secrets.randbelow(int(area_size[0])),
            secrets.randbelow(int(area_size[1])),
            0 if len(area_size) < 3 else secrets.randbelow(int(area_size[2])),
        )

        try:
            blockchain_manager.register_node(
                node_id=node_id,
                node_type="validator",
                position=position,
                coverage_radius=float(validator_props["coverage_radius"]),
            )
            nodes_created.append(node_id)
            node_index += 1
        except Exception as e:
            logger.error(
                f"Failed to register validator node {node_id}: {e}", exc_info=True
            )

    # Create regular nodes
    for _ in range(regular_count):
        node_id = f"node_{node_index}"
        position = (
            secrets.randbelow(int(area_size[0])),
            secrets.randbelow(int(area_size[1])),
            0 if len(area_size) < 3 else secrets.randbelow(int(area_size[2])),
        )
        try:
            blockchain_manager.register_node(
                node_id=node_id,
                node_type="regular",
                position=position,
                coverage_radius=float(regular_props["coverage_radius"]),
            )
            nodes_created.append(node_id)
            node_index += 1
        except Exception as e:
            logger.error(
                f"Failed to register regular node {node_id}: {e}", exc_info=True
            )

    logger.info(
        "Created and registered %s nodes in BlockchainManager", len(nodes_created)
    )
    return nodes_created


def generate_transactions(config, blockchain_manager, nodes, current_time):
    """Generate random transactions from nodes"""
    logger = logging.getLogger("generate_transactions")
    transaction_count = 0

    node_props = config.get("node_properties", {})
    regular_props = node_props.get("regular", {"transaction_generation_rate": 0.1})
    validator_props = node_props.get("validator", {"transaction_generation_rate": 0.05})

    for node_id in nodes:
        if node_id not in blockchain_manager.nodes:
            logger.warning(
                "Node %s listed for tx generation but not found in manager.", node_id
            )
            continue

        node = blockchain_manager.nodes[node_id]
        # Get rate based on node type
        if node.node_type == "validator":
            generation_rate = validator_props.get("transaction_generation_rate", 0.05)
        else:
            generation_rate = regular_props.get("transaction_generation_rate", 0.1)

        if random.random() < float(generation_rate):
            # Create a simple transaction
            data = {
                "timestamp": current_time,
                "message": f"Transaction from {node_id} at {current_time:.2f}",
                "value": random.uniform(1.0, 100.0),
            }

            try:
                transaction = blockchain_manager.create_transaction(node_id, data)
                if transaction:
                    transaction_count += 1
            except Exception as e:
                logger.error(
                    f"Error creating/propagating transaction for {node_id}: {e}",
                    exc_info=True,
                )

    return transaction_count


def create_blocks(config, blockchain_manager, nodes, current_time):
    """Create blocks from pending transactions"""
    logger = logging.getLogger("create_blocks")
    block_time = float(config["blockchain"].get("block_time", 10.0))
    block_count = 0

    # Only validator nodes can create blocks
    validator_nodes = [
        node_id
        for node_id in nodes
        if node_id in blockchain_manager.nodes
        and blockchain_manager.nodes[node_id].node_type == "validator"
    ]

    # Check if it's time to create a block
    # Use a small tolerance for floating point comparison
    time_since_last_block = current_time % block_time
    create_block_now = (
        time_since_last_block < 0.1 or abs(time_since_last_block - block_time) < 0.1
    )

    # More robust check: create block roughly every block_time seconds
    # Need to track last block creation time per validator or globally?
    # Simple approach: one block creation attempt per interval globally
    if create_block_now:
        # Select a random validator to attempt block creation
        if validator_nodes:
            selected_validator = secrets.choice(validator_nodes)

            try:
                # Attempt to create a block (manager handles pending tx)
                new_block = blockchain_manager.create_block(selected_validator)
                if new_block:
                    block_count += 1
                    logger.info(
                        f"Block {new_block.index} created by {selected_validator} at time {current_time:.2f}"
                    )
            except Exception as e:
                logger.error(
                    f"Error creating/propagating block for {selected_validator}: {e}",
                    exc_info=True,
                )

    return block_count


def save_simulation_state(config, blockchain_manager, current_time, last_save_time):
    """Save current simulation state periodically"""
    logger = logging.getLogger("save_state")
    save_interval = float(config["logging"].get("save_state_interval", 30.0))
    save_path_base = config["output"]["save_path"]

    if current_time - last_save_time >= save_interval:
        state_file = os.path.join(
            save_path_base, f"state_{int(round(current_time))}.json"
        )
        try:
            blockchain_manager.save_state(state_file)
            logger.info(
                f"Simulation state saved to {state_file} at t={current_time:.2f}"
            )
            return current_time
        except Exception as e:
            logger.error(
                f"Failed to save state at time {current_time:.2f}: {e}", exc_info=True
            )
    return last_save_time


def run_simulation(config, config_path, ns3_path=None):
    """Main simulation runner function"""
    logger = setup_logging(config)
    logger.info(
        "Starting distributed blockchain simulation: %s",
        config.get("simulation_name", "UnnamedSim"),
    )

    # --- Initialization ---
    ns3_adapter = None
    if ns3_path:
        try:
            logger.info("Initializing NS3Adapter with path: %s", ns3_path)
            # Initialize adapter, pass config path if needed, or let it use its default
            adapter_config_file = config.get("ns3", {}).get("adapter_config")
            ns3_adapter = NS3Adapter(config_file=adapter_config_file, ns3_path=ns3_path)
            # Explicitly set the adapter's config to the main sim config if needed
            # This depends on NS3Adapter's design; assume it uses its own or defaults for now.
            # ns3_adapter.config = config # Uncomment if NS3Adapter needs the main config
            logger.info(
                "NS3Adapter initialized successfully. Version: %s",
                ns3_adapter.get_ns3_version(),
            )
        except Exception as e:
            logger.error("Failed to initialize NS3Adapter: %s", e, exc_info=True)
            return False
    else:
        logger.warning(
            "NS-3 path not provided, proceeding without NS-3 mobility/network simulation."
        )
        return False

    # Create blockchain manager
    # Pass the config file PATH, which is now an argument
    blockchain_manager = DistributedBlockchainManager(config_path=config_path)

    # Create nodes and register them in the blockchain manager
    # Use the node IDs ('node_0', 'node_1', ...) returned by create_nodes
    sim_node_ids = create_nodes(config, blockchain_manager)
    if not sim_node_ids:
        logger.error("Failed to create simulation nodes.")
        if ns3_adapter:
            ns3_adapter.cleanup()
        return False

    logger.info("Initializing blockchain network...")
    if not blockchain_manager.initialize_blockchain_network():
        logger.error("Failed to initialize blockchain network.")
        if ns3_adapter:
            ns3_adapter.cleanup()
        return False
    logger.info("Blockchain network initialized")

    # --- Start NS-3 Simulation (if adapter exists) ---
    ns3_started = False
    if ns3_adapter:
        logger.info("Starting NS-3 background simulation...")
        sim_duration = float(config.get("simulation_time", 300.0))
        # Get resolution from config, default if not present
        ns3_resolution = float(config.get("ns3", {}).get("position_resolution", 0.5))
        # NS-3 output dir should be distinct or managed
        # Ensure base output path exists
        base_output_path = config["output"]["save_path"]
        os.makedirs(base_output_path, exist_ok=True)
        ns3_output_dir = os.path.join(base_output_path, "ns3_run_output")

        ns3_started = ns3_adapter.start_ns3_simulation(
            duration=sim_duration + 5.0,
            resolution=ns3_resolution,
            output_dir=ns3_output_dir,
        )
        if not ns3_started:
            logger.error("Failed to start NS-3 simulation process. Aborting.")
            try:
                blockchain_manager.save_state(
                    os.path.join(
                        config["output"]["save_path"],
                        "final_state_ns3_start_error.json",
                    )
                )
            except Exception:
                pass
            return False
        logger.info("NS-3 simulation process appears to have started successfully.")

    # --- Main Simulation Loop ---
    start_time = time.time()
    current_sim_time = 0.0
    # Use a smaller time step for the Python loop to react faster to NS-3 updates
    python_loop_step = float(config.get("python_loop_step", 0.2))
    last_progress_log_time = -10.0
    last_save_time = -1.0

    total_transactions = 0
    total_blocks = 0

    sim_duration = float(config.get("simulation_time", 300.0))
    logger.info("Running simulation for %s seconds", sim_duration)

    simulation_successful = True

    try:
        while current_sim_time < sim_duration:
            loop_start_time = time.time()

            # 1. Get Node Positions from NS-3 (if integrated)
            if ns3_adapter and ns3_started:
                if (
                    ns3_adapter.ns3_process
                    and ns3_adapter.ns3_process.poll() is not None
                ):
                    logger.error(
                        "NS-3 process terminated prematurely with code %d. Stopping simulation.",
                        ns3_adapter.ns3_process.poll(),
                    )
                    simulation_successful = False
                    break

                ns3_positions = ns3_adapter.get_ns3_node_positions()
                if ns3_positions:
                    nodes_updated = 0
                    for node_id, pos in ns3_positions.items():
                        if node_id in blockchain_manager.nodes:
                            if blockchain_manager.update_node_position(node_id, pos):
                                nodes_updated += 1
                        else:
                            logger.warning(
                                "Node ID %s from NS-3 not found in Blockchain Manager",
                                node_id,
                            )

            # If not using NS-3, we currently don't have a fallback mobility model here.
            # The simulation would run with static nodes if NS-3 isn't used.

            # 2. Update Node Connections (based on potentially updated positions)
            blockchain_manager.update_topology()

            # 3. Generate Transactions
            tx_count = generate_transactions(
                config, blockchain_manager, sim_node_ids, current_sim_time
            )
            total_transactions += tx_count

            # 4. Process Pending Transactions (within Blockchain Manager)
            # Removing incorrect call - processing is handled by block creation
            # blockchain_manager.process_all_pending_transactions()

            # 5. Create and Propagate Blocks (handle consensus internally)
            block_count = create_blocks(
                config, blockchain_manager, sim_node_ids, current_sim_time
            )
            total_blocks += block_count

            # 6. Save State Periodically
            last_save_time = save_simulation_state(
                config, blockchain_manager, current_sim_time, last_save_time
            )

            # 7. Collect Metrics
            # Removing attempt to collect non-existent metrics
            # try:
            #     current_metrics = blockchain_manager.collect_metrics()
            #     current_metrics['simulation_time'] = round(current_sim_time, 2)
            #     metrics.append(current_metrics)
            # except Exception as e:
            #     logger.warning(f"Failed to collect metrics at time {current_sim_time:.2f}: {e}")

            # 8. Advance Time and Progress Log
            current_sim_time += python_loop_step

            elapsed_wall_time = time.time() - start_time
            loop_wall_time = time.time() - loop_start_time

            if current_sim_time - last_progress_log_time >= 10.0:
                progress = (current_sim_time / sim_duration) * 100
                est_remaining_wall_time = (
                    (
                        elapsed_wall_time
                        / current_sim_time
                        * (sim_duration - current_sim_time)
                    )
                    if current_sim_time > 0
                    else 0
                )
                logger.info(
                    f"Sim Progress: {progress:.1f}% (Sim Time: {current_sim_time:.1f}s / {sim_duration}s, "
                    f"Wall Time: {elapsed_wall_time:.1f}s, Tx: {total_transactions}, Blk: {total_blocks})"
                )
                last_progress_log_time = current_sim_time

            sleep_duration = python_loop_step - loop_wall_time
            if sleep_duration > 0:
                time.sleep(sleep_duration)

    except KeyboardInterrupt:
        logger.warning("Simulation interrupted by user.")
        simulation_successful = False
    except Exception as e:
        logger.error("Critical error during simulation loop: %s", e, exc_info=True)
        simulation_successful = False
    finally:
        logger.info("Simulation loop finished or interrupted.")
        if ns3_adapter:
            logger.info("Stopping NS-3 simulation process...")
            ns3_adapter.cleanup()
            logger.info("NS-3 simulation stop sequence initiated.")

        final_state_path = os.path.join(
            config["output"]["save_path"], "final_state.json"
        )
        try:
            blockchain_manager.save_state(final_state_path)
            logger.info(f"Final simulation state saved to {final_state_path}")
        except Exception as e:
            logger.error(f"Failed to save final state: {e}")

        total_elapsed_wall_time = time.time() - start_time
        logger.info(
            f"Simulation completed. Success: {simulation_successful}. Wall time: {total_elapsed_wall_time:.2f} seconds"
        )
        logger.info(f"Total transactions generated: {total_transactions}")
        logger.info(f"Total blocks created: {total_blocks}")

        try:
            final_status = blockchain_manager.get_network_status()
            logger.info(f"Final network status: {final_status}")
        except Exception as e:
            logger.error(f"Failed to get final network status: {e}")

    return simulation_successful


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run distributed blockchain simulation with optional NS-3 integration"
    )

    # Default config path relative to this script's location -> config dir
    default_config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "config", "distributed.json")
    )
    parser.add_argument(
        "-c",
        "--config",
        default=default_config_path,
        help=f"Path to config file (default: {default_config_path})",
    )
    # Add NS-3 path argument
    parser.add_argument(
        "--ns3-path",
        help="Path to NS-3 installation directory (required for NS-3 integration)",
    )
    # Argument to disable NS-3 even if path is found (for debugging)
    parser.add_argument(
        "--no-ns3",
        action="store_true",
        help="Force running without NS-3 integration, even if ns3-path is found.",
    )
    args = parser.parse_args()

    # Get absolute path of the config file
    config_path = os.path.abspath(args.config)

    # Load configuration first to set up logging properly
    try:
        config = load_config(config_path)
    except Exception:
        # Error already logged by load_config
        return 1

    # Setup logging based on loaded config (or defaults if logging section missing)
    logger = setup_logging(config)

    # Determine NS-3 path
    ns3_path = None
    if args.no_ns3:
        logger.info("--no-ns3 flag set. NS-3 integration will be disabled.")
    else:
        if args.ns3_path:
            ns3_path = os.path.abspath(args.ns3_path)
            logger.info(f"Using provided NS-3 path: {ns3_path}")
        else:
            # Try to get NS-3 path from paths_manager
            ns3_path_from_manager = get_ns3_dir()
            if ns3_path_from_manager:
                ns3_path = ns3_path_from_manager
                logger.info(f"Using NS-3 path from paths_manager: {ns3_path}")
            else:
                logger.warning(
                    "NS-3 path not provided via --ns3-path and not found in paths_manager."
                )
                logger.warning("Proceeding without NS-3 integration.")

        if ns3_path and not os.path.isdir(ns3_path):
            logger.error(
                f"Determined NS-3 path does not exist or is not a directory: {ns3_path}"
            )
            ns3_path = None

    # Ensure 'output' key and 'save_path' exist in config before running sim
    if "output" not in config or "save_path" not in config["output"]:
        logger.warning(
            "Configuration file is missing 'output' section or 'save_path' key."
        )
        default_output_dir = os.path.join(
            get_results_dir() or ".", "default_sim_output"
        )
        config["output"] = config.get("output", {})
        config["output"]["save_path"] = config["output"].get(
            "save_path", default_output_dir
        )
        logger.warning("Using default output path: %s", config["output"]["save_path"])

    # Ensure the base output directory exists before simulation starts
    try:
        os.makedirs(config["output"]["save_path"], exist_ok=True)
    except OSError as e:
        logger.error(
            f"Could not create base output directory {config['output']['save_path']}: {e}"
        )
        return 1

    # Run the main simulation logic
    exit_code = 0
    try:
        # Pass config_path to run_simulation
        success = run_simulation(config, config_path, ns3_path)
        exit_code = 0 if success else 1
    except Exception as e:
        logger.critical(
            f"Unhandled critical error during simulation execution: {e}", exc_info=True
        )
        exit_code = 1

    logger.info(f"Simulation script finished with exit code {exit_code}.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

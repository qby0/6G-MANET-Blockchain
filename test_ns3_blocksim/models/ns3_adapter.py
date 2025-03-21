#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified NS3 Adapter class for interacting with NS-3 simulation environment.
This adapter provides functionality for both basic NS-3 operations and blockchain integration.
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

# Import paths manager
from models.paths_manager import get_config_dir, get_ns3_dir, get_results_dir

logger = logging.getLogger(__name__)


class NS3Adapter:
    """
    A unified adapter for interacting with NS-3 simulation environment.
    This class handles both basic operations and blockchain integration features.
    """

    def __init__(
        self, config_file: Optional[str] = None, ns3_path: Optional[str] = None
    ):
        """
        Initialize the NS-3 adapter with the path to NS-3 and optional config file.

        Args:
            config_file: Path to the configuration file (if None, default configuration is used)
            ns3_path: Path to NS-3 directory, if None, get_ns3_dir() will be used
        """
        # Set up logging
        self.logger = logging.getLogger("NS3Adapter")

        # Get NS-3 path from parameter, or from paths_manager if not provided
        self.ns3_path = ns3_path if ns3_path else get_ns3_dir()
        if not self.ns3_path:
            # If paths_manager doesn't have it, try environment
            self.ns3_path = os.environ.get("NS3_DIR")
            if not self.ns3_path:
                self.logger.error(
                    "NS-3 path not specified and not found in environment or paths_manager"
                )
                raise ValueError(
                    "NS-3 path not found. Please specify it or set NS3_DIR in env_paths.json or environment"
                )

        # Verify NS-3 path exists
        if not os.path.exists(self.ns3_path):
            raise FileNotFoundError(f"NS-3 directory not found at {self.ns3_path}")

        # Initialize NS-3 script path
        self.ns3_script = os.path.join(self.ns3_path, "ns3")

        # Check if NS-3 script exists
        if not os.path.exists(self.ns3_script):
            logger.warning(
                f"NS-3 script not found at {self.ns3_script}, some functionality may be limited"
            )

        logger.info(
            "NS3Adapter initialized with NS-3 path: %s",
            self.ns3_path,
        )

        # Load configuration for blockchain integration if provided
        if config_file:
            self.config_file = config_file
        else:
            # Use default configuration file from the config directory
            self.config_file = os.path.join(get_config_dir(), "integrated.json")
            self.logger.info(
                "Using default configuration file: %s",
                self.config_file,
            )

        # Load configuration if file exists
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            self.logger.info(
                "Configuration loaded from: %s",
                self.config_file,
            )
        else:
            self.logger.warning(
                "Configuration file not found: %s",
                self.config_file,
            )
            self.logger.info("Using default configuration")
            self.config = self._get_default_config()

        # Create output directory using paths_manager
        self.output_dir = os.path.join(
            get_results_dir(), self.config.get("simulation_name", "integrated_sim")
        )
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info(
            "Output directory: %s", self.output_dir
        )

        # Initialize state variables for blockchain integration
        self.simulation_running = False
        self.current_state: Dict[str, Any] = {}
        self.network_events: List[Any] = []
        self.blockchain_events: List[Any] = []

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for the integrated simulation.

        Returns:
            Dictionary with default configuration
        """
        return {
            "simulation_name": "integrated_ns3_blockchain",
            "simulation_time": 300.0,
            "time_resolution": 0.1,
            "random_seed": 42,
            "network": {
                "type": "manet",
                "node_count": 20,
                "validator_percentage": 0.2,
                "area_size": [1000, 1000],
                "mobility_model": "RandomWalk2dMobilityModel",
                "speed": 5.0,
            },
            "blockchain": {
                "consensus_threshold": 0.67,
                "block_time": 10.0,
                "max_propagation_rounds": 5,
                "transaction_rate": 0.05,
            },
            "ns3": {
                "routing_protocol": "AODV",
                "packet_size": 1024,
                "data_rate": "2Mbps",
                "wifi_standard": "802.11g",
            },
            "output": {"save_path": self.output_dir, "format": "json"},
        }

    def get_ns3_version(self) -> str:
        """
        Get the version of NS-3 installed.

        Returns:
            The version string of NS-3
        """
        if not os.path.exists(self.ns3_script):
            return "Unknown (ns3 script not found)"

        try:
            # Run ns3 --version to get version
            result = subprocess.run(
                [self.ns3_script, "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Extract version from output
            version_match = re.search(r"ns-3\.(\d+\.\d+)", result.stdout)
            if version_match:
                return version_match.group(0)
            return f"Unknown format: {result.stdout.strip()}"
        except subprocess.CalledProcessError as e:
            logger.error("Error getting NS-3 version: %s", e)
            return f"Error: {e}"
        except Exception as e:
            logger.error("Unexpected error getting NS-3 version: %s", e)
            return f"Unexpected error: {e}"

    def list_modules(self) -> List[str]:
        """
        List all available NS-3 modules.

        Returns:
            List of module names
        """
        if not os.path.exists(self.ns3_script):
            logger.warning("Cannot list modules: ns3 script not found")
            return []

        try:
            # Run ns3 show modules to get available modules
            result = subprocess.run(
                [self.ns3_script, "show", "modules"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Extract module names
            modules = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith(("*", "=")):
                    modules.append(line)
            return modules
        except subprocess.CalledProcessError as e:
            logger.error("Error listing NS-3 modules: %s", e)
            return []
        except Exception as e:
            logger.error("Unexpected error listing NS-3 modules: %s", e)
            return []

    def run_simulation(
        self, sim_program: str, args: Dict[str, str]
    ) -> Tuple[bool, str]:
        """
        Run an NS-3 simulation with the given program and arguments.

        Args:
            sim_program: Name of the simulation program
            args: Dictionary of arguments to pass to the simulation

        Returns:
            (success, output) tuple
        """
        if not os.path.exists(self.ns3_script):
            logger.error("Cannot run simulation: ns3 script not found")
            return False, "NS-3 script not found"

        # Build command
        cmd = [self.ns3_script, "run", sim_program]

        # Add arguments
        for key, value in args.items():
            cmd.append(f"--{key}={value}")

        try:
            # Run simulation
            logger.info(
                "Running NS-3 simulation: %(' '.join(cmd))s",
                {" ".join(cmd): " ".join(cmd)},
            )
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            logger.error("Error running simulation: %s", e)
            return False, f"Error: {e.stderr}"
        except Exception as e:
            logger.error("Unexpected error running simulation: %s", e)
            return False, f"Unexpected error: {e}"

    def setup_ns3_script(self) -> str:
        """
        Sets up the NS-3 script for integrated simulation.

        Returns:
            Path to the NS-3 script
        """
        # Implement NS-3 script setup logic
        # This would create or modify NS-3 script files as needed
        return os.path.join(self.ns3_path, "scratch", "integrated-sim.cc")

    def run_integrated_simulation(self) -> Dict[str, Any]:
        """
        Run the integrated NS-3 and blockchain simulation.

        Returns:
            Dictionary with simulation results
        """
        self.logger.info("Starting integrated simulation")
        self.simulation_running = True

        # Placeholder for integrated simulation logic
        # In a real implementation, this would:
        # 1. Set up the NS-3 simulation with blockchain integration
        # 2. Run the simulation
        # 3. Collect and process results

        self.simulation_running = False
        self.logger.info("Integrated simulation completed")

        # Return results
        return {
            "simulation_time": self.config["simulation_time"],
            "node_count": self.config["network"]["node_count"],
            "blockchain_events": len(self.blockchain_events),
            "network_events": len(self.network_events),
        }

    def get_simulation_state(self) -> Dict[str, Any]:
        """
        Get the current state of the integrated simulation.

        Returns:
            Dictionary with current simulation state
        """
        # Create a more meaningful simulation state
        simulation_state = {
            "timestamp": time.time(),
            "simulation_name": self.config.get("simulation_name", "integrated_sim"),
            "simulation_time_elapsed": self.config.get("simulation_time", 300.0),
            "network": {
                "nodes_count": self.config.get("network", {}).get("node_count", 0),
                "validator_percentage": self.config.get("network", {}).get(
                    "validator_percentage", 0.2
                ),
                "area_size": self.config.get("network", {}).get(
                    "area_size", [1000, 1000]
                ),
                "connected_nodes": len(self.current_state.get("connected_nodes", [])),
                "network_events": len(self.network_events),
            },
            "blockchain": {
                "blocks_created": len(self.current_state.get("blocks", [])),
                "transactions_processed": len(
                    self.current_state.get("transactions", [])
                ),
                "blockchain_events": len(self.blockchain_events),
            },
            "performance": {
                "average_latency": self.current_state.get("average_latency", 0.0),
                "throughput": self.current_state.get("throughput", 0.0),
                "consensus_rounds": self.current_state.get("consensus_rounds", 0),
            },
        }

        return simulation_state

    def save_results(
        self, results: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """
        Save simulation results to a file.

        Args:
            results: Dictionary with simulation results
            filename: Name of the output file (without path)

        Returns:
            Path to the saved file
        """
        if not filename:
            filename = f"{self.config['simulation_name']}_results.json"

        output_path = os.path.join(self.output_dir, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        self.logger.info(
            "Results saved to: %s", output_path
        )
        return output_path

    def __str__(self) -> str:
        """String representation of the NS3Adapter"""
        return f"NS3Adapter(ns3_path={self.ns3_path})"


# Module test code
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Create the adapter
        adapter = NS3Adapter()

        # Run a simple test
        results = adapter.run_integrated_simulation()

        # Save results
        adapter.save_results(results)

        print("Test completed successfully")

    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified NS3 Adapter class for interacting with NS-3 simulation environment.
This adapter provides functionality for both basic NS-3 operations and blockchain integration.
"""

import io
import json
import logging
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd  # Need pandas for efficient CSV reading

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
        if os.path.isfile(self.config_file):
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
        self.logger.info("Output directory: %s", self.output_dir)

        # Initialize state variables for blockchain integration
        self.simulation_running = False
        self.current_state: Dict[str, Any] = {}
        self.network_events: List[Any] = []
        self.blockchain_events: List[Any] = []
        self.ns3_process = None
        self.ns3_output_dir = None
        self.ns3_pos_file = None

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for the integrated simulation.

        Returns:
            Dictionary with default configuration
        """
        # Создаем базовый конфиг и output_dir для него
        self.output_dir = os.path.join(get_results_dir(), "integrated_ns3_blockchain")
        os.makedirs(self.output_dir, exist_ok=True)

        return {
            "simulation_name": "integrated_ns3_blockchain",
            "simulation_time": 300.0,
            "time_resolution": 0.1,
            "random_seed": 42,
            "network": {
                "type": "manet",
                "node_count": 20,
                "validator_percentage": 0.2,
                "area_size": [1000, 1000, 100],
                "mobility_model": "SixGMobilityModel",
                "speed": {"min": 0.5, "max": 30.0},
                "clustering_factor": 0.7,
                "update_interval": 0.01,
                "3d_enabled": True,
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
                cwd=self.ns3_path,  # Run from ns3 directory
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
                cwd=self.ns3_path,  # Run from ns3 directory
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
        NOTE: This runs the simulation to completion, not in the background.

        Args:
            sim_program: Name of the simulation program (e.g., 'scratch/my_sim')
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
            logger.info("Running NS-3 simulation: %s", " ".join(cmd))
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=self.ns3_path,  # Run from ns3 directory
            )
            logger.info("NS-3 simulation completed successfully")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            logger.error("NS-3 simulation failed: %s", e)
            logger.error("NS-3 stderr: %s", e.stderr)
            return False, e.stderr
        except Exception as e:
            logger.error("Unexpected error running NS-3 simulation: %s", e)
            return False, str(e)

    def start_ns3_simulation(
        self, duration: float, resolution: float, output_dir: str
    ) -> bool:
        """
        Starts the manet-blockchain-sim.cc NS-3 script in the background.

        Args:
            duration: Simulation duration for NS-3.
            resolution: Time resolution for position recording in NS-3.
            output_dir: Directory where NS-3 will write its output files.

        Returns:
            True if the process started successfully, False otherwise.
        """
        if not os.path.exists(self.ns3_script):
            self.logger.error(
                "Cannot start NS-3 simulation: ns3 script not found at %s",
                self.ns3_script,
            )
            return False

        # Ensure the output directory exists
        self.ns3_output_dir = os.path.abspath(output_dir)
        os.makedirs(self.ns3_output_dir, exist_ok=True)
        self.ns3_pos_file = os.path.join(self.ns3_output_dir, "node_positions.csv")

        # Clean up previous position file if it exists
        if os.path.exists(self.ns3_pos_file):
            try:
                os.remove(self.ns3_pos_file)
                self.logger.info(
                    "Removed existing NS-3 position file: %s", self.ns3_pos_file
                )
            except OSError as e:
                self.logger.error(
                    "Failed to remove existing position file %s: %s",
                    self.ns3_pos_file,
                    e,
                )
                # Decide if this is fatal or not, for now we continue cautiously
                pass

        sim_program = "scratch/manet-blockchain-sim"
        # We will run the command from the ns-3 directory itself,
        # and tell the script where to put output using outputDir arg.
        # Note: The .cc script needs to correctly use outputDir argument.
        # Let's assume manet-blockchain-sim.cc uses outputDir correctly.
        cmd = [
            self.ns3_script,
            "run",
            sim_program,
            "--",  # Separator for script arguments
            f"--duration={duration}",
            f"--resolution={resolution}",
            f"--outputDir={self.ns3_output_dir}",  # Pass output dir to the script
        ]

        try:
            self.logger.info("Starting NS-3 simulation: %s", " ".join(cmd))
            # Start NS-3 as a background process
            self.ns3_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.ns3_path,  # Run the ns3 script from its directory
            )
            self.simulation_running = True
            self.logger.info(
                "NS-3 simulation process started (PID: %d)", self.ns3_process.pid
            )
            # Give NS-3 a moment to start up and create the file (at least two resolutions)
            initial_wait = max(3, resolution * 2)
            time.sleep(initial_wait)
            # Check for the position file, but do not abort if it's missing
            if not os.path.exists(self.ns3_pos_file):
                self.logger.warning(
                    "NS-3 position file not found after startup: %s. Continuing without initial positions.",
                    self.ns3_pos_file,
                )
            else:
                self.logger.info("NS-3 position file found: %s", self.ns3_pos_file)
            return True
        except Exception as e:
            self.logger.error(
                "Failed to start NS-3 simulation process: %s", e, exc_info=True
            )
            self.simulation_running = False
            return False

    def stop_ns3_simulation(self):
        """Stops the background NS-3 simulation process."""
        if self.ns3_process and self.simulation_running:
            # Check if process is still running
            if self.ns3_process.poll() is None:
                try:
                    self.logger.info(
                        "Terminating NS-3 simulation process (PID: %d)...",
                        self.ns3_process.pid,
                    )
                    self.ns3_process.terminate()
                    # Wait a bit for graceful termination
                    stdout, stderr = self.ns3_process.communicate(timeout=5)
                    self.logger.info("NS-3 simulation process terminated.")
                    if stdout:
                        self.logger.debug("NS-3 stdout: %s", stdout)
                    if stderr:
                        self.logger.warning("NS-3 stderr on termination: %s", stderr)

                except subprocess.TimeoutExpired:
                    self.logger.warning(
                        "NS-3 process did not terminate gracefully, killing..."
                    )
                    self.ns3_process.kill()
                    # Ensure kill is effective
                    time.sleep(0.5)
                    if self.ns3_process.poll() is None:
                        self.logger.error(
                            "Failed to kill NS-3 process (PID: %d)",
                            self.ns3_process.pid,
                        )
                    else:
                        self.logger.info("NS-3 simulation process killed.")
                except Exception as e:
                    self.logger.error(
                        "Error stopping NS-3 process: %s", e, exc_info=True
                    )
            else:
                self.logger.info(
                    "NS-3 process (PID: %d) already terminated with code %d.",
                    self.ns3_process.pid,
                    self.ns3_process.poll(),
                )
                # Attempt to read any remaining output
                try:
                    stdout, stderr = self.ns3_process.communicate(timeout=1)
                    if stdout:
                        self.logger.debug("NS-3 remaining stdout: %s", stdout)
                    if stderr:
                        self.logger.warning("NS-3 remaining stderr: %s", stderr)
                except Exception:
                    pass  # Ignore errors here

            self.ns3_process = None
            self.simulation_running = False
        # else:
        #      self.logger.debug("NS-3 simulation process was not running or already stopped.")

    def get_ns3_node_positions(self) -> Optional[Dict[str, Tuple[float, float, float]]]:
        """
        Reads the latest node positions from the NS-3 output file.

        Returns:
            A dictionary mapping node_id (str) to (x, y, z) tuple,
            or None if the file cannot be read or is empty.
        """
        if not self.ns3_pos_file:
            self.logger.warning("NS-3 position file path not set.")
            return None
        if not os.path.exists(self.ns3_pos_file):
            # It's possible NS-3 hasn't created it yet or finished and it was cleaned up
            # Check if the process is still running
            if self.ns3_process and self.ns3_process.poll() is None:
                self.logger.debug(
                    "NS-3 position file not found (%s), but NS-3 process is still running. Waiting for file creation.",
                    self.ns3_pos_file,
                )
            else:
                self.logger.warning(
                    "NS-3 position file not found (%s) and NS-3 process is not running.",
                    self.ns3_pos_file,
                )
            return None

        try:
            # Read the entire file content - might be large for long simulations
            # Consider optimization later if needed (e.g., seek to end, read backwards)
            with open(self.ns3_pos_file, "r") as f:
                content = f.read()

            if not content.strip():
                self.logger.debug("NS-3 position file is empty: %s", self.ns3_pos_file)
                return None

            # Use pandas to read CSV, handling potential errors
            # Read into a string buffer first to handle potential incomplete last lines
            try:
                # Skip initial rows that might be empty or corrupted during startup
                df = pd.read_csv(
                    io.StringIO(content), low_memory=False
                )  # low_memory=False might help with parsing mixed types
            except (pd.errors.ParserError, pd.errors.EmptyDataError) as parse_error:
                self.logger.warning(
                    "Pandas parsing error reading NS-3 pos file (%s): %s. Trying to read without last line.",
                    self.ns3_pos_file,
                    parse_error,
                )
                lines = content.strip().split("\n")
                # Filter out potentially empty lines
                lines = [line for line in lines if line.strip()]
                if len(lines) > 1:  # Need at least header + one data row
                    content_minus_last = "\n".join(lines[:-1])
                    try:
                        df = pd.read_csv(io.StringIO(content_minus_last))
                    except Exception as inner_e:
                        self.logger.error(
                            "Failed to parse NS-3 position file even without last line (%s): %s",
                            self.ns3_pos_file,
                            inner_e,
                        )
                        return None
                else:  # Only header or header + partial line, or corrupted file
                    self.logger.warning(
                        "Not enough valid lines in NS-3 position file to parse: %s",
                        self.ns3_pos_file,
                    )
                    return None

            if df.empty:
                self.logger.debug(
                    "Parsed DataFrame from NS-3 position file is empty: %s",
                    self.ns3_pos_file,
                )
                return None

            # Get the last row (latest time)
            last_row = df.iloc[-1]
            latest_time = last_row["time"]

            positions = {}
            # Column names are like 'time', 'node0', 'x', 'y', 'z', 'node1', 'x.1', 'y.1', 'z.1', etc.
            num_nodes = (len(df.columns) - 1) // 4  # time + 4 cols per node
            for i in range(num_nodes):
                # NS-3 node IDs are 0-indexed
                node_id_in_script = (
                    f"node_{i}"  # Map NS-3 index i to Python node ID format
                )
                node_col_ns3 = f"node{i}"  # Column name in CSV header from NS-3 script
                x_col = "x" if i == 0 else f"x.{i}"
                y_col = "y" if i == 0 else f"y.{i}"
                z_col = "z" if i == 0 else f"z.{i}"

                # Check if columns exist (robustness) and data is valid
                if (
                    node_col_ns3 in last_row
                    and x_col in last_row
                    and y_col in last_row
                    and z_col in last_row
                ):
                    try:
                        # Attempt conversion, handle potential non-numeric data
                        x = float(last_row[x_col])
                        y = float(last_row[y_col])
                        z = float(last_row[z_col])
                        positions[node_id_in_script] = (x, y, z)
                    except (ValueError, TypeError) as convert_error:
                        self.logger.warning(
                            f"Could not convert position data for node {i} at time {latest_time} in {self.ns3_pos_file}. Data: x='{last_row[x_col]}', y='{last_row[y_col]}', z='{last_row[z_col]}'. Error: {convert_error}"
                        )
                else:
                    self.logger.warning(
                        f"Missing position columns for node {i} (expected {node_col_ns3}, {x_col}, {y_col}, {z_col}) in {self.ns3_pos_file} at time {latest_time}."
                    )

            # self.logger.debug("Read positions from NS-3 for time %f: %d nodes", latest_time, len(positions))
            return positions

        except FileNotFoundError:
            # This might be normal if NS-3 finishes before Python script checks last time
            if self.ns3_process and self.ns3_process.poll() is None:
                self.logger.warning(
                    "NS-3 position file disappeared while NS-3 process still running: %s",
                    self.ns3_pos_file,
                )
            return None
        except pd.errors.EmptyDataError:
            self.logger.warning(
                "NS-3 position file exists but pandas read it as empty: %s",
                self.ns3_pos_file,
            )
            return None
        except Exception as e:
            self.logger.error(
                "Unhandled error reading or parsing NS-3 position file (%s): %s",
                self.ns3_pos_file,
                e,
                exc_info=True,
            )
            return None

    # --- Blockchain Integration Methods (Placeholder/Example) ---

    def setup_integrated_simulation(self, config: Dict[str, Any]):
        """
        Set up the integrated simulation environment.
        (Currently a placeholder, assumes NS-3 handles network setup)
        """
        self.logger.info("Setting up integrated simulation environment based on config")
        # Here, you might configure specific NS-3 parameters if needed
        # For now, we assume the NS-3 script handles its own setup based on args
        pass

    def update_blockchain_state(self, blockchain_events: List[Any]):
        """
        Send blockchain events/state changes to NS-3 (if needed).
        (Currently a placeholder, requires NS-3 script modification)
        """
        self.logger.debug(
            "Updating NS-3 with %d blockchain events (Not Implemented)",
            len(blockchain_events),
        )
        # This would require IPC or file-based communication back to NS-3
        pass

    def get_network_events(self) -> List[Any]:
        """
        Get network events from NS-3 (e.g., packet transmissions, link changes).
        (Currently a placeholder, requires NS-3 script modification and output)
        """
        self.logger.debug("Fetching network events from NS-3 (Not Implemented)")
        # This would require NS-3 to log specific events to a file or use IPC
        # For now, return empty list
        return []

    # --- Visualization Methods ---

    def enable_visualization(self, enable: bool = True, filename: str = "netanim.xml"):
        """
        Enable or disable NetAnim visualization generation in NS-3.
        (Note: This requires the NS-3 script to support this dynamically or via args)
        """
        self.logger.info(
            "%s NetAnim visualization (filename: %s)",
            "Enabling" if enable else "Disabling",
            filename,
        )
        # This functionality depends heavily on the specific NS-3 script.
        # The current manet-blockchain-sim.cc creates animation.xml by default.
        # We might need to pass a flag or modify the config passed to NS-3.
        # For now, this method doesn't directly control the running sim's visualization.
        pass

    # --- Helper Methods ---

    def cleanup(self):
        """Clean up any resources used by the adapter, like stopping NS-3."""
        self.logger.info("Cleaning up NS3Adapter resources...")
        self.stop_ns3_simulation()

    def __del__(self):
        # Ensure cleanup happens when the object is garbage collected
        self.cleanup()


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

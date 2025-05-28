#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface for integration between NS-3 and BlockSim.
Provides data exchange and synchronization between simulators.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("IntegrationInterface")


class IntegrationInterface:
    """Class for NS-3 and BlockSim integration"""

    def __init__(self, config_path: Optional[Any] = None):
        """
        Initializes integration interface.

        Args:
            config_path (str, optional): Path to configuration file. Defaults to None.
        """
        self.nodes: Dict[str, Any] = {}  # Dictionary for storing node information
        self.links: Dict[
            str, Any
        ] = {}  # Dictionary for storing link information between nodes
        self.transactions: List[Any] = []  # List of transactions
        self.simulation_time = 0.0  # Current simulation time
        self.config: Dict[str, Any] = {}  # Simulation configuration

        # Load configuration if specified
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
                logger.info(
                    "Configuration loaded from %s", config_path,
                )

    def register_node(
        self,
        node_id: str,
        position: Tuple[float, float, float],
        node_type: str,
        capabilities: Dict[str, Any],
    ) -> bool:
        """
        Registers a new node in the system.

        Args:
            node_id (str): Unique node identifier
            position (Tuple[float, float, float]): Node coordinates (x, y, z)
            node_type (str): Node type (base_station, validator, regular)
            capabilities (Dict[str, Any]): Node capabilities parameters

        Returns:
            bool: True if node successfully registered, False otherwise
        """
        if node_id in self.nodes:
            logger.warning("Node %s already registered", node_id)
            return False

        self.nodes[node_id] = {
            "position": position,
            "type": node_type,
            "capabilities": capabilities,
            "connections": [],
            "active": True,
            "trust_rating": 0.5 if node_type != "base_station" else 1.0,
            "registered_time": self.simulation_time,
        }

        logger.info("Node %s successfully registered", node_id)
        return True

    def update_node_position(
        self, node_id: str, position: Tuple[float, float, float]
    ) -> bool:
        """
        Updates node position.

        Args:
            node_id (str): Node identifier
            position (Tuple[float, float, float]): New coordinates (x, y, z)

        Returns:
            bool: True if position successfully updated, False otherwise
        """
        if node_id not in self.nodes:
            logger.error("Node %s not found", node_id)
            return False

        old_position = self.nodes[node_id]["position"]
        self.nodes[node_id]["position"] = position

        logger.debug(
            "Node %s moved from %s to %s", (node_id, old_position, old_position),
        )
        return True

    def register_connection(
        self, node1_id: str, node2_id: str, quality: float, bandwidth: float
    ) -> bool:
        """
        Registers connection between two nodes.

        Args:
            node1_id (str): First node identifier
            node2_id (str): Second node identifier
            quality (float): Connection quality (0.0-1.0)
            bandwidth (float): Connection bandwidth (Mbps)

        Returns:
            bool: True if connection successfully registered, False otherwise
        """
        if node1_id not in self.nodes or node2_id not in self.nodes:
            logger.error(
                "One or both nodes not found: %s, %s", (node1_id, node2_id),
            )
            return False

        connection_id = f"{min(node1_id, node2_id)}_{max(node1_id, node2_id)}"

        if connection_id in self.links:
            # Update existing connection
            self.links[connection_id]["quality"] = quality
            self.links[connection_id]["bandwidth"] = bandwidth
            logger.debug(
                "Connection %s updated", connection_id
            )
        else:
            # Create new connection
            self.links[connection_id] = {
                "nodes": [node1_id, node2_id],
                "quality": quality,
                "bandwidth": bandwidth,
                "established_time": self.simulation_time,
                "active": True,
            }

            # Update connection lists for both nodes
            self.nodes[node1_id]["connections"].append(node2_id)
            self.nodes[node2_id]["connections"].append(node1_id)

            logger.info(
                "Connection between nodes %s and %s established", node1_id, node2_id
            )

        return True

    def send_transaction(
        self, source_id: str, target_id: str, transaction_data: Dict[str, Any]
    ) -> str:
        """
        Sends transaction from one node to another.

        Args:
            source_id (str): Source node identifier
            target_id (str): Target node identifier
            transaction_data (Dict[str, Any]): Transaction data

        Returns:
            str: Transaction identifier or empty string in case of error
        """
        if source_id not in self.nodes:
            logger.error(
                "Source node %s not found", source_id
            )
            return ""

        if target_id not in self.nodes:
            logger.error(
                "Target node %s not found", target_id
            )
            return ""

        # Check if direct connection or path exists between nodes
        if not self._check_path_exists(source_id, target_id):
            logger.error(
                "No available path between nodes %s and %s", (source_id, target_id),
            )
            return ""

        # Generate unique transaction identifier
        import uuid

        tx_id = f"tx_{uuid.uuid4().hex[:8]}"

        # Create transaction
        transaction = {
            "id": tx_id,
            "source": source_id,
            "target": target_id,
            "data": transaction_data,
            "timestamp": self.simulation_time,
            "status": "pending",
            "path": self._find_shortest_path(source_id, target_id),
        }

        self.transactions.append(transaction)
        logger.info("Transaction %s created and sent", tx_id)

        return tx_id

    def process_pending_transactions(self) -> int:
        """
        Processes pending transactions.

        Returns:
            int: Number of processed transactions
        """
        count = 0
        for tx in self.transactions:
            if tx["status"] == "pending":
                # Simulate transaction passing through network
                # In real integration, this would be linked to BlockSim
                tx["status"] = "processed"
                count += 1

        logger.info("Processed %s transactions", count)
        return count

    def advance_time(self, time_delta: float) -> None:
        """
        Advances simulation time forward.

        Args:
            time_delta (float): Time increment for advancing (in seconds)
        """
        self.simulation_time += time_delta
        logger.debug(
            "Simulation time advanced to %s", self.simulation_time,
        )

    def get_network_state(self) -> Dict[str, Any]:
        """
        Returns current network state.

        Returns:
            Dict[str, Any]: Dictionary with network state
        """
        return {
            "simulation_time": self.simulation_time,
            "nodes": self.nodes,
            "links": self.links,
            "transactions": self.transactions,
        }

    def save_state(self, filepath: str) -> bool:
        """
        Saves current interface state to JSON file.

        Args:
            filepath (str): Path to save state

        Returns:
            bool: True if state successfully saved, False otherwise
        """
        try:
            # Check if directory exists and create if not
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(
                        "Directory created %s", directory
                    )
                except PermissionError:
                    logger.error(
                        f"Permission error: cannot create directory {directory}"
                    )
                    logger.error(
                        "Please check filesystem access permissions"
                    )
                    return False
                except Exception as e:
                    logger.error(
                        "Error creating directory %s: %s", (directory, e),
                    )
                    return False

            # Check write permissions if file already exists
            if os.path.exists(filepath):
                if not os.access(filepath, os.W_OK):
                    logger.error(
                        f"Permission error: no write access to file {filepath}"
                    )
                    logger.error("Please check file access permissions")
                    return False

            # Try to open file and write data
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.get_network_state(), f, indent=2)
            logger.info(
                "Simulation state saved to %s", filepath
            )
            return True
        except PermissionError:
            logger.error(
                "Permission error: cannot write to file %s", filepath,
            )
            logger.error("Please check file and directory access permissions")
            return False
        except Exception as e:
            logger.error("Error saving state: %s", e)
            return False

    def load_state(self, filepath: str) -> bool:
        """
        Loads interface state from JSON file.

        Args:
            filepath (str): Path to state file

        Returns:
            bool: True if state successfully loaded, False otherwise
        """
        try:
            # Check file existence
            if not os.path.exists(filepath):
                logger.error(
                    "State file %s does not exist", filepath
                )
                return False

            # Check read permissions
            if not os.access(filepath, os.R_OK):
                logger.error(
                    f"Permission error: no read access to file {filepath}"
                )
                logger.error("Please check file access permissions")
                return False

            # Try to open file and read data
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)

            # Load state
            self.nodes = state.get("nodes", {})
            self.links = state.get("links", {})
            self.transactions = state.get("transactions", [])
            self.simulation_time = state.get("time", 0.0)

            logger.info(
                "Simulation state loaded from %s", filepath
            )
            return True
        except PermissionError:
            logger.error(
                "Permission error: cannot read file %s", filepath,
            )
            logger.error("Please check file access permissions")
            return False
        except json.JSONDecodeError:
            logger.error(
                "JSON decoding error in file %s", filepath
            )
            return False
        except Exception as e:
            logger.error("Error loading state: %s", e)
            return False

    def _check_path_exists(self, source_id: str, target_id: str) -> bool:
        """
        Checks if path exists between two nodes.

        Args:
            source_id (str): Source node identifier
            target_id (str): Target node identifier

        Returns:
            bool: True if path exists, False otherwise
        """
        # Simple case using breadth-first search
        visited = set()
        queue = [source_id]

        while queue:
            node_id = queue.pop(0)

            if node_id == target_id:
                return True

            if node_id in visited:
                continue

            visited.add(node_id)

            if node_id in self.nodes:
                for connected_node in self.nodes[node_id].get("connections", []):
                    if connected_node not in visited:
                        queue.append(connected_node)

        return False

    def _find_shortest_path(self, source_id: str, target_id: str) -> List[str]:
        """
        Finds shortest path between two nodes.

        Args:
            source_id (str): Source node identifier
            target_id (str): Target node identifier

        Returns:
            List[str]: List of node identifiers forming the path
        """
        # Implement simple breadth-first search algorithm
        visited = set()
        queue = [(source_id, [source_id])]

        while queue:
            node_id, path = queue.pop(0)

            if node_id == target_id:
                return path

            if node_id in visited:
                continue

            visited.add(node_id)

            if node_id in self.nodes:
                for connected_node in self.nodes[node_id].get("connections", []):
                    if connected_node not in visited:
                        new_path = path + [connected_node]
                        queue.append((connected_node, new_path))

        return []  # Path not found


if __name__ == "__main__":
    # Example usage
    interface = IntegrationInterface()

    # Register base station
    interface.register_node(
        "base_station_1",
        (0.0, 0.0, 10.0),
        "base_station",
        {"computational_power": 100, "storage": 1000, "battery": None},
    )

    # Register two mobile nodes
    interface.register_node(
        "node_1",
        (10.0, 10.0, 1.5),
        "regular",
        {"computational_power": 10, "storage": 50, "battery": 0.9},
    )

    interface.register_node(
        "node_2",
        (20.0, 20.0, 1.5),
        "validator",
        {"computational_power": 20, "storage": 100, "battery": 0.8},
    )

    # Establish connections
    interface.register_connection("base_station_1", "node_1", 0.9, 100.0)
    interface.register_connection("node_1", "node_2", 0.7, 50.0)

    # Send transaction
    tx_id = interface.send_transaction(
        "node_1", "node_2", {"type": "data_transfer", "size": 1024, "priority": "high"}
    )

    # Advance time and process transactions
    interface.advance_time(1.0)
    interface.process_pending_transactions()

    # Save state
    interface.save_state(os.path.join(tempfile.gettempdir(), "simulation_state.json"))

    print("Example completed successfully.")

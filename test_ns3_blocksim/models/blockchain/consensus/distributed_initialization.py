import json
import logging
import time
from typing import Dict, List, Optional, Set, Tuple

from ..core.blockchain import Blockchain
from ..network.node import Node


class DistributedInitialization:
    """
    Handles the distributed initialization of the blockchain across all nodes in the network
    without requiring a base station.
    """

    def __init__(self, threshold_percentage: float = 0.67):
        """
        Initialize with a threshold percentage required for consensus
        Default is 2/3 (0.67) of nodes must agree
        """
        self.threshold_percentage = threshold_percentage
        self.logger = logging.getLogger(__name__)

    def initialize_network(self, nodes: Dict[str, Node]) -> Dict[str, Blockchain]:
        """
        Initialize blockchain across all nodes in the network
        Returns a dictionary of node_id -> blockchain
        """
        self.logger.info(
            f"Starting distributed blockchain initialization with {len(nodes)} nodes"
        )

        # Create empty blockchains for each node
        node_blockchains: Dict[str, Blockchain] = {}
        for node_id, node in nodes.items():
            blockchain = Blockchain(node_id)
            node_blockchains[node_id] = blockchain
            node.update_blockchain_status(True, 1)  # Genesis block only

        self.logger.info(
            "Created initial blockchain for %s nodes",
            len(nodes),
        )
        return node_blockchains

    def get_node_neighbors(self, node_id: str, nodes: Dict[str, Node]) -> List[str]:
        """Get all neighbors for a specific node based on coverage radius"""
        if node_id not in nodes:
            return []

        current_node = nodes[node_id]
        neighbors = []

        for other_id, other_node in nodes.items():
            if other_id != node_id and current_node.is_within_range(other_node):
                neighbors.append(other_id)

        return neighbors

    def update_neighbor_connections(self, nodes: Dict[str, Node]) -> None:
        """Update neighbor connections for all nodes based on current positions"""
        for node_id, node in nodes.items():
            neighbors = self.get_node_neighbors(node_id, nodes)
            node.update_neighbors(neighbors)

    def propagate_genesis_blocks(
        self,
        nodes: Dict[str, Node],
        node_blockchains: Dict[str, Blockchain],
        max_rounds: int = 10,
    ) -> Dict[str, Dict[str, int]]:
        """
        Propagate genesis blocks across the network to establish consensus
        Returns a dictionary of node_id -> {genesis_hash -> count}
        """
        # Track genesis blocks seen by each node
        node_genesis_blocks: Dict[str, Dict[str, int]] = {
            node_id: {} for node_id in nodes
        }

        # Initialize with each node's own genesis block
        for node_id, blockchain in node_blockchains.items():
            genesis_hash = blockchain.chain[0].hash
            node_genesis_blocks[node_id][genesis_hash] = 1

        # Propagate for a fixed number of rounds
        for round_num in range(max_rounds):
            self.logger.info(
                "Propagation round %s/%s",
                round_num + 1, max_rounds,
            )

            # Make a copy of the current state to avoid immediate updates
            current_state = {
                node_id: node_genesis_blocks[node_id].copy()
                for node_id in node_genesis_blocks
            }

            # Each node shares its known genesis blocks with neighbors
            for node_id, node in nodes.items():
                for neighbor_id in node.neighbors:
                    if neighbor_id in nodes:
                        # Share all known genesis blocks with the neighbor
                        for genesis_hash, count in current_state[node_id].items():
                            if genesis_hash in node_genesis_blocks[neighbor_id]:
                                node_genesis_blocks[neighbor_id][genesis_hash] += 1
                            else:
                                node_genesis_blocks[neighbor_id][genesis_hash] = 1

            # Check if we have reached convergence
            if self._check_convergence(node_genesis_blocks, nodes):
                self.logger.info(
                    "Convergence reached after %s rounds",
                    round_num + 1,
                )
                break

        return node_genesis_blocks

    def _check_convergence(
        self, node_genesis_blocks: Dict[str, Dict[str, int]], nodes: Dict[str, Node]
    ) -> bool:
        """Check if the network has reached convergence on genesis blocks"""
        # Count the total number of nodes
        total_nodes = len(nodes)

        # For each node, check if it has seen a dominant genesis block
        for node_id, genesis_blocks in node_genesis_blocks.items():
            if not genesis_blocks:  # Skip nodes with no data
                continue

            # Find the most common genesis block
            most_common_hash = max(genesis_blocks, key=genesis_blocks.get)
            most_common_count = genesis_blocks[most_common_hash]

            # Check if it exceeds the threshold
            if most_common_count / total_nodes >= self.threshold_percentage:
                return True

        return False

    def select_winning_genesis(
        self, node_genesis_blocks: Dict[str, Dict[str, int]], nodes: Dict[str, Node]
    ) -> Optional[str]:
        """
        Select the winning genesis block hash based on the majority consensus
        Returns the hash of the winning genesis block or None if no consensus
        """
        # Count total votes for each genesis hash
        total_votes: Dict[str, int] = {}

        for node_id, genesis_blocks in node_genesis_blocks.items():
            for genesis_hash, count in genesis_blocks.items():
                if genesis_hash in total_votes:
                    total_votes[genesis_hash] += count
                else:
                    total_votes[genesis_hash] = count

        # Find the most voted genesis hash
        if not total_votes:
            return None

        winning_hash = max(total_votes, key=total_votes.get)
        winning_votes = total_votes[winning_hash]

        # Check if it meets the threshold
        if winning_votes / len(nodes) >= self.threshold_percentage:
            return winning_hash

        return None

    def synchronize_blockchains(
        self,
        winning_hash: str,
        nodes: Dict[str, Node],
        node_blockchains: Dict[str, Blockchain],
    ) -> None:
        """
        Synchronize all blockchains to use the winning genesis block
        """
        # Find a blockchain with the winning genesis hash
        winning_blockchain = None
        for blockchain in node_blockchains.values():
            if blockchain.chain[0].hash == winning_hash:
                winning_blockchain = blockchain
                break

        if not winning_blockchain:
            self.logger.warning(
                "No blockchain found with winning hash %s",
                winning_hash,
            )
            return

        # Replace genesis blocks for all nodes
        for node_id, blockchain in node_blockchains.items():
            if blockchain.chain[0].hash != winning_hash:
                # Clone the winning blockchain but set node_id to the current node
                blockchain.chain = [block for block in winning_blockchain.chain]
                blockchain.node_id = node_id

        self.logger.info(
            f"Synchronized all blockchains to use genesis block {winning_hash[:8]}..."
        )

    def perform_distributed_initialization(
        self, nodes: Dict[str, Node]
    ) -> Dict[str, Blockchain]:
        """
        Complete distributed blockchain initialization process
        """
        # Step 1: Initialize blockchains for all nodes
        node_blockchains = self.initialize_network(nodes)

        # Step 2: Update neighbor connections
        self.update_neighbor_connections(nodes)

        # Step 3: Propagate genesis blocks to establish consensus
        node_genesis_blocks = self.propagate_genesis_blocks(nodes, node_blockchains)

        # Step 4: Select winning genesis block
        winning_hash = self.select_winning_genesis(node_genesis_blocks, nodes)

        if winning_hash:
            # Step 5: Synchronize all blockchains to use the winning genesis
            self.synchronize_blockchains(winning_hash, nodes, node_blockchains)
            self.logger.info(
                "Distributed blockchain initialization completed successfully"
            )
        else:
            self.logger.error("Failed to reach consensus on genesis block")

        return node_blockchains

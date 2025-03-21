import unittest
import sys
import os
import logging
from typing import Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.blockchain.core.blockchain import Blockchain
from models.blockchain.core.block import Block
from models.blockchain.network.node import Node
from models.blockchain.consensus.distributed_initialization import DistributedInitialization
from models.integration.distributed_blockchain_manager import DistributedBlockchainManager


class TestDistributedInitialization(unittest.TestCase):
    """
    Test cases for distributed blockchain initialization
    """
    
    def setUp(self):
        """Set up test environment"""
        logging.basicConfig(level=logging.INFO)
        
        # Create a set of nodes
        self.nodes: Dict[str, Node] = {}
        
        # Create nodes in a grid pattern for testing
        for i in range(5):
            for j in range(5):
                node_id = f"node_{i}_{j}"
                position = (i * 100, j * 100, 0)  # Grid with 100 unit spacing
                
                # Make some nodes validators
                node_type = "validator" if (i + j) % 5 == 0 else "regular"
                
                node = Node(
                    node_id=node_id,
                    node_type=node_type,
                    position=position,
                    coverage_radius=150.0  # Coverage radius larger than grid spacing
                )
                
                self.nodes[node_id] = node
                
        self.distributed_init = DistributedInitialization()
        
    def test_neighbor_connections(self):
        """Test that neighbor connections are correctly established"""
        self.distributed_init.update_neighbor_connections(self.nodes)
        
        # Check a few sample nodes for correct neighbors
        # Center node should have 8 neighbors (adjacent and diagonal)
        center_node = self.nodes["node_2_2"]
        self.assertEqual(len(center_node.neighbors), 8)
        
        # Corner node should have 3 neighbors
        corner_node = self.nodes["node_0_0"]
        self.assertEqual(len(corner_node.neighbors), 3)
        
        # Edge node should have 5 neighbors
        edge_node = self.nodes["node_0_2"]
        self.assertEqual(len(edge_node.neighbors), 5)
        
    def test_blockchain_initialization(self):
        """Test that blockchains are correctly initialized for all nodes"""
        node_blockchains = self.distributed_init.initialize_network(self.nodes)
        
        # Verify all nodes have a blockchain
        self.assertEqual(len(node_blockchains), len(self.nodes))
        
        # Verify all blockchains have a genesis block
        for node_id, blockchain in node_blockchains.items():
            self.assertEqual(len(blockchain.chain), 1)
            self.assertEqual(blockchain.chain[0].index, 0)
            self.assertEqual(blockchain.chain[0].previous_hash, "0" * 64)
            
    def test_genesis_block_propagation(self):
        """Test that genesis blocks propagate correctly through the network"""
        # Initialize the network
        node_blockchains = self.distributed_init.initialize_network(self.nodes)
        
        # Update neighbor connections
        self.distributed_init.update_neighbor_connections(self.nodes)
        
        # Propagate genesis blocks
        node_genesis_blocks = self.distributed_init.propagate_genesis_blocks(
            self.nodes, node_blockchains, max_rounds=5
        )
        
        # Check that each node has received at least its own genesis block
        for node_id in self.nodes:
            self.assertGreaterEqual(len(node_genesis_blocks[node_id]), 1)
            
        # Most nodes should have received multiple genesis blocks due to proximity
        center_node_id = "node_2_2"
        self.assertGreater(len(node_genesis_blocks[center_node_id]), 1)
        
    def test_consensus_reaching(self):
        """Test that nodes can reach consensus on the genesis block"""
        # Initialize the network
        node_blockchains = self.distributed_init.initialize_network(self.nodes)
        
        # Artificially make all nodes have the same genesis block (first node's)
        first_node_id = list(node_blockchains.keys())[0]
        genesis_block = node_blockchains[first_node_id].chain[0]
        
        for node_id, blockchain in node_blockchains.items():
            blockchain.chain[0] = genesis_block
            
        # Update neighbor connections
        self.distributed_init.update_neighbor_connections(self.nodes)
        
        # Propagate genesis blocks
        node_genesis_blocks = self.distributed_init.propagate_genesis_blocks(
            self.nodes, node_blockchains, max_rounds=5
        )
        
        # Should be able to select a winning genesis
        winning_hash = self.distributed_init.select_winning_genesis(
            node_genesis_blocks, self.nodes
        )
        
        self.assertIsNotNone(winning_hash)
        self.assertEqual(winning_hash, genesis_block.hash)
        
    def test_complete_initialization_process(self):
        """Test the complete distributed initialization process"""
        # Execute complete process
        node_blockchains = self.distributed_init.perform_distributed_initialization(self.nodes)
        
        # All nodes should have a blockchain
        self.assertEqual(len(node_blockchains), len(self.nodes))
        
        # All blockchains should have the same genesis block
        genesis_hashes = set()
        for blockchain in node_blockchains.values():
            genesis_hashes.add(blockchain.chain[0].hash)
            
        self.assertEqual(len(genesis_hashes), 1)
        
    def test_blockchain_manager(self):
        """Test the blockchain manager integration"""
        manager = DistributedBlockchainManager()
        
        # Register the same nodes in the manager
        for node_id, node in self.nodes.items():
            manager.register_node(
                node_id=node_id,
                node_type=node.node_type,
                position=node.position,
                coverage_radius=node.coverage_radius
            )
            
        # Initialize the blockchain network
        success = manager.initialize_blockchain_network()
        self.assertTrue(success)
        
        # Check that all nodes have blockchains
        for node_id in self.nodes:
            info = manager.get_node_blockchain_info(node_id)
            self.assertTrue(info["has_blockchain"])
            self.assertEqual(info["blockchain_height"], 1)
            
        # Check network status
        status = manager.get_network_status()
        self.assertEqual(status["total_nodes"], len(self.nodes))
        self.assertTrue(status["blockchain_consistency"])


if __name__ == "__main__":
    unittest.main() 
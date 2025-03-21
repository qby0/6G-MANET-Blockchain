import json
import logging
import os
import time
from typing import Dict, List, Optional, Any

from ..blockchain.core.blockchain import Blockchain
from ..blockchain.core.block import Block
from ..blockchain.network.node import Node
from ..blockchain.consensus.distributed_initialization import DistributedInitialization


class DistributedBlockchainManager:
    """
    Manager class to handle the integration between NS-3 and the distributed blockchain
    """
    def __init__(self, config_path: str = None):
        self.logger = logging.getLogger(__name__)
        self.nodes: Dict[str, Node] = {}
        self.node_blockchains: Dict[str, Blockchain] = {}
        self.config = self._load_config(config_path)
        self.distributed_init = DistributedInitialization(
            threshold_percentage=self.config.get("consensus_threshold", 0.67)
        )
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "consensus_threshold": 0.67,
            "block_time": 10.0,  # seconds
            "max_propagation_rounds": 10,
            "heartbeat_interval": 5.0  # seconds
        }
        
        if not config_path or not os.path.exists(config_path):
            self.logger.warning("Config file not found, using defaults")
            return default_config
            
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing values
                default_config.update(config)
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return default_config
    
    def register_node(self, node_id: str, node_type: str, position: tuple, 
                     coverage_radius: float) -> str:
        """
        Register a new node in the network
        Returns the node's ID
        """
        if node_id in self.nodes:
            self.logger.warning(f"Node {node_id} already exists, updating properties")
            self.nodes[node_id].node_type = node_type
            self.nodes[node_id].position = position
            self.nodes[node_id].coverage_radius = coverage_radius
            return node_id
            
        # Create new node
        node = Node(
            node_id=node_id,
            node_type=node_type,
            position=position,
            coverage_radius=coverage_radius
        )
        
        self.nodes[node_id] = node
        self.logger.info(f"Registered node {node_id} of type {node_type}")
        
        return node_id
        
    def update_node_position(self, node_id: str, position: tuple) -> bool:
        """Update a node's position"""
        if node_id not in self.nodes:
            self.logger.warning(f"Node {node_id} does not exist")
            return False
            
        self.nodes[node_id].update_position(position)
        return True
        
    def initialize_blockchain_network(self) -> bool:
        """
        Initialize the blockchain network in a distributed way
        """
        if not self.nodes:
            self.logger.error("No nodes available to initialize the blockchain network")
            return False
            
        self.logger.info(f"Initializing distributed blockchain with {len(self.nodes)} nodes")
        
        # Perform distributed initialization
        try:
            self.node_blockchains = self.distributed_init.perform_distributed_initialization(self.nodes)
            
            # Update node blockchain status
            for node_id, blockchain in self.node_blockchains.items():
                if node_id in self.nodes:
                    self.nodes[node_id].update_blockchain_status(
                        has_blockchain=True,
                        height=len(blockchain.chain)
                    )
                    
            self.logger.info("Distributed blockchain initialization completed")
            return True
        except Exception as e:
            self.logger.error(f"Error during blockchain initialization: {e}")
            return False
            
    def update_topology(self) -> None:
        """Update the network topology based on current node positions"""
        self.distributed_init.update_neighbor_connections(self.nodes)
        
    def create_transaction(self, node_id: str, transaction_data: Dict) -> Optional[Dict]:
        """
        Create a new transaction from a node
        Returns the transaction dictionary if successful
        """
        if node_id not in self.nodes or node_id not in self.node_blockchains:
            self.logger.warning(f"Node {node_id} not found or has no blockchain")
            return None
            
        # Create signed transaction
        timestamp = time.time()
        transaction = {
            "sender": node_id,
            "timestamp": timestamp,
            "data": transaction_data
        }
        
        # Sign the transaction
        signature = self.nodes[node_id].sign_message(transaction)
        transaction["signature"] = signature
        
        # Add to pending transactions
        blockchain = self.node_blockchains[node_id]
        blockchain.add_transaction(transaction)
        
        return transaction
        
    def propagate_transaction(self, transaction: Dict) -> List[str]:
        """
        Propagate a transaction to neighboring nodes
        Returns list of nodes that received the transaction
        """
        if "sender" not in transaction or transaction["sender"] not in self.nodes:
            self.logger.warning("Invalid transaction sender")
            return []
            
        sender_id = transaction["sender"]
        sender_node = self.nodes[sender_id]
        received_nodes = []
        
        # Propagate to neighbors
        for neighbor_id in sender_node.neighbors:
            if neighbor_id in self.node_blockchains:
                self.node_blockchains[neighbor_id].add_transaction(transaction)
                received_nodes.append(neighbor_id)
                
        return received_nodes
        
    def create_block(self, node_id: str) -> Optional[Block]:
        """
        Create a new block from pending transactions for a node
        """
        if node_id not in self.node_blockchains:
            self.logger.warning(f"Node {node_id} has no blockchain")
            return None
            
        blockchain = self.node_blockchains[node_id]
        new_block = blockchain.create_block_from_transactions()
        
        if new_block:
            # Update node's blockchain height
            self.nodes[node_id].update_blockchain_status(
                has_blockchain=True,
                height=len(blockchain.chain)
            )
            
        return new_block
        
    def propagate_block(self, node_id: str, block: Block) -> List[str]:
        """
        Propagate a block to neighboring nodes
        Returns list of nodes that received the block
        """
        if node_id not in self.nodes:
            return []
            
        sender_node = self.nodes[node_id]
        received_nodes = []
        
        # Propagate to neighbors
        for neighbor_id in sender_node.neighbors:
            if neighbor_id in self.node_blockchains:
                neighbor_blockchain = self.node_blockchains[neighbor_id]
                
                # Check if the block is valid and can be added
                last_block = neighbor_blockchain.last_block
                if block.previous_hash == last_block.hash and block.index == last_block.index + 1:
                    # Add the block
                    neighbor_blockchain.chain.append(block)
                    
                    # Update node's blockchain height
                    self.nodes[neighbor_id].update_blockchain_status(
                        has_blockchain=True,
                        height=len(neighbor_blockchain.chain)
                    )
                    
                    received_nodes.append(neighbor_id)
                    
        return received_nodes
        
    def get_node_blockchain_info(self, node_id: str) -> Dict:
        """Get blockchain information for a specific node"""
        if node_id not in self.nodes:
            return {"error": f"Node {node_id} not found"}
            
        if node_id not in self.node_blockchains:
            return {
                "node_id": node_id,
                "has_blockchain": False,
                "blockchain_height": 0,
                "pending_transactions": 0
            }
            
        blockchain = self.node_blockchains[node_id]
        return {
            "node_id": node_id,
            "has_blockchain": True,
            "blockchain_height": len(blockchain.chain),
            "pending_transactions": len(blockchain.pending_transactions),
            "genesis_hash": blockchain.chain[0].hash if blockchain.chain else None,
            "latest_hash": blockchain.last_block.hash if blockchain.chain else None
        }
        
    def get_network_status(self) -> Dict:
        """Get overall network status"""
        # Count nodes by type
        node_types = {}
        for node in self.nodes.values():
            if node.node_type in node_types:
                node_types[node.node_type] += 1
            else:
                node_types[node.node_type] = 1
                
        # Get blockchain statistics
        blockchain_heights = [len(bc.chain) for bc in self.node_blockchains.values()]
        max_height = max(blockchain_heights) if blockchain_heights else 0
        min_height = min(blockchain_heights) if blockchain_heights else 0
        avg_height = sum(blockchain_heights) / len(blockchain_heights) if blockchain_heights else 0
        
        # Check blockchain consistency
        genesis_hashes = set()
        for bc in self.node_blockchains.values():
            if bc.chain:
                genesis_hashes.add(bc.chain[0].hash)
                
        is_consistent = len(genesis_hashes) <= 1
        
        return {
            "total_nodes": len(self.nodes),
            "node_types": node_types,
            "blockchains": len(self.node_blockchains),
            "max_blockchain_height": max_height,
            "min_blockchain_height": min_height,
            "avg_blockchain_height": avg_height,
            "blockchain_consistency": is_consistent,
            "timestamp": time.time()
        }
        
    def save_state(self, state_dir: str) -> bool:
        """Save the current state of the network"""
        os.makedirs(state_dir, exist_ok=True)
        
        try:
            # Save nodes
            nodes_data = {node_id: node.to_dict() for node_id, node in self.nodes.items()}
            with open(os.path.join(state_dir, "nodes.json"), 'w') as f:
                json.dump(nodes_data, f, indent=4)
                
            # Save blockchains
            for node_id, blockchain in self.node_blockchains.items():
                blockchain_path = os.path.join(state_dir, f"blockchain_{node_id}.json")
                blockchain.save_to_file(blockchain_path)
                
            self.logger.info(f"Network state saved to {state_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
            return False
            
    def load_state(self, state_dir: str) -> bool:
        """Load the network state from saved files"""
        if not os.path.exists(state_dir):
            self.logger.error(f"State directory {state_dir} does not exist")
            return False
            
        try:
            # Load nodes
            nodes_path = os.path.join(state_dir, "nodes.json")
            if os.path.exists(nodes_path):
                with open(nodes_path, 'r') as f:
                    nodes_data = json.load(f)
                    
                self.nodes = {
                    node_id: Node.from_dict(node_data) 
                    for node_id, node_data in nodes_data.items()
                }
                
            # Load blockchains
            self.node_blockchains = {}
            for node_id in self.nodes:
                blockchain_path = os.path.join(state_dir, f"blockchain_{node_id}.json")
                if os.path.exists(blockchain_path):
                    blockchain = Blockchain.load_from_file(blockchain_path)
                    if blockchain:
                        self.node_blockchains[node_id] = blockchain
                        
            self.logger.info(f"Network state loaded from {state_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")
            return False 
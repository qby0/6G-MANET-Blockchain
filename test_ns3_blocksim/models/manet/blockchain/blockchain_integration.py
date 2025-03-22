#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Blockchain Integration Module for 6G MANET Simulations
Connects the 6G mobility model with blockchain simulation components,
enabling distributed consensus in mobile networks.
"""

import logging
import time
import json
import os
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

from models.manet.mobility.sixg_mobility_model import SixGMobilityModel

logger = logging.getLogger(__name__)

class BlockchainMobilityIntegration:
    """
    Integration layer between blockchain and mobility models.
    Connects node movements with blockchain validation and consensus.
    """
    
    def __init__(self, mobility_model: SixGMobilityModel, config: Dict[str, Any] = None):
        """
        Initialize blockchain-mobility integration with configuration.
        
        Args:
            mobility_model: The 6G mobility model to use
            config: Integration configuration
        """
        self.logger = logging.getLogger("BlockchainMobilityIntegration")
        self.mobility_model = mobility_model
        
        # Default blockchain configuration
        default_config = {
            "consensus_threshold": 0.67,
            "block_time": 1.0,          # Block creation interval (seconds)
            "transaction_rate": 0.2,     # Transactions per node per second
            "max_propagation_rounds": 5, # Rounds to propagate a block
            "validator_percentage": 0.2, # Percentage of nodes as validators
            "connectivity_range": 200,   # Communication range between nodes (meters)
            "bandwidth": 10,             # Mbps between nodes when in range
            "latency_per_meter": 0.001,  # Additional latency per meter (ms)
            "packet_loss": 0.05,         # Probability of packet loss
            "data_dir": "blockchain_data" # Directory to store blockchain data
        }
        
        # Merge provided config with defaults
        self.config = default_config.copy()
        if config:
            self.config.update(config)
            
        # Load or initialize blockchain
        self._initialize_blockchain()
        
        # Select validator nodes based on percentage
        self._select_validators()
        
        # Track transactions and blocks
        self.pending_transactions = []
        self.blocks = []
        self.network_state = {}
        self.simulation_time = 0.0
        
        # Track network connectivity based on node positions
        self.connectivity_matrix = np.zeros(
            (self.mobility_model.config["node_count"], 
             self.mobility_model.config["node_count"]),
            dtype=bool
        )
        
        # Create data directory
        os.makedirs(self.config["data_dir"], exist_ok=True)
        
        self.logger.info(
            "Blockchain-Mobility integration initialized with %d nodes (%d validators)",
            self.mobility_model.config["node_count"],
            len(self.validators)
        )
    
    def _initialize_blockchain(self):
        """Initialize blockchain for the simulation"""
        try:
            # Попытка использовать существующую модель блокчейна
            from models.blockchain_model_example import SimpleBlockchain
            self.blockchain = SimpleBlockchain(
                consensus_threshold=self.config["consensus_threshold"],
                block_time=self.config["block_time"]
            )
            self.logger.info("Initialized SimpleBlockchain model")
        except ImportError:
            # Если не найдена существующая модель, создаем простую симуляцию
            self.logger.warning("SimpleBlockchain model not found, using simplified simulation")
            class SimplifiedBlockchain:
                def __init__(self, config):
                    self.blocks = []
                    self.transactions = []
                    self.config = config
                    
                def add_transaction(self, tx):
                    self.transactions.append(tx)
                    return True
                    
                def create_block(self, proposer):
                    if not self.transactions:
                        return None
                    
                    # Используем до 10 транзакций или все доступные, если их меньше
                    tx_count = min(10, len(self.transactions))
                    transactions = self.transactions[:tx_count]
                    self.transactions = self.transactions[tx_count:]
                    
                    block = {
                        "index": len(self.blocks) + 1,
                        "timestamp": time.time(),
                        "transactions": transactions,
                        "proposer": proposer,
                        "validators": [],
                        "hash": f"block_{len(self.blocks) + 1}_{int(time.time())}"
                    }
                    
                    self.blocks.append(block)
                    return block
                    
                def validate_block(self, block, validator):
                    if validator not in block["validators"]:
                        block["validators"].append(validator)
                    
                    # Проверяем, достигнут ли консенсус
                    if len(block["validators"]) >= self.config["consensus_threshold"]:
                        block["confirmed"] = True
                        block["confirmation_time"] = time.time()
                        return True
                    return False
                
            self.blockchain = SimplifiedBlockchain(self.config)
    
    def _select_validators(self):
        """Select validator nodes based on configuration"""
        node_count = self.mobility_model.config["node_count"]
        validator_count = int(node_count * self.config["validator_percentage"])
        
        # Ensure at least one validator
        validator_count = max(1, validator_count)
        
        # Randomly select validators
        self.validators = set(np.random.choice(
            node_count, 
            size=validator_count, 
            replace=False
        ).tolist())
        
        self.logger.info("Selected %d nodes as blockchain validators", len(self.validators))
    
    def update_connectivity(self):
        """Update node connectivity matrix based on positions and range"""
        positions = self.mobility_model.get_positions()
        node_count = len(positions)
        
        # Reset connectivity matrix
        self.connectivity_matrix = np.zeros((node_count, node_count), dtype=bool)
        
        # Update connectivity based on distance
        for i in range(node_count):
            for j in range(i+1, node_count):  # Only compute upper triangle
                # Calculate Euclidean distance between nodes
                distance = np.linalg.norm(positions[i] - positions[j])
                
                # Check if nodes are within communication range
                if distance <= self.config["connectivity_range"]:
                    # Nodes are connected
                    self.connectivity_matrix[i, j] = True
                    self.connectivity_matrix[j, i] = True  # Symmetric
        
        # Diagonal is always True (node connected to itself)
        np.fill_diagonal(self.connectivity_matrix, True)
        
        # Count connections
        connections = np.sum(self.connectivity_matrix) - node_count  # Subtract self-connections
        avg_connections = connections / node_count
        
        return avg_connections
    
    def generate_transactions(self, time_delta: float):
        """Generate random transactions based on transaction rate"""
        node_count = self.mobility_model.config["node_count"]
        tx_count = int(node_count * self.config["transaction_rate"] * time_delta)
        
        if tx_count <= 0:
            return []
            
        transactions = []
        for _ in range(tx_count):
            # Random sender and recipient
            sender = np.random.randint(0, node_count)
            recipient = np.random.randint(0, node_count)
            while recipient == sender:
                recipient = np.random.randint(0, node_count)
                
            # Create transaction
            tx = {
                "sender": sender,
                "recipient": recipient,
                "timestamp": self.simulation_time,
                "amount": np.random.uniform(0.1, 10.0),
                "id": f"tx_{int(time.time()*1000)}_{sender}_{recipient}"
            }
            
            transactions.append(tx)
            # Add to blockchain
            self.blockchain.add_transaction(tx)
            
        return transactions
    
    def process_blocks(self):
        """Process block creation and validation"""
        # Only validators can propose blocks
        for validator in self.validators:
            # Check if it's time to create a new block
            if np.random.random() < 0.1:  # 10% chance per validator per update
                block = self.blockchain.create_block(validator)
                if block:
                    self.logger.debug("Validator %d created new block %d", validator, block["index"])
                    
                    # Add to local blocks list for tracking
                    self.blocks.append(block)
                    
                    # Simulate block propagation
                    self._propagate_block(block, validator)
    
    def _propagate_block(self, block, source_node):
        """Simulate block propagation through the network"""
        # Nodes that have received the block
        received_nodes = {source_node}
        
        # Simulate multiple rounds of propagation
        for _ in range(self.config["max_propagation_rounds"]):
            new_receivers = set()
            
            # For each node that has the block
            for node in received_nodes:
                # Find connected nodes
                connected_nodes = np.where(self.connectivity_matrix[node])[0]
                
                # Propagate to connected nodes
                for connected_node in connected_nodes:
                    if connected_node not in received_nodes:
                        # Calculate probability of successful transmission
                        # Higher packet loss for longer distances
                        positions = self.mobility_model.get_positions()
                        distance = np.linalg.norm(positions[node] - positions[connected_node])
                        packet_loss_prob = self.config["packet_loss"] * (distance / self.config["connectivity_range"])
                        packet_loss_prob = min(0.9, packet_loss_prob)  # Cap at 90%
                        
                        # Check if transmission is successful
                        if np.random.random() > packet_loss_prob:
                            new_receivers.add(connected_node)
                            
                            # If receiver is a validator, they validate the block
                            if connected_node in self.validators:
                                self.blockchain.validate_block(block, connected_node)
            
            # Add new receivers to the set of nodes that have the block
            received_nodes.update(new_receivers)
            
            # If all nodes have received the block, stop propagation
            if len(received_nodes) == self.mobility_model.config["node_count"]:
                break
    
    def update(self, time_delta: float = 0.1):
        """
        Update blockchain and mobility models in sync.
        
        Args:
            time_delta: Simulation time step in seconds
        
        Returns:
            Dict containing simulation state
        """
        # Update simulation time
        self.simulation_time += time_delta
        
        # Update node positions
        self.mobility_model.update_positions(time_delta)
        
        # Update connectivity
        avg_connections = self.update_connectivity()
        
        # Generate transactions
        transactions = self.generate_transactions(time_delta)
        
        # Process blocks
        self.process_blocks()
        
        # Update network state
        self.network_state = {
            "time": self.simulation_time,
            "node_count": self.mobility_model.config["node_count"],
            "validator_count": len(self.validators),
            "avg_connections": avg_connections,
            "transactions_generated": len(transactions),
            "total_transactions": len(self.blockchain.transactions),
            "block_count": len(self.blocks),
            "connectivity": self.connectivity_matrix.sum() / 
                        (self.mobility_model.config["node_count"] ** 2)
        }
        
        return self.network_state
    
    def save_state(self, filename: Optional[str] = None):
        """Save current blockchain state to file"""
        if not filename:
            filename = f"blockchain_state_{int(self.simulation_time)}.json"
            
        filepath = os.path.join(self.config["data_dir"], filename)
        
        state = {
            "time": self.simulation_time,
            "blocks": self.blocks,
            "validator_nodes": list(self.validators),
            "network_state": self.network_state,
            "config": self.config
        }
        
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)
            
        self.logger.info("Saved blockchain state to %s", filepath)
        return filepath
    
    def get_state_for_visualization(self):
        """Get state data formatted for visualization"""
        positions = self.mobility_model.get_positions()
        node_data = []
        
        # Prepare node data for visualization
        for i in range(self.mobility_model.config["node_count"]):
            node = {
                "id": i,
                "position": positions[i].tolist(),
                "is_validator": i in self.validators,
                "connections": np.where(self.connectivity_matrix[i])[0].tolist(),
                "connection_count": np.sum(self.connectivity_matrix[i])
            }
            node_data.append(node)
            
        return {
            "time": self.simulation_time,
            "nodes": node_data,
            "blocks": self.blocks,
            "network_state": self.network_state
        }
        
    def __str__(self):
        """String representation"""
        return (f"BlockchainMobilityIntegration(nodes={self.mobility_model.config['node_count']}, "
                f"validators={len(self.validators)}, blocks={len(self.blocks)})")


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create mobility model
    from models.manet.mobility.sixg_mobility_model import SixGMobilityModel
    model = SixGMobilityModel()
    
    # Create blockchain integration
    integration = BlockchainMobilityIntegration(model)
    
    # Run simulation
    for step in range(100):
        state = integration.update(0.1)
        if step % 10 == 0:
            logger.info(f"Step {step}: {state}")
    
    # Save final state
    integration.save_state("final_state.json") 
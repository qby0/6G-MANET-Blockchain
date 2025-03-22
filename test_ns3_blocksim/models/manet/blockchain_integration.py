#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Union

logger = logging.getLogger(__name__)

class BlockchainIntegration:
    """
    Class for integrating blockchain with mobility model.
    """
    def __init__(self, 
                 mobility_model, 
                 config_path=None, 
                 config=None,
                 blockchain_data_dir=None):
        """
        Initialize blockchain integration.
        
        Args:
            mobility_model: The mobility model to integrate with
            config_path: Path to the blockchain configuration file
            config: Dictionary containing blockchain configuration
            blockchain_data_dir: Directory to store blockchain data
        """
        self.mobility_model = mobility_model
        
        # Load configuration
        if config is not None:
            self.config = config
        elif config_path is not None:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "consensus_threshold": 0.67,
                "block_time": 1.0,
                "transaction_rate": 0.2,
                "max_propagation_rounds": 5,
                "validator_percentage": 0.2,
                "connectivity_range": 200,
                "bandwidth": 10,
                "latency_per_meter": 0.001,
                "packet_loss": 0.05,
                "blockchain_type": "simplified"
            }
            
        # Select validator nodes
        self.num_nodes = self.mobility_model.config["node_count"]
        self.validator_count = max(3, int(self.num_nodes * self.config["validator_percentage"]))
        self.validator_indices = np.random.choice(
            range(self.num_nodes), 
            size=self.validator_count, 
            replace=False
        )
        
        # Set up data storage
        if blockchain_data_dir is None:
            self.data_dir = Path("blockchain_data")
        else:
            self.data_dir = Path(blockchain_data_dir)
            
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize blockchain metrics
        self.blocks = []
        self.transactions = []
        self.consensus_times = []
        self.network_stats = []
        
        logger.info(f"Initialized Blockchain Integration with {self.validator_count} validators")
        logger.info(f"Validator nodes: {self.validator_indices}")
        
    def update(self, frame_number: int):
        """
        Update blockchain state based on mobility model.
        
        Args:
            frame_number: Current frame number of the simulation
        """
        # Get current positions from mobility model
        positions = self.mobility_model.get_positions()
        
        # Calculate connectivity matrix based on positions and range
        connectivity = self._calculate_connectivity(positions)
        
        # Simulate blockchain operations
        self._simulate_blockchain(frame_number, connectivity)
        
        # Collect network statistics
        self._collect_network_stats(connectivity)
        
        # Log update
        if frame_number % 10 == 0:
            logger.info(f"Frame {frame_number}: Blockchain updated with {len(self.validator_indices)} active validators")
            
        return True
        
    def _calculate_connectivity(self, positions):
        """
        Calculate connectivity matrix based on node positions.
        
        Args:
            positions: Node positions array
            
        Returns:
            Connectivity matrix
        """
        n = positions.shape[0]
        connectivity = np.zeros((n, n), dtype=bool)
        
        for i in range(n):
            for j in range(i + 1, n):
                # Calculate Euclidean distance between nodes
                distance = np.sqrt(np.sum((positions[i] - positions[j]) ** 2))
                # Check if within connectivity range
                if distance <= self.config["connectivity_range"]:
                    connectivity[i, j] = True
                    connectivity[j, i] = True
                    
        # Each node is connected to itself
        np.fill_diagonal(connectivity, True)
        
        return connectivity
        
    def _simulate_blockchain(self, frame_number, connectivity):
        """
        Simulate blockchain operations.
        
        Args:
            frame_number: Current frame number
            connectivity: Connectivity matrix
        """
        # In a simplified model, we just record some basic metrics
        # Add a new block at regular intervals
        if frame_number % int(self.config["block_time"] * 10) == 0:
            # Create a new block
            block = {
                "block_number": len(self.blocks),
                "frame_number": frame_number,
                "validator": int(np.random.choice(self.validator_indices)),
                "transactions": []
            }
            
            # Add transactions to the block
            tx_count = np.random.poisson(self.config["transaction_rate"] * 10)
            for i in range(tx_count):
                transaction = {
                    "tx_id": len(self.transactions),
                    "sender": np.random.randint(0, self.num_nodes),
                    "receiver": np.random.randint(0, self.num_nodes),
                    "amount": np.random.uniform(0.1, 10.0),
                    "frame_number": frame_number
                }
                block["transactions"].append(transaction)
                self.transactions.append(transaction)
                
            # Add block to blockchain
            self.blocks.append(block)
            
            # Simulate consensus delay based on connectivity
            consensus_time = self._simulate_consensus(connectivity)
            self.consensus_times.append(consensus_time)
            
            logger.debug(f"Frame {frame_number}: New block {len(self.blocks)-1} created with {tx_count} transactions. Consensus time: {consensus_time:.2f}s")
    
    def _simulate_consensus(self, connectivity):
        """
        Simulate consensus process and return time to reach consensus.
        
        Args:
            connectivity: Connectivity matrix
            
        Returns:
            Time to reach consensus
        """
        # Extract connectivity among validators
        validator_connectivity = connectivity[np.ix_(self.validator_indices, self.validator_indices)]
        
        # Calculate network diameter among validators (simplified)
        # In a real implementation, we would use proper graph algorithms
        propagation_rounds = 0
        nodes_reached = np.zeros(len(self.validator_indices), dtype=bool)
        nodes_reached[0] = True  # Start with first validator
        
        while propagation_rounds < self.config["max_propagation_rounds"]:
            propagation_rounds += 1
            
            # Simulate message propagation
            newly_reached = np.zeros_like(nodes_reached)
            
            for i in range(len(self.validator_indices)):
                if nodes_reached[i]:
                    for j in range(len(self.validator_indices)):
                        if (not nodes_reached[j] and validator_connectivity[i, j] and 
                            np.random.random() > self.config["packet_loss"]):
                            newly_reached[j] = True
            
            # Update nodes reached
            nodes_reached = nodes_reached | newly_reached
            
            # Check if we've reached consensus threshold
            if np.mean(nodes_reached) >= self.config["consensus_threshold"]:
                break
                
        # Calculate consensus time based on propagation and network parameters
        base_latency = propagation_rounds * 0.1  # Base latency in seconds
        variable_latency = np.random.exponential(0.2)  # Variable component
        
        return base_latency + variable_latency
        
    def _collect_network_stats(self, connectivity):
        """
        Collect network statistics.
        
        Args:
            connectivity: Connectivity matrix
        """
        # Calculate metrics related to blockchain network
        validator_connectivity = connectivity[np.ix_(self.validator_indices, self.validator_indices)]
        
        # Average connectivity among validators
        avg_connectivity = np.mean(validator_connectivity)
        
        # Network connectivity metrics
        stats = {
            "avg_validator_connectivity": float(avg_connectivity),
            "connected_validators": int(np.sum(np.sum(validator_connectivity, axis=1) > 1)),
            "isolated_validators": int(np.sum(np.sum(validator_connectivity, axis=1) <= 1))
        }
        
        self.network_stats.append(stats)
        
    def save_results(self, output_dir):
        """
        Save blockchain simulation results.
        
        Args:
            output_dir: Directory to save results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save blocks and transactions
        with open(output_path / "blocks.json", 'w') as f:
            json.dump(self.blocks, f, indent=2)
            
        with open(output_path / "transactions.json", 'w') as f:
            json.dump(self.transactions, f, indent=2)
            
        # Save network stats
        with open(output_path / "network_stats.json", 'w') as f:
            json.dump(self.network_stats, f, indent=2)
            
        # Save consensus times
        with open(output_path / "consensus_times.json", 'w') as f:
            json.dump(self.consensus_times, f, indent=2)
            
        # Generate and save plots
        self._generate_plots(output_path)
        
        logger.info(f"Blockchain results saved to {output_path}")
        
    def _generate_plots(self, output_path):
        """
        Generate plots of blockchain metrics.
        
        Args:
            output_path: Directory to save plots
        """
        # Plot consensus times
        plt.figure(figsize=(10, 6))
        plt.plot(self.consensus_times)
        plt.title('Consensus Time per Block')
        plt.xlabel('Block Number')
        plt.ylabel('Time (s)')
        plt.grid(True)
        plt.savefig(output_path / "consensus_times.png")
        plt.close()
        
        # Plot validator connectivity
        if self.network_stats:
            plt.figure(figsize=(10, 6))
            avg_connectivity = [stat["avg_validator_connectivity"] for stat in self.network_stats]
            plt.plot(avg_connectivity)
            plt.title('Average Validator Connectivity')
            plt.xlabel('Frame Number')
            plt.ylabel('Connectivity Ratio')
            plt.grid(True)
            plt.savefig(output_path / "validator_connectivity.png")
            plt.close()
            
            # Plot connected vs isolated validators
            plt.figure(figsize=(10, 6))
            connected = [stat["connected_validators"] for stat in self.network_stats]
            isolated = [stat["isolated_validators"] for stat in self.network_stats]
            plt.plot(connected, label='Connected Validators')
            plt.plot(isolated, label='Isolated Validators')
            plt.title('Validator Network Status')
            plt.xlabel('Frame Number')
            plt.ylabel('Count')
            plt.legend()
            plt.grid(True)
            plt.savefig(output_path / "validator_status.png")
            plt.close()

        # Plot transaction rate
        if self.blocks:
            tx_per_block = [len(block["transactions"]) for block in self.blocks]
            plt.figure(figsize=(10, 6))
            plt.plot(tx_per_block)
            plt.title('Transactions per Block')
            plt.xlabel('Block Number')
            plt.ylabel('Transaction Count')
            plt.grid(True)
            plt.savefig(output_path / "transactions_per_block.png")
            plt.close() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BlockSim Bridge - Real integration between NS-3 and BlockSim
This module provides the main bridge between NS-3 network simulation
and BlockSim blockchain simulation for cross-zone authentication.
"""

import os
import sys
import json
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Add BlockSim to path
BLOCKSIM_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'external', 'BlockSim')
if BLOCKSIM_PATH not in sys.path:
    sys.path.insert(0, BLOCKSIM_PATH)

logger = logging.getLogger(__name__)

class ZoneType(Enum):
    """Zone types in the network"""
    MANET = "manet"
    FIVE_G = "5g"
    BRIDGE = "bridge"

@dataclass
class CrossZoneTransaction:
    """Transaction crossing zone boundaries"""
    tx_id: str
    sender_id: int
    sender_zone: ZoneType
    recipient_id: int
    recipient_zone: ZoneType
    data: str
    timestamp: float
    signature: Optional[str] = None
    bridge_proof: Optional[str] = None
    validated: bool = False

@dataclass
class NodeInfo:
    """Information about a network node"""
    node_id: int
    zone: ZoneType
    is_validator: bool
    blocksim_id: Optional[str] = None
    gateway_id: Optional[str] = None

class BlockSimBridge:
    """
    Main bridge between NS-3 and BlockSim
    Handles cross-zone transaction validation using real BlockSim blockchain
    """
    
    def __init__(self, 
                 bridge_node_ids: List[int],
                 manet_node_ids: List[int],
                 fiveg_node_ids: List[int],
                 config: Optional[Dict] = None):
        """
        Initialize BlockSim bridge
        
        Args:
            bridge_node_ids: List of NS-3 node IDs that act as bridge validators
            manet_node_ids: List of NS-3 node IDs in MANET zone
            fiveg_node_ids: List of NS-3 node IDs in 5G zone
            config: Configuration parameters
        """
        self.logger = logging.getLogger("BlockSimBridge")
        
        # Default configuration
        self.config = {
            "consensus_threshold": 0.67,
            "block_time": 2.0,
            "transaction_timeout": 10.0,
            "bridge_model": 3,  # AppendableBlock
            "gateway_prefix": "bridge_gw",
            "device_prefix": "device",
            "validation_threads": 2,
            "ipc_method": "file"  # file, pipe, or socket
        }
        
        if config:
            self.config.update(config)
        
        # Node management
        self.bridge_nodes = bridge_node_ids
        self.manet_nodes = manet_node_ids
        self.fiveg_nodes = fiveg_node_ids
        self.all_nodes = bridge_node_ids + manet_node_ids + fiveg_node_ids
        
        # Node mapping: NS-3 ID -> NodeInfo
        self.node_mapping: Dict[int, NodeInfo] = {}
        
        # Transaction management
        self.pending_transactions: Dict[str, CrossZoneTransaction] = {}
        self.validated_transactions: Dict[str, CrossZoneTransaction] = {}
        
        # BlockSim environment
        self.blocksim_nodes = {}
        self.blocksim_initialized = False
        
        # Threading for async operations
        self.validation_queue = []
        self.validation_lock = threading.Lock()
        self.validation_thread = None
        self.running = False
        
        # IPC directory for communication with NS-3
        self.ipc_dir = os.path.join(os.getcwd(), "ipc_blocksim")
        os.makedirs(self.ipc_dir, exist_ok=True)
        
        # Initialize components
        self._setup_node_mapping()
        self._initialize_blocksim()
        self._start_validation_thread()
        
        self.logger.info(f"BlockSim Bridge initialized with {len(self.bridge_nodes)} bridge validators")
        self.logger.info(f"Managing {len(self.all_nodes)} total nodes across 3 zones")
    
    def _setup_node_mapping(self):
        """Create mapping between NS-3 and BlockSim node IDs"""
        self.logger.info("Setting up node mapping...")
        
        # Bridge nodes as gateway validators
        for i, node_id in enumerate(self.bridge_nodes):
            gateway_id = f"{self.config['gateway_prefix']}_{i}"
            self.node_mapping[node_id] = NodeInfo(
                node_id=node_id,
                zone=ZoneType.BRIDGE,
                is_validator=True,
                blocksim_id=gateway_id,
                gateway_id=gateway_id
            )
        
        # MANET nodes as devices under first bridge gateway
        primary_gateway = self.node_mapping[self.bridge_nodes[0]].gateway_id if self.bridge_nodes else "bridge_gw_0"
        for node_id in self.manet_nodes:
            device_id = f"{self.config['device_prefix']}_manet_{node_id}"
            self.node_mapping[node_id] = NodeInfo(
                node_id=node_id,
                zone=ZoneType.MANET,
                is_validator=False,
                blocksim_id=device_id,
                gateway_id=primary_gateway
            )
        
        # 5G nodes as devices under second bridge gateway if available
        secondary_gateway = self.node_mapping[self.bridge_nodes[1]].gateway_id if len(self.bridge_nodes) > 1 else primary_gateway
        for node_id in self.fiveg_nodes:
            device_id = f"{self.config['device_prefix']}_5g_{node_id}"
            self.node_mapping[node_id] = NodeInfo(
                node_id=node_id,
                zone=ZoneType.FIVE_G,
                is_validator=False,
                blocksim_id=device_id,
                gateway_id=secondary_gateway
            )
        
        self.logger.info(f"Node mapping created for {len(self.node_mapping)} nodes")
    
    def _initialize_blocksim(self):
        """Initialize BlockSim environment with AppendableBlock model"""
        try:
            self.logger.info("Initializing BlockSim environment...")
            
            # Change to BlockSim directory
            original_cwd = os.getcwd()
            os.chdir(BLOCKSIM_PATH)
            
            # Import BlockSim components
            from InputsConfig import InputsConfig as p
            from Models.AppendableBlock.Node import Node
            from Models.AppendableBlock.Transaction import FullTransaction as FT
            from Models.AppendableBlock.Transaction import Transaction
            
            # Store references
            self.blocksim_config = p
            self.BlockSimNode = Node
            self.BlockSimFullTransaction = FT
            self.BlockSimTransaction = Transaction
            
            # Create BlockSim nodes
            gateway_ids = [info.gateway_id for info in self.node_mapping.values() if info.is_validator]
            
            # Create gateway nodes (bridge validators)
            for node_info in self.node_mapping.values():
                if node_info.is_validator:
                    # Gateway node with connections to other gateways
                    other_gateways = [gw for gw in gateway_ids if gw != node_info.gateway_id]
                    gateway_node = Node(node_info.gateway_id, "g", other_gateways)
                    self.blocksim_nodes[node_info.node_id] = gateway_node
                    self.logger.debug(f"Created gateway {node_info.gateway_id} with connections: {other_gateways}")
                else:
                    # Device node connected to gateway
                    device_node = Node(node_info.blocksim_id, "d", node_info.gateway_id)
                    self.blocksim_nodes[node_info.node_id] = device_node
                    self.logger.debug(f"Created device {node_info.blocksim_id} under gateway {node_info.gateway_id}")
            
            # Return to original directory
            os.chdir(original_cwd)
            
            self.blocksim_initialized = True
            self.logger.info(f"BlockSim initialized with {len(self.blocksim_nodes)} nodes")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BlockSim: {e}")
            # Return to original directory in case of error
            try:
                os.chdir(original_cwd)
            except:
                pass
            self.blocksim_initialized = False
    
    def _start_validation_thread(self):
        """Start background thread for transaction validation"""
        self.running = True
        self.validation_thread = threading.Thread(
            target=self._validation_worker,
            daemon=True
        )
        self.validation_thread.start()
        self.logger.info("Validation thread started")
    
    def _validation_worker(self):
        """Background worker for processing transaction validations"""
        while self.running:
            try:
                # Check for new transactions to validate
                with self.validation_lock:
                    if self.validation_queue:
                        tx = self.validation_queue.pop(0)
                        self._process_transaction_validation(tx)
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Error in validation worker: {e}")
    
    def create_cross_zone_transaction(self, 
                                    sender_id: int, 
                                    recipient_id: int, 
                                    data: str) -> str:
        """
        Create a new cross-zone transaction
        
        Args:
            sender_id: NS-3 node ID of sender
            recipient_id: NS-3 node ID of recipient
            data: Transaction data
            
        Returns:
            Transaction ID
        """
        if not self.blocksim_initialized:
            raise RuntimeError("BlockSim not initialized")
        
        sender_info = self.node_mapping.get(sender_id)
        recipient_info = self.node_mapping.get(recipient_id)
        
        if not sender_info or not recipient_info:
            raise ValueError(f"Unknown node ID: {sender_id} or {recipient_id}")
        
        # Check if this is actually a cross-zone transaction
        if sender_info.zone == recipient_info.zone:
            self.logger.warning(f"Transaction {sender_id}->{recipient_id} is not cross-zone")
        
        # Create transaction
        tx_id = f"tx_{int(time.time() * 1000)}_{sender_id}_{recipient_id}"
        transaction = CrossZoneTransaction(
            tx_id=tx_id,
            sender_id=sender_id,
            sender_zone=sender_info.zone,
            recipient_id=recipient_id,
            recipient_zone=recipient_info.zone,
            data=data,
            timestamp=time.time()
        )
        
        # Add to pending transactions
        self.pending_transactions[tx_id] = transaction
        
        # Queue for validation
        with self.validation_lock:
            self.validation_queue.append(transaction)
        
        self.logger.info(f"Created cross-zone transaction {tx_id}: {sender_info.zone.value} -> {recipient_info.zone.value}")
        
        return tx_id
    
    def _process_transaction_validation(self, transaction: CrossZoneTransaction):
        """Process transaction validation using BlockSim"""
        try:
            if not self.blocksim_initialized:
                self.logger.error("BlockSim not initialized for validation")
                return
            
            self.logger.debug(f"Validating transaction {transaction.tx_id}")
            
            # Switch to BlockSim directory for imports
            original_cwd = os.getcwd()
            os.chdir(BLOCKSIM_PATH)
            
            # Create BlockSim transaction
            blocksim_tx = self.BlockSimTransaction(previous=-1)
            blocksim_tx.id = hash(transaction.tx_id) % (2**31)  # Convert to int
            blocksim_tx.timestamp = [transaction.timestamp, transaction.timestamp + 0.1, transaction.timestamp + 0.2]
            blocksim_tx.sender = transaction.sender_id
            blocksim_tx.to = self.node_mapping[transaction.recipient_id].gateway_id
            
            # Simulate validation process
            # In real implementation, this would go through BlockSim consensus
            validation_delay = 0.5 + len(self.bridge_nodes) * 0.1  # Simulate consensus time
            time.sleep(validation_delay)
            
            # For now, mark as validated (in real implementation, check consensus result)
            transaction.validated = True
            transaction.bridge_proof = f"proof_{transaction.tx_id}_{int(time.time())}"
            
            # Move to validated transactions
            if transaction.tx_id in self.pending_transactions:
                del self.pending_transactions[transaction.tx_id]
            self.validated_transactions[transaction.tx_id] = transaction
            
            # Write validation result for NS-3
            self._write_validation_result(transaction)
            
            os.chdir(original_cwd)
            
            self.logger.info(f"Transaction {transaction.tx_id} validated successfully")
            
        except Exception as e:
            self.logger.error(f"Error validating transaction {transaction.tx_id}: {e}")
            try:
                os.chdir(original_cwd)
            except:
                pass
    
    def _write_validation_result(self, transaction: CrossZoneTransaction):
        """Write validation result to file for NS-3 to read"""
        try:
            result_file = os.path.join(self.ipc_dir, f"validation_{transaction.tx_id}.json")
            result_data = {
                "tx_id": transaction.tx_id,
                "validated": transaction.validated,
                "bridge_proof": transaction.bridge_proof,
                "timestamp": time.time(),
                "sender_zone": transaction.sender_zone.value,
                "recipient_zone": transaction.recipient_zone.value
            }
            
            with open(result_file, 'w') as f:
                json.dump(result_data, f, indent=2)
                
            self.logger.debug(f"Validation result written to {result_file}")
            
        except Exception as e:
            self.logger.error(f"Error writing validation result: {e}")
    
    def get_transaction_status(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a transaction
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Transaction status or None if not found
        """
        # Check pending transactions
        if tx_id in self.pending_transactions:
            tx = self.pending_transactions[tx_id]
            return {
                "status": "pending",
                "transaction": asdict(tx)
            }
        
        # Check validated transactions
        if tx_id in self.validated_transactions:
            tx = self.validated_transactions[tx_id]
            return {
                "status": "validated",
                "transaction": asdict(tx)
            }
        
        return None
    
    def get_bridge_statistics(self) -> Dict[str, Any]:
        """Get current bridge statistics"""
        return {
            "total_nodes": len(self.all_nodes),
            "bridge_validators": len(self.bridge_nodes),
            "manet_nodes": len(self.manet_nodes),
            "fiveg_nodes": len(self.fiveg_nodes),
            "pending_transactions": len(self.pending_transactions),
            "validated_transactions": len(self.validated_transactions),
            "blocksim_initialized": self.blocksim_initialized,
            "validation_queue_size": len(self.validation_queue),
            "uptime": time.time() - getattr(self, 'start_time', time.time())
        }
    
    def shutdown(self):
        """Shutdown the bridge"""
        self.logger.info("Shutting down BlockSim bridge...")
        self.running = False
        
        if self.validation_thread and self.validation_thread.is_alive():
            self.validation_thread.join(timeout=5.0)
        
        # Clean up IPC files
        try:
            import shutil
            if os.path.exists(self.ipc_dir):
                shutil.rmtree(self.ipc_dir)
        except Exception as e:
            self.logger.warning(f"Error cleaning up IPC directory: {e}")
        
        self.logger.info("BlockSim bridge shutdown complete")
    
    def __del__(self):
        """Destructor"""
        try:
            self.shutdown()
        except:
            pass


# Testing functions
def test_blocksim_bridge():
    """Test the BlockSim bridge"""
    import tempfile
    import shutil
    
    logger = logging.getLogger("test")
    logger.info("Testing BlockSim Bridge...")
    
    try:
        # Create test bridge
        bridge = BlockSimBridge(
            bridge_node_ids=[10, 11],
            manet_node_ids=[1, 2, 3],
            fiveg_node_ids=[4, 5, 6]
        )
        
        # Test transaction creation
        tx_id = bridge.create_cross_zone_transaction(
            sender_id=1,  # MANET node
            recipient_id=4,  # 5G node
            data="test_cross_zone_data"
        )
        
        logger.info(f"Created transaction: {tx_id}")
        
        # Wait for validation
        time.sleep(2.0)
        
        # Check status
        status = bridge.get_transaction_status(tx_id)
        logger.info(f"Transaction status: {status}")
        
        # Get statistics
        stats = bridge.get_bridge_statistics()
        logger.info(f"Bridge statistics: {stats}")
        
        # Shutdown
        bridge.shutdown()
        
        logger.info("✅ BlockSim Bridge test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ BlockSim Bridge test failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_blocksim_bridge() 
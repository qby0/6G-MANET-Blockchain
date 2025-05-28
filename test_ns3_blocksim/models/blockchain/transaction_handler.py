#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cross-Zone Transaction Handler
Manages transactions crossing zone boundaries between 5G and MANET zones
with full BlockSim integration and cryptographic validation.
"""

import json
import logging
import os
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from .blocksim_bridge import BlockSimBridge, CrossZoneTransaction, ZoneType
from .crypto_manager import CrossZoneCrypto, TransactionSignature

logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    """Transaction processing status"""
    CREATED = "created"
    SIGNED = "signed"
    ROUTING = "routing"
    BRIDGE_VALIDATING = "bridge_validating"
    VALIDATED = "validated"
    DELIVERED = "delivered"
    FAILED = "failed"

class TransactionType(Enum):
    """Types of cross-zone transactions"""
    DATA_TRANSFER = "data_transfer"
    ZONE_TRANSITION = "zone_transition"
    AUTHENTICATION = "authentication"
    CONSENSUS = "consensus"

@dataclass
class TransactionEvent:
    """Event in transaction lifecycle"""
    timestamp: float
    event_type: str
    node_id: int
    zone: ZoneType
    details: Dict[str, Any]

@dataclass
class ExtendedTransaction(CrossZoneTransaction):
    """Extended transaction with processing details"""
    transaction_type: TransactionType = TransactionType.DATA_TRANSFER
    status: TransactionStatus = TransactionStatus.CREATED
    routing_path: List[int] = None
    events: List[TransactionEvent] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.routing_path is None:
            self.routing_path = []
        if self.events is None:
            self.events = []

class CrossZoneTransactionHandler:
    """
    Handles cross-zone transaction processing with BlockSim integration
    Manages the full lifecycle from creation to delivery
    """
    
    def __init__(self, 
                 blocksim_bridge: BlockSimBridge,
                 crypto_manager: CrossZoneCrypto,
                 config: Optional[Dict] = None):
        """
        Initialize transaction handler
        
        Args:
            blocksim_bridge: BlockSim bridge instance
            crypto_manager: Crypto manager instance
            config: Configuration parameters
        """
        self.logger = logging.getLogger("CrossZoneTransactionHandler")
        
        self.bridge = blocksim_bridge
        self.crypto = crypto_manager
        
        # Default configuration
        self.config = {
            "transaction_timeout": 30.0,
            "max_routing_hops": 10,
            "retry_delay": 2.0,
            "batch_size": 10,
            "validation_timeout": 15.0,
            "delivery_confirmation": True,
            "enable_metrics": True
        }
        
        if config:
            self.config.update(config)
        
        # Transaction storage
        self.active_transactions: Dict[str, ExtendedTransaction] = {}
        self.completed_transactions: Dict[str, ExtendedTransaction] = {}
        self.failed_transactions: Dict[str, ExtendedTransaction] = {}
        
        # Processing queues
        self.signing_queue: List[str] = []
        self.routing_queue: List[str] = []
        self.validation_queue: List[str] = []
        self.delivery_queue: List[str] = []
        
        # Threading
        self.processing_lock = threading.Lock()
        self.processor_thread = None
        self.running = False
        
        # Callbacks for NS-3 integration
        self.callbacks: Dict[str, Callable] = {}
        
        # Metrics
        self.metrics = {
            "transactions_created": 0,
            "transactions_completed": 0,
            "transactions_failed": 0,
            "total_validation_time": 0.0,
            "total_routing_time": 0.0,
            "average_latency": 0.0
        }
        
        # Start processing thread
        self._start_processor()
        
        self.logger.info("Cross-Zone Transaction Handler initialized")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register callback for transaction events
        
        Args:
            event_type: Type of event ("routing", "validation", "delivery", etc.)
            callback: Callback function
        """
        self.callbacks[event_type] = callback
        self.logger.debug(f"Registered callback for {event_type}")
    
    def create_transaction(self,
                          sender_id: int,
                          recipient_id: int,
                          data: str,
                          transaction_type: TransactionType = TransactionType.DATA_TRANSFER,
                          metadata: Optional[Dict] = None) -> str:
        """
        Create a new cross-zone transaction
        
        Args:
            sender_id: Sender node ID
            recipient_id: Recipient node ID
            data: Transaction data
            transaction_type: Type of transaction
            metadata: Additional metadata
            
        Returns:
            Transaction ID
        """
        try:
            # Create base transaction via bridge
            tx_id = self.bridge.create_cross_zone_transaction(
                sender_id, recipient_id, data
            )
            
            # Get base transaction
            bridge_tx = self.bridge.pending_transactions.get(tx_id)
            if not bridge_tx:
                raise RuntimeError("Failed to create bridge transaction")
            
            # Create extended transaction
            extended_tx = ExtendedTransaction(
                tx_id=bridge_tx.tx_id,
                sender_id=bridge_tx.sender_id,
                sender_zone=bridge_tx.sender_zone,
                recipient_id=bridge_tx.recipient_id,
                recipient_zone=bridge_tx.recipient_zone,
                data=bridge_tx.data,
                timestamp=bridge_tx.timestamp,
                transaction_type=transaction_type,
                status=TransactionStatus.CREATED
            )
            
            # Add metadata if provided
            if metadata:
                extended_tx.data = json.dumps({
                    "payload": data,
                    "metadata": metadata
                })
            
            # Add creation event
            self._add_event(extended_tx, "created", extended_tx.sender_id, {
                "transaction_type": transaction_type.value,
                "data_size": len(data),
                "metadata": metadata or {}
            })
            
            # Store transaction
            self.active_transactions[tx_id] = extended_tx
            
            # Queue for signing
            with self.processing_lock:
                self.signing_queue.append(tx_id)
            
            # Update metrics
            self.metrics["transactions_created"] += 1
            
            self.logger.info(f"Created transaction {tx_id}: {extended_tx.sender_zone.value} -> {extended_tx.recipient_zone.value}")
            
            return tx_id
            
        except Exception as e:
            self.logger.error(f"Failed to create transaction: {e}")
            raise
    
    def _start_processor(self):
        """Start background processing thread"""
        self.running = True
        self.processor_thread = threading.Thread(
            target=self._processor_worker,
            daemon=True
        )
        self.processor_thread.start()
        self.logger.info("Transaction processor started")
    
    def _processor_worker(self):
        """Background worker for transaction processing"""
        while self.running:
            try:
                # Process signing queue
                self._process_signing_queue()
                
                # Process routing queue
                self._process_routing_queue()
                
                # Process validation queue
                self._process_validation_queue()
                
                # Process delivery queue
                self._process_delivery_queue()
                
                # Check for timeouts
                self._check_timeouts()
                
                time.sleep(0.1)  # Small delay
                
            except Exception as e:
                self.logger.error(f"Error in processor worker: {e}")
    
    def _process_signing_queue(self):
        """Process transactions waiting for signing"""
        with self.processing_lock:
            if not self.signing_queue:
                return
            
            tx_id = self.signing_queue.pop(0)
        
        if tx_id not in self.active_transactions:
            return
        
        tx = self.active_transactions[tx_id]
        
        try:
            # Create transaction data for signing
            sign_data = {
                "tx_id": tx.tx_id,
                "sender_id": tx.sender_id,
                "recipient_id": tx.recipient_id,
                "data": tx.data,
                "timestamp": tx.timestamp,
                "transaction_type": tx.transaction_type.value
            }
            
            # Sign transaction
            signature = self.crypto.sign_transaction(sign_data, tx.sender_id)
            if not signature:
                self._fail_transaction(tx, "signing_failed", "Failed to sign transaction")
                return
            
            # Update transaction
            tx.signature = signature.signature
            tx.status = TransactionStatus.SIGNED
            
            self._add_event(tx, "signed", tx.sender_id, {
                "signature_algorithm": signature.algorithm,
                "public_key_hash": signature.public_key_hash[:16]
            })
            
            # Queue for routing
            with self.processing_lock:
                self.routing_queue.append(tx_id)
            
            self.logger.debug(f"Transaction {tx_id} signed successfully")
            
        except Exception as e:
            self._fail_transaction(tx, "signing_error", str(e))
    
    def _process_routing_queue(self):
        """Process transactions waiting for routing"""
        with self.processing_lock:
            if not self.routing_queue:
                return
            
            tx_id = self.routing_queue.pop(0)
        
        if tx_id not in self.active_transactions:
            return
        
        tx = self.active_transactions[tx_id]
        
        try:
            routing_start = time.time()
            
            # Determine routing path
            routing_path = self._calculate_routing_path(tx)
            if not routing_path:
                self._fail_transaction(tx, "routing_failed", "No routing path found")
                return
            
            tx.routing_path = routing_path
            tx.status = TransactionStatus.ROUTING
            
            routing_time = time.time() - routing_start
            self.metrics["total_routing_time"] += routing_time
            
            self._add_event(tx, "routing_calculated", tx.sender_id, {
                "routing_path": routing_path,
                "routing_hops": len(routing_path),
                "routing_time": routing_time
            })
            
            # Trigger NS-3 routing callback
            if "routing" in self.callbacks:
                self.callbacks["routing"](tx_id, routing_path)
            
            # Queue for validation if crosses zones
            if self._requires_bridge_validation(tx):
                with self.processing_lock:
                    self.validation_queue.append(tx_id)
            else:
                # Direct to delivery if no bridge validation needed
                with self.processing_lock:
                    self.delivery_queue.append(tx_id)
            
            self.logger.debug(f"Transaction {tx_id} routed: {len(routing_path)} hops")
            
        except Exception as e:
            self._fail_transaction(tx, "routing_error", str(e))
    
    def _process_validation_queue(self):
        """Process transactions waiting for bridge validation"""
        with self.processing_lock:
            if not self.validation_queue:
                return
            
            tx_id = self.validation_queue.pop(0)
        
        if tx_id not in self.active_transactions:
            return
        
        tx = self.active_transactions[tx_id]
        
        try:
            validation_start = time.time()
            tx.status = TransactionStatus.BRIDGE_VALIDATING
            
            # Find bridge validator in routing path
            bridge_validator = self._find_bridge_validator(tx.routing_path)
            if not bridge_validator:
                self._fail_transaction(tx, "no_bridge_validator", "No bridge validator in path")
                return
            
            # Create transaction data for validation
            validation_data = {
                "tx_id": tx.tx_id,
                "sender_id": tx.sender_id,
                "recipient_id": tx.recipient_id,
                "data": tx.data,
                "signature": tx.signature,
                "routing_path": tx.routing_path,
                "timestamp": tx.timestamp
            }
            
            # Generate cross-zone proof
            proof = self.crypto.generate_cross_zone_proof(
                validation_data,
                bridge_validator,
                tx.sender_zone.value,
                tx.recipient_zone.value
            )
            
            if not proof:
                self._fail_transaction(tx, "proof_generation_failed", "Failed to generate cross-zone proof")
                return
            
            tx.bridge_proof = json.dumps(proof)
            tx.validated = True
            tx.status = TransactionStatus.VALIDATED
            
            validation_time = time.time() - validation_start
            self.metrics["total_validation_time"] += validation_time
            
            self._add_event(tx, "validated", bridge_validator, {
                "bridge_validator": bridge_validator,
                "proof_hash": proof["proof_hash"][:16],
                "validation_time": validation_time
            })
            
            # Trigger validation callback
            if "validation" in self.callbacks:
                self.callbacks["validation"](tx_id, proof)
            
            # Queue for delivery
            with self.processing_lock:
                self.delivery_queue.append(tx_id)
            
            self.logger.debug(f"Transaction {tx_id} validated by bridge {bridge_validator}")
            
        except Exception as e:
            self._fail_transaction(tx, "validation_error", str(e))
    
    def _process_delivery_queue(self):
        """Process transactions ready for delivery"""
        with self.processing_lock:
            if not self.delivery_queue:
                return
            
            tx_id = self.delivery_queue.pop(0)
        
        if tx_id not in self.active_transactions:
            return
        
        tx = self.active_transactions[tx_id]
        
        try:
            # Trigger delivery callback
            if "delivery" in self.callbacks:
                delivery_success = self.callbacks["delivery"](tx_id, tx.routing_path, tx.bridge_proof)
                
                if delivery_success:
                    self._complete_transaction(tx)
                else:
                    self._retry_transaction(tx, "delivery_failed")
            else:
                # No callback, assume successful delivery
                self._complete_transaction(tx)
            
        except Exception as e:
            self._fail_transaction(tx, "delivery_error", str(e))
    
    def _calculate_routing_path(self, tx: ExtendedTransaction) -> List[int]:
        """
        Calculate routing path for transaction
        
        Args:
            tx: Transaction to route
            
        Returns:
            List of node IDs in routing path
        """
        # Simple routing: sender -> bridge -> recipient
        # In real implementation, use NS-3 AODV routing
        
        path = [tx.sender_id]
        
        # If cross-zone, add bridge validator
        if tx.sender_zone != tx.recipient_zone:
            # Find appropriate bridge validator
            bridge_validator = None
            for bridge_id in self.bridge.bridge_nodes:
                # In real implementation, check connectivity and load
                bridge_validator = bridge_id
                break
            
            if bridge_validator:
                path.append(bridge_validator)
        
        path.append(tx.recipient_id)
        
        return path
    
    def _requires_bridge_validation(self, tx: ExtendedTransaction) -> bool:
        """Check if transaction requires bridge validation"""
        return tx.sender_zone != tx.recipient_zone
    
    def _find_bridge_validator(self, routing_path: List[int]) -> Optional[int]:
        """Find bridge validator in routing path"""
        for node_id in routing_path:
            if node_id in self.bridge.bridge_nodes:
                return node_id
        return None
    
    def _add_event(self, tx: ExtendedTransaction, event_type: str, node_id: int, details: Dict):
        """Add event to transaction history"""
        event = TransactionEvent(
            timestamp=time.time(),
            event_type=event_type,
            node_id=node_id,
            zone=self.bridge.node_mapping.get(node_id, type('obj', (object,), {'zone': ZoneType.MANET})).zone,
            details=details
        )
        tx.events.append(event)
    
    def _complete_transaction(self, tx: ExtendedTransaction):
        """Mark transaction as completed"""
        tx.status = TransactionStatus.DELIVERED
        
        # Calculate latency
        latency = time.time() - tx.timestamp
        self.metrics["average_latency"] = (
            (self.metrics["average_latency"] * self.metrics["transactions_completed"] + latency) /
            (self.metrics["transactions_completed"] + 1)
        )
        
        self._add_event(tx, "delivered", tx.recipient_id, {
            "total_latency": latency,
            "total_hops": len(tx.routing_path)
        })
        
        # Move to completed transactions
        if tx.tx_id in self.active_transactions:
            del self.active_transactions[tx.tx_id]
        self.completed_transactions[tx.tx_id] = tx
        
        self.metrics["transactions_completed"] += 1
        
        self.logger.info(f"Transaction {tx.tx_id} completed successfully (latency: {latency:.3f}s)")
    
    def _fail_transaction(self, tx: ExtendedTransaction, reason: str, details: str):
        """Mark transaction as failed"""
        tx.status = TransactionStatus.FAILED
        
        self._add_event(tx, "failed", 0, {
            "reason": reason,
            "details": details,
            "retry_count": tx.retry_count
        })
        
        # Move to failed transactions
        if tx.tx_id in self.active_transactions:
            del self.active_transactions[tx.tx_id]
        self.failed_transactions[tx.tx_id] = tx
        
        self.metrics["transactions_failed"] += 1
        
        self.logger.error(f"Transaction {tx.tx_id} failed: {reason} - {details}")
    
    def _retry_transaction(self, tx: ExtendedTransaction, reason: str):
        """Retry failed transaction"""
        if tx.retry_count >= tx.max_retries:
            self._fail_transaction(tx, reason, f"Max retries ({tx.max_retries}) exceeded")
            return
        
        tx.retry_count += 1
        
        self._add_event(tx, "retry", 0, {
            "reason": reason,
            "retry_count": tx.retry_count,
            "max_retries": tx.max_retries
        })
        
        # Re-queue for appropriate processing step
        with self.processing_lock:
            if tx.status == TransactionStatus.CREATED:
                self.signing_queue.append(tx.tx_id)
            elif tx.status == TransactionStatus.SIGNED:
                self.routing_queue.append(tx.tx_id)
            elif tx.status == TransactionStatus.ROUTING:
                self.validation_queue.append(tx.tx_id)
            elif tx.status == TransactionStatus.VALIDATED:
                self.delivery_queue.append(tx.tx_id)
        
        self.logger.warning(f"Retrying transaction {tx.tx_id} (attempt {tx.retry_count}/{tx.max_retries})")
    
    def _check_timeouts(self):
        """Check for timed out transactions"""
        current_time = time.time()
        timeout_transactions = []
        
        for tx_id, tx in self.active_transactions.items():
            if current_time - tx.timestamp > self.config["transaction_timeout"]:
                timeout_transactions.append(tx)
        
        for tx in timeout_transactions:
            self._fail_transaction(tx, "timeout", f"Transaction timed out after {self.config['transaction_timeout']}s")
    
    def get_transaction_status(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed transaction status"""
        # Check active transactions
        if tx_id in self.active_transactions:
            tx = self.active_transactions[tx_id]
            return {
                "status": "active",
                "transaction": asdict(tx),
                "current_status": tx.status.value,
                "events": [asdict(event) for event in tx.events]
            }
        
        # Check completed transactions
        if tx_id in self.completed_transactions:
            tx = self.completed_transactions[tx_id]
            return {
                "status": "completed",
                "transaction": asdict(tx),
                "final_status": tx.status.value,
                "events": [asdict(event) for event in tx.events]
            }
        
        # Check failed transactions
        if tx_id in self.failed_transactions:
            tx = self.failed_transactions[tx_id]
            return {
                "status": "failed",
                "transaction": asdict(tx),
                "final_status": tx.status.value,
                "events": [asdict(event) for event in tx.events]
            }
        
        return None
    
    def get_handler_statistics(self) -> Dict[str, Any]:
        """Get transaction handler statistics"""
        return {
            "active_transactions": len(self.active_transactions),
            "completed_transactions": len(self.completed_transactions),
            "failed_transactions": len(self.failed_transactions),
            "queue_sizes": {
                "signing": len(self.signing_queue),
                "routing": len(self.routing_queue),
                "validation": len(self.validation_queue),
                "delivery": len(self.delivery_queue)
            },
            "metrics": self.metrics.copy(),
            "config": self.config.copy()
        }
    
    def shutdown(self):
        """Shutdown transaction handler"""
        self.logger.info("Shutting down transaction handler...")
        self.running = False
        
        if self.processor_thread and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=5.0)
        
        self.logger.info("Transaction handler shutdown complete")


# Testing functions
def test_transaction_handler():
    """Test the transaction handler"""
    import time
    from .blocksim_bridge import BlockSimBridge
    from .crypto_manager import CrossZoneCrypto
    
    logger = logging.getLogger("test")
    logger.info("Testing Cross-Zone Transaction Handler...")
    
    try:
        # Create components
        bridge = BlockSimBridge(
            bridge_node_ids=[10, 11],
            manet_node_ids=[1, 2, 3],
            fiveg_node_ids=[4, 5, 6]
        )
        
        crypto = CrossZoneCrypto()
        
        # Generate keys
        for node_id in [1, 4, 10, 11]:
            crypto.generate_node_keys(node_id)
        
        # Create transaction handler
        handler = CrossZoneTransactionHandler(bridge, crypto)
        
        # Test transaction creation
        tx_id = handler.create_transaction(
            sender_id=1,  # MANET node
            recipient_id=4,  # 5G node
            data="test_cross_zone_data",
            transaction_type=TransactionType.DATA_TRANSFER
        )
        
        logger.info(f"Created transaction: {tx_id}")
        
        # Wait for processing
        time.sleep(3.0)
        
        # Check status
        status = handler.get_transaction_status(tx_id)
        logger.info(f"Transaction status: {status['current_status'] if status else 'Not found'}")
        
        # Get statistics
        stats = handler.get_handler_statistics()
        logger.info(f"Handler statistics: {stats}")
        
        # Shutdown
        handler.shutdown()
        bridge.shutdown()
        
        logger.info("✅ Transaction Handler test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Transaction Handler test failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_transaction_handler() 
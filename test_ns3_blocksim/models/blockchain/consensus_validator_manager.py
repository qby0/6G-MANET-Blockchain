#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Consensus-based Validator Management System
Implements ValidatorLeave/ManetNodeEnter exchange algorithm with mobility support
"""

import time
import json
import logging
import hashlib
import threading
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict

class NodeStatus(Enum):
    """Node status enumeration"""
    ACTIVE = "active"
    LEAVING = "leaving"
    RETIRED = "retired"
    CANDIDATE = "candidate"
    JOINING = "joining"
    APPROVED = "approved"

class ZoneType(Enum):
    """Network zone types"""
    FIVE_G = "5g"
    MANET = "manet" 
    BRIDGE = "bridge"
    UNKNOWN = "unknown"

class TransactionType(Enum):
    """Validator transaction types"""
    LEAVE_TX = "leave_tx"
    JOIN_TX = "join_tx"
    VOTE_TX = "vote_tx"
    PROMOTE_TX = "promote_tx"

@dataclass
class ValidatorNode:
    """Represents a validator node"""
    node_id: int
    zone: ZoneType
    status: NodeStatus
    rssi_6g: float  # Signal strength to 6G base station
    battery_level: float  # Battery percentage (0.0 - 1.0)
    cert_valid: bool  # Certificate validity
    last_activity: float  # Timestamp of last activity
    validator_since: Optional[float] = None  # When became validator
    dual_radio: bool = False  # Gateway-validator capability
    pub_key_6g: Optional[str] = None  # 6G chain public key
    pub_key_manet: Optional[str] = None  # MANET chain public key
    leave_threshold: float = -80.0  # RSSI threshold for leaving
    performance_score: float = 1.0  # Performance metric (0.0 - 1.0)

@dataclass
class ValidatorTransaction:
    """Transaction for validator management"""
    tx_id: str
    tx_type: TransactionType
    node_id: int
    timestamp: float
    last_block_hash: str
    signature: str
    data: Dict[str, Any]
    votes: Dict[int, bool] = None  # node_id -> approve/reject
    finalized: bool = False

@dataclass
class ConsensusRound:
    """PBFT consensus round"""
    round_id: str
    transaction: ValidatorTransaction
    prepare_votes: Dict[int, bool]
    commit_votes: Dict[int, bool]
    phase: str  # "prepare", "commit", "finalized"
    timeout: float
    success: bool = False

class ConsensusValidatorManager:
    """
    Manages validator selection using consensus with mobility support
    Implements ValidatorLeave/ManetNodeEnter exchange algorithm
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize consensus validator manager"""
        self.logger = logging.getLogger("ConsensusValidatorManager")
        
        # Default configuration
        self.config = {
            "rssi_leave_threshold": -80.0,  # dBm
            "rssi_enter_threshold": -70.0,  # dBm
            "battery_threshold": 0.2,  # 20%
            "consensus_threshold": 0.67,  # 2/3 majority
            "min_validators": 3,
            "max_validators": 7,
            "vote_timeout": 30.0,  # seconds
            "heartbeat_interval": 10.0,  # seconds
            "performance_window": 300.0,  # 5 minutes
            "dual_radio_preference": True,
            "bridge_zone_radius": 60.0,  # meters from base station
            "enable_rotation": True,
            "rotation_interval": 300.0  # 5 minutes
        }
        
        if config:
            self.config.update(config)
        
        # Validator state
        self.active_validators: Dict[int, ValidatorNode] = {}
        self.candidate_nodes: Dict[int, ValidatorNode] = {}
        self.retired_validators: Dict[int, ValidatorNode] = {}
        
        # Consensus state
        self.pending_transactions: Dict[str, ValidatorTransaction] = {}
        self.consensus_rounds: Dict[str, ConsensusRound] = {}
        self.last_block_hash: str = "genesis_block_hash"
        
        # Base station (always present)
        self.base_station_id: int = 0
        
        # Threading
        self.consensus_lock = threading.Lock()
        self.heartbeat_thread = None
        self.running = False
        
        # Metrics
        self.metrics = {
            "total_leave_transactions": 0,
            "total_join_transactions": 0,
            "successful_promotions": 0,
            "failed_consensus": 0,
            "average_consensus_time": 0.0,
            "validator_changes": 0
        }
        
        self.logger.info("Consensus Validator Manager initialized")
        self.logger.info(f"Min validators: {self.config['min_validators']}, Max: {self.config['max_validators']}")
    
    def start(self):
        """Start the validator manager"""
        self.running = True
        self._start_heartbeat_thread()
        self.logger.info("Consensus Validator Manager started")
    
    def stop(self):
        """Stop the validator manager"""
        self.running = False
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5.0)
        self.logger.info("Consensus Validator Manager stopped")
    
    def _start_heartbeat_thread(self):
        """Start heartbeat monitoring thread"""
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_worker,
            daemon=True
        )
        self.heartbeat_thread.start()
    
    def _heartbeat_worker(self):
        """Background worker for monitoring and maintenance"""
        while self.running:
            try:
                self._monitor_validators()
                self._process_consensus_rounds()
                self._cleanup_expired_transactions()
                time.sleep(self.config["heartbeat_interval"])
            except Exception as e:
                self.logger.error(f"Error in heartbeat worker: {e}")
    
    def register_node(self, 
                     node_id: int, 
                     zone: ZoneType,
                     rssi_6g: float = -60.0,
                     battery_level: float = 1.0,
                     cert_valid: bool = True,
                     dual_radio: bool = False) -> bool:
        """
        Register a new node as potential validator candidate
        
        Args:
            node_id: Node identifier
            zone: Current network zone
            rssi_6g: Signal strength to 6G base station
            battery_level: Battery level (0.0 - 1.0)
            cert_valid: Certificate validity
            dual_radio: Gateway-validator capability
            
        Returns:
            True if registered successfully
        """
        try:
            # Create validator node
            validator_node = ValidatorNode(
                node_id=node_id,
                zone=zone,
                status=NodeStatus.CANDIDATE,
                rssi_6g=rssi_6g,
                battery_level=battery_level,
                cert_valid=cert_valid,
                last_activity=time.time(),
                dual_radio=dual_radio,
                leave_threshold=self.config["rssi_leave_threshold"]
            )
            
            # Check eligibility
            if self._is_eligible_candidate(validator_node):
                self.candidate_nodes[node_id] = validator_node
                self.logger.info(f"Node {node_id} registered as validator candidate")
                
                # Auto-promote if we need more validators
                if len(self.active_validators) < self.config["min_validators"]:
                    self._auto_promote_candidate(node_id)
                
                return True
            else:
                self.logger.warning(f"Node {node_id} not eligible for validator role")
                return False
                
        except Exception as e:
            self.logger.error(f"Error registering node {node_id}: {e}")
            return False
    
    def update_node_status(self, 
                          node_id: int, 
                          rssi_6g: Optional[float] = None,
                          battery_level: Optional[float] = None,
                          zone: Optional[ZoneType] = None):
        """
        Update node status (mobility, battery, signal strength)
        
        Args:
            node_id: Node identifier
            rssi_6g: New signal strength
            battery_level: New battery level
            zone: New zone (if changed)
        """
        try:
            # Find node in active validators or candidates
            node = None
            if node_id in self.active_validators:
                node = self.active_validators[node_id]
            elif node_id in self.candidate_nodes:
                node = self.candidate_nodes[node_id]
            
            if not node:
                return
            
            # Update fields
            if rssi_6g is not None:
                node.rssi_6g = rssi_6g
            if battery_level is not None:
                node.battery_level = battery_level
            if zone is not None:
                node.zone = zone
            
            node.last_activity = time.time()
            
            # ИСПРАВЛЕНО: Проверяем зону - валидаторы не должны быть в MANET
            if (node_id in self.active_validators and 
                zone is not None and 
                zone == ZoneType.MANET):
                self.logger.info(f"Validator {node_id} moved to MANET zone, initiating leave")
                self._initiate_validator_leave(node_id, "entered_manet_zone")
                return
            
            # Check if validator should leave due to weak signal
            if (node_id in self.active_validators and 
                rssi_6g is not None and 
                rssi_6g < node.leave_threshold):
                self._initiate_validator_leave(node_id, "weak_signal")
            
            # Check if candidate is now eligible
            elif (node_id in self.candidate_nodes and 
                  rssi_6g is not None and 
                  rssi_6g > self.config["rssi_enter_threshold"]):
                self._check_candidate_promotion(node_id)
            
        except Exception as e:
            self.logger.error(f"Error updating node {node_id} status: {e}")
    
    def _is_eligible_candidate(self, node: ValidatorNode) -> bool:
        """Check if node is eligible to become validator"""
        conditions = [
            node.cert_valid,
            node.battery_level > self.config["battery_threshold"],
            node.rssi_6g > self.config["rssi_enter_threshold"],
            node.zone in [ZoneType.BRIDGE, ZoneType.FIVE_G]  # Prefer bridge/5G nodes
        ]
        
        return all(conditions)
    
    def _auto_promote_candidate(self, candidate_id: int):
        """Auto-promote candidate when validators are needed"""
        if candidate_id not in self.candidate_nodes:
            return
        
        candidate = self.candidate_nodes[candidate_id]
        
        # ИСПРАВЛЕНО: Дополнительная проверка зоны при автопромоушене
        # MANET узлы не должны становиться валидаторами даже при нехватке валидаторов
        if candidate.zone not in [ZoneType.BRIDGE, ZoneType.FIVE_G]:
            self.logger.debug(f"Candidate {candidate_id} in {candidate.zone.value} zone not eligible for auto-promotion")
            return
        
        # Create join transaction
        join_tx = self._create_join_transaction(candidate)
        
        # Fast-track approval if we're below minimum
        if len(self.active_validators) < self.config["min_validators"]:
            self._approve_join_transaction(join_tx.tx_id)
            self.logger.info(f"Fast-tracked promotion of candidate {candidate_id}")
    
    def _initiate_validator_leave(self, validator_id: int, reason: str):
        """Initiate validator leaving process"""
        if validator_id not in self.active_validators:
            return
        
        validator = self.active_validators[validator_id]
        
        if validator.status != NodeStatus.ACTIVE:
            return  # Already leaving
        
        try:
            # Mark as leaving
            validator.status = NodeStatus.LEAVING
            
            # Create leave transaction
            leave_tx = ValidatorTransaction(
                tx_id=f"leave_{validator_id}_{int(time.time() * 1000)}",
                tx_type=TransactionType.LEAVE_TX,
                node_id=validator_id,
                timestamp=time.time(),
                last_block_hash=self.last_block_hash,
                signature=self._sign_transaction(validator_id, {
                    "action": "leave",
                    "reason": reason,
                    "node_id": validator_id
                }),
                data={
                    "reason": reason,
                    "rssi_6g": validator.rssi_6g,
                    "battery_level": validator.battery_level,
                    "zone": validator.zone.value
                }
            )
            
            # Add to pending transactions
            with self.consensus_lock:
                self.pending_transactions[leave_tx.tx_id] = leave_tx
            
            self.logger.info(f"Validator {validator_id} initiated leave process: {reason}")
            self.metrics["total_leave_transactions"] += 1
            
            # Start consensus round
            self._start_consensus_round(leave_tx)
            
        except Exception as e:
            self.logger.error(f"Error initiating validator leave for {validator_id}: {e}")
    
    def _create_join_transaction(self, candidate: ValidatorNode) -> ValidatorTransaction:
        """Create join transaction for candidate"""
        join_tx = ValidatorTransaction(
            tx_id=f"join_{candidate.node_id}_{int(time.time() * 1000)}",
            tx_type=TransactionType.JOIN_TX,
            node_id=candidate.node_id,
            timestamp=time.time(),
            last_block_hash=self.last_block_hash,
            signature=self._sign_transaction(candidate.node_id, {
                "action": "join",
                "node_id": candidate.node_id
            }),
            data={
                "zone": candidate.zone.value,
                "rssi_6g": candidate.rssi_6g,
                "battery_level": candidate.battery_level,
                "dual_radio": candidate.dual_radio,
                "cert_valid": candidate.cert_valid,
                "pub_key_6g": candidate.pub_key_6g,
                "pub_key_manet": candidate.pub_key_manet
            }
        )
        
        # Add to pending transactions
        with self.consensus_lock:
            self.pending_transactions[join_tx.tx_id] = join_tx
        
        self.logger.info(f"Created join transaction for candidate {candidate.node_id}")
        self.metrics["total_join_transactions"] += 1
        
        return join_tx
    
    def _start_consensus_round(self, transaction: ValidatorTransaction):
        """Start PBFT consensus round for transaction"""
        round_id = f"consensus_{transaction.tx_id}_{int(time.time() * 1000)}"
        
        consensus_round = ConsensusRound(
            round_id=round_id,
            transaction=transaction,
            prepare_votes={},
            commit_votes={},
            phase="prepare",
            timeout=time.time() + self.config["vote_timeout"]
        )
        
        with self.consensus_lock:
            self.consensus_rounds[round_id] = consensus_round
        
        self.logger.info(f"Started consensus round {round_id} for {transaction.tx_type.value}")
        
        # Broadcast to all validators for voting
        self._broadcast_consensus_request(consensus_round)
    
    def _broadcast_consensus_request(self, consensus_round: ConsensusRound):
        """Broadcast consensus request to all active validators (legacy method)"""
        # Используем новый асинхронный метод для избежания блокировок
        self._broadcast_consensus_request_async(consensus_round)
    
    def _broadcast_consensus_request_async(self, consensus_round: ConsensusRound):
        """Broadcast consensus request asynchronously to avoid blocking"""
        # Include base station in voting
        all_validators = list(self.active_validators.keys()) + [self.base_station_id]
        
        # Process votes quickly without blocking
        for validator_id in all_validators:
            try:
                vote = self._simulate_validator_vote(validator_id, consensus_round.transaction)
                
                # Record vote
                with self.consensus_lock:
                    round_id = consensus_round.round_id
                    if round_id in self.consensus_rounds:  # Check round still exists
                        current_round = self.consensus_rounds[round_id]
                        if current_round.phase == "prepare":
                            current_round.prepare_votes[validator_id] = vote
                        elif current_round.phase == "commit":
                            current_round.commit_votes[validator_id] = vote
                
                self.logger.debug(f"Validator {validator_id} voted {vote} for {consensus_round.transaction.tx_id}")
            except Exception as e:
                self.logger.warning(f"Failed to get vote from validator {validator_id}: {e}")
    
    def _finalize_consensus(self, consensus_round: ConsensusRound):
        """Finalize successful consensus round (legacy method)"""
        # Используем новый асинхронный метод
        self._finalize_consensus_async(consensus_round)
    
    def _finalize_consensus_async(self, consensus_round: ConsensusRound):
        """Finalize consensus asynchronously to avoid blocking"""
        try:
            transaction = consensus_round.transaction
            
            if transaction.tx_type == TransactionType.LEAVE_TX:
                self._finalize_validator_leave(transaction.node_id)
            
            elif transaction.tx_type == TransactionType.JOIN_TX:
                self._finalize_validator_join(transaction.node_id)
            
            # Update last block hash (simulate blockchain update)
            self.last_block_hash = hashlib.sha256(
                f"{self.last_block_hash}_{transaction.tx_id}_{time.time()}".encode()
            ).hexdigest()[:16]
            
            self.metrics["validator_changes"] += 1
            
        except Exception as e:
            self.logger.error(f"Error finalizing consensus: {e}")
    
    def _finalize_validator_leave(self, validator_id: int):
        """Finalize validator leaving process"""
        if validator_id not in self.active_validators:
            return
        
        validator = self.active_validators[validator_id]
        validator.status = NodeStatus.RETIRED
        
        # Move to retired validators
        self.retired_validators[validator_id] = validator
        del self.active_validators[validator_id]
        
        self.logger.info(f"Validator {validator_id} successfully left the network")
        
        # Check if we need to promote candidates
        if len(self.active_validators) < self.config["min_validators"]:
            self._promote_best_candidate()
    
    def _finalize_validator_join(self, candidate_id: int):
        """Finalize validator joining process"""
        if candidate_id not in self.candidate_nodes:
            return
        
        candidate = self.candidate_nodes[candidate_id]
        candidate.status = NodeStatus.ACTIVE
        candidate.validator_since = time.time()
        
        # Move to active validators
        self.active_validators[candidate_id] = candidate
        del self.candidate_nodes[candidate_id]
        
        self.logger.info(f"Candidate {candidate_id} successfully promoted to validator")
        self.metrics["successful_promotions"] += 1
    
    def _promote_best_candidate(self):
        """Promote the best available candidate"""
        # Защита от рекурсивных вызовов
        if hasattr(self, '_promoting_candidate') and self._promoting_candidate:
            self.logger.debug("Already promoting a candidate, skipping")
            return
        
        if not self.candidate_nodes:
            return
        
        # Проверяем, что мы действительно нуждаемся в валидаторах
        if len(self.active_validators) >= self.config["min_validators"]:
            return
        
        try:
            self._promoting_candidate = True
            
            # Score candidates
            best_candidate_id = None
            best_score = -1.0
            
            for candidate_id, candidate in self.candidate_nodes.items():
                if not self._is_eligible_candidate(candidate):
                    continue
                
                # Calculate composite score
                score = (
                    candidate.rssi_6g / -50.0 +  # Signal strength (normalized)
                    candidate.battery_level +     # Battery level
                    candidate.performance_score + # Performance
                    (0.2 if candidate.dual_radio else 0.0)  # Dual radio bonus
                )
                
                if score > best_score:
                    best_score = score
                    best_candidate_id = candidate_id
            
            if best_candidate_id:
                # Проверяем, что кандидат еще не участвует в консенсусе
                existing_rounds = []
                with self.consensus_lock:
                    for round_id, round_data in self.consensus_rounds.items():
                        if (round_data.transaction.tx_type == TransactionType.JOIN_TX and 
                            round_data.transaction.node_id == best_candidate_id):
                            existing_rounds.append(round_id)
                
                if not existing_rounds:
                    join_tx = self._create_join_transaction(self.candidate_nodes[best_candidate_id])
                    self._start_consensus_round(join_tx)
                    self.logger.info(f"Promoting best candidate {best_candidate_id} (score: {best_score:.2f})")
                else:
                    self.logger.debug(f"Candidate {best_candidate_id} already in consensus round")
            
        finally:
            self._promoting_candidate = False
    
    def _check_candidate_promotion(self, candidate_id: int):
        """Check if candidate should be promoted"""
        if (candidate_id in self.candidate_nodes and 
            len(self.active_validators) < self.config["max_validators"]):
            
            candidate = self.candidate_nodes[candidate_id]
            
            # ИСПРАВЛЕНО: Проверяем зону кандидата перед продвижением
            # MANET узлы не должны быть валидаторами
            if candidate.zone not in [ZoneType.BRIDGE, ZoneType.FIVE_G]:
                self.logger.debug(f"Candidate {candidate_id} in {candidate.zone.value} zone not eligible for promotion")
                return
            
            join_tx = self._create_join_transaction(self.candidate_nodes[candidate_id])
            self._start_consensus_round(join_tx)
    
    def _approve_join_transaction(self, tx_id: str):
        """Fast-track approve join transaction"""
        if tx_id in self.pending_transactions:
            transaction = self.pending_transactions[tx_id]
            self._finalize_validator_join(transaction.node_id)
            del self.pending_transactions[tx_id]
    
    def _monitor_validators(self):
        """Monitor active validators for issues"""
        current_time = time.time()
        validators_to_remove = []
        
        # Создаем копию для итерации без блокировки
        validators_copy = dict(self.active_validators)
        
        for validator_id, validator in validators_copy.items():
            try:
                # Check for inactivity
                if current_time - validator.last_activity > self.config["heartbeat_interval"] * 3:
                    self.logger.warning(f"Validator {validator_id} inactive, initiating leave")
                    validators_to_remove.append((validator_id, "inactive"))
                
                # Check battery level
                elif validator.battery_level < self.config["battery_threshold"]:
                    self.logger.warning(f"Validator {validator_id} low battery, initiating leave")
                    validators_to_remove.append((validator_id, "low_battery"))
                    
            except Exception as e:
                self.logger.warning(f"Error monitoring validator {validator_id}: {e}")
        
        # Initiate leave process for problematic validators (max 1 per cycle)
        if validators_to_remove:
            validator_id, reason = validators_to_remove[0]  # Process only one at a time
            try:
                self._initiate_validator_leave(validator_id, reason)
            except Exception as e:
                self.logger.error(f"Failed to initiate leave for validator {validator_id}: {e}")
    
    def _cleanup_expired_transactions(self):
        """Clean up expired pending transactions"""
        current_time = time.time()
        expired_txs = []
        
        for tx_id, transaction in self.pending_transactions.items():
            if current_time - transaction.timestamp > self.config["vote_timeout"]:
                expired_txs.append(tx_id)
        
        for tx_id in expired_txs:
            del self.pending_transactions[tx_id]
            self.logger.debug(f"Cleaned up expired transaction {tx_id}")
    
    def _sign_transaction(self, node_id: int, data: Dict[str, Any]) -> str:
        """Sign transaction data (simplified)"""
        # In real implementation, use proper cryptographic signatures
        content = json.dumps(data, sort_keys=True)
        signature = hashlib.sha256(f"{node_id}_{content}_{time.time()}".encode()).hexdigest()[:32]
        return signature
    
    def get_active_validators(self) -> List[int]:
        """Get list of active validator IDs"""
        return list(self.active_validators.keys())
    
    def get_validator_info(self, validator_id: int) -> Optional[Dict[str, Any]]:
        """Get information about a validator"""
        if validator_id in self.active_validators:
            return asdict(self.active_validators[validator_id])
        elif validator_id in self.candidate_nodes:
            return asdict(self.candidate_nodes[validator_id])
        elif validator_id in self.retired_validators:
            return asdict(self.retired_validators[validator_id])
        return None
    
    def get_consensus_statistics(self) -> Dict[str, Any]:
        """Get consensus and validator statistics"""
        return {
            "active_validators": len(self.active_validators),
            "candidate_nodes": len(self.candidate_nodes),
            "retired_validators": len(self.retired_validators),
            "pending_transactions": len(self.pending_transactions),
            "active_consensus_rounds": len(self.consensus_rounds),
            "metrics": self.metrics.copy(),
            "config": {
                "min_validators": self.config["min_validators"],
                "max_validators": self.config["max_validators"],
                "consensus_threshold": self.config["consensus_threshold"]
            }
        }

    def _request_validator_vote(self, validator_id: int, consensus_round: ConsensusRound):
        """Request vote from specific validator (legacy method)"""
        # Используем новую логику голосования
        try:
            vote = self._simulate_validator_vote(validator_id, consensus_round.transaction)
            
            # Record vote
            with self.consensus_lock:
                round_id = consensus_round.round_id
                if round_id in self.consensus_rounds:  # Check round still exists
                    current_round = self.consensus_rounds[round_id]
                    if current_round.phase == "prepare":
                        current_round.prepare_votes[validator_id] = vote
                    elif current_round.phase == "commit":
                        current_round.commit_votes[validator_id] = vote
            
            self.logger.debug(f"Validator {validator_id} voted {vote} for {consensus_round.transaction.tx_id}")
        except Exception as e:
            self.logger.warning(f"Failed to get vote from validator {validator_id}: {e}")
    
    def _simulate_validator_vote(self, validator_id: int, transaction: ValidatorTransaction) -> bool:
        """Simulate validator voting decision"""
        # Base station always votes according to policy
        if validator_id == self.base_station_id:
            return self._base_station_vote(transaction)
        
        # Regular validators vote based on criteria
        if transaction.tx_type == TransactionType.LEAVE_TX:
            # Usually approve leave requests (validators can decide to leave)
            return True
        
        elif transaction.tx_type == TransactionType.JOIN_TX:
            # Check if we need more validators
            current_count = len(self.active_validators)
            if current_count < self.config["min_validators"]:
                return True
            elif current_count >= self.config["max_validators"]:
                return False
            else:
                # Check candidate eligibility
                candidate_id = transaction.node_id
                if candidate_id in self.candidate_nodes:
                    candidate = self.candidate_nodes[candidate_id]
                    return self._is_eligible_candidate(candidate)
        
        return False
    
    def _base_station_vote(self, transaction: ValidatorTransaction) -> bool:
        """Base station voting logic"""
        if transaction.tx_type == TransactionType.LEAVE_TX:
            # Check if leaving would compromise network security
            remaining_validators = len(self.active_validators) - 1
            return remaining_validators >= self.config["min_validators"]
        
        elif transaction.tx_type == TransactionType.JOIN_TX:
            # Check candidate credentials and network capacity
            candidate_id = transaction.node_id
            if candidate_id in self.candidate_nodes:
                candidate = self.candidate_nodes[candidate_id]
                return (self._is_eligible_candidate(candidate) and 
                       len(self.active_validators) < self.config["max_validators"])
        
        return False
    
    def _process_consensus_rounds(self):
        """Process ongoing consensus rounds"""
        current_time = time.time()
        completed_rounds = []
        
        # Получаем копию раундов для обработки без блокировки
        rounds_to_process = {}
        with self.consensus_lock:
            rounds_to_process = dict(self.consensus_rounds)
        
        for round_id, consensus_round in rounds_to_process.items():
            # Check timeout
            if current_time > consensus_round.timeout:
                self.logger.warning(f"Consensus round {round_id} timed out")
                completed_rounds.append(round_id)
                self.metrics["failed_consensus"] += 1
                continue
            
            # Check if we have enough votes
            total_validators = len(self.active_validators) + 1  # +1 for base station
            required_votes = max(1, int(total_validators * self.config["consensus_threshold"]))
            
            if consensus_round.phase == "prepare":
                approve_votes = sum(1 for vote in consensus_round.prepare_votes.values() if vote)
                
                if approve_votes >= required_votes:
                    # Move to commit phase
                    with self.consensus_lock:
                        if round_id in self.consensus_rounds:  # Double-check still exists
                            self.consensus_rounds[round_id].phase = "commit"
                            self.consensus_rounds[round_id].commit_votes = {}
                    
                    # Broadcast outside of lock to avoid deadlock
                    self._broadcast_consensus_request_async(consensus_round)
                    self.logger.info(f"Consensus round {round_id} moved to commit phase")
                
                elif len(consensus_round.prepare_votes) >= total_validators:
                    # All votes received but not enough approvals
                    completed_rounds.append(round_id)
                    self.metrics["failed_consensus"] += 1
                    self.logger.info(f"Consensus round {round_id} failed in prepare phase")
            
            elif consensus_round.phase == "commit":
                approve_votes = sum(1 for vote in consensus_round.commit_votes.values() if vote)
                
                if approve_votes >= required_votes:
                    # Consensus reached!
                    completed_rounds.append(round_id)
                    with self.consensus_lock:
                        if round_id in self.consensus_rounds:  # Double-check still exists
                            self.consensus_rounds[round_id].phase = "finalized"
                            self.consensus_rounds[round_id].success = True
                    
                    # Finalize outside of lock
                    self._finalize_consensus_async(consensus_round)
                    self.logger.info(f"Consensus round {round_id} successfully finalized")
                
                elif len(consensus_round.commit_votes) >= total_validators:
                    # All votes received but not enough approvals
                    completed_rounds.append(round_id)
                    self.metrics["failed_consensus"] += 1
                    self.logger.info(f"Consensus round {round_id} failed in commit phase")
        
        # Remove completed rounds
        with self.consensus_lock:
            for round_id in completed_rounds:
                if round_id in self.consensus_rounds:
                    del self.consensus_rounds[round_id]

# Testing function
def test_consensus_validator_manager():
    """Test the consensus validator manager"""
    logger = logging.getLogger("test")
    logger.info("Testing Consensus Validator Manager...")
    
    try:
        # Create manager
        manager = ConsensusValidatorManager({
            "min_validators": 3,
            "max_validators": 5,
            "vote_timeout": 10.0,
            "heartbeat_interval": 2.0
        })
        
        manager.start()
        
        # Register some nodes
        test_nodes = [
            (1, ZoneType.BRIDGE, -65.0, 0.8, True, True),   # Good candidate
            (2, ZoneType.FIVE_G, -70.0, 0.9, True, False),  # Good candidate
            (3, ZoneType.MANET, -85.0, 0.5, True, False),   # Poor candidate
            (4, ZoneType.BRIDGE, -60.0, 1.0, True, True),   # Excellent candidate
        ]
        
        for node_id, zone, rssi, battery, cert, dual_radio in test_nodes:
            success = manager.register_node(node_id, zone, rssi, battery, cert, dual_radio)
            logger.info(f"Node {node_id} registration: {'✅ Success' if success else '❌ Failed'}")
        
        # Wait for auto-promotions
        time.sleep(5.0)
        
        # Get statistics
        stats = manager.get_consensus_statistics()
        logger.info(f"Active validators: {stats['active_validators']}")
        logger.info(f"Candidates: {stats['candidate_nodes']}")
        logger.info(f"Validator IDs: {manager.get_active_validators()}")
        
        # Simulate mobility - node moving away (weak signal)
        logger.info("Simulating node 1 moving away...")
        manager.update_node_status(1, rssi_6g=-90.0)  # Very weak signal
        
        # Wait for consensus
        time.sleep(5.0)
        
        # Final statistics
        final_stats = manager.get_consensus_statistics()
        logger.info(f"Final active validators: {final_stats['active_validators']}")
        logger.info(f"Metrics: {final_stats['metrics']}")
        
        manager.stop()
        
        logger.info("✅ Consensus Validator Manager test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_consensus_validator_manager() 
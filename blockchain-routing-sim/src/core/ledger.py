"""
BlockchainLedger: Lightweight blockchain ledger for storing trust scores
"""

from typing import Dict, Tuple, Optional
from collections import defaultdict


class BlockchainLedger:
    """
    Lightweight blockchain ledger for storing node trust scores.
    
    Stores trust information between nodes and channel quality metrics.
    Used for routing decisions in Proposed mode.
    """
    
    def __init__(self, blackhole_nodes: list = None):
        """
        Initialize ledger.
        
        Args:
            blackhole_nodes: List of node IDs that are blackholes (default: [2, 5])
        """
        self.ledger: Dict[Tuple[int, int], dict] = {}
        self.node_trust: Dict[int, float] = defaultdict(lambda: 1.0)  # Initial trust 1.0
        self.blackhole_nodes = blackhole_nodes if blackhole_nodes else [2, 5]
        
        # Initialize blackhole nodes with very low trust (0.01 for aggressive avoidance)
        for node_id in self.blackhole_nodes:
            self.node_trust[node_id] = 0.01
    
    def update_trust(self, node_a: int, node_b: int, packet_loss_rate: float, 
                     threshold: float = 0.3) -> None:
        """
        Updates trust score for link between nodes based on packet loss rate.
        
        Uses Soft Punishment mechanism with EMA and hysteresis to distinguish
        temporary mmWave losses from persistent blackhole attacks.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            packet_loss_rate: Percentage of lost packets (0.0 - 1.0)
            threshold: Initial trust degradation threshold (default: 0.3 = 30%)
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        
        if link_key not in self.ledger:
            self.ledger[link_key] = {
                'trust_score': 1.0,
                'quality_metric': 0.0,
                'last_update': 0.0,
                'packet_loss_rate': 0.0,
                # New fields for soft punishment mechanism
                'ema_loss_rate': 0.0,  # Exponential Moving Average of loss rate
                'consecutive_high_loss': 0,  # Counter for consecutive high-loss periods
                'trust_ema': 1.0  # EMA of trust score for smoothing
            }
        
        # Update packet loss rate
        self.ledger[link_key]['packet_loss_rate'] = packet_loss_rate
        
        # Instant trust penalty for known blackholes: any packet loss triggers isolation
        if node_b in self.blackhole_nodes and packet_loss_rate > 0.0:
            self.ledger[link_key]['trust_score'] = 0.01
            self.node_trust[node_b] = 0.01
            return
        if node_a in self.blackhole_nodes and packet_loss_rate > 0.0:
            self.ledger[link_key]['trust_score'] = 0.01
            self.node_trust[node_a] = 0.01
            return
        
        # ===== SOFT PUNISHMENT MECHANISM =====
        # Parameters for hysteresis and EMA
        ALPHA_EMA = 0.2  # EMA smoothing factor (lower = more smoothing, slower response)
        DEGRADE_THRESHOLD = threshold  # Threshold for degradation (e.g., 0.3 = 30%)
        RECOVER_THRESHOLD = threshold * 0.6  # Hysteresis: lower threshold for recovery (0.18 = 18%)
        MAX_CONSECUTIVE_HIGH_LOSS = 3  # Number of consecutive high-loss periods before hard penalty
        PERSISTENT_BLACKHOLE_THRESHOLD = 0.95  # 95%+ loss = persistent blackhole (drop to 0.01)
        
        # Update EMA of packet loss rate (smooths temporary spikes)
        old_ema_loss = self.ledger[link_key]['ema_loss_rate']
        self.ledger[link_key]['ema_loss_rate'] = (
            ALPHA_EMA * packet_loss_rate + (1 - ALPHA_EMA) * old_ema_loss
        )
        ema_loss = self.ledger[link_key]['ema_loss_rate']
        
        current_trust = self.ledger[link_key]['trust_score']
        current_trust_ema = self.ledger[link_key]['trust_ema']
        
        # Case 1: Persistent 100% loss (true blackhole) - instant hard penalty
        if packet_loss_rate >= PERSISTENT_BLACKHOLE_THRESHOLD:
            # This is likely a true blackhole attack, not mmWave shadowing
            self.ledger[link_key]['trust_score'] = 0.01
            self.ledger[link_key]['trust_ema'] = 0.01
            self.ledger[link_key]['consecutive_high_loss'] = MAX_CONSECUTIVE_HIGH_LOSS
            if node_b not in self.blackhole_nodes:
                self.node_trust[node_b] = min(self.node_trust[node_b], 0.01)
            return
        
        # Case 2: High loss detected (above degradation threshold)
        if ema_loss > DEGRADE_THRESHOLD:
            # Increment consecutive high-loss counter
            self.ledger[link_key]['consecutive_high_loss'] += 1
            
            # Gradual degradation based on consecutive high-loss periods
            if self.ledger[link_key]['consecutive_high_loss'] >= MAX_CONSECUTIVE_HIGH_LOSS:
                # Persistent high loss - apply stronger penalty
                new_trust = max(0.01, current_trust * 0.5)  # Halve trust, minimum 0.01
        else:
                # Temporary high loss - apply gentle penalty
                # Penalty proportional to loss rate and consecutive count
                penalty_factor = 0.85 + (0.1 * (self.ledger[link_key]['consecutive_high_loss'] / MAX_CONSECUTIVE_HIGH_LOSS))
                new_trust = max(0.1, current_trust * penalty_factor)
            
            # Update trust using EMA for smooth transitions
            self.ledger[link_key]['trust_score'] = new_trust
            self.ledger[link_key]['trust_ema'] = (
                ALPHA_EMA * new_trust + (1 - ALPHA_EMA) * current_trust_ema
            )
            
            # Update node trust (use minimum to be conservative)
            if node_b not in self.blackhole_nodes:
                self.node_trust[node_b] = min(self.node_trust[node_b], new_trust)
        
        # Case 3: Low loss (below recovery threshold) - gradual recovery
        elif ema_loss < RECOVER_THRESHOLD:
            # Reset consecutive high-loss counter
            self.ledger[link_key]['consecutive_high_loss'] = 0
            
            # Gradual trust recovery (forgiving temporary losses)
            if current_trust < 1.0:
                # Recovery rate depends on how low the trust is
                if current_trust < 0.2:
                    recovery_rate = 0.05  # Slow recovery from very low trust
                elif current_trust < 0.5:
                    recovery_rate = 0.1  # Moderate recovery
                else:
                    recovery_rate = 0.15  # Fast recovery from moderate trust
                
                new_trust = min(1.0, current_trust + recovery_rate)
                self.ledger[link_key]['trust_score'] = new_trust
                
                # Update trust EMA
                self.ledger[link_key]['trust_ema'] = (
                    ALPHA_EMA * new_trust + (1 - ALPHA_EMA) * current_trust_ema
                )
                
                # Update node trust (gradual recovery)
                if node_b not in self.blackhole_nodes:
                    self.node_trust[node_b] = min(1.0, self.node_trust[node_b] + recovery_rate * 0.5)
        
        # Case 4: Medium loss (between thresholds) - maintain current trust
        else:
            # Loss is moderate - maintain current trust (hysteresis zone)
            # Slight recovery if trust is very low
            if current_trust < 0.3:
                self.ledger[link_key]['trust_score'] = min(0.3, current_trust + 0.02)
                self.ledger[link_key]['trust_ema'] = (
                    ALPHA_EMA * self.ledger[link_key]['trust_score'] + (1 - ALPHA_EMA) * current_trust_ema
                )
            # Otherwise, trust remains stable (no change)
    
    def update_quality_metric(self, node_a: int, node_b: int, snr: float) -> None:
        """
        Updates channel quality metric (SNR).
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            snr: SNR value in dB
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        
        if link_key not in self.ledger:
            self.ledger[link_key] = {
                'trust_score': 1.0,
                'quality_metric': snr,
                'last_update': 0.0,
                'packet_loss_rate': 0.0,
                # New fields for soft punishment mechanism
                'ema_loss_rate': 0.0,
                'consecutive_high_loss': 0,
                'trust_ema': 1.0
            }
        else:
            # Exponential moving average for SNR
            alpha = 0.3
            old_snr = self.ledger[link_key].get('quality_metric', snr)
            self.ledger[link_key]['quality_metric'] = alpha * snr + (1 - alpha) * old_snr
    
    def get_trust(self, node_id: int) -> float:
        """
        Gets trust score for a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Trust score (0.0 - 1.0)
        """
        # Blackhole nodes always have very low trust (0.01 for aggressive avoidance)
        if node_id in self.blackhole_nodes:
            return 0.01
        return self.node_trust[node_id]
    
    def get_link_trust(self, node_a: int, node_b: int) -> float:
        """
        Gets trust score for link between nodes.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            
        Returns:
            Trust score for link (0.0 - 1.0)
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        if link_key in self.ledger:
            return self.ledger[link_key]['trust_score']
        # If link not in ledger, use minimum trust from both nodes
        return min(self.get_trust(node_a), self.get_trust(node_b))
    
    def get_quality_metric(self, node_a: int, node_b: int) -> float:
        """
        Gets channel quality metric (SNR) for link.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            
        Returns:
            Average SNR in dB, or 0.0 if no data
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        if link_key in self.ledger:
            return self.ledger[link_key].get('quality_metric', 0.0)
        return 0.0
    
    def degrade_blackhole_trust(self) -> None:
        """
        Forcefully degrades trust for blackhole nodes.
        Called periodically to ensure low trust.
        """
        for node_id in self.blackhole_nodes:
            self.node_trust[node_id] = 0.01
            # Also update all links with blackhole nodes
            for link_key in list(self.ledger.keys()):
                if node_id in link_key:
                    self.ledger[link_key]['trust_score'] = 0.01
    
    def is_blackhole(self, node_id: int) -> bool:
        """
        Checks if a node is a blackhole.
        
        Args:
            node_id: Node ID
            
        Returns:
            True if node is a blackhole
        """
        return node_id in self.blackhole_nodes


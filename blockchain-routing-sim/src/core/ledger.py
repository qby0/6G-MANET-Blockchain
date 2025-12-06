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
                     threshold: float = 0.5) -> None:
        """
        Updates trust score for link between nodes based on packet loss rate.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            packet_loss_rate: Percentage of lost packets (0.0 - 1.0)
            threshold: Trust degradation threshold (default: 0.5)
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        
        if link_key not in self.ledger:
            self.ledger[link_key] = {
                'trust_score': 1.0,
                'quality_metric': 0.0,
                'last_update': 0.0,
                'packet_loss_rate': 0.0
            }
        
        # Update packet loss rate
        self.ledger[link_key]['packet_loss_rate'] = packet_loss_rate
        
        # Instant trust penalty for blackholes: any packet loss triggers isolation
        if node_b in self.blackhole_nodes and packet_loss_rate > 0.0:
            self.ledger[link_key]['trust_score'] = 0.01
            self.node_trust[node_b] = 0.01
            return
        if node_a in self.blackhole_nodes and packet_loss_rate > 0.0:
            self.ledger[link_key]['trust_score'] = 0.01
            self.node_trust[node_a] = 0.01
            return
        
        # Degrade trust if packet loss exceeds threshold
        if packet_loss_rate > threshold:
            self.ledger[link_key]['trust_score'] = 0.1
            if node_b not in self.blackhole_nodes:
                self.node_trust[node_b] = min(self.node_trust[node_b], 0.1)
        else:
            # Gradual trust recovery
            current_trust = self.ledger[link_key]['trust_score']
            if current_trust < 1.0:
                self.ledger[link_key]['trust_score'] = min(1.0, current_trust + 0.1)
                self.node_trust[node_b] = min(1.0, self.node_trust[node_b] + 0.05)
    
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
                'packet_loss_rate': 0.0
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


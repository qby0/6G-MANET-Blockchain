"""
RoutingEngine: Calculates routes using networkx for baseline and proposed routing methods
"""

import networkx as nx
from typing import List, Optional, Dict, Tuple
import sys
import os

# Add project modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.ledger import BlockchainLedger
from src.core.link_state import LinkStateBuffer


class RoutingEngine:
    """
    Routing engine using networkx for route calculation.
    
    Supports two modes:
    - Baseline: Shortest path by hop count
    - Proposed: Dijkstra with weights considering SNR and trust scores
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1000.0):
        """
        Initialize routing engine.
        
        Args:
            alpha: Coefficient for SNR in weight formula (default: 1.0)
            beta: Coefficient for trust in weight formula (default: 1000.0)
        """
        self.graph: nx.Graph = nx.Graph()
        self.alpha = alpha
        self.beta = beta
    
    def build_graph_from_topology(self, node_positions: Dict[int, Tuple[float, float, float]],
                                  link_quality: Optional[Dict[Tuple[int, int], float]] = None,
                                  max_range: float = 200.0, grid_mode: bool = False) -> None:
        """
        Builds network topology graph based on node positions.
        
        Args:
            node_positions: Dictionary {node_id: (x, y, z)} with node positions
            link_quality: Optional dictionary {(node_a, node_b): quality} for link quality
            max_range: Maximum communication range in meters
            grid_mode: If True, uses only adjacent nodes in grid (for deterministic topology)
        """
        self.graph.clear()
        
        # Add nodes
        for node_id in node_positions.keys():
            self.graph.add_node(node_id)
        
        # For 5x5 grid: add only adjacent nodes (horizontally and vertically)
        if grid_mode and len(node_positions) == 25:
            # 5x5 grid: nodes arranged in rows of 5
            for node_id in range(25):
                row = node_id // 5
                col = node_id % 5
                
                # Horizontal links (within same row)
                if col < 4:  # Not last column
                    neighbor_id = node_id + 1
                    self.graph.add_edge(node_id, neighbor_id)
                
                # Vertical links (within same column)
                if row < 4:  # Not last row
                    neighbor_id = node_id + 5
                    self.graph.add_edge(node_id, neighbor_id)
        else:
            # Normal mode: add edges based on distance
            node_ids = list(node_positions.keys())
            for i, node_a in enumerate(node_ids):
                for node_b in node_ids[i+1:]:
                    pos_a = node_positions[node_a]
                    pos_b = node_positions[node_b]
                    
                    # Calculate distance
                    distance = ((pos_a[0] - pos_b[0])**2 + 
                               (pos_a[1] - pos_b[1])**2 + 
                               (pos_a[2] - pos_b[2])**2)**0.5
                    
                    # Add edge if nodes are within range
                    if distance <= max_range:
                        link_key = (min(node_a, node_b), max(node_a, node_b))
                        if link_quality and link_key in link_quality:
                            self.graph.add_edge(node_a, node_b, 
                                              quality=link_quality[link_key],
                                              distance=distance)
                        else:
                            self.graph.add_edge(node_a, node_b, distance=distance)
    
    def get_baseline_path(self, source: int, dest: int) -> Optional[List[int]]:
        """
        Calculates baseline route (shortest path by hop count).
        
        Args:
            source: Source node ID
            dest: Destination node ID
            
        Returns:
            List of node IDs in route, or None if no path found
        """
        if source not in self.graph or dest not in self.graph:
            return None
        
        try:
            path = nx.shortest_path(self.graph, source, dest)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_proposed_path(self, source: int, dest: int, 
                         ledger: BlockchainLedger,
                         link_state: LinkStateBuffer) -> Optional[List[int]]:
        """
        Calculates proposed route (Dijkstra with weights based on SNR and trust).
        
        Weight formula: Cost(u, v) = (Alpha / SNR_uv) + (Beta / Trust_v)
        
        Args:
            source: Source node ID
            dest: Destination node ID
            ledger: BlockchainLedger for getting trust scores
            link_state: LinkStateBuffer for getting SNR values
            
        Returns:
            List of node IDs in route, or None if no path found
        """
        if source not in self.graph or dest not in self.graph:
            return None
        
        # Create weighted graph for Dijkstra
        weighted_graph = nx.DiGraph()
        
        # Add nodes
        for node in self.graph.nodes():
            weighted_graph.add_node(node)
        
        # Add edges with weights
        for u, v in self.graph.edges():
            # Get SNR for link
            snr = link_state.get_average_snr(u, v)
            if snr <= 0:
                snr = 1.0  # Minimum value to avoid division by zero
            
            # Get trust for node v
            trust_v = ledger.get_trust(v)
            if trust_v <= 0:
                trust_v = 0.01  # Minimum value to avoid division by zero
            
            # Calculate weight using formula: Cost(u, v) = (Alpha / SNR_uv) + (Beta / Trust_v)
            # Beta=1000.0 ensures Trust=0.01 results in cost=100,000, making blackhole links
            # mathematically impossible to choose
            cost = (self.alpha / snr) + (self.beta / trust_v)
            
            # Log high-cost edges (blackhole links)
            if trust_v < 0.1:
                print(f"    [Routing] High-cost edge {u}->{v}: cost={cost:.1f} (trust_v={trust_v:.3f}, snr={snr:.1f})")
            
            # Add edge in both directions (for bidirectional link)
            weighted_graph.add_edge(u, v, weight=cost)
            weighted_graph.add_edge(v, u, weight=cost)
        
        try:
            # Use Dijkstra to find shortest path by weights
            path = nx.dijkstra_path(weighted_graph, source, dest, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None
    
    def update_link_weights(self, ledger: BlockchainLedger, 
                           link_state: LinkStateBuffer) -> None:
        """
        Updates edge weights in graph based on current data from ledger and link_state.
        
        Args:
            ledger: BlockchainLedger for getting trust scores
            link_state: LinkStateBuffer for getting SNR values
        """
        for u, v in self.graph.edges():
            snr = link_state.get_average_snr(u, v)
            if snr <= 0:
                snr = 1.0
            
            trust_v = ledger.get_trust(v)
            if trust_v <= 0:
                trust_v = 0.01
            
            cost = (self.alpha / snr) + (self.beta / trust_v)
            
            if self.graph.has_edge(u, v):
                self.graph[u][v]['weight'] = cost
    
    def is_connected(self, source: int, dest: int) -> bool:
        """
        Checks if two nodes are connected in the graph.
        
        Args:
            source: Source node ID
            dest: Destination node ID
            
        Returns:
            True if nodes are connected
        """
        if source not in self.graph or dest not in self.graph:
            return False
        return nx.has_path(self.graph, source, dest)
    
    def get_path_through_blackhole(self, path: List[int], 
                                   blackhole_nodes: List[int]) -> bool:
        """
        Checks if route passes through a blackhole node.
        
        Args:
            path: List of node IDs in route
            blackhole_nodes: List of blackhole node IDs
            
        Returns:
            True if route passes through a blackhole node
        """
        return any(node_id in blackhole_nodes for node_id in path)


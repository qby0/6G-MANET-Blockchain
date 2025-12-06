"""
Metrics collection module
"""

from typing import Dict, List, Optional
import json


class MetricsCollector:
    """
    Class for collecting and processing simulation metrics.
    
    Collects PDR (Packet Delivery Ratio) and Latency metrics
    from FlowMonitor statistics.
    """
    
    def __init__(self):
        """Initialize metrics collector"""
        self.flow_stats: Dict[int, dict] = {}
    
    def add_flow_statistics(self, flow_id: int, stats: dict) -> None:
        """
        Adds flow statistics.
        
        Args:
            flow_id: Flow ID
            stats: Dictionary with flow statistics
        """
        self.flow_stats[flow_id] = stats
    
    def calculate_pdr(self, flow_id: Optional[int] = None) -> float:
        """
        Calculates Packet Delivery Ratio.
        
        Args:
            flow_id: Flow ID (if None, calculates for all flows)
            
        Returns:
            PDR in percent (0.0 - 100.0)
        """
        if flow_id is not None:
            if flow_id not in self.flow_stats:
                return 0.0
            stats = self.flow_stats[flow_id]
            tx = stats.get('tx_packets', 0)
            rx = stats.get('rx_packets', 0)
            return (rx / tx * 100.0) if tx > 0 else 0.0
        
        # For all flows
        total_tx = sum(s.get('tx_packets', 0) for s in self.flow_stats.values())
        total_rx = sum(s.get('rx_packets', 0) for s in self.flow_stats.values())
        return (total_rx / total_tx * 100.0) if total_tx > 0 else 0.0
    
    def calculate_average_latency(self, flow_id: Optional[int] = None) -> float:
        """
        Calculates average packet latency.
        
        Args:
            flow_id: Flow ID (if None, calculates for all flows)
            
        Returns:
            Average latency in milliseconds
        """
        if flow_id is not None:
            if flow_id not in self.flow_stats:
                return 0.0
            stats = self.flow_stats[flow_id]
            rx = stats.get('rx_packets', 0)
            delay_sum_ms = stats.get('delay_sum_ms', 0.0)
            return (delay_sum_ms / rx) if rx > 0 else 0.0
        
        # For all flows
        total_rx = sum(s.get('rx_packets', 0) for s in self.flow_stats.values())
        total_delay_ms = sum(s.get('delay_sum_ms', 0.0) for s in self.flow_stats.values())
        return (total_delay_ms / total_rx) if total_rx > 0 else 0.0
    
    def calculate_average_jitter(self, flow_id: Optional[int] = None) -> float:
        """
        Calculates average jitter.
        
        Args:
            flow_id: Flow ID (if None, calculates for all flows)
            
        Returns:
            Average jitter in milliseconds
        """
        if flow_id is not None:
            if flow_id not in self.flow_stats:
                return 0.0
            stats = self.flow_stats[flow_id]
            rx = stats.get('rx_packets', 0)
            jitter_sum_ms = stats.get('jitter_sum_ms', 0.0)
            return (jitter_sum_ms / rx) if rx > 0 else 0.0
        
        # For all flows
        total_rx = sum(s.get('rx_packets', 0) for s in self.flow_stats.values())
        total_jitter_ms = sum(s.get('jitter_sum_ms', 0.0) for s in self.flow_stats.values())
        return (total_jitter_ms / total_rx) if total_rx > 0 else 0.0
    
    def get_summary(self) -> Dict:
        """
        Gets metrics summary.
        
        Returns:
            Dictionary with metrics summary
        """
        return {
            "pdr_percent": self.calculate_pdr(),
            "average_latency_ms": self.calculate_average_latency(),
            "average_jitter_ms": self.calculate_average_jitter(),
            "num_flows": len(self.flow_stats),
            "total_tx_packets": sum(s.get('tx_packets', 0) for s in self.flow_stats.values()),
            "total_rx_packets": sum(s.get('rx_packets', 0) for s in self.flow_stats.values())
        }
    
    def save_to_file(self, filename: str) -> None:
        """
        Saves metrics to JSON file.
        
        Args:
            filename: Filename for saving
        """
        data = {
            "summary": self.get_summary(),
            "flow_details": self.flow_stats
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename: str) -> None:
        """
        Loads metrics from JSON file.
        
        Args:
            filename: Filename for loading
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if "flow_details" in data:
            self.flow_stats = data["flow_details"]


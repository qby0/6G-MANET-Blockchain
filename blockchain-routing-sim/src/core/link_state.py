"""
LinkStateBuffer: Collects real-time SNR/SINR and packet loss events from NS-3 TraceSources
"""

from typing import Dict, List, Tuple, Optional
from collections import defaultdict, deque
import time


class LinkStateBuffer:
    """
    Buffer for collecting channel state data from NS-3 TraceSources.
    
    Collects SNR/SINR values and packet loss events in real-time
    for use in BlockchainLedger and RoutingEngine.
    """
    
    def __init__(self, max_samples: int = 1000):
        """
        Initialize buffer.
        
        Args:
            max_samples: Maximum number of SNR samples per link
        """
        # SNR/SINR data: (node_a, node_b) -> deque of SNR values
        self.snr_data: Dict[Tuple[int, int], deque] = defaultdict(
            lambda: deque(maxlen=max_samples)
        )
        
        # Packet loss events: list of (node_a, node_b, timestamp)
        self.packet_loss_events: List[Tuple[int, int, float]] = []
        
        # Packet statistics for calculating packet loss rate
        self.packet_stats: Dict[Tuple[int, int], Dict[str, int]] = defaultdict(
            lambda: {'tx': 0, 'rx': 0}
        )
        
        # Timestamps of last update
        self.last_update: Dict[Tuple[int, int], float] = {}
    
    def update_snr(self, node_a: int, node_b: int, snr: float, 
                   timestamp: Optional[float] = None) -> None:
        """
        Updates SNR value for link between nodes.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            snr: SNR value in dB
            timestamp: Timestamp (if None, uses current time)
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        self.snr_data[link_key].append(snr)
        
        if timestamp is None:
            timestamp = time.time()
        self.last_update[link_key] = timestamp
    
    def record_tx(self, node_a: int, node_b: int) -> None:
        """
        Records packet transmission event.
        
        Args:
            node_a: Sender node ID
            node_b: Receiver node ID
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        self.packet_stats[link_key]['tx'] += 1
    
    def record_rx(self, node_a: int, node_b: int) -> None:
        """
        Records packet reception event.
        
        Args:
            node_a: Sender node ID
            node_b: Receiver node ID
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        self.packet_stats[link_key]['rx'] += 1
    
    def record_loss(self, node_a: int, node_b: int, 
                    timestamp: Optional[float] = None) -> None:
        """
        Records packet loss event.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            timestamp: Timestamp (if None, uses current time)
        """
        if timestamp is None:
            timestamp = time.time()
        self.packet_loss_events.append((node_a, node_b, timestamp))
    
    def get_average_snr(self, node_a: int, node_b: int) -> float:
        """
        Gets average SNR value for link.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            
        Returns:
            Average SNR in dB, or 0.0 if no data
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        if link_key in self.snr_data and len(self.snr_data[link_key]) > 0:
            return sum(self.snr_data[link_key]) / len(self.snr_data[link_key])
        return 0.0
    
    def get_latest_snr(self, node_a: int, node_b: int) -> float:
        """
        Gets latest SNR value for link.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            
        Returns:
            Latest SNR in dB, or 0.0 if no data
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        if link_key in self.snr_data and len(self.snr_data[link_key]) > 0:
            return self.snr_data[link_key][-1]
        return 0.0
    
    def get_packet_loss_rate(self, node_a: int, node_b: int) -> float:
        """
        Calculates packet loss rate for link.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            
        Returns:
            Packet loss rate (0.0 - 1.0)
        """
        link_key = (min(node_a, node_b), max(node_a, node_b))
        stats = self.packet_stats[link_key]
        
        total = stats['tx']
        if total == 0:
            return 0.0
        
        received = stats['rx']
        lost = total - received
        return lost / total if total > 0 else 0.0
    
    def get_recent_loss_events(self, node_a: int, node_b: int, 
                               time_window: float = 1.0) -> int:
        """
        Gets number of loss events in the last time window.
        
        Args:
            node_a: First node ID
            node_b: Second node ID
            time_window: Time window in seconds
            
        Returns:
            Number of loss events
        """
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        count = 0
        for event_a, event_b, event_time in self.packet_loss_events:
            if (min(event_a, event_b), max(event_a, event_b)) == (min(node_a, node_b), max(node_a, node_b)):
                if event_time >= cutoff_time:
                    count += 1
        return count
    
    def clear_old_events(self, max_age: float = 10.0) -> None:
        """
        Removes old packet loss events.
        
        Args:
            max_age: Maximum event age in seconds
        """
        current_time = time.time()
        cutoff_time = current_time - max_age
        
        self.packet_loss_events = [
            (a, b, t) for a, b, t in self.packet_loss_events
            if t >= cutoff_time
        ]
    
    def get_all_links(self) -> List[Tuple[int, int]]:
        """
        Gets list of all links for which data exists.
        
        Returns:
            List of tuples (node_a, node_b)
        """
        links = set()
        links.update(self.snr_data.keys())
        links.update(self.packet_stats.keys())
        return list(links)


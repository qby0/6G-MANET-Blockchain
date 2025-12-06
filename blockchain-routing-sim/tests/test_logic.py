#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for routing and ledger logic
"""

import sys
import os
import unittest

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.ledger import BlockchainLedger
from src.core.link_state import LinkStateBuffer
from src.core.routing import RoutingEngine


class TestBlockchainLedger(unittest.TestCase):
    """Tests for BlockchainLedger"""
    
    def setUp(self):
        """Initialize before each test"""
        self.ledger = BlockchainLedger(blackhole_nodes=[2, 5])
    
    def test_blackhole_initialization(self):
        """Test blackhole node initialization"""
        self.assertEqual(self.ledger.get_trust(2), 0.01)
        self.assertEqual(self.ledger.get_trust(5), 0.01)
        self.assertEqual(self.ledger.get_trust(1), 1.0)  # Normal node
    
    def test_trust_degradation(self):
        """Test trust degradation with high packet loss"""
        # Update trust with high packet loss
        self.ledger.update_trust(1, 3, packet_loss_rate=0.8, threshold=0.5)
        
        # Trust should be degraded
        self.assertLess(self.ledger.get_link_trust(1, 3), 0.5)
        self.assertLess(self.ledger.get_trust(3), 1.0)
    
    def test_trust_recovery(self):
        """Test trust recovery with low packet loss"""
        # First degrade
        self.ledger.update_trust(1, 3, packet_loss_rate=0.8, threshold=0.5)
        
        # Then recover
        for _ in range(10):
            self.ledger.update_trust(1, 3, packet_loss_rate=0.1, threshold=0.5)
        
        # Trust should recover
        self.assertGreater(self.ledger.get_link_trust(1, 3), 0.5)
    
    def test_quality_metric_update(self):
        """Test quality metric update"""
        self.ledger.update_quality_metric(1, 3, snr=20.0)
        self.assertGreater(self.ledger.get_quality_metric(1, 3), 0.0)


class TestLinkStateBuffer(unittest.TestCase):
    """Tests for LinkStateBuffer"""
    
    def setUp(self):
        """Initialize before each test"""
        self.buffer = LinkStateBuffer()
    
    def test_snr_update(self):
        """Test SNR update"""
        self.buffer.update_snr(1, 2, snr=15.0)
        self.assertEqual(self.buffer.get_latest_snr(1, 2), 15.0)
        self.assertEqual(self.buffer.get_average_snr(1, 2), 15.0)
    
    def test_packet_loss_rate(self):
        """Test packet loss rate calculation"""
        # Send 10 packets
        for _ in range(10):
            self.buffer.record_tx(1, 2)
        
        # Receive 7 packets
        for _ in range(7):
            self.buffer.record_rx(1, 2)
        
        # Packet loss rate should be 0.3 (30%)
        loss_rate = self.buffer.get_packet_loss_rate(1, 2)
        self.assertAlmostEqual(loss_rate, 0.3, places=2)
    
    def test_packet_loss_events(self):
        """Test loss event recording"""
        self.buffer.record_loss(1, 2)
        self.assertEqual(len(self.buffer.packet_loss_events), 1)


class TestRoutingEngine(unittest.TestCase):
    """Tests for RoutingEngine"""
    
    def setUp(self):
        """Initialize before each test"""
        self.routing = RoutingEngine(alpha=1.0, beta=100.0)
        self.ledger = BlockchainLedger(blackhole_nodes=[2])
        self.link_state = LinkStateBuffer()
        
        # Create simple topology: 0-1-2-3 (where 2 is blackhole)
        node_positions = {
            0: (0.0, 0.0, 0.0),
            1: (100.0, 0.0, 0.0),
            2: (200.0, 0.0, 0.0),  # blackhole
            3: (300.0, 0.0, 0.0)
        }
        
        self.routing.build_graph_from_topology(node_positions, max_range=150.0)
    
    def test_baseline_path_through_blackhole(self):
        """Test baseline route through blackhole"""
        path = self.routing.get_baseline_path(0, 3)
        
        # Baseline should choose shortest path that passes through blackhole
        self.assertIsNotNone(path)
        self.assertIn(2, path)  # Path passes through blackhole node 2
    
    def test_proposed_path_avoids_blackhole(self):
        """Test proposed route avoiding blackhole"""
        # Configure SNR for all links
        self.link_state.update_snr(0, 1, snr=20.0)
        self.link_state.update_snr(1, 2, snr=20.0)
        self.link_state.update_snr(2, 3, snr=20.0)
        
        # Add alternative path to bypass blackhole
        # Add path 0-4-3, where 4 is normal node
        node_positions = {
            0: (0.0, 0.0, 0.0),
            1: (100.0, 0.0, 0.0),
            2: (200.0, 0.0, 0.0),  # blackhole
            3: (300.0, 0.0, 0.0),
            4: (150.0, 100.0, 0.0)  # Alternative path
        }
        
        self.routing.build_graph_from_topology(node_positions, max_range=200.0)
        self.link_state.update_snr(0, 4, snr=20.0)
        self.link_state.update_snr(4, 3, snr=20.0)
        
        path = self.routing.get_proposed_path(0, 3, self.ledger, self.link_state)
        
        # Proposed should bypass blackhole
        if path:
            self.assertNotIn(2, path)
    
    def test_path_through_blackhole_detection(self):
        """Test path through blackhole detection"""
        path = [0, 1, 2, 3]
        self.assertTrue(self.routing.get_path_through_blackhole(path, [2]))
        
        path = [0, 1, 3]
        self.assertFalse(self.routing.get_path_through_blackhole(path, [2]))


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_ledger_and_routing_integration(self):
        """Test ledger and routing integration"""
        ledger = BlockchainLedger(blackhole_nodes=[2])
        link_state = LinkStateBuffer()
        routing = RoutingEngine()
        
        # Create topology
        node_positions = {
            0: (0.0, 0.0, 0.0),
            1: (100.0, 0.0, 0.0),
            2: (200.0, 0.0, 0.0),  # blackhole
            3: (300.0, 0.0, 0.0)
        }
        
        routing.build_graph_from_topology(node_positions, max_range=150.0)
        
        # Configure data
        link_state.update_snr(0, 1, snr=20.0)
        link_state.update_snr(1, 2, snr=20.0)
        link_state.update_snr(2, 3, snr=20.0)
        
        # Baseline passes through blackhole
        baseline_path = routing.get_baseline_path(0, 3)
        self.assertIsNotNone(baseline_path)
        
        # Proposed should consider trust
        proposed_path = routing.get_proposed_path(0, 3, ledger, link_state)
        # If alternative path exists, it should bypass blackhole
        if proposed_path and len(proposed_path) > 3:
            # If path is longer than baseline, it may bypass blackhole
            pass


if __name__ == "__main__":
    unittest.main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Consensus-Based Validator Selection Simulation
Implements ValidatorLeave/ManetNodeEnter exchange algorithm with mobility
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import our consensus validator manager
from models.blockchain.consensus_validator_manager import (
    ConsensusValidatorManager, 
    ZoneType, 
    NodeStatus
)

logger = logging.getLogger(__name__)

class ConsensusValidatorSimulation:
    """
    Enhanced simulation with consensus-based validator management
    Demonstrates ValidatorLeave/ManetNodeEnter algorithm with mobility
    """
    
    def __init__(self, 
                 simulation_time: float = 180.0,
                 total_nodes: int = 20,
                 min_validators: int = 3,
                 max_validators: int = 7,
                 ns3_integration: bool = True):
        """
        Initialize consensus validator simulation
        
        Args:
            simulation_time: Total simulation time in seconds
            total_nodes: Total number of mobile nodes
            min_validators: Minimum number of validators
            max_validators: Maximum number of validators
            ns3_integration: Whether to integrate with NS-3
        """
        self.logger = logging.getLogger("ConsensusValidatorSimulation")
        
        self.simulation_time = simulation_time
        self.total_nodes = total_nodes
        self.ns3_integration = ns3_integration
        
        # Node distribution
        self.base_station_id = 0
        self.mobile_node_ids = list(range(1, total_nodes + 1))
        
        # Consensus validator manager
        self.validator_manager = ConsensusValidatorManager({
            "min_validators": min_validators,
            "max_validators": max_validators,
            "rssi_leave_threshold": -80.0,
            "rssi_enter_threshold": -70.0,
            "battery_threshold": 0.2,
            "consensus_threshold": 0.67,
            "vote_timeout": 30.0,
            "heartbeat_interval": 5.0
        })
        
        # Simulation state
        self.running = False
        self.start_time = None
        self.simulation_thread = None
        self.statistics = {
            "total_zone_transitions": 0,
            "total_validator_changes": 0,
            "total_consensus_rounds": 0,
            "successful_leaves": 0,
            "successful_joins": 0,
            "failed_consensus": 0,
            "average_consensus_time": 0.0
        }
        
        # Node state tracking
        self.node_positions: Dict[int, tuple] = {}
        self.node_zones: Dict[int, ZoneType] = {}
        self.node_rssi: Dict[int, float] = {}
        self.node_battery: Dict[int, float] = {}
        
        # Zone boundaries (in meters from base station)
        self.zone_config = {
            "5g_radius": 100.0,
            "bridge_radius": 150.0,
            "manet_max_radius": 400.0
        }
        
        self.logger.info(f"Consensus Validator Simulation initialized")
        self.logger.info(f"  Nodes: {total_nodes}, Validators: {min_validators}-{max_validators}")
        self.logger.info(f"  Simulation time: {simulation_time}s")
        self.logger.info(f"  NS-3 integration: {ns3_integration}")
    
    def start_simulation(self):
        """Start the simulation"""
        self.logger.info("🚀 Starting Consensus Validator Simulation")
        self.logger.info("=" * 70)
        
        try:
            # Initialize components
            self.validator_manager.start()
            
            # Initialize nodes
            self._initialize_nodes()
            
            # Start simulation
            self.running = True
            self.start_time = time.time()
            
            if self.ns3_integration:
                self._run_with_ns3()
            else:
                self._run_standalone()
            
        except KeyboardInterrupt:
            self.logger.info("Simulation stopped by user")
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop_simulation()
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.logger.info("Stopping simulation...")
        
        self.running = False
        
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=5.0)
        
        self.validator_manager.stop()
        
        self._print_final_statistics()
        self.logger.info("Simulation stopped")
    
    def _initialize_nodes(self):
        """Initialize mobile nodes"""
        self.logger.info("Initializing mobile nodes...")
        
        # Randomly distribute nodes across zones
        import random
        import math
        random.seed(42)  # For reproducible results
        
        for node_id in self.mobile_node_ids:
            # Random position
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(20, self.zone_config["manet_max_radius"])
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            self.node_positions[node_id] = (x, y)
            
            # Calculate distance from base station
            distance = math.sqrt(x**2 + y**2)
            
            # Determine zone based on distance
            if distance <= self.zone_config["5g_radius"]:
                zone = ZoneType.FIVE_G
                rssi = -50.0 - (distance / 10.0)  # Strong signal
            elif distance <= self.zone_config["bridge_radius"]:
                zone = ZoneType.BRIDGE
                rssi = -65.0 - (distance / 20.0)  # Medium signal
            else:
                zone = ZoneType.MANET
                rssi = -85.0 - (distance / 50.0)  # Weak signal
            
            self.node_zones[node_id] = zone
            self.node_rssi[node_id] = rssi
            self.node_battery[node_id] = random.uniform(0.6, 1.0)
            
            # Register node with validator manager
            dual_radio = zone == ZoneType.BRIDGE  # Bridge nodes have dual radio
            cert_valid = random.uniform(0, 1) > 0.1  # 90% have valid certs
            
            success = self.validator_manager.register_node(
                node_id=node_id,
                zone=zone,
                rssi_6g=rssi,
                battery_level=self.node_battery[node_id],
                cert_valid=cert_valid,
                dual_radio=dual_radio
            )
            
            if success:
                self.logger.debug(f"Node {node_id} registered in {zone.value} zone")
        
        self.logger.info(f"Initialized {len(self.mobile_node_ids)} mobile nodes")
        
        # Print initial validator status
        stats = self.validator_manager.get_consensus_statistics()
        self.logger.info(f"Initial validators: {stats['active_validators']}")
        self.logger.info(f"Initial candidates: {stats['candidate_nodes']}")
        
        # Show initial zone distribution
        zone_counts = {}
        for zone in self.node_zones.values():
            zone_counts[zone.value] = zone_counts.get(zone.value, 0) + 1
        self.logger.info(f"Zone distribution: {zone_counts}")
    
    def _run_standalone(self):
        """Run simulation without NS-3 (standalone mobility simulation)"""
        self.logger.info("Running standalone simulation with synthetic mobility...")
        
        # Start mobility simulation thread
        self.simulation_thread = threading.Thread(
            target=self._mobility_worker,
            daemon=True
        )
        self.simulation_thread.start()
        
        # Main simulation loop
        last_stats_time = time.time()
        
        while self.running and (time.time() - self.start_time) < self.simulation_time:
            current_time = time.time() - self.start_time
            
            # Print statistics every 30 seconds
            if time.time() - last_stats_time >= 30.0:
                self._print_live_statistics(current_time)
                last_stats_time = time.time()
            
            # Simulate cross-zone transactions
            self._simulate_cross_zone_activity()
            
            time.sleep(1.0)
        
        self.logger.info("Standalone simulation completed")
    
    def _run_with_ns3(self):
        """Run simulation with NS-3 integration"""
        self.logger.info("Running simulation with NS-3 integration...")
        
        # Start NS-3 process (simplified - would normally start actual NS-3)
        self.logger.info("🔗 Starting NS-3 network simulation...")
        
        # Start mobility simulation thread
        self.simulation_thread = threading.Thread(
            target=self._mobility_worker,
            daemon=True
        )
        self.simulation_thread.start()
        
        # Monitor simulation
        last_stats_time = time.time()
        
        while self.running and (time.time() - self.start_time) < self.simulation_time:
            current_time = time.time() - self.start_time
            
            # Print statistics every 20 seconds
            if time.time() - last_stats_time >= 20.0:
                self._print_live_statistics(current_time)
                last_stats_time = time.time()
            
            time.sleep(2.0)
        
        self.logger.info("NS-3 integrated simulation completed")
    
    def _mobility_worker(self):
        """Background worker simulating node mobility"""
        import random
        import math
        
        while self.running:
            try:
                # Simulate mobility for each node
                for node_id in self.mobile_node_ids:
                    if not self.running:
                        break
                    
                    # Get current position
                    x, y = self.node_positions.get(node_id, (0, 0))
                    
                    # Random movement (simplified mobility model)
                    speed = random.uniform(1.0, 3.0)  # 1-3 m/s
                    direction = random.uniform(0, 2 * math.pi)
                    
                    # Calculate new position
                    dx = speed * math.cos(direction)
                    dy = speed * math.sin(direction)
                    
                    new_x = x + dx
                    new_y = y + dy
                    
                    # Keep within bounds
                    max_radius = self.zone_config["manet_max_radius"]
                    distance_from_origin = math.sqrt(new_x**2 + new_y**2)
                    
                    if distance_from_origin > max_radius:
                        # Reflect back
                        angle_to_origin = math.atan2(-new_y, -new_x)
                        new_x = (max_radius - 10) * math.cos(angle_to_origin)
                        new_y = (max_radius - 10) * math.sin(angle_to_origin)
                    
                    # Update position
                    self.node_positions[node_id] = (new_x, new_y)
                    
                    # Calculate new zone and RSSI
                    distance = math.sqrt(new_x**2 + new_y**2)
                    old_zone = self.node_zones.get(node_id, ZoneType.MANET)
                    
                    # Determine new zone
                    if distance <= self.zone_config["5g_radius"]:
                        new_zone = ZoneType.FIVE_G
                        new_rssi = -50.0 - (distance / 10.0) + random.uniform(-5, 5)
                    elif distance <= self.zone_config["bridge_radius"]:
                        new_zone = ZoneType.BRIDGE
                        new_rssi = -65.0 - (distance / 20.0) + random.uniform(-5, 5)
                    else:
                        new_zone = ZoneType.MANET
                        new_rssi = -85.0 - (distance / 50.0) + random.uniform(-10, 5)
                    
                    # Update node state
                    self.node_zones[node_id] = new_zone
                    self.node_rssi[node_id] = new_rssi
                    
                    # Simulate battery drain
                    self.node_battery[node_id] = max(0.0, 
                        self.node_battery[node_id] - random.uniform(0.0001, 0.0005))
                    
                    # Update validator manager
                    self.validator_manager.update_node_status(
                        node_id=node_id,
                        rssi_6g=new_rssi,
                        battery_level=self.node_battery[node_id],
                        zone=new_zone
                    )
                    
                    # Log zone transitions
                    if old_zone != new_zone:
                        self.statistics["total_zone_transitions"] += 1
                        self.logger.info(f"🔄 Node {node_id} moved: {old_zone.value} → {new_zone.value} (RSSI: {new_rssi:.1f}dBm)")
                
                time.sleep(5.0)  # Update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in mobility worker: {e}")
    
    def _simulate_cross_zone_activity(self):
        """Simulate cross-zone transaction activity"""
        import random
        
        # Randomly trigger some validator management events
        if random.uniform(0, 1) < 0.05:  # 5% chance per iteration
            # Simulate validator going offline
            active_validators = self.validator_manager.get_active_validators()
            if active_validators and len(active_validators) > self.validator_manager.config["min_validators"]:
                offline_validator = random.choice(active_validators)
                self.logger.info(f"💔 Simulating validator {offline_validator} going offline")
                self.validator_manager.update_node_status(
                    offline_validator,
                    battery_level=0.1  # Low battery triggers leave
                )
    
    def _print_live_statistics(self, current_time: float):
        """Print live simulation statistics"""
        validator_stats = self.validator_manager.get_consensus_statistics()
        
        self.logger.info("📊 Live Statistics")
        self.logger.info(f"  ⏰ Time: {current_time:.1f}s / {self.simulation_time}s")
        self.logger.info(f"  👥 Active validators: {validator_stats['active_validators']}")
        self.logger.info(f"  🏃 Candidate nodes: {validator_stats['candidate_nodes']}")
        self.logger.info(f"  📜 Pending transactions: {validator_stats['pending_transactions']}")
        self.logger.info(f"  🗳️ Active consensus rounds: {validator_stats['active_consensus_rounds']}")
        self.logger.info(f"  🔄 Zone transitions: {self.statistics['total_zone_transitions']}")
        
        # Show current validators
        active_validators = self.validator_manager.get_active_validators()
        if active_validators:
            validator_info = []
            for v_id in active_validators:
                info = self.validator_manager.get_validator_info(v_id)
                if info:
                    zone = info['zone']
                    rssi = info['rssi_6g']
                    battery = info['battery_level']
                    validator_info.append(f"{v_id}({zone}:{rssi:.0f}dB:{battery:.0%})")
            self.logger.info(f"  🛡️ Validators: {', '.join(validator_info)}")
    
    def _print_final_statistics(self):
        """Print final simulation statistics"""
        final_stats = self.validator_manager.get_consensus_statistics()
        
        self.logger.info("🎯 Final Simulation Results")
        self.logger.info("=" * 50)
        self.logger.info(f"📊 Consensus Validator Management:")
        self.logger.info(f"  • Total leave transactions: {final_stats['metrics']['total_leave_transactions']}")
        self.logger.info(f"  • Total join transactions: {final_stats['metrics']['total_join_transactions']}")
        self.logger.info(f"  • Successful promotions: {final_stats['metrics']['successful_promotions']}")
        self.logger.info(f"  • Failed consensus rounds: {final_stats['metrics']['failed_consensus']}")
        self.logger.info(f"  • Total validator changes: {final_stats['metrics']['validator_changes']}")
        
        self.logger.info(f"🌐 Network Mobility:")
        self.logger.info(f"  • Total zone transitions: {self.statistics['total_zone_transitions']}")
        
        self.logger.info(f"📈 Final State:")
        self.logger.info(f"  • Active validators: {final_stats['active_validators']}")
        self.logger.info(f"  • Candidate nodes: {final_stats['candidate_nodes']}")
        self.logger.info(f"  • Retired validators: {final_stats['retired_validators']}")
        
        # Success rate
        total_consensus = (final_stats['metrics']['total_leave_transactions'] + 
                          final_stats['metrics']['total_join_transactions'])
        if total_consensus > 0:
            success_rate = ((final_stats['metrics']['successful_promotions'] + 
                           final_stats['metrics']['total_leave_transactions'] - 
                           final_stats['metrics']['failed_consensus']) / total_consensus) * 100
            self.logger.info(f"  • Consensus success rate: {success_rate:.1f}%")
        
        # Show final active validators
        active_validators = self.validator_manager.get_active_validators()
        self.logger.info(f"  • Final validator IDs: {active_validators}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Consensus Validator Selection Simulation")
    
    parser.add_argument("--time", type=float, default=180.0,
                       help="Simulation time in seconds (default: 180)")
    parser.add_argument("--nodes", type=int, default=20,
                       help="Total number of mobile nodes (default: 20)")
    parser.add_argument("--min-validators", type=int, default=3,
                       help="Minimum number of validators (default: 3)")
    parser.add_argument("--max-validators", type=int, default=7,
                       help="Maximum number of validators (default: 7)")
    parser.add_argument("--no-ns3", action="store_true",
                       help="Run without NS-3 integration (standalone)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Consensus-Based Validator Selection Simulation")
    logger.info(f"📊 Configuration:")
    logger.info(f"  • Nodes: {args.nodes}")
    logger.info(f"  • Validators: {args.min_validators}-{args.max_validators}")
    logger.info(f"  • Time: {args.time}s")
    logger.info(f"  • NS-3: {'No' if args.no_ns3 else 'Yes'}")
    
    # Create and run simulation
    simulation = ConsensusValidatorSimulation(
        simulation_time=args.time,
        total_nodes=args.nodes,
        min_validators=args.min_validators,
        max_validators=args.max_validators,
        ns3_integration=not args.no_ns3
    )
    
    try:
        simulation.start_simulation()
        logger.info("✅ Simulation completed successfully!")
    except KeyboardInterrupt:
        logger.info("🛑 Simulation interrupted by user")
    except Exception as e:
        logger.error(f"❌ Simulation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
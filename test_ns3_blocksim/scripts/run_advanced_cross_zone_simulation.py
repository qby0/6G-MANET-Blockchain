#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Cross-Zone Blockchain Simulation with Consensus Validator Management
Enhanced simulation with ValidatorLeave/ManetNodeEnter algorithm and mobility
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import consensus validator system
from models.blockchain.consensus_validator_manager import (
    ConsensusValidatorManager, 
    ZoneType, 
    NodeStatus
)

logger = logging.getLogger(__name__)

class AdvancedCrossZoneRunner:
    """
    Enhanced cross-zone simulation with consensus-based validator management
    Integrates ValidatorLeave/ManetNodeEnter algorithm with NS-3 and BlockSim
    """
    
    def __init__(self, 
                 ns3_dir: str = None,
                 simulation_time: float = 120.0,
                 manet_nodes: int = 8,
                 fiveg_nodes: int = 6,
                 bridge_nodes: int = 3,
                 fiveg_radius: float = 100.0,
                 min_validators: int = 3,
                 max_validators: int = 7,
                 enable_consensus: bool = True):
        """
        Initialize enhanced cross-zone runner
        
        Args:
            ns3_dir: Path to NS-3
            simulation_time: Simulation time in seconds
            manet_nodes: Number of MANET nodes
            fiveg_nodes: Number of 5G nodes
            bridge_nodes: Number of bridge validators
            fiveg_radius: 5G coverage radius
            min_validators: Minimum validators for consensus
            max_validators: Maximum validators for consensus
            enable_consensus: Enable consensus validator management
        """
        self.logger = logging.getLogger("AdvancedCrossZoneRunner")
        
        # Simulation parameters
        self.simulation_time = simulation_time
        self.manet_nodes = manet_nodes
        self.fiveg_nodes = fiveg_nodes
        self.bridge_nodes = bridge_nodes
        self.fiveg_radius = fiveg_radius
        self.enable_consensus = enable_consensus
        
        # Total nodes (including base station)
        self.base_station_id = 0
        self.total_nodes = 1 + manet_nodes + fiveg_nodes + bridge_nodes
        
        # NS-3 configuration
        if ns3_dir is None:
            self.ns3_dir = project_root / "external" / "ns-3"
        else:
            self.ns3_dir = Path(ns3_dir)
        
        self.ns3_script = "advanced-cross-zone-blockchain-fixed"
        
        # Process management
        self.ns3_process = None
        self.running = False
        self.start_time = None
        
        # Consensus validator management
        if enable_consensus:
            self.validator_manager = ConsensusValidatorManager({
                "min_validators": min_validators,
                "max_validators": max_validators,
                "rssi_leave_threshold": -80.0,
                "rssi_enter_threshold": -70.0,
                "battery_threshold": 0.2,
                "consensus_threshold": 0.67,
                "vote_timeout": 30.0,
                "heartbeat_interval": 5.0,
                "bridge_zone_radius": 150.0
            })
        else:
            self.validator_manager = None
        
        # Statistics tracking
        self.statistics = {
            "zone_transitions": 0,
            "validator_rotations": 0,
            "cross_zone_transactions": 0,
            "validated_transactions": 0,
            "consensus_rounds": 0,
            "successful_validator_changes": 0,
            "failed_consensus": 0
        }
        
        # Node state tracking for consensus system
        self.node_positions: Dict[int, Tuple[float, float, float]] = {}
        self.node_zones: Dict[int, ZoneType] = {}
        self.node_rssi: Dict[int, float] = {}
        self.node_battery: Dict[int, float] = {}
        
        # Zone boundaries (meters from base station)
        self.zone_config = {
            "5g_radius": fiveg_radius,
            "bridge_radius": fiveg_radius + 50.0,
            "manet_max_radius": 400.0
        }
        
        self.logger.info(f"Advanced Cross-Zone Runner with Consensus Validators initialized")
        self.logger.info(f"  NS-3 Directory: {self.ns3_dir}")
        self.logger.info(f"  Configuration: {manet_nodes}M + {fiveg_nodes}5G + {bridge_nodes}B nodes")
        self.logger.info(f"  Simulation: {simulation_time}s, 5G radius: {fiveg_radius}m")
        self.logger.info(f"  Consensus: {'Enabled' if enable_consensus else 'Disabled'}")
        if enable_consensus:
            self.logger.info(f"  Validators: {min_validators}-{max_validators}")
    
    def setup_environment(self):
        """Setup simulation environment"""
        self.logger.info("Setting up environment...")
        
        # Check NS-3
        if not self.ns3_dir.exists():
            raise RuntimeError(f"NS-3 directory not found: {self.ns3_dir}")
        
        # Check if NS-3 is built
        ns3_build_dir = self.ns3_dir / "build"
        if not ns3_build_dir.exists():
            self.logger.warning("NS-3 not built, attempting to build...")
            self._build_ns3()
        
        # Initialize consensus validator system if enabled
        if self.enable_consensus and self.validator_manager:
            self.validator_manager.start()
            self._initialize_consensus_nodes()
        
        self.logger.info("Environment setup completed")
    
    def _build_ns3(self):
        """Build NS-3"""
        self.logger.info("Building NS-3...")
        
        try:
            original_cwd = os.getcwd()
            os.chdir(self.ns3_dir)
            
            # Configure
            configure_cmd = ["python3", "ns3", "configure", "--enable-examples", "--enable-tests"]
            result = subprocess.run(configure_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"NS-3 configure failed: {result.stderr}")
                raise RuntimeError("NS-3 configure failed")
            
            # Build
            build_cmd = ["python3", "ns3", "build"]
            result = subprocess.run(build_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"NS-3 build failed: {result.stderr}")
                raise RuntimeError("NS-3 build failed")
            
            os.chdir(original_cwd)
            self.logger.info("NS-3 built successfully")
            
        except Exception as e:
            try:
                os.chdir(original_cwd)
            except:
                pass
            raise
    
    def _initialize_consensus_nodes(self):
        """Initialize nodes in the consensus validator system"""
        if not self.validator_manager:
            return
        
        import random
        import math
        random.seed(42)  # For reproducible results
        
        self.logger.info("Initializing consensus validator nodes...")
        
        node_id = 1  # Start after base station (ID 0)
        
        # Initialize bridge nodes (preferentially become validators)
        for i in range(self.bridge_nodes):
            # Position in bridge zone
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(self.zone_config["5g_radius"] + 10, 
                                  self.zone_config["bridge_radius"] - 10)
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 1.5  # Node height
            
            self.node_positions[node_id] = (x, y, z)
            self.node_zones[node_id] = ZoneType.BRIDGE
            self.node_rssi[node_id] = -65.0 - (radius / 20.0) + random.uniform(-5, 5)
            self.node_battery[node_id] = random.uniform(0.7, 1.0)
            
            # Register with validator manager
            success = self.validator_manager.register_node(
                node_id=node_id,
                zone=ZoneType.BRIDGE,
                rssi_6g=self.node_rssi[node_id],
                battery_level=self.node_battery[node_id],
                cert_valid=True,
                dual_radio=True  # Bridge nodes have dual radio
            )
            
            if success:
                self.logger.info(f"🌉 Bridge node {node_id} registered as validator candidate")
            
            node_id += 1
        
        # Initialize 5G nodes
        for i in range(self.fiveg_nodes):
            # Position in 5G zone
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(20, self.zone_config["5g_radius"] - 10)
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 1.5
            
            self.node_positions[node_id] = (x, y, z)
            self.node_zones[node_id] = ZoneType.FIVE_G
            self.node_rssi[node_id] = -50.0 - (radius / 10.0) + random.uniform(-3, 3)
            self.node_battery[node_id] = random.uniform(0.6, 1.0)
            
            # Register with validator manager
            success = self.validator_manager.register_node(
                node_id=node_id,
                zone=ZoneType.FIVE_G,
                rssi_6g=self.node_rssi[node_id],
                battery_level=self.node_battery[node_id],
                cert_valid=random.uniform(0, 1) > 0.1,  # 90% have valid certs
                dual_radio=False
            )
            
            if success:
                self.logger.info(f"📡 5G node {node_id} registered as validator candidate")
            
            node_id += 1
        
        # Initialize MANET nodes
        for i in range(self.manet_nodes):
            # Position in MANET zone
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(self.zone_config["bridge_radius"] + 10, 
                                  self.zone_config["manet_max_radius"])
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 1.5
            
            self.node_positions[node_id] = (x, y, z)
            self.node_zones[node_id] = ZoneType.MANET
            self.node_rssi[node_id] = -85.0 - (radius / 50.0) + random.uniform(-10, 5)
            self.node_battery[node_id] = random.uniform(0.5, 0.9)
            
            # Register with validator manager (MANET nodes less likely to be validators)
            success = self.validator_manager.register_node(
                node_id=node_id,
                zone=ZoneType.MANET,
                rssi_6g=self.node_rssi[node_id],
                battery_level=self.node_battery[node_id],
                cert_valid=random.uniform(0, 1) > 0.2,  # 80% have valid certs
                dual_radio=False
            )
            
            if success:
                self.logger.debug(f"📱 MANET node {node_id} registered as potential candidate")
            
            node_id += 1
        
        # Print initial validator status
        if self.validator_manager:
            stats = self.validator_manager.get_consensus_statistics()
            self.logger.info(f"🛡️ Initial validators: {stats['active_validators']}")
            self.logger.info(f"🏃 Initial candidates: {stats['candidate_nodes']}")
            
            # Show zone distribution
            zone_counts = {}
            for zone in self.node_zones.values():
                zone_counts[zone.value] = zone_counts.get(zone.value, 0) + 1
            self.logger.info(f"🗺️ Zone distribution: {zone_counts}")
    
    def _start_mobility_simulation(self):
        """Start background mobility simulation for consensus validators"""
        if not self.enable_consensus or not self.validator_manager:
            return
        
        def mobility_worker():
            import random
            import math
            
            while self.running:
                try:
                    # Simulate mobility for each node
                    for node_id in range(1, self.total_nodes):
                        if not self.running:
                            break
                        
                        # Get current position
                        x, y, z = self.node_positions.get(node_id, (0, 0, 1.5))
                        
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
                        self.node_positions[node_id] = (new_x, new_y, z)
                        
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
                        if node_id in self.node_battery:
                            self.node_battery[node_id] = max(0.0, 
                                self.node_battery[node_id] - random.uniform(0.0001, 0.0005))
                        
                        # Update validator manager
                        self.validator_manager.update_node_status(
                            node_id=node_id,
                            rssi_6g=new_rssi,
                            battery_level=self.node_battery.get(node_id, 0.5),
                            zone=new_zone
                        )
                        
                        # Log zone transitions
                        if old_zone != new_zone:
                            self.statistics["zone_transitions"] += 1
                            self.logger.info(f"🔄 Node {node_id} moved: {old_zone.value} → {new_zone.value} (RSSI: {new_rssi:.1f}dBm)")
                    
                    time.sleep(5.0)  # Update every 5 seconds
                    
                except Exception as e:
                    self.logger.error(f"Error in mobility worker: {e}")
        
        # Start mobility thread
        mobility_thread = threading.Thread(target=mobility_worker, daemon=True)
        mobility_thread.start()
        self.logger.info("🚶 Mobility simulation started")
    
    def run_simulation(self):
        """Run NS-3 simulation with consensus validator integration"""
        self.logger.info("Starting Enhanced Cross-Zone Blockchain simulation...")
        
        original_cwd = os.getcwd()
        
        try:
            os.chdir(self.ns3_dir)
            
            # Build NS-3 command
            cmd = [
                "python3", "ns3", "run",
                f"{self.ns3_script} "
                f"--nManetNodes={self.manet_nodes} "
                f"--n5gNodes={self.fiveg_nodes} "
                f"--nBridgeNodes={self.bridge_nodes} "
                f"--simulationTime={self.simulation_time} "
                f"--fivegRadius={self.fiveg_radius} "
                f"--enableNetAnim=true"
            ]
            
            self.logger.info(f"Running: {' '.join(cmd)}")
            
            # Start NS-3 process
            self.ns3_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start mobility simulation for consensus
            self.running = True
            self.start_time = time.time()
            self._start_mobility_simulation()
            
            # Monitor simulation output
            last_stats_time = time.time()
            
            while True:
                output = self.ns3_process.stdout.readline()
                if output == '' and self.ns3_process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    
                    # Filter and log important output
                    if any(marker in line for marker in ["🚀", "📊", "🔗", "✅", "❌", "⏰", "🔄", "📡", "🏁", "🚶", "🎯"]):
                        self.logger.info(f"NS-3: {line}")
                    
                    # Track statistics
                    if "🔄 Node" in line and "changed zone" in line:
                        self.statistics["zone_transitions"] += 1
                    elif "🔄 Validator rotation" in line:
                        self.statistics["validator_rotations"] += 1
                    elif "🚀 Node" in line and "sending cross-zone tx" in line:
                        self.statistics["cross_zone_transactions"] += 1
                    elif "✅ Validator" in line and "validated transaction" in line:
                        self.statistics["validated_transactions"] += 1
                
                # Print live statistics every 30 seconds
                current_time = time.time()
                if current_time - last_stats_time >= 30.0:
                    self._print_live_statistics()
                    last_stats_time = current_time
            
            return_code = self.ns3_process.poll()
            self.running = False
            
            os.chdir(original_cwd)
            
            if return_code == 0:
                self.logger.info("✅ Enhanced Cross-Zone simulation completed successfully")
                self._print_final_statistics()
                return True
            else:
                self.logger.error(f"❌ Simulation failed with code {return_code}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error running simulation: {e}")
            self.running = False
            try:
                os.chdir(original_cwd)
            except:
                pass
            return False
    
    def _print_live_statistics(self):
        """Print live simulation statistics"""
        if not self.enable_consensus or not self.validator_manager:
            return
        
        current_time = time.time() - self.start_time if self.start_time else 0
        validator_stats = self.validator_manager.get_consensus_statistics()
        
        self.logger.info("📊 Live Consensus Statistics")
        self.logger.info(f"  ⏰ Time: {current_time:.1f}s / {self.simulation_time}s")
        self.logger.info(f"  🛡️ Active validators: {validator_stats['active_validators']}")
        self.logger.info(f"  🏃 Candidate nodes: {validator_stats['candidate_nodes']}")
        self.logger.info(f"  📜 Pending transactions: {validator_stats['pending_transactions']}")
        self.logger.info(f"  🗳️ Active consensus rounds: {validator_stats['active_consensus_rounds']}")
        self.logger.info(f"  🔄 Zone transitions: {self.statistics['zone_transitions']}")
        
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
        self.logger.info("📊 Final Simulation Statistics:")
        self.logger.info(f"  🔄 Zone transitions: {self.statistics['zone_transitions']}")
        self.logger.info(f"  🔁 Validator rotations: {self.statistics['validator_rotations']}")
        self.logger.info(f"  🚀 Cross-zone transactions: {self.statistics['cross_zone_transactions']}")
        self.logger.info(f"  ✅ Validated transactions: {self.statistics['validated_transactions']}")
        
        if self.enable_consensus and self.validator_manager:
            final_stats = self.validator_manager.get_consensus_statistics()
            
            self.logger.info("🎯 Consensus Validator Results:")
            self.logger.info(f"  • Leave transactions: {final_stats['metrics']['total_leave_transactions']}")
            self.logger.info(f"  • Join transactions: {final_stats['metrics']['total_join_transactions']}")
            self.logger.info(f"  • Successful promotions: {final_stats['metrics']['successful_promotions']}")
            self.logger.info(f"  • Failed consensus: {final_stats['metrics']['failed_consensus']}")
            self.logger.info(f"  • Total validator changes: {final_stats['metrics']['validator_changes']}")
            
            # Success rate
            total_consensus = (final_stats['metrics']['total_leave_transactions'] + 
                             final_stats['metrics']['total_join_transactions'])
            if total_consensus > 0:
                success_rate = ((final_stats['metrics']['successful_promotions'] + 
                               final_stats['metrics']['total_leave_transactions'] - 
                               final_stats['metrics']['failed_consensus']) / total_consensus) * 100
                self.logger.info(f"  • Consensus success rate: {success_rate:.1f}%")
            
            # Final state
            active_validators = self.validator_manager.get_active_validators()
            self.logger.info(f"  • Final active validators: {len(active_validators)} ({active_validators})")
    
    def run(self):
        """Run complete simulation"""
        self.logger.info("🚀 Starting Enhanced Advanced Cross-Zone Blockchain Simulation")
        self.logger.info("=" * 80)
        
        try:
            # Setup environment
            self.setup_environment()
            
            # Run simulation
            success = self.run_simulation()
            
            if success:
                self.logger.info("🎉 Enhanced simulation completed successfully!")
                self.logger.info("📁 Check advanced-cross-zone-blockchain-fixed.xml for NetAnim visualization")
                self.logger.info("🎯 Features demonstrated:")
                self.logger.info("  • Dynamic zone transitions (5G ↔ MANET ↔ Bridge)")
                self.logger.info("  • Consensus-based validator management")
                self.logger.info("  • ValidatorLeave/ManetNodeEnter algorithm")
                self.logger.info("  • PBFT consensus for validator changes")
                self.logger.info("  • RSSI-based automatic validator rotation")
                self.logger.info("  • Cross-zone transaction validation")
                self.logger.info("  • Cryptographic signatures")
                self.logger.info("  • Mobile nodes with AODV routing")
            
            return success
            
        except KeyboardInterrupt:
            self.logger.info("Simulation stopped by user")
            return False
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up...")
        
        self.running = False
        
        # Stop NS-3 process
        if self.ns3_process:
            try:
                self.ns3_process.terminate()
                self.ns3_process.wait(timeout=5)
            except:
                try:
                    self.ns3_process.kill()
                except:
                    pass
        
        # Stop validator manager
        if self.enable_consensus and self.validator_manager:
            self.validator_manager.stop()
        
        self.logger.info("Cleanup completed")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Enhanced Advanced Cross-Zone Blockchain Simulation")
    
    # Network configuration
    parser.add_argument("--manet-nodes", type=int, default=8,
                       help="Number of MANET nodes (default: 8)")
    parser.add_argument("--5g-nodes", type=int, default=6, dest="fiveg_nodes",
                       help="Number of 5G nodes (default: 6)")
    parser.add_argument("--bridge-nodes", type=int, default=3,
                       help="Number of bridge validators (default: 3)")
    parser.add_argument("--time", type=float, default=120.0,
                       help="Simulation time in seconds (default: 120)")
    parser.add_argument("--5g-radius", type=float, default=100.0, dest="fiveg_radius",
                       help="5G coverage radius in meters (default: 100)")
    parser.add_argument("--ns3-dir", type=str, default=None,
                       help="NS-3 directory (default: auto-detect)")
    
    # Consensus validator configuration
    parser.add_argument("--min-validators", type=int, default=3,
                       help="Minimum number of validators (default: 3)")
    parser.add_argument("--max-validators", type=int, default=7,
                       help="Maximum number of validators (default: 7)")
    parser.add_argument("--disable-consensus", action="store_true",
                       help="Disable consensus validator management")
    
    # Logging
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Enhanced Advanced Cross-Zone Blockchain Simulation")
    
    total_nodes = 1 + args.manet_nodes + args.fiveg_nodes + args.bridge_nodes  # +1 for BS
    logger.info(f"📊 Total nodes: {total_nodes} (1 BS + {args.bridge_nodes} Bridge + {args.manet_nodes} MANET + {args.fiveg_nodes} 5G)")
    logger.info(f"⏰ Simulation time: {args.time}s")
    logger.info(f"📡 5G coverage: {args.fiveg_radius}m radius")
    
    if not args.disable_consensus:
        logger.info(f"🛡️ Consensus validators: {args.min_validators}-{args.max_validators}")
        logger.info("🎯 Features: ValidatorLeave/ManetNodeEnter + PBFT consensus")
    else:
        logger.info("⚠️ Consensus validator management disabled")
    
    # Create and run enhanced runner
    runner = AdvancedCrossZoneRunner(
        ns3_dir=args.ns3_dir,
        simulation_time=args.time,
        manet_nodes=args.manet_nodes,
        fiveg_nodes=args.fiveg_nodes,
        bridge_nodes=args.bridge_nodes,
        fiveg_radius=args.fiveg_radius,
        min_validators=args.min_validators,
        max_validators=args.max_validators,
        enable_consensus=not args.disable_consensus
    )
    
    success = runner.run()
    
    if success:
        logger.info("🎉 All done! Check NetAnim file for visualization.")
        logger.info("🏆 Enhanced with consensus-based validator management!")
    else:
        logger.error("❌ Simulation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
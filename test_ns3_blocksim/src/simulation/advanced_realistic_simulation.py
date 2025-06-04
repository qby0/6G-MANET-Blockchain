#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Realistic Cross-Zone Blockchain Simulation

This simulation uses realistic device parameters and generates comprehensive
statistics with beautiful visualizations showing device performance,
energy consumption, network dynamics, and blockchain metrics.
"""

import json
import logging
import os
import random
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import pandas as pd
import argparse

# Import our realistic device manager
from models.realistic_device_manager import RealisticDeviceManager, DeviceCapabilities

# Configure matplotlib for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    """Represents a blockchain transaction"""
    tx_id: str
    timestamp: float
    sender: str
    receiver: str
    amount: float
    zone: str
    energy_cost: float
    processing_time: float
    status: str  # pending, confirmed, failed

@dataclass
class Block:
    """Represents a blockchain block"""
    block_id: int
    timestamp: float
    transactions: List[str]
    validator: str
    zone: str
    consensus_time: float
    energy_consumed: float
    size_bytes: int

@dataclass
class NetworkEvent:
    """Represents a network event"""
    timestamp: float
    event_type: str
    node_id: str
    zone_from: Optional[str]
    zone_to: Optional[str]
    energy_cost: float
    success: bool

@dataclass
class DeviceState:
    """Current state of a device"""
    device_id: str
    current_zone: str
    position: Tuple[float, float]
    battery_level: float
    transactions_sent: int
    transactions_processed: int
    blocks_validated: int
    total_energy_consumed: float
    online: bool
    performance_score: float

class AdvancedRealisticSimulation:
    """
    Advanced simulation with realistic device parameters and comprehensive statistics
    """
    
    def __init__(self, scenario_name: str = "medium_district"):
        """Initialize the simulation"""
        self.device_manager = RealisticDeviceManager()
        self.scenario = self.device_manager.generate_simulation_scenario(scenario_name)
        
        # Simulation state
        self.current_time = 0.0
        self.devices: Dict[str, DeviceCapabilities] = {}
        self.device_states: Dict[str, DeviceState] = {}
        self.transactions: List[Transaction] = []
        self.blocks: List[Block] = []
        self.network_events: List[NetworkEvent] = []
        
        # Statistics tracking
        self.stats = {
            'energy_consumption': defaultdict(list),
            'zone_distribution': defaultdict(list),
            'transaction_throughput': [],
            'consensus_latency': [],
            'device_performance': defaultdict(list),
            'battery_levels': defaultdict(list),
            'zone_transitions': defaultdict(int),
            'network_quality': [],
            'validator_performance': defaultdict(list)
        }
        
        # Initialize devices
        self._initialize_devices()
        
        logger.info(f"Initialized simulation with {len(self.devices)} devices")
    
    def _initialize_devices(self):
        """Initialize all devices from scenario"""
        for device_info in self.scenario['devices']:
            device_id = device_info['device_id']
            device_type = device_info['device_type']
            
            # Get device capabilities
            capabilities = self.device_manager.devices[device_id]
            self.devices[device_id] = capabilities
            
            # Initialize device state
            initial_zone = self._assign_initial_zone(device_type)
            initial_position = self._generate_initial_position(device_type)
            
            self.device_states[device_id] = DeviceState(
                device_id=device_id,
                current_zone=initial_zone,
                position=initial_position,
                battery_level=100.0,
                transactions_sent=0,
                transactions_processed=0,
                blocks_validated=0,
                total_energy_consumed=0.0,
                online=True,
                performance_score=1.0
            )
    
    def _assign_initial_zone(self, device_type: str) -> str:
        """Assign initial zone based on device type"""
        if device_type in ['base_station_5g', 'small_cell', 'edge_server']:
            return '5g'
        elif device_type == 'iot_sensor':
            return random.choice(['5g', 'manet'])
        else:  # smartphone, vehicle
            return random.choice(['5g', 'bridge', 'manet'])
    
    def _generate_initial_position(self, device_type: str) -> Tuple[float, float]:
        """Generate initial position for device"""
        area_size = np.sqrt(self.scenario['area_km2']) * 1000  # Convert to meters
        
        if device_type in ['base_station_5g', 'edge_server']:
            # Place infrastructure at strategic locations
            x = random.uniform(0.2 * area_size, 0.8 * area_size)
            y = random.uniform(0.2 * area_size, 0.8 * area_size)
        else:
            # Random placement for mobile devices
            x = random.uniform(0, area_size)
            y = random.uniform(0, area_size)
        
        return (x, y)
    
    def run_simulation(self, duration_seconds: int = 600):
        """Run the main simulation loop"""
        logger.info(f"Starting simulation for {duration_seconds} seconds")
        
        time_step = 1.0  # 1 second steps
        steps = int(duration_seconds / time_step)
        
        for step in range(steps):
            self.current_time = step * time_step
            
            # Update device positions and zones
            self._update_device_mobility()
            
            # Generate transactions
            self._generate_transactions()
            
            # Process consensus rounds
            if step % 5 == 0:  # Consensus every 5 seconds
                self._run_consensus_round()
            
            # Update device states
            self._update_device_states()
            
            # Collect statistics
            self._collect_statistics()
            
            # Progress indicator
            if step % 60 == 0:  # Every minute
                progress = (step / steps) * 100
                logger.info(f"Simulation progress: {progress:.1f}%")
        
        logger.info("Simulation completed")
    
    def _update_device_mobility(self):
        """Update device positions and handle zone transitions"""
        for device_id, device in self.devices.items():
            state = self.device_states[device_id]
            
            if device.mobility_type == 'static':
                continue
            
            # Update position based on mobility model
            new_position = self._calculate_new_position(device, state)
            state.position = new_position
            
            # Check for zone transitions
            new_zone = self._determine_zone(new_position, device)
            if new_zone != state.current_zone:
                self._handle_zone_transition(device_id, state.current_zone, new_zone)
                state.current_zone = new_zone
    
    def _calculate_new_position(self, device: DeviceCapabilities, state: DeviceState) -> Tuple[float, float]:
        """Calculate new position based on mobility model"""
        current_x, current_y = state.position
        max_speed_ms = device.max_speed_kmh / 3.6  # Convert km/h to m/s
        max_distance = max_speed_ms * 1.0  # 1 second time step
        
        if device.mobility_type == 'pedestrian':
            # Random walk with occasional stops
            if random.random() < 0.1:  # 10% chance to stop
                return state.position
            
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(0, max_distance)
            
        elif device.mobility_type == 'vehicular':
            # More directed movement
            angle = random.uniform(-np.pi/4, np.pi/4)  # ±45 degrees
            distance = random.uniform(max_distance * 0.5, max_distance)
            
        else:
            return state.position
        
        new_x = current_x + distance * np.cos(angle)
        new_y = current_y + distance * np.sin(angle)
        
        # Keep within simulation area
        area_size = np.sqrt(self.scenario['area_km2']) * 1000
        new_x = max(0, min(area_size, new_x))
        new_y = max(0, min(area_size, new_y))
        
        return (new_x, new_y)
    
    def _determine_zone(self, position: Tuple[float, float], device: DeviceCapabilities) -> str:
        """Determine which zone a device is in based on position and signal strength"""
        # Simplified zone determination based on distance to infrastructure
        min_distance_to_5g = float('inf')
        
        for other_id, other_device in self.devices.items():
            if other_device.device_type in ['base_station_5g', 'small_cell']:
                other_state = self.device_states[other_id]
                distance = np.sqrt((position[0] - other_state.position[0])**2 + 
                                 (position[1] - other_state.position[1])**2)
                min_distance_to_5g = min(min_distance_to_5g, distance)
        
        # Zone determination based on distance
        if min_distance_to_5g < 500:  # Within 500m of 5G infrastructure
            return '5g'
        elif min_distance_to_5g < 1000:  # Within 1000m
            return 'bridge'
        else:
            return 'manet'
    
    def _handle_zone_transition(self, device_id: str, from_zone: str, to_zone: str):
        """Handle zone transition with energy cost and latency"""
        transition_cost = self.device_manager.get_zone_transition_cost(device_id, from_zone, to_zone)
        
        # Record network event
        event = NetworkEvent(
            timestamp=self.current_time,
            event_type='zone_transition',
            node_id=device_id,
            zone_from=from_zone,
            zone_to=to_zone,
            energy_cost=transition_cost['energy_mj'],
            success=random.random() < transition_cost['success_probability']
        )
        self.network_events.append(event)
        
        # Update device energy
        state = self.device_states[device_id]
        state.total_energy_consumed += transition_cost['energy_mj']
        
        # Update battery for mobile devices
        if self.devices[device_id].device_type in ['smartphone', 'iot_sensor']:
            battery_drain = transition_cost['energy_mj'] / 1000  # Convert mJ to relative battery drain
            state.battery_level = max(0, state.battery_level - battery_drain)
        
        # Update statistics
        self.stats['zone_transitions'][f"{from_zone}_to_{to_zone}"] += 1
    
    def _generate_transactions(self):
        """Generate realistic transactions based on device activity"""
        # Transaction rate depends on zone and device type
        for device_id, device in self.devices.items():
            state = self.device_states[device_id]
            
            if not state.online or state.battery_level < 5:
                continue
            
            # Calculate transaction probability based on device type and zone
            base_rate = {
                'smartphone': 0.1,
                'iot_sensor': 0.05,
                'vehicle': 0.15,
                'base_station_5g': 0.02,
                'edge_server': 0.01
            }.get(device.device_type, 0.1)
            
            zone_multiplier = {'5g': 1.5, 'bridge': 1.0, 'manet': 0.7}.get(state.current_zone, 1.0)
            
            if random.random() < base_rate * zone_multiplier:
                self._create_transaction(device_id)
    
    def _create_transaction(self, sender_id: str):
        """Create a new transaction"""
        # Select random receiver
        potential_receivers = [d for d in self.device_states.keys() 
                             if d != sender_id and self.device_states[d].online]
        if not potential_receivers:
            return
        
        receiver_id = random.choice(potential_receivers)
        sender_state = self.device_states[sender_id]
        
        # Calculate transaction cost
        energy_cost = self.device_manager.calculate_energy_consumption(
            sender_id, 'wifi_tx', 0.1  # 100ms transmission
        )
        
        transaction = Transaction(
            tx_id=f"tx_{len(self.transactions)}_{int(self.current_time)}",
            timestamp=self.current_time,
            sender=sender_id,
            receiver=receiver_id,
            amount=random.uniform(0.1, 100.0),
            zone=sender_state.current_zone,
            energy_cost=energy_cost,
            processing_time=random.uniform(0.01, 0.1),
            status='pending'
        )
        
        self.transactions.append(transaction)
        sender_state.transactions_sent += 1
        sender_state.total_energy_consumed += energy_cost
    
    def _run_consensus_round(self):
        """Run a consensus round with realistic validator selection"""
        # Select validators based on capabilities and stake
        validators = self._select_validators()
        
        if len(validators) < 3:  # Need minimum validators
            return
        
        # Get pending transactions
        pending_txs = [tx for tx in self.transactions if tx.status == 'pending']
        if not pending_txs:
            return
        
        # Select transactions for block (limit by block size)
        max_tx_per_block = 50
        block_txs = pending_txs[:max_tx_per_block]
        
        # Calculate consensus time based on validator performance
        consensus_start_time = time.time()
        consensus_energy = 0
        
        for validator_id in validators:
            consensus_req = self.device_manager.get_consensus_requirements(validator_id, len(self.blocks))
            consensus_energy += consensus_req['requirements']['energy_cost_mj']
        
        consensus_time = random.uniform(0.5, 2.0)  # 0.5-2 seconds
        
        # Create block
        primary_validator = validators[0]
        block = Block(
            block_id=len(self.blocks),
            timestamp=self.current_time,
            transactions=[tx.tx_id for tx in block_txs],
            validator=primary_validator,
            zone=self.device_states[primary_validator].current_zone,
            consensus_time=consensus_time,
            energy_consumed=consensus_energy,
            size_bytes=len(block_txs) * 250  # ~250 bytes per transaction
        )
        
        self.blocks.append(block)
        
        # Update transaction status
        for tx in block_txs:
            tx.status = 'confirmed'
        
        # Update validator statistics
        for validator_id in validators:
            validator_state = self.device_states[validator_id]
            validator_state.blocks_validated += 1
            validator_state.transactions_processed += len(block_txs) // len(validators)
            validator_state.total_energy_consumed += consensus_energy / len(validators)
        
        # Record consensus latency
        self.stats['consensus_latency'].append(consensus_time)
    
    def _select_validators(self) -> List[str]:
        """Select validators based on capabilities and stake"""
        candidates = []
        
        for device_id, device in self.devices.items():
            state = self.device_states[device_id]
            
            if not state.online or state.battery_level < 20:
                continue
            
            # Check consensus requirements
            requirements = self.device_manager.get_consensus_requirements(device_id, len(self.blocks))
            if requirements and requirements['capabilities']['can_participate']:
                score = requirements['participation_score']
                candidates.append((device_id, score))
        
        # Sort by score and select top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        num_validators = min(7, len(candidates))  # 3-7 validators
        
        return [candidate[0] for candidate in candidates[:num_validators]]
    
    def _update_device_states(self):
        """Update device states including battery drain and performance"""
        for device_id, device in self.devices.items():
            state = self.device_states[device_id]
            
            # Skip offline devices
            if not state.online:
                continue
            
            # Calculate idle energy consumption
            idle_energy = self.device_manager.calculate_energy_consumption(
                device_id, 'idle', 1.0
            )
            state.total_energy_consumed += idle_energy
            
            # Battery drain for mobile devices
            if device.device_type in ['smartphone', 'iot_sensor']:
                battery_drain = idle_energy / 10000  # Convert to relative battery drain
                state.battery_level = max(0, state.battery_level - battery_drain)
                
                # Device goes offline if battery too low
                if state.battery_level < 5:
                    state.online = False
            
            # Performance degradation over time (heat, wear, etc.)
            state.performance_score *= 0.9999  # Very slow degradation
    
    def _collect_statistics(self):
        """Collect comprehensive statistics"""
        # Energy consumption by device type
        for device_id, state in self.device_states.items():
            device_type = self.devices[device_id].device_type
            self.stats['energy_consumption'][device_type].append(state.total_energy_consumed)
            self.stats['battery_levels'][device_type].append(state.battery_level)
            self.stats['device_performance'][device_type].append(state.performance_score)
        
        # Zone distribution
        zone_counts = {'5g': 0, 'bridge': 0, 'manet': 0}
        for state in self.device_states.values():
            if state.online:
                zone_counts[state.current_zone] += 1
        
        for zone, count in zone_counts.items():
            self.stats['zone_distribution'][zone].append(count)
        
        # Transaction throughput (transactions per minute)
        recent_txs = [tx for tx in self.transactions 
                     if tx.timestamp > self.current_time - 60]
        self.stats['transaction_throughput'].append(len(recent_txs))
        
        # Network quality (average signal strength simulation)
        network_quality = random.uniform(0.7, 1.0)  # Simplified
        self.stats['network_quality'].append(network_quality)
        
        # Validator performance
        for device_id, state in self.device_states.items():
            if state.blocks_validated > 0:
                device_type = self.devices[device_id].device_type
                efficiency = state.blocks_validated / max(1, state.total_energy_consumed / 1000)
                self.stats['validator_performance'][device_type].append(efficiency)
    
    def generate_comprehensive_report(self, output_dir: str = "results"):
        """Generate comprehensive simulation report with beautiful visualizations"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        logger.info("Generating comprehensive simulation report...")
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create subplots for comprehensive dashboard
        fig = plt.figure(figsize=(20, 24))
        
        # 1. Energy Consumption Analysis
        ax1 = plt.subplot(4, 3, 1)
        self._plot_energy_consumption(ax1)
        
        # 2. Device Performance Over Time
        ax2 = plt.subplot(4, 3, 2)
        self._plot_device_performance(ax2)
        
        # 3. Zone Distribution
        ax3 = plt.subplot(4, 3, 3)
        self._plot_zone_distribution(ax3)
        
        # 4. Transaction Throughput
        ax4 = plt.subplot(4, 3, 4)
        self._plot_transaction_throughput(ax4)
        
        # 5. Battery Levels
        ax5 = plt.subplot(4, 3, 5)
        self._plot_battery_levels(ax5)
        
        # 6. Consensus Performance
        ax6 = plt.subplot(4, 3, 6)
        self._plot_consensus_performance(ax6)
        
        # 7. Network Quality
        ax7 = plt.subplot(4, 3, 7)
        self._plot_network_quality(ax7)
        
        # 8. Zone Transitions
        ax8 = plt.subplot(4, 3, 8)
        self._plot_zone_transitions(ax8)
        
        # 9. Validator Performance
        ax9 = plt.subplot(4, 3, 9)
        self._plot_validator_performance(ax9)
        
        # 10. Device Distribution
        ax10 = plt.subplot(4, 3, 10)
        self._plot_device_distribution(ax10)
        
        # 11. Blockchain Growth
        ax11 = plt.subplot(4, 3, 11)
        self._plot_blockchain_growth(ax11)
        
        # 12. Energy Efficiency
        ax12 = plt.subplot(4, 3, 12)
        self._plot_energy_efficiency(ax12)
        
        plt.tight_layout()
        plt.suptitle(f'Cross-Zone Blockchain Simulation Report\n'
                    f'Scenario: {self.scenario.get("name", "Custom")} | Duration: {self.current_time:.0f}s | '
                    f'Devices: {len(self.devices)} | Transactions: {len(self.transactions)} | '
                    f'Blocks: {len(self.blocks)}', 
                    fontsize=16, y=0.98)
        
        # Save main dashboard
        dashboard_path = output_path / "simulation_dashboard.png"
        plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate individual detailed plots
        self._generate_detailed_plots(output_path)
        
        # Generate summary statistics
        self._generate_summary_statistics(output_path)
        
        logger.info(f"Comprehensive report generated in {output_path}")
        return str(output_path)
    
    def _plot_energy_consumption(self, ax):
        """Plot energy consumption by device type"""
        device_types = list(self.stats['energy_consumption'].keys())
        if not device_types:
            ax.text(0.5, 0.5, 'No Energy Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        final_consumption = []
        for device_type in device_types:
            consumption_data = self.stats['energy_consumption'][device_type]
            if consumption_data:
                final_consumption.append(consumption_data[-1])
            else:
                final_consumption.append(0)
        
        bars = ax.bar(device_types, final_consumption, color=sns.color_palette("husl", len(device_types)))
        ax.set_title('Total Energy Consumption by Device Type', fontweight='bold')
        ax.set_ylabel('Energy (mJ)')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom')
    
    def _plot_device_performance(self, ax):
        """Plot device performance over time"""
        if not self.stats['device_performance']:
            ax.text(0.5, 0.5, 'No Performance Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        for device_type, performance_data in self.stats['device_performance'].items():
            if performance_data:
                time_points = np.linspace(0, self.current_time, len(performance_data))
                ax.plot(time_points, performance_data, label=device_type, linewidth=2)
        
        ax.set_title('Device Performance Over Time', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Performance Score')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_zone_distribution(self, ax):
        """Plot current zone distribution"""
        zone_counts = {}
        for state in self.device_states.values():
            if state.online:
                zone_counts[state.current_zone] = zone_counts.get(state.current_zone, 0) + 1
        
        if not zone_counts:
            ax.text(0.5, 0.5, 'No Zone Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        zones = list(zone_counts.keys())
        counts = list(zone_counts.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        wedges, texts, autotexts = ax.pie(counts, labels=zones, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        ax.set_title('Current Zone Distribution', fontweight='bold')
    
    def _plot_transaction_throughput(self, ax):
        """Plot transaction throughput over time"""
        if not self.stats['transaction_throughput']:
            ax.text(0.5, 0.5, 'No Transaction Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        time_points = np.linspace(0, self.current_time, len(self.stats['transaction_throughput']))
        ax.plot(time_points, self.stats['transaction_throughput'], color='#FF6B6B', linewidth=2)
        ax.fill_between(time_points, self.stats['transaction_throughput'], alpha=0.3, color='#FF6B6B')
        
        ax.set_title('Transaction Throughput', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Transactions per Minute')
        ax.grid(True, alpha=0.3)
    
    def _plot_battery_levels(self, ax):
        """Plot current battery levels for mobile devices"""
        mobile_devices = ['smartphone', 'iot_sensor']
        battery_data = {}
        
        for device_id, device in self.devices.items():
            if device.device_type in mobile_devices:
                state = self.device_states[device_id]
                device_type = device.device_type
                if device_type not in battery_data:
                    battery_data[device_type] = []
                battery_data[device_type].append(state.battery_level)
        
        if not battery_data:
            ax.text(0.5, 0.5, 'No Battery Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        device_types = list(battery_data.keys())
        battery_levels = [battery_data[dt] for dt in device_types]
        
        bp = ax.boxplot(battery_levels, labels=device_types, patch_artist=True)
        colors = ['#FF6B6B', '#4ECDC4']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_title('Current Battery Levels', fontweight='bold')
        ax.set_ylabel('Battery Level (%)')
        ax.grid(True, alpha=0.3)
    
    def _plot_consensus_performance(self, ax):
        """Plot consensus latency over time"""
        if not self.stats['consensus_latency']:
            ax.text(0.5, 0.5, 'No Consensus Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        ax.hist(self.stats['consensus_latency'], bins=20, alpha=0.7, color='#45B7D1', edgecolor='black')
        ax.set_title('Consensus Latency Distribution', fontweight='bold')
        ax.set_xlabel('Consensus Time (seconds)')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
    
    def _plot_network_quality(self, ax):
        """Plot network quality over time"""
        if not self.stats['network_quality']:
            ax.text(0.5, 0.5, 'No Network Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        time_points = np.linspace(0, self.current_time, len(self.stats['network_quality']))
        ax.plot(time_points, self.stats['network_quality'], color='#4ECDC4', linewidth=2)
        ax.fill_between(time_points, self.stats['network_quality'], alpha=0.3, color='#4ECDC4')
        
        ax.set_title('Network Quality Over Time', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Quality Score')
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)
    
    def _plot_zone_transitions(self, ax):
        """Plot zone transition counts"""
        if not self.stats['zone_transitions']:
            ax.text(0.5, 0.5, 'No Transition Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        transitions = list(self.stats['zone_transitions'].keys())
        counts = list(self.stats['zone_transitions'].values())
        
        bars = ax.bar(transitions, counts, color=sns.color_palette("husl", len(transitions)))
        ax.set_title('Zone Transitions', fontweight='bold')
        ax.set_ylabel('Count')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
    
    def _plot_validator_performance(self, ax):
        """Plot validator efficiency by device type"""
        if not self.stats['validator_performance']:
            ax.text(0.5, 0.5, 'No Validator Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        device_types = list(self.stats['validator_performance'].keys())
        efficiency_data = [self.stats['validator_performance'][dt] for dt in device_types]
        
        bp = ax.boxplot(efficiency_data, labels=device_types, patch_artist=True)
        colors = sns.color_palette("husl", len(device_types))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_title('Validator Efficiency', fontweight='bold')
        ax.set_ylabel('Blocks/Energy (1/kJ)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
    
    def _plot_device_distribution(self, ax):
        """Plot device type distribution"""
        device_counts = {}
        for device in self.devices.values():
            device_type = device.device_type
            device_counts[device_type] = device_counts.get(device_type, 0) + 1
        
        if not device_counts:
            ax.text(0.5, 0.5, 'No Device Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        device_types = list(device_counts.keys())
        counts = list(device_counts.values())
        colors = sns.color_palette("husl", len(device_types))
        
        wedges, texts, autotexts = ax.pie(counts, labels=device_types, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        ax.set_title('Device Type Distribution', fontweight='bold')
    
    def _plot_blockchain_growth(self, ax):
        """Plot blockchain growth over time"""
        if not self.blocks:
            ax.text(0.5, 0.5, 'No Blockchain Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        block_times = [block.timestamp for block in self.blocks]
        block_indices = list(range(len(self.blocks)))
        
        ax.step(block_times, block_indices, where='post', color='#FF6B6B', linewidth=2)
        ax.fill_between(block_times, block_indices, step='post', alpha=0.3, color='#FF6B6B')
        
        ax.set_title('Blockchain Growth', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Block Count')
        ax.grid(True, alpha=0.3)
    
    def _plot_energy_efficiency(self, ax):
        """Plot energy efficiency (transactions per energy unit)"""
        if not self.transactions or not self.device_states:
            ax.text(0.5, 0.5, 'No Efficiency Data', ha='center', va='center', transform=ax.transAxes)
            return
        
        total_energy = sum(state.total_energy_consumed for state in self.device_states.values())
        total_transactions = len([tx for tx in self.transactions if tx.status == 'confirmed'])
        
        if total_energy > 0:
            efficiency = total_transactions / (total_energy / 1000)  # transactions per kJ
        else:
            efficiency = 0
        
        # Create a simple metric display
        ax.bar(['System'], [efficiency], color='#45B7D1')
        ax.set_title('System Energy Efficiency', fontweight='bold')
        ax.set_ylabel('Transactions per kJ')
        
        # Add value label
        ax.text(0, efficiency, f'{efficiency:.2f}', ha='center', va='bottom')
    
    def _generate_detailed_plots(self, output_path: Path):
        """Generate detailed individual plots"""
        # Create detailed energy analysis
        plt.figure(figsize=(12, 8))
        for device_type, energy_data in self.stats['energy_consumption'].items():
            if energy_data:
                time_points = np.linspace(0, self.current_time, len(energy_data))
                plt.plot(time_points, energy_data, label=device_type, linewidth=2)
        
        plt.title('Energy Consumption Over Time by Device Type', fontsize=14, fontweight='bold')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Cumulative Energy (mJ)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / "energy_consumption_detailed.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create detailed zone distribution over time
        plt.figure(figsize=(12, 8))
        for zone, distribution_data in self.stats['zone_distribution'].items():
            if distribution_data:
                time_points = np.linspace(0, self.current_time, len(distribution_data))
                plt.plot(time_points, distribution_data, label=f'{zone} zone', linewidth=2)
        
        plt.title('Zone Distribution Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Number of Devices')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / "zone_distribution_detailed.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_summary_statistics(self, output_path: Path):
        """Generate summary statistics JSON"""
        summary = {
            'simulation_overview': {
                'scenario': self.scenario.get('name', 'Custom'),
                'duration': self.current_time,
                'total_devices': len(self.devices),
                'total_transactions': len(self.transactions),
                'confirmed_transactions': len([tx for tx in self.transactions if tx.status == 'confirmed']),
                'total_blocks': len(self.blocks),
                'simulation_timestamp': datetime.now().isoformat()
            },
            'device_statistics': {
                'by_type': {},
                'energy_consumption': {},
                'battery_status': {}
            },
            'network_statistics': {
                'zone_transitions': dict(self.stats['zone_transitions']),
                'average_consensus_latency': np.mean(self.stats['consensus_latency']) if self.stats['consensus_latency'] else 0,
                'transaction_throughput_peak': max(self.stats['transaction_throughput']) if self.stats['transaction_throughput'] else 0,
                'average_network_quality': np.mean(self.stats['network_quality']) if self.stats['network_quality'] else 0
            },
            'performance_metrics': {
                'total_energy_consumed': sum(state.total_energy_consumed for state in self.device_states.values()),
                'energy_per_transaction': 0,
                'consensus_efficiency': 0,
                'device_uptime': len([s for s in self.device_states.values() if s.online]) / len(self.device_states) * 100
            }
        }
        
        # Calculate device statistics by type
        for device_id, device in self.devices.items():
            device_type = device.device_type
            state = self.device_states[device_id]
            
            if device_type not in summary['device_statistics']['by_type']:
                summary['device_statistics']['by_type'][device_type] = {
                    'count': 0,
                    'total_energy': 0,
                    'avg_battery': 0,
                    'transactions_sent': 0,
                    'blocks_validated': 0
                }
            
            stats = summary['device_statistics']['by_type'][device_type]
            stats['count'] += 1
            stats['total_energy'] += state.total_energy_consumed
            stats['avg_battery'] += state.battery_level
            stats['transactions_sent'] += state.transactions_sent
            stats['blocks_validated'] += state.blocks_validated
        
        # Calculate averages
        for device_type, stats in summary['device_statistics']['by_type'].items():
            if stats['count'] > 0:
                stats['avg_battery'] /= stats['count']
                stats['avg_energy'] = stats['total_energy'] / stats['count']
        
        # Calculate performance metrics
        confirmed_txs = len([tx for tx in self.transactions if tx.status == 'confirmed'])
        total_energy = summary['performance_metrics']['total_energy_consumed']
        
        if confirmed_txs > 0 and total_energy > 0:
            summary['performance_metrics']['energy_per_transaction'] = total_energy / confirmed_txs
        
        if len(self.blocks) > 0 and total_energy > 0:
            summary['performance_metrics']['consensus_efficiency'] = len(self.blocks) / (total_energy / 1000)
        
        # Save summary
        with open(output_path / "simulation_summary.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)

def main():
    """Main function to run the advanced realistic simulation"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Advanced Realistic Cross-Zone Blockchain Simulation')
    parser.add_argument('--scenario', type=str, default='medium_district',
                        help='Simulation scenario (small_campus, medium_district, large_city)')
    parser.add_argument('--duration', type=int, default=600,
                        help='Simulation duration in seconds')
    parser.add_argument('--output-dir', type=str, default='results',
                        help='Output directory for results')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🚀 Starting Advanced Realistic Cross-Zone Blockchain Simulation")
    print("=" * 70)
    
    try:
        # Create and run simulation
        simulation = AdvancedRealisticSimulation(args.scenario)
        
        print(f"📊 Scenario: {args.scenario}")
        print(f"⏱️  Duration: {args.duration} seconds ({args.duration//60}:{args.duration%60:02d})")
        print(f"🔧 Devices: {len(simulation.devices)}")
        print(f"📍 Area: {simulation.scenario['area_km2']} km²")
        print(f"📁 Output: {args.output_dir}/")
        print()
        
        # Run simulation
        simulation.run_simulation(args.duration)
        
        # Generate comprehensive report
        print("\n📈 Generating comprehensive report with visualizations...")
        report_path = simulation.generate_comprehensive_report(args.output_dir)
        
        print(f"\n✅ Simulation completed successfully!")
        print(f"📁 Results saved to: {report_path}")
        print(f"📊 Generated dashboard: {report_path}/simulation_dashboard.png")
        print(f"📋 Summary statistics: {report_path}/simulation_summary.json")
        
        # Print quick summary
        total_energy = sum(state.total_energy_consumed for state in simulation.device_states.values())
        confirmed_txs = len([tx for tx in simulation.transactions if tx.status == 'confirmed'])
        online_devices = len([s for s in simulation.device_states.values() if s.online])
        
        print(f"\n📈 Quick Summary:")
        print(f"   Total Transactions: {len(simulation.transactions):,}")
        print(f"   Confirmed Transactions: {confirmed_txs:,}")
        print(f"   Total Blocks: {len(simulation.blocks):,}")
        print(f"   Total Energy Consumed: {total_energy:.1f} mJ")
        if confirmed_txs > 0:
            print(f"   Energy per Transaction: {total_energy/confirmed_txs:.1f} mJ")
        print(f"   Active Devices: {online_devices}/{len(simulation.devices)}")
        print(f"   Device Uptime: {(online_devices/len(simulation.devices)*100):.1f}%")
        
        # Device type breakdown
        device_type_counts = {}
        for device in simulation.devices.values():
            device_type = device.device_type
            device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
        
        print(f"\n🔧 Device Breakdown:")
        for device_type, count in device_type_counts.items():
            online_count = sum(1 for device_id, state in simulation.device_states.items() 
                             if simulation.devices[device_id].device_type == device_type and state.online)
            print(f"   {device_type:15}: {online_count:3d}/{count:3d} online")
        
        # Zone distribution
        zone_counts = {}
        for state in simulation.device_states.values():
            if state.online:
                zone_counts[state.current_zone] = zone_counts.get(state.current_zone, 0) + 1
        
        if zone_counts:
            print(f"\n📡 Current Zone Distribution:")
            for zone, count in zone_counts.items():
                percentage = (count / online_devices) * 100
                print(f"   {zone:10} zone: {count:3d} devices ({percentage:5.1f}%)")
        
        # Transaction rate analysis
        if simulation.current_time > 0:
            tx_rate = len(simulation.transactions) / simulation.current_time * 60
            confirmed_rate = confirmed_txs / simulation.current_time * 60
            print(f"\n📊 Transaction Rates:")
            print(f"   Total: {tx_rate:.1f} tx/min")
            print(f"   Confirmed: {confirmed_rate:.1f} tx/min")
            print(f"   Success Rate: {(confirmed_txs/max(1, len(simulation.transactions))*100):.1f}%")
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
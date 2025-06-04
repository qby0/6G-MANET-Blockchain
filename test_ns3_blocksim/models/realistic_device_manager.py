#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Realistic Device Manager for Cross-Zone Blockchain Simulation

This module provides realistic device parameters based on current technology
specifications for smartphones, IoT devices, vehicles, base stations, and edge servers.
"""

import json
import logging
import os
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DeviceCapabilities:
    """Represents the capabilities of a specific device"""
    device_id: str
    device_type: str
    cpu_performance: float  # GFLOPS
    ram_gb: float
    battery_mah: int
    network_interfaces: List[str]
    max_tx_power: Dict[str, float]  # dBm
    signatures_per_sec: int
    stake_weight: float
    mobility_type: str
    max_speed_kmh: float

@dataclass
class NetworkConditions:
    """Represents current network conditions"""
    environment_type: str
    interference_level: float  # dBm
    path_loss_exponent: float
    node_density: int
    signal_strength: float  # dBm

class RealisticDeviceManager:
    """
    Manager for realistic device parameters and capabilities
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize device manager with configuration
        
        Args:
            config_path: Path to device configuration JSON file
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.devices = {}  # Active device instances
        self._device_counter = 0
        
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        current_dir = Path(__file__).parent
        config_dir = current_dir.parent / "config"
        return str(config_dir / "realistic_device_config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load device configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded device configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            return self._get_fallback_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Provide fallback configuration if file loading fails"""
        return {
            "device_types": {
                "smartphone": {
                    "hardware": {"cpu_performance_gflops": 10, "ram_gb": 8},
                    "power": {"battery_mah": 4000},
                    "blockchain": {"signatures_per_sec": 300, "stake_weight": 1.0},
                    "mobility": {"type": "pedestrian", "max_speed_kmh": 7}
                }
            },
            "environment_profiles": {
                "urban_normal": {
                    "interference_floor_dbm": -75,
                    "path_loss_exponent": 3.8,
                    "node_density_per_km2": 2000
                }
            }
        }
    
    def create_device(self, device_type: str, custom_params: Optional[Dict] = None) -> DeviceCapabilities:
        """
        Create a new device with realistic parameters
        
        Args:
            device_type: Type of device (smartphone, iot_sensor, vehicle, etc.)
            custom_params: Optional custom parameters to override defaults
            
        Returns:
            DeviceCapabilities object with realistic parameters
        """
        if device_type not in self.config["device_types"]:
            logger.warning(f"Unknown device type: {device_type}, using smartphone defaults")
            device_type = "smartphone"
        
        device_config = self.config["device_types"][device_type].copy()
        
        # Apply custom parameters if provided
        if custom_params:
            self._merge_params(device_config, custom_params)
        
        # Add realistic variance to parameters
        device_config = self._add_parameter_variance(device_config, device_type)
        
        device_id = f"{device_type}_{self._device_counter}"
        self._device_counter += 1
        
        # Handle different memory units (GB vs MB)
        ram_gb = device_config["hardware"].get("ram_gb")
        if ram_gb is None:
            ram_mb = device_config["hardware"].get("ram_mb", 512)
            ram_gb = ram_mb / 1024  # Convert MB to GB
        
        # Handle different battery units and types
        battery_mah = device_config["power"].get("battery_mah")
        if battery_mah is None:
            # For vehicles, use backup battery if available
            battery_mah = device_config["power"].get("backup_battery_mah", 4000)
        
        # Handle network interfaces (some infrastructure devices don't have this field)
        network_interfaces = device_config["network"].get("interfaces", [])
        if not network_interfaces:
            # Provide defaults based on device type
            if device_type == "base_station_5g":
                network_interfaces = ["5g", "fiber"]
            elif device_type == "small_cell":
                network_interfaces = ["5g", "ethernet"]
            elif device_type == "edge_server":
                network_interfaces = ["ethernet", "fiber"]
            else:
                network_interfaces = ["wifi"]  # Default fallback
        
        # Handle max_tx_power (infrastructure devices may not have this)
        max_tx_power = device_config["network"].get("max_tx_power_dbm", {})
        if not max_tx_power:
            # Provide defaults for infrastructure
            if device_type in ["base_station_5g", "small_cell"]:
                max_tx_power = {"5g": 46, "fiber": 0}  # High power for base stations
            else:
                max_tx_power = {"wifi": 20}  # Default WiFi power
        
        # Handle mobility configuration (infrastructure devices may not have this)
        mobility_config = device_config.get("mobility", {})
        mobility_type = mobility_config.get("type", "fixed")  # Default to fixed for infrastructure
        max_speed_kmh = mobility_config.get("max_speed_kmh", 0)  # Default to 0 for fixed devices
        
        # Create device capabilities object
        capabilities = DeviceCapabilities(
            device_id=device_id,
            device_type=device_type,
            cpu_performance=device_config["hardware"]["cpu_performance_gflops"],
            ram_gb=ram_gb,
            battery_mah=battery_mah,
            network_interfaces=network_interfaces,
            max_tx_power=max_tx_power,
            signatures_per_sec=device_config["blockchain"]["signatures_per_sec"],
            stake_weight=device_config["blockchain"]["stake_weight"],
            mobility_type=mobility_type,
            max_speed_kmh=max_speed_kmh
        )
        
        self.devices[device_id] = capabilities
        logger.info(f"Created {device_type} device: {device_id}")
        
        return capabilities
    
    def _merge_params(self, base_config: Dict, custom_params: Dict):
        """Recursively merge custom parameters into base configuration"""
        for key, value in custom_params.items():
            if isinstance(value, dict) and key in base_config:
                self._merge_params(base_config[key], value)
            else:
                base_config[key] = value
    
    def _add_parameter_variance(self, config: Dict, device_type: str) -> Dict:
        """
        Add realistic variance to device parameters
        
        Real devices have manufacturing tolerances and degradation over time
        """
        variance_factors = {
            "smartphone": {"cpu": 0.1, "battery": 0.15, "network": 0.05},
            "iot_sensor": {"cpu": 0.05, "battery": 0.3, "network": 0.1},
            "vehicle": {"cpu": 0.08, "battery": 0.1, "network": 0.03},
            "base_station_5g": {"cpu": 0.02, "battery": 0.05, "network": 0.01},
            "edge_server": {"cpu": 0.03, "battery": 0.02, "network": 0.01}
        }
        
        factors = variance_factors.get(device_type, {"cpu": 0.1, "battery": 0.15, "network": 0.05})
        
        # Add variance to CPU performance
        if "cpu_performance_gflops" in config["hardware"]:
            base_perf = config["hardware"]["cpu_performance_gflops"]
            variance = random.uniform(-factors["cpu"], factors["cpu"])
            config["hardware"]["cpu_performance_gflops"] = base_perf * (1 + variance)
        
        # Add variance to battery capacity (handle different battery types)
        battery_keys = ["battery_mah", "backup_battery_mah"]
        for battery_key in battery_keys:
            if battery_key in config["power"]:
                base_battery = config["power"][battery_key]
                variance = random.uniform(-factors["battery"], factors["battery"])
                config["power"][battery_key] = int(base_battery * (1 + variance))
                break  # Only modify one battery parameter
        
        # Add variance to network performance
        if "signatures_per_sec" in config["blockchain"]:
            base_sigs = config["blockchain"]["signatures_per_sec"]
            variance = random.uniform(-factors["network"], factors["network"])
            config["blockchain"]["signatures_per_sec"] = int(base_sigs * (1 + variance))
        
        return config
    
    def get_environment_conditions(self, environment_type: str = "urban_normal") -> NetworkConditions:
        """
        Get realistic network conditions for given environment
        
        Args:
            environment_type: Type of environment (urban_dense, suburban, rural, etc.)
            
        Returns:
            NetworkConditions object with realistic network parameters
        """
        if environment_type not in self.config["environment_profiles"]:
            logger.warning(f"Unknown environment: {environment_type}, using urban_normal")
            environment_type = "urban_normal"
        
        env_config = self.config["environment_profiles"][environment_type]
        
        # Add realistic time-varying conditions
        base_interference = env_config["interference_floor_dbm"]
        interference_variance = random.uniform(-5, 10)  # Real interference varies
        current_interference = base_interference + interference_variance
        
        return NetworkConditions(
            environment_type=environment_type,
            interference_level=current_interference,
            path_loss_exponent=env_config["path_loss_exponent"],
            node_density=env_config["node_density_per_km2"],
            signal_strength=random.uniform(-110, -60)  # Current RSSI
        )
    
    def calculate_energy_consumption(self, device_id: str, operation: str, duration_sec: float) -> float:
        """
        Calculate realistic energy consumption for device operation
        
        Args:
            device_id: Device identifier
            operation: Type of operation (idle, tx, consensus, etc.)
            duration_sec: Duration of operation in seconds
            
        Returns:
            Energy consumption in millijoules (mJ)
        """
        if device_id not in self.devices:
            logger.error(f"Device not found: {device_id}")
            return 0.0
        
        device = self.devices[device_id]
        device_config = self.config["device_types"][device.device_type]
        
        # Get base power consumption (handle both mW and W units)
        power_profile = device_config["power"].get("consumption_mw", {})
        power_profile_w = device_config["power"].get("consumption_w", {})
        
        # Map operations to power consumption modes
        operation_power_map = {
            "idle": power_profile.get("idle", power_profile_w.get("idle", 0.05) * 1000),
            "cpu_active": power_profile.get("cpu_active", power_profile.get("active", power_profile_w.get("active", 1.0) * 1000)),
            "wifi_tx": power_profile.get("wifi_tx", 300),
            "5g_tx": power_profile.get("5g_tx", 600),
            "consensus": power_profile.get("cpu_active", power_profile.get("active", power_profile_w.get("active", 1.0) * 1000)) * 1.2,  # Extra load
            "signature": power_profile.get("cpu_active", power_profile.get("active", power_profile_w.get("active", 1.0) * 1000)) * 0.5,
            "hash": power_profile.get("cpu_active", power_profile.get("active", power_profile_w.get("active", 1.0) * 1000)) * 0.3
        }
        
        power_mw = operation_power_map.get(operation, power_profile.get("idle", 50))
        
        # Convert to energy (mJ = mW * seconds)
        energy_mj = power_mw * duration_sec
        
        # Add realistic efficiency factors
        efficiency_factor = self._get_efficiency_factor(device.device_type, operation)
        energy_mj *= efficiency_factor
        
        return energy_mj
    
    def _get_efficiency_factor(self, device_type: str, operation: str) -> float:
        """Get efficiency factor based on device type and operation"""
        efficiency_map = {
            "smartphone": {"idle": 1.0, "cpu_active": 0.9, "wifi_tx": 0.8, "5g_tx": 0.7},
            "iot_sensor": {"idle": 1.0, "cpu_active": 0.95, "wifi_tx": 0.85},
            "vehicle": {"idle": 1.0, "cpu_active": 0.95, "5g_tx": 0.9},
            "base_station_5g": {"idle": 1.0, "cpu_active": 0.98, "5g_tx": 0.95},
            "edge_server": {"idle": 1.0, "cpu_active": 0.99, "5g_tx": 0.98}
        }
        
        device_eff = efficiency_map.get(device_type, {"idle": 1.0, "cpu_active": 0.9})
        return device_eff.get(operation, 1.0)
    
    def estimate_battery_lifetime(self, device_id: str, usage_pattern: Dict[str, float]) -> float:
        """
        Estimate realistic battery lifetime based on usage pattern
        
        Args:
            device_id: Device identifier
            usage_pattern: Dictionary of operation -> time_fraction
                          e.g., {"idle": 0.8, "cpu_active": 0.15, "wifi_tx": 0.05}
            
        Returns:
            Estimated battery lifetime in hours
        """
        if device_id not in self.devices:
            logger.error(f"Device not found: {device_id}")
            return 0.0
        
        device = self.devices[device_id]
        device_config = self.config["device_types"][device.device_type]
        
        # Calculate average power consumption
        power_profile = device_config["power"].get("consumption_mw", {})
        power_profile_w = device_config["power"].get("consumption_w", {})
        avg_power_mw = 0.0
        
        for operation, time_fraction in usage_pattern.items():
            # Get power in mW, converting from W if necessary
            operation_power = power_profile.get(operation)
            if operation_power is None:
                operation_power_w = power_profile_w.get(operation, power_profile_w.get("idle", 0.05))
                operation_power = operation_power_w * 1000  # Convert W to mW
            
            if operation_power is None:
                operation_power = power_profile.get("idle", 50)  # Default fallback
            
            avg_power_mw += operation_power * time_fraction
        
        # Get battery capacity
        battery_mah = device.battery_mah
        voltage_v = device_config["power"].get("voltage_v", 3.7)
        battery_energy_wh = (battery_mah * voltage_v) / 1000  # Convert to Wh
        battery_energy_mj = battery_energy_wh * 3600 * 1000  # Convert to mJ
        
        # Calculate lifetime (accounting for battery degradation)
        degradation_factor = 0.8  # 80% usable capacity (realistic)
        usable_energy_mj = battery_energy_mj * degradation_factor
        
        if avg_power_mw > 0:
            lifetime_hours = usable_energy_mj / (avg_power_mw * 3600)
        else:
            lifetime_hours = float('inf')
        
        return lifetime_hours
    
    def get_performance_scaling(self, device_type: str, metric: str, load_factor: float) -> float:
        """
        Get realistic performance scaling under load
        
        Args:
            device_type: Type of device
            metric: Performance metric (throughput, latency, etc.)
            load_factor: Current load as fraction of maximum (0.0 to 1.0)
            
        Returns:
            Performance scaling factor (1.0 = nominal performance)
        """
        # Realistic performance degradation curves
        scaling_curves = {
            "smartphone": {
                "throughput": lambda x: 1.0 - 0.3 * x**2,  # Quadratic degradation
                "latency": lambda x: 1.0 + 0.5 * x,  # Linear increase
                "energy": lambda x: 1.0 + 0.4 * x**1.5  # Superlinear increase
            },
            "iot_sensor": {
                "throughput": lambda x: 1.0 - 0.5 * x**2,  # More sensitive
                "latency": lambda x: 1.0 + 1.0 * x,
                "energy": lambda x: 1.0 + 0.6 * x**1.5
            },
            "base_station_5g": {
                "throughput": lambda x: 1.0 - 0.1 * x**2,  # More resilient
                "latency": lambda x: 1.0 + 0.2 * x,
                "energy": lambda x: 1.0 + 0.2 * x
            }
        }
        
        device_curves = scaling_curves.get(device_type, scaling_curves["smartphone"])
        scaling_func = device_curves.get(metric, lambda x: 1.0)
        
        return max(0.1, scaling_func(load_factor))  # Minimum 10% performance
    
    def get_zone_transition_cost(self, device_id: str, from_zone: str, to_zone: str) -> Dict[str, float]:
        """
        Calculate realistic cost of zone transition
        
        Args:
            device_id: Device identifier
            from_zone: Source zone (5g, manet, bridge)
            to_zone: Target zone (5g, manet, bridge)
            
        Returns:
            Dictionary with energy_mj, latency_ms, success_probability
        """
        if device_id not in self.devices:
            return {"energy_mj": 0, "latency_ms": 0, "success_probability": 0}
        
        device = self.devices[device_id]
        
        # Transition costs based on zone types and device capabilities
        transition_costs = {
            ("manet", "bridge"): {"energy": 10, "latency": 100, "success": 0.95},
            ("bridge", "5g"): {"energy": 15, "latency": 150, "success": 0.98},
            ("5g", "bridge"): {"energy": 12, "latency": 120, "success": 0.97},
            ("bridge", "manet"): {"energy": 8, "latency": 80, "success": 0.93},
            ("5g", "manet"): {"energy": 20, "latency": 200, "success": 0.90},
            ("manet", "5g"): {"energy": 25, "latency": 250, "success": 0.88}
        }
        
        transition_key = (from_zone, to_zone)
        base_cost = transition_costs.get(transition_key, {"energy": 10, "latency": 100, "success": 0.9})
        
        # Adjust based on device capabilities
        device_factor = {
            "smartphone": 1.0,
            "iot_sensor": 1.5,  # Less capable
            "vehicle": 0.8,  # Better connectivity
            "base_station_5g": 0.5,  # Highly capable
            "edge_server": 0.3  # Most capable
        }.get(device.device_type, 1.0)
        
        return {
            "energy_mj": base_cost["energy"] * device_factor,
            "latency_ms": base_cost["latency"] * device_factor,
            "success_probability": min(0.99, base_cost["success"] / device_factor)
        }
    
    def get_consensus_requirements(self, device_id: str, consensus_round: int) -> Dict[str, Any]:
        """
        Get realistic consensus participation requirements
        
        Args:
            device_id: Device identifier
            consensus_round: Current consensus round number
            
        Returns:
            Dictionary with requirements and capabilities
        """
        if device_id not in self.devices:
            return {}
        
        device = self.devices[device_id]
        device_config = self.config["device_types"][device.device_type]
        
        # Base requirements
        base_memory_mb = 5
        base_computation_gflops = 1
        base_network_mbps = 10
        
        # Scale with consensus round (complexity grows)
        round_factor = 1 + (consensus_round % 100) * 0.01  # 1% increase per round, reset every 100
        
        requirements = {
            "memory_required_mb": base_memory_mb * round_factor,
            "computation_required_gflops": base_computation_gflops * round_factor,
            "network_bandwidth_mbps": base_network_mbps * round_factor,
            "estimated_duration_sec": 1.0 + round_factor,
            "energy_cost_mj": self.calculate_energy_consumption(device_id, "consensus", round_factor * 2)
        }
        
        # Device capabilities
        capabilities = {
            "memory_available_mb": device.ram_gb * 1024 * 0.1,  # 10% available for consensus
            "computation_available_gflops": device.cpu_performance * 0.8,  # 80% available
            "can_participate": True
        }
        
        # Check if device can participate
        if (requirements["memory_required_mb"] > capabilities["memory_available_mb"] or
            requirements["computation_required_gflops"] > capabilities["computation_available_gflops"]):
            capabilities["can_participate"] = False
        
        # Battery check for mobile devices
        if device.device_type in ["smartphone", "iot_sensor"]:
            current_battery_percent = self._estimate_current_battery(device_id)
            if current_battery_percent < 20:  # Below 20% battery
                capabilities["can_participate"] = False
        
        return {
            "requirements": requirements,
            "capabilities": capabilities,
            "participation_score": self._calculate_participation_score(device, requirements, capabilities)
        }
    
    def _estimate_current_battery(self, device_id: str) -> float:
        """Estimate current battery level (simplified)"""
        # In real implementation, this would track actual usage
        return random.uniform(20, 100)  # 20-100% battery
    
    def _calculate_participation_score(self, device: DeviceCapabilities, 
                                     requirements: Dict, capabilities: Dict) -> float:
        """Calculate device suitability score for consensus participation"""
        if not capabilities["can_participate"]:
            return 0.0
        
        # Score based on excess capability
        memory_ratio = capabilities["memory_available_mb"] / requirements["memory_required_mb"]
        compute_ratio = capabilities["computation_available_gflops"] / requirements["computation_required_gflops"]
        
        # Weighted score
        capability_score = (memory_ratio * 0.3 + compute_ratio * 0.7)
        stake_score = device.stake_weight
        
        # Device type bonus
        type_bonus = {
            "edge_server": 1.5,
            "base_station_5g": 1.3,
            "vehicle": 1.1,
            "smartphone": 1.0,
            "iot_sensor": 0.7
        }.get(device.device_type, 1.0)
        
        final_score = capability_score * stake_score * type_bonus
        return min(10.0, final_score)  # Cap at 10.0
    
    def generate_simulation_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        Generate a complete simulation scenario with realistic device distribution
        
        Args:
            scenario_name: Name of predefined scenario (small_campus, medium_district, etc.)
            
        Returns:
            Complete scenario configuration
        """
        if scenario_name not in self.config["simulation_scenarios"]:
            logger.warning(f"Unknown scenario: {scenario_name}, using small_campus")
            scenario_name = "small_campus"
        
        scenario_config = self.config["simulation_scenarios"][scenario_name].copy()
        devices = []
        
        # Create devices according to distribution
        for device_type, count in scenario_config["node_distribution"].items():
            for i in range(count):
                device = self.create_device(device_type)
                devices.append({
                    "device_id": device.device_id,
                    "device_type": device.device_type,
                    "capabilities": device.__dict__
                })
        
        # Add environment conditions
        env_type = scenario_config["environment"]
        environment = self.get_environment_conditions(env_type)
        
        scenario_config["devices"] = devices
        scenario_config["environment_conditions"] = environment.__dict__
        scenario_config["total_devices"] = len(devices)
        scenario_config["name"] = scenario_name
        
        return scenario_config
    
    def get_device_stats(self) -> Dict[str, Any]:
        """Get statistics about managed devices"""
        stats = {
            "total_devices": len(self.devices),
            "by_type": {},
            "total_compute_gflops": 0,
            "total_signatures_per_sec": 0,
            "avg_battery_mah": 0
        }
        
        for device in self.devices.values():
            # Count by type
            if device.device_type not in stats["by_type"]:
                stats["by_type"][device.device_type] = 0
            stats["by_type"][device.device_type] += 1
            
            # Aggregate capabilities
            stats["total_compute_gflops"] += device.cpu_performance
            stats["total_signatures_per_sec"] += device.signatures_per_sec
            stats["avg_battery_mah"] += device.battery_mah
        
        if len(self.devices) > 0:
            stats["avg_battery_mah"] /= len(self.devices)
        
        return stats 
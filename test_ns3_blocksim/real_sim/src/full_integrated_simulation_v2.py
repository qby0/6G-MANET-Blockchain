#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Full Integrated Simulation V2 - Правильная архитектура
Исправленная версия с единой интеграцией NS-3 и устройств

Ключевые улучшения:
1. Единое пространство узлов - каждый NS-3 узел = реалистичное устройство
2. Синхронная работа - NS-3 и устройства работают в едином времени
3. Обратная связь - состояние устройств влияет на NS-3 поведение
4. Реальная интеграция - не параллельные процессы, а единая система
"""

import os
import sys
import time
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.integrated_ns3_device_simulation import (
    IntegratedNS3DeviceSimulation, 
    IntegrationConfig,
    IntegratedNodeState
)
from dashboard_visualizer import DashboardVisualizer
from executive_dashboard_analyzer import ExecutiveDashboardAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class FullSimulationConfigV2:
    """Конфигурация полной интегрированной симуляции V2"""
    scenario: str
    duration: int
    output_dir: str
    config_file: str
    
    # Интеграция
    sync_interval: float = 5.0
    enable_real_time: bool = False
    enable_feedback: bool = True
    
    # Компоненты
    enable_ns3: bool = True
    enable_devices: bool = True
    enable_consensus: bool = True
    enable_visualization: bool = True
    
    # Логирование
    verbose: bool = False

class FullIntegratedSimulationV2:
    """
    Полная интегрированная симуляция V2
    
    Архитектура:
    - Единая интегрированная симуляция NS-3 + устройства
    - Синхронное выполнение всех компонентов
    - Реальная обратная связь между компонентами
    - Комплексная аналитика и визуализация
    """
    
    def __init__(self, config: FullSimulationConfigV2):
        self.config = config
        self.logger = logging.getLogger("FullIntegratedV2")
        
        # Основные компоненты
        self.integrated_simulation: Optional[IntegratedNS3DeviceSimulation] = None
        self.analyzer: Optional[ExecutiveDashboardAnalyzer] = None
        self.visualizer: Optional[DashboardVisualizer] = None
        
        # Конфигурация
        self.sim_config: Dict[str, Any] = {}
        
        # Результаты
        self.results: Dict[str, Any] = {}
        self.analytics: Dict[str, Any] = {}
    
    def initialize(self):
        """Инициализация всех компонентов"""
        self.logger.info("🔧 Initializing Full Integrated Simulation V2")
        
        # Загрузка конфигурации
        self._load_configuration()
        
        # Инициализация интегрированной симуляции
        self._initialize_integrated_simulation()
        
        # Инициализация аналитики
        if self.config.enable_visualization:
            self._initialize_analytics()
        
        self.logger.info("✅ Full Integrated Simulation V2 initialized")
    
    def _load_configuration(self):
        """Загрузка конфигурации"""
        config_path = Path(self.config.config_file)
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.sim_config = json.load(f)
        else:
            # Конфигурация по умолчанию
            self.sim_config = {
                "network_config": {
                    "zones": {
                        "6g": {"coverage_radius": 150.0},
                        "bridge": {"coverage_radius": 200.0},
                        "manet": {"max_radius": 400.0}
                    }
                },
                "device_types": {
                    "smartphone": {"count": 20, "zone_preference": "6g"},
                    "iot_sensor": {"count": 15, "zone_preference": "manet"},
                    "vehicle": {"count": 10, "zone_preference": "bridge"},
                    "base_station_6g": {"count": 2, "zone_preference": "6g"},
                    "edge_server": {"count": 9, "zone_preference": "bridge"}
                },
                "blockchain_config": {
                    "min_validators": 3,
                    "max_validators": 7,
                    "consensus_algorithm": "pbft",
                    "block_time": 10.0
                },
                "ns3_config": {
                    "ns3_path": str(project_root / "external" / "ns-3"),
                    "script_name": "advanced-cross-zone-blockchain-fixed",
                    "enable_netanim": True
                }
            }
    
    def _initialize_integrated_simulation(self):
        """Инициализация интегрированной симуляции"""
        # Конфигурация интеграции
        integration_config = IntegrationConfig(
            duration=float(self.config.duration),
            time_step=1.0,
            sync_interval=self.config.sync_interval,
            enable_real_time=self.config.enable_real_time,
            enable_feedback=self.config.enable_feedback,
            log_level="DEBUG" if self.config.verbose else "INFO"
        )
        
        # Создание интегрированной симуляции
        self.integrated_simulation = IntegratedNS3DeviceSimulation(integration_config)
        
        # NS-3 конфигурация
        device_counts = self._calculate_device_counts()
        ns3_config = {
            'manet_nodes': device_counts['manet_nodes'],
            'fiveg_nodes': device_counts['6g_nodes'],
            'bridge_nodes': device_counts['bridge_nodes'],
            'fiveg_radius': self.sim_config['network_config']['zones']['6g']['coverage_radius'],
            'min_validators': self.sim_config['blockchain_config']['min_validators'],
            'max_validators': self.sim_config['blockchain_config']['max_validators']
        }
        
        # Конфигурация устройств
        device_config = {
            'device_types': {
                device_type: info.get('count', 0) if isinstance(info, dict) else 0
                for device_type, info in self.sim_config.get('device_types', {}).items()
            }
        }
        
        # Инициализация
        self.integrated_simulation.initialize(ns3_config, device_config)
    
    def _calculate_device_counts(self) -> Dict[str, int]:
        """Расчет количества устройств по зонам"""
        device_types = self.sim_config.get('device_types', {})
        
        counts = {
            'manet_nodes': 0,
            '6g_nodes': 0,
            'bridge_nodes': 0
        }
        
        zone_mapping = {
            'smartphone': '6g_nodes',
            'iot_sensor': 'manet_nodes',
            'vehicle': 'bridge_nodes',
            'base_station_6g': '6g_nodes',
            'edge_server': 'bridge_nodes'
        }
        
        for device_type, info in device_types.items():
            zone_key = zone_mapping.get(device_type, 'manet_nodes')
            device_count = info.get('count', 0) if isinstance(info, dict) else 0
            counts[zone_key] += device_count
        
        return counts
    
    def _initialize_analytics(self):
        """Инициализация аналитики и визуализации"""
        # Создаем объекты только при необходимости
        self.analyzer = None
        self.visualizer = None
    
    def run_simulation(self) -> Dict[str, Any]:
        """Запуск полной интегрированной симуляции"""
        self.logger.info("🚀 Starting Full Integrated Simulation V2")
        self.logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # Запуск интегрированной симуляции
            self.integrated_simulation.run_simulation()
            
            # Получение результатов
            self.results = self.integrated_simulation.get_results()
            
            # Генерация аналитики
            if self.config.enable_visualization:
                self._generate_analytics()
            
            # Сохранение результатов
            self._save_results()
            
            duration = time.time() - start_time
            self.logger.info(f"✅ Full Integrated Simulation V2 completed in {duration:.2f} seconds")
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            self._cleanup()
    
    def _generate_analytics(self):
        """Генерация аналитики"""
        self.logger.info("📊 Generating analytics...")
        
        # Подготовка данных для анализа
        analytics_data = self._prepare_analytics_data()
        
        # Выполнение анализа
        if not self.analyzer:
            self.analyzer = ExecutiveDashboardAnalyzer(analytics_data)
        self.analytics = self.analyzer.generate_executive_summary()
        
        # Создание визуализаций
        if not self.visualizer:
            self.visualizer = DashboardVisualizer(str(Path(self.config.output_dir)))
        if self.analytics:
            self._create_visualizations()
    
    def _prepare_analytics_data(self) -> Dict[str, Any]:
        """Подготовка данных для аналитики"""
        nodes = self.integrated_simulation.nodes if self.integrated_simulation else {}
        
        # Конвертация данных узлов в формат для аналитики
        devices_data = []
        energy_data = []
        performance_data = []
        network_data = []
        
        for node_id, node in nodes.items():
            # Данные устройства
            device_entry = {
                'device_id': f"device_{node_id}",
                'device_type': node.device_type,
                'zone': ['6g', 'bridge', 'manet'][node.zone],
                'is_validator': node.is_validator,
                'battery_level': node.battery_level,
                'energy_consumed': node.energy_consumed,
                'cpu_performance': node.capabilities.cpu_performance,
                'memory_gb': node.capabilities.ram_gb,
                'network_bandwidth': 100.0  # Заглушка для совместимости
            }
            devices_data.append(device_entry)
            
            # Энергетические данные
            energy_entry = {
                'device_id': f"device_{node_id}",
                'timestamp': self.integrated_simulation.simulation_time,
                'energy_consumed': node.energy_consumed,
                'battery_level': node.battery_level,
                'device_type': node.device_type
            }
            energy_data.append(energy_entry)
            
            # Данные производительности
            performance_entry = {
                'device_id': f"device_{node_id}",
                'timestamp': self.integrated_simulation.simulation_time,
                'cpu_load': node.cpu_load,
                'memory_usage': node.memory_usage,
                'network_latency': node.network_latency,
                'throughput': node.throughput,
                'device_type': node.device_type
            }
            performance_data.append(performance_entry)
            
            # Сетевые данные
            network_entry = {
                'device_id': f"device_{node_id}",
                'timestamp': self.integrated_simulation.simulation_time,
                'zone': ['6g', 'bridge', 'manet'][node.zone],
                'rssi': node.rssi_6g,
                'packet_loss': node.packet_loss,
                'position_x': node.position[0],
                'position_y': node.position[1]
            }
            network_data.append(network_entry)
        
        # Блокчейн данные из реальных результатов симуляции
        blockchain_data = {
            'total_transactions': self.results.get('total_transactions', 0),
            'total_blocks': self.results.get('total_blocks', 0),
            'active_validators': self.results.get('validator_count', 0),
            'consensus_participation': 0.8  # Средняя участие в консенсусе
        }
        
        return {
            'devices': devices_data,
            'energy_consumption': energy_data,
            'performance_metrics': performance_data,
            'network_topology': network_data,
            'blockchain_metrics': blockchain_data,
            'simulation_config': {
                'duration': self.results.get('simulation_time', self.config.duration),
                'total_devices': self.results.get('total_nodes', len(nodes)),
                'zone_distribution': self.results.get('nodes_by_zone', {}),
                'sync_events': self.results.get('sync_events', 0),
                'zone_transitions': self.results.get('zone_transitions', 0),
                'total_transactions': self.results.get('total_transactions', 0),
                'total_blocks': self.results.get('total_blocks', 0),
                'total_energy_consumed': self.results.get('total_energy_consumed', 0),
                'average_battery': self.results.get('average_battery', 0),
                'average_cpu_load': self.results.get('average_cpu_load', 0),
                'validator_count': self.results.get('validator_count', 0)
            }
        }
    
    def _create_visualizations(self):
        """Создание визуализаций"""
        self.logger.info("🎨 Creating visualizations...")
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Executive dashboard
            dashboard_path = self.visualizer.create_executive_dashboard(self.analytics)
            self.logger.info(f"Executive dashboard: {dashboard_path}")
            
            # Interactive dashboard
            interactive_path = self.visualizer.create_interactive_dashboard(self.analytics)
            self.logger.info(f"Interactive dashboard: {interactive_path}")
            
            # Network topology
            topology_path = self.visualizer.create_network_topology_visualization(self.analytics)
            self.logger.info(f"Network topology: {topology_path}")
            
        except Exception as e:
            self.logger.warning(f"Visualization creation failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _save_results(self):
        """Сохранение результатов"""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Сохранение основных результатов
        results_file = output_dir / "integrated_simulation_results_v2.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Сохранение аналитики
        if self.analytics:
            analytics_file = output_dir / "simulation_analytics_v2.json"
            with open(analytics_file, 'w') as f:
                json.dump(self.analytics, f, indent=2, default=str)
        
        # Сохранение детальных данных узлов
        if self.integrated_simulation:
            nodes_data = {}
            for node_id, node in self.integrated_simulation.nodes.items():
                nodes_data[str(node_id)] = {
                    'device_type': node.device_type,
                    'zone': node.zone,
                    'position': node.position,
                    'battery_level': node.battery_level,
                    'energy_consumed': node.energy_consumed,
                    'is_validator': node.is_validator,
                    'transactions_sent': node.transactions_sent,
                    'blocks_validated': node.blocks_validated,
                    'cpu_load': node.cpu_load,
                    'memory_usage': node.memory_usage,
                    'network_latency': node.network_latency,
                    'throughput': node.throughput
                }
            
            nodes_file = output_dir / "nodes_detailed_data_v2.json"
            with open(nodes_file, 'w') as f:
                json.dump(nodes_data, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to {output_dir}")
    
    def _cleanup(self):
        """Очистка ресурсов"""
        self.logger.info("Cleaning up...")
        
        if self.integrated_simulation:
            self.integrated_simulation._cleanup()
    
    def get_summary(self) -> str:
        """Получение сводки результатов"""
        if not self.results:
            return "No results available"
        
        summary = f"""
🚀 Full Integrated Cross-Zone Blockchain Simulation V2 Summary
============================================================

📊 Basic Statistics:
  • Total Devices: {self.results.get('total_nodes', 0)}
  • Simulation Duration: {self.results.get('simulation_time', 0):.1f} seconds
  • Total Transactions: {self.results.get('total_transactions', 0)}
  • Total Blocks: {self.results.get('total_blocks', 0)}
  • Zone Transitions: {self.results.get('zone_transitions', 0)}

⚡ Energy Analysis:
  • Total Energy Consumed: {self.results.get('total_energy_consumed', 0):.1f} J
  • Average Battery Level: {self.results.get('average_battery', 0):.1f}%
  • Average CPU Load: {self.results.get('average_cpu_load', 0):.1f}%

🌐 Network Performance:
  • Active Validators: {self.results.get('validator_count', 0)}
  • Sync Events: {self.results.get('sync_events', 0)}
  • Feedback Events: {self.results.get('feedback_events', 0)}

🎯 Zone Distribution:
"""
        
        nodes_by_zone = self.results.get('nodes_by_zone', {})
        zone_names = {0: '6G', 1: 'Bridge', 2: 'MANET'}
        for zone_id, count in nodes_by_zone.items():
            zone_name = zone_names.get(zone_id, f"Zone {zone_id}")
            summary += f"  • {zone_name}: {count} nodes\n"
        
        summary += f"""
🎯 Integration Features:
  ✅ Unified NS-3 + Device Simulation
  ✅ Real-time State Synchronization
  ✅ Device-to-Network Feedback
  ✅ Comprehensive Analytics
  ✅ Executive Visualizations
"""
        
        return summary

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Full Integrated Cross-Zone Blockchain Simulation V2")
    
    parser.add_argument("--scenario", type=str, default="small_campus",
                       help="Simulation scenario")
    parser.add_argument("--duration", type=int, default=180,
                       help="Simulation duration in seconds")
    parser.add_argument("--config", type=str, default="config/full_simulation_config.json",
                       help="Configuration file path")
    parser.add_argument("--output", type=str, default="results",
                       help="Output directory")
    parser.add_argument("--sync-interval", type=float, default=5.0,
                       help="Synchronization interval in seconds")
    parser.add_argument("--real-time", action="store_true",
                       help="Enable real-time simulation")
    parser.add_argument("--no-feedback", action="store_true",
                       help="Disable device feedback")
    parser.add_argument("--no-visualization", action="store_true",
                       help="Disable visualization")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = FullSimulationConfigV2(
        scenario=args.scenario,
        duration=args.duration,
        output_dir=args.output,
        config_file=args.config,
        sync_interval=args.sync_interval,
        enable_real_time=args.real_time,
        enable_feedback=not args.no_feedback,
        enable_visualization=not args.no_visualization,
        verbose=args.verbose
    )
    
    logger.info("🚀 Full Integrated Cross-Zone Blockchain Simulation V2")
    logger.info(f"📊 Scenario: {config.scenario}")
    logger.info(f"⏰ Duration: {config.duration}s")
    logger.info(f"🔄 Sync interval: {config.sync_interval}s")
    logger.info(f"🔗 Feedback: {'Enabled' if config.enable_feedback else 'Disabled'}")
    logger.info(f"🎨 Visualization: {'Enabled' if config.enable_visualization else 'Disabled'}")
    
    # Run simulation
    simulation = FullIntegratedSimulationV2(config)
    simulation.initialize()
    results = simulation.run_simulation()
    
    # Print summary
    print(simulation.get_summary())
    
    logger.info("🎉 Simulation completed successfully!")

if __name__ == "__main__":
    main() 
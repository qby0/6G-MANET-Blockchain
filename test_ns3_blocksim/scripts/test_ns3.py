#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования работоспособности NS-3 в рамках проекта.
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime
from pathlib import Path

# Добавляем путь к моделям
sys.path.append(str(Path(__file__).parent.parent))

from models.ns3_adapter import NS3Adapter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ns3_test.log")
    ]
)
logger = logging.getLogger("NS3Test")

def create_test_scenario():
    """Создает тестовый сценарий симуляции."""
    nodes = {
        "base_station_1": {
            "type": "base_station",
            "position": (0.0, 0.0, 10.0),
            "capabilities": {"computational_power": 100, "storage": 1000}
        },
        "node_1": {
            "type": "regular",
            "position": (100.0, 100.0, 1.5),
            "capabilities": {"computational_power": 10, "storage": 50, "battery": 0.9}
        },
        "node_2": {
            "type": "validator",
            "position": (200.0, 200.0, 1.5),
            "capabilities": {"computational_power": 20, "storage": 100, "battery": 0.8}
        }
    }
    
    links = {
        "bs1_n1": {
            "nodes": ["base_station_1", "node_1"],
            "quality": 0.9,
            "bandwidth": 100.0
        },
        "n1_n2": {
            "nodes": ["node_1", "node_2"],
            "quality": 0.7,
            "bandwidth": 50.0
        }
    }
    
    params = {
        "simulation_time": 10.0,  # Короткое время для тестирования
        "wifi_standard": "80211g",
        "propagation_model": "friis",
        "routing_protocol": "aodv"
    }
    
    return nodes, links, params

def find_ns3_path():
    """
    Автоматически определяет путь к NS-3 в рамках проекта.
    
    Returns:
        str: Путь к NS-3 или None, если не найден
    """
    # Путь к текущему скрипту
    current_script = Path(__file__)
    
    # Путь к корневой директории проекта
    project_root = current_script.parent.parent
    
    # Возможные пути к NS-3 в проекте
    potential_paths = [
        project_root / "external" / "ns-3",
        project_root.parent / "external" / "ns-3",
        project_root.parent / "ns-3",
    ]
    
    # Проверяем каждый потенциальный путь
    for path in potential_paths:
        if path.exists() and (path / "ns3").exists():
            logger.info(f"Automatically found NS-3 path: {path}")
            return str(path)
    
    return None

def main():
    """Основная функция тестирования NS-3."""
    parser = argparse.ArgumentParser(description="Тестирование работоспособности NS-3.")
    parser.add_argument("--ns3-path", type=str, help="Путь к директории NS-3")
    parser.add_argument("--output-dir", type=str, default=None, 
                      help="Директория для сохранения результатов")
    parser.add_argument("--duration", type=float, default=10.0,
                      help="Продолжительность симуляции в секундах")
    
    args = parser.parse_args()
    
    # Определяем путь к NS-3
    ns3_path = args.ns3_path
    if not ns3_path:
        # Пытаемся автоматически определить путь
        ns3_path = find_ns3_path()
        if not ns3_path:
            # Если не найден, пробуем переменную окружения
            ns3_path = os.environ.get("NS3_DIR")
            if not ns3_path:
                logger.error("Failed to automatically detect NS-3 path. Please use --ns3-path or set the NS3_DIR environment variable")
                sys.exit(1)
    
    # Проверяем существование директории NS-3
    if not os.path.exists(ns3_path):
        logger.error(f"NS-3 directory not found: {ns3_path}")
        sys.exit(1)
    
    logger.info(f"Using NS-3 from directory: {ns3_path}")
    
    # Создаем выходную директорию, если не указана
    if not args.output_dir:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = os.path.join(Path(__file__).parent.parent, "results", f"test_ns3_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = args.output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Results will be saved to: {output_dir}")
    
    try:
        # Создаем адаптер NS-3
        logger.info("Initializing NS-3 adapter...")
        adapter = NS3Adapter(ns3_path)
        
        # Создаем скрипт для симуляции MANET
        logger.info("Creating MANET simulation script...")
        script_path = adapter.create_ns3_manet_script()
        
        # Проверка базовой работоспособности NS-3
        logger.info("Checking NS-3 functionality...")
        if not os.path.exists(os.path.join(ns3_path, "ns3")):
            logger.error("NS-3 executable not found. Make sure NS-3 is installed correctly.")
            sys.exit(1)
        
        # Тест компиляции скрипта
        logger.info("Testing script compilation...")
        if not adapter.compile_ns3_script("manet-blockchain-sim"):
            logger.error("Error compiling NS-3 script.")
            sys.exit(1)
        
        # Создаем тестовый сценарий
        logger.info("Creating test simulation scenario...")
        nodes, links, params = create_test_scenario()
        
        # Создаем файл сценария
        logger.info("Creating scenario file for NS-3...")
        scenario_file = adapter.create_scenario_file(nodes, links, params)
        
        # Запускаем симуляцию
        logger.info(f"Running test simulation for {args.duration} seconds...")
        results = adapter.run_simulation(
            scenario_file, 
            duration=args.duration,
            time_resolution=0.1,
            output_dir=output_dir
        )
        
        # Сохраняем результаты
        results_file = os.path.join(output_dir, "test_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Testing completed successfully. Results saved to {results_file}")
        logger.info("Brief simulation results:")
        logger.info(f"- Simulation time: {results.get('simulation_time', 'N/A')}")
        logger.info(f"- Packets sent: {results.get('network_stats', {}).get('packets_sent', 'N/A')}")
        logger.info(f"- Packets received: {results.get('network_stats', {}).get('packets_received', 'N/A')}")
        logger.info(f"- Average delay: {results.get('network_stats', {}).get('average_delay', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Error testing NS-3: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
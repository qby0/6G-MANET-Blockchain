#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска NS-3 симуляции 5G базовой станции с MANET и блокчейном.
Обеспечивает удобный интерфейс для запуска C++ симуляции из NS-3.
"""
import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("5GBasestationSimulation")


def find_ns3_path():
    """
    Автоматически определяет путь к NS-3 в проекте.
    
    Returns:
        str: Путь к NS-3 или None, если не найден
    """
    current_script = Path(__file__)
    project_root = current_script.parent.parent
    
    # Проверяем внешний NS-3
    ns3_path = project_root / "external" / "ns-3"
    if ns3_path.exists() and (ns3_path / "ns3").exists():
        logger.info(f"Found NS-3 at: {ns3_path}")
        return str(ns3_path)
    
    logger.error("NS-3 not found in project")
    return None


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="5G Base Station + MANET + Blockchain Simulation"
    )
    
    parser.add_argument(
        "--nodes", 
        type=int, 
        default=16, 
        help="Количество MANET узлов (по умолчанию: 16)"
    )
    parser.add_argument(
        "--duration", 
        type=float, 
        default=45.0, 
        help="Длительность симуляции в секундах (по умолчанию: 45)"
    )
    parser.add_argument(
        "--basestation-range", 
        type=float, 
        default=300.0, 
        help="Радиус покрытия 5G базовой станции в метрах (по умолчанию: 300)"
    )
    parser.add_argument(
        "--output-file", 
        type=str, 
        default="", 
        help="Имя файла NetAnim анимации (по умолчанию: auto-generated)"
    )
    parser.add_argument(
        "--ns3-path", 
        type=str, 
        default="", 
        help="Путь к директории NS-3 (автоопределение если не указано)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="../results/5g_basestation", 
        help="Directory for saving results"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug messages"
    )
    parser.add_argument(
        "--quick", 
        action="store_true", 
        help="Quick simulation (15 sec, 8 nodes)"
    )
    
    return parser.parse_args()


def prepare_output_paths(args):
    """Prepare paths for output files."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    # Create results directory relative to current script
    current_script = Path(__file__)
    project_root = current_script.parent.parent
    
    # Determine absolute path to results directory
    if args.output_dir.startswith("../"):
        output_dir = project_root / args.output_dir[3:]  # Remove "../"
    else:
        output_dir = Path(args.output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate animation filename if not specified
    if not args.output_file:
        animation_file = f"5g_basestation_sim_{timestamp}.xml"
    else:
        animation_file = args.output_file
    
    # Full absolute path to animation file
    animation_path = output_dir / animation_file
    
    return str(animation_path.absolute()), str(output_dir.absolute())


def run_ns3_simulation(ns3_path, args, animation_path):
    """Run NS-3 simulation."""
    logger.info("Starting NS-3 5G Base Station simulation...")
    
    # Переходим в директорию NS-3
    original_cwd = os.getcwd()
    os.chdir(ns3_path)
    
    try:
        # Формируем команду
        cmd = [
            "./ns3", "run",
            f"scratch/simple-manet-5g-basestation",
            "--",
            f"--nNodes={args.nodes}",
            f"--simulationTime={args.duration}",
            f"--bsRange={args.basestation_range}",
            f"--outputFile={animation_path}"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        logger.info(f"Parameters:")
        logger.info(f"  - MANET Nodes: {args.nodes}")
        logger.info(f"  - Duration: {args.duration} seconds")
        logger.info(f"  - 5G Base Station Range: {args.basestation_range}m")
        logger.info(f"  - Animation File: {animation_path}")
        
        # Запускаем симуляцию
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=args.duration + 60  # Добавляем буфер времени
        )
        
        if result.returncode == 0:
            logger.info("NS-3 simulation completed successfully!")
            if result.stdout:
                print("\n" + "="*60)
                print("SIMULATION OUTPUT:")
                print("="*60)
                print(result.stdout)
        else:
            logger.error(f"NS-3 simulation failed with return code: {result.returncode}")
            if result.stderr:
                logger.error(f"Error output: {result.stderr}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"Simulation timed out after {args.duration + 60} seconds")
        return False
    except Exception as e:
        logger.error(f"Error running NS-3 simulation: {e}")
        return False
    finally:
        os.chdir(original_cwd)


def save_simulation_summary(args, animation_path, output_dir, success):
    """Save simulation summary."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    summary = {
        "timestamp": timestamp,
        "simulation_type": "5G_Base_Station_MANET_Blockchain",
        "parameters": {
            "nodes": args.nodes,
            "duration": args.duration,
            "basestation_range": args.basestation_range,
            "validators_percentage": 25  # Из кода C++
        },
        "files": {
            "animation_file": animation_path if success else None,
            "output_directory": output_dir
        },
        "success": success,
        "features": [
            "5G microcell base station (300m range)",
            "MANET with WiFi ad-hoc connectivity", 
            "AODV routing protocol",
            "Blockchain with 25% validator nodes",
            "Real-time 5G coverage visualization",
            "Energy consumption tracking",
            "Dynamic load balancing"
        ]
    }
    
    summary_file = Path(output_dir) / f"summary_{timestamp}.json"
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Simulation summary saved to: {summary_file}")
    except Exception as e:
        logger.error(f"Failed to save summary: {e}")


def main():
    """Main function."""
    args = parse_arguments()
    
    # Настройка логирования
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Быстрая симуляция
    if args.quick:
        args.nodes = 8
        args.duration = 15.0
        args.basestation_range = 250.0
        logger.info("Quick simulation mode: 8 nodes, 15 seconds, 250m range")
    
    # Определяем путь к NS-3
    ns3_path = args.ns3_path if args.ns3_path else find_ns3_path()
    if not ns3_path:
        logger.error("NS-3 not found. Please specify --ns3-path or install NS-3 in external/ns-3")
        return 1
    
    # Подготавливаем пути
    animation_path, output_dir = prepare_output_paths(args)
    
    logger.info("🎬 Starting 5G Base Station + MANET + Blockchain Simulation")
    logger.info("=" * 65)
    
    # Запускаем симуляцию
    success = run_ns3_simulation(ns3_path, args, animation_path)
    
    # Сохраняем резюме
    save_simulation_summary(args, animation_path, output_dir, success)
    
    if success:
        logger.info("\n✅ Simulation completed successfully!")
        logger.info(f"📁 Results saved to: {output_dir}")
        logger.info(f"🎞️  Animation file: {animation_path}")
        logger.info("\n🚀 To view animation:")
        logger.info(f"   1. Install NetAnim viewer")
        logger.info(f"   2. Open: {animation_path}")
        logger.info("\n📊 Features visualized:")
        logger.info("   • 5G base station coverage area")
        logger.info("   • Node mobility and MANET connectivity")
        logger.info("   • Blockchain validator activity")
        logger.info("   • Energy consumption over time")
        logger.info("   • Dynamic load balancing")
        return 0
    else:
        logger.error("\n❌ Simulation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
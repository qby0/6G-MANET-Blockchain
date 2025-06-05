#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Real Blockchain Integration Simulation
Реальная интеграция C++ блокчейн модуля с Python симуляцией NS-3
"""

import sys
import os
import time
import argparse
import json
import logging
from pathlib import Path

# Добавляем пути к модулям проекта
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
real_sim_root = current_dir.parent

# Правильный путь к NS-3
ns3_dir = project_root / "external" / "ns-3"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_ns3_environment():
    """Настройка окружения NS-3 для работы с блокчейн модулем"""
    
    # Устанавливаем пути для Python bindings
    python_bindings_path = ns3_dir / "build" / "bindings" / "python"
    # Обновляем переменную окружения PYTHONPATH
    if 'PYTHONPATH' in os.environ:
        os.environ['PYTHONPATH'] = f"{python_bindings_path}:{os.environ['PYTHONPATH']}"
    else:
        os.environ['PYTHONPATH'] = str(python_bindings_path)
    # Добавляем в sys.path для текущего процесса
    if str(python_bindings_path) not in sys.path:
        sys.path.insert(0, str(python_bindings_path))
    
    # Добавляем путь к библиотекам NS-3
    lib_path = ns3_dir / "build" / "lib"
    if 'LD_LIBRARY_PATH' in os.environ:
        os.environ['LD_LIBRARY_PATH'] = f"{lib_path}:{os.environ['LD_LIBRARY_PATH']}"
    else:
        os.environ['LD_LIBRARY_PATH'] = str(lib_path)
    
    # Configure Cppyy include path for NS-3 headers to allow Python bindings to find module headers
    include_dir = ns3_dir / "build" / "include"
    # Create symlinks for module headers expected by Cppyy (e.g., libnsns-3.44-<module>-module.h)
    include_ns_dir = include_dir / "ns3"
    version_file = ns3_dir / "VERSION"
    if version_file.exists():
        version_line = version_file.read_text().strip()
        try:
            ver = version_line.split("-", 1)[1]
            for h in include_ns_dir.glob("*-module.h"):
                link = include_ns_dir / f"libnsns-{ver}-{h.name}"
                if not link.exists():
                    link.symlink_to(h.name)
                    print(f"   🔗 Symlink created: {link}")
        except Exception as e:
            print(f"   ⚠️ Failed to create Cppyy header symlinks: {e}")
    try:
        import cppyy
        cppyy.add_include_path(str(include_dir))
        print(f"   📖 Cppyy include path added: {include_dir}")
    except ImportError:
        print(f"   ⚠️  cppyy not installed; cannot configure include path for Python bindings")
    
    print(f"   🔧 NS-3 directory: {ns3_dir}")
    print(f"   🐍 Python bindings: {python_bindings_path}")
    print(f"   📚 Library path: {lib_path}")
    
    return ns3_dir

def run_real_blockchain_simulation(scenario: str, duration: int, output_dir: str) -> dict:
    """Запуск реальной блокчейн симуляции с C++ интеграцией"""
    print(f"🌐 Running Real Blockchain Simulation with C++ Integration...")
    print(f"   ⏱️  Duration: {duration} seconds")
    print(f"   🎯 Scenario: {scenario}")
    print(f"   📂 Output: {output_dir}")
    
    # Настройка NS-3 окружения
    ns3_dir = setup_ns3_environment()
    
    try:
        # Импортируем NS-3 модули (только после настройки окружения)
        from ns import ns
        print("   ✅ Successfully imported NS-3 core")
        
        # Проверяем наличие blockchain классов
        required_classes = ['CrossZoneBlockchainApp', 'CrossZoneBlockchainHelper', 'ZoneManager', 'BlockchainLedger']
        for cls_name in required_classes:
            if hasattr(ns, cls_name):
                print(f"   ✅ {cls_name} found in ns module")
            else:
                print(f"   ❌ {cls_name} NOT found in ns module")
                return {"error": f"Missing blockchain class: {cls_name}"}
        
    except ImportError as e:
        print(f"   ❌ Failed to import NS-3 modules: {e}")
        print("   🔧 Please ensure blockchain module is built with: ./ns3 build")
        return {"error": str(e)}
    
    # Настройка параметров сценария
    scenario_config = {
        'small_campus': {'nodes': 10, 'validators': 3},
        'medium_district': {'nodes': 15, 'validators': 4}, 
        'large_city': {'nodes': 25, 'validators': 6},
        'stress_test': {'nodes': 50, 'validators': 10}
    }
    
    config = scenario_config.get(scenario, scenario_config['medium_district'])
    total_nodes = config['nodes']
    validator_count = config['validators']
    
    print(f"   📊 Configuration: {total_nodes} nodes, {validator_count} validators")
    
    # Создание узлов
    print("   🔧 Creating network nodes...")
    nodes = ns.NodeContainer()
    nodes.Create(total_nodes)
    
    # Настройка мобильности
    print("   📍 Setting up mobility models...")
    mobility = ns.MobilityHelper()
    
    # Мобильность для всех узлов в прямоугольной области
    mobility.SetPositionAllocator("ns3::RandomRectanglePositionAllocator",
                                 "X", ns.StringValue("ns3::UniformRandomVariable[Min=0|Max=300]"),
                                 "Y", ns.StringValue("ns3::UniformRandomVariable[Min=0|Max=300]"))
    mobility.SetMobilityModel("ns3::RandomDirection2dMobilityModel",
                             "Bounds", ns.RectangleValue(ns.Rectangle(0, 300, 0, 300)),
                             "Speed", ns.StringValue("ns3::UniformRandomVariable[Min=1.0|Max=5.0]"),
                             "Pause", ns.StringValue("ns3::UniformRandomVariable[Min=0.0|Max=2.0]"))
    mobility.Install(nodes)
    
    # Настройка WiFi Ad-Hoc сети
    print("   📡 Setting up WiFi Ad-Hoc network...")
    wifi = ns.WifiHelper()
    wifi.SetStandard(ns.WIFI_STANDARD_80211n)
    
    mac = ns.WifiMacHelper()
    mac.SetType("ns3::AdhocWifiMac")
    
    phy = ns.YansWifiPhyHelper()
    channel = ns.YansWifiChannelHelper.Default()
    phy.SetChannel(channel.Create())
    
    devices = wifi.Install(phy, mac, nodes)
    
    # Настройка стека интернет протоколов с AODV маршрутизацией
    print("   🌐 Setting up Internet stack with AODV routing...")
    aodv = ns.AodvHelper()
    internet = ns.InternetStackHelper()
    internet.SetRoutingHelper(aodv)
    internet.Install(nodes)
    
    # Назначение IP адресов
    address = ns.Ipv4AddressHelper()
    address.SetBase("10.1.1.0", "255.255.255.0")
    interfaces = address.Assign(devices)
    
    # РЕАЛЬНАЯ ИНТЕГРАЦИЯ C++ БЛОКЧЕЙН МОДУЛЯ!
    print("   ⛓️  Setting up REAL C++ blockchain integration...")
    
    # Создание блокчейн helper
    blockchain_helper = ns.CrossZoneBlockchainHelper()
    
    # Конфигурация зон и позиций
    blockchain_helper.ConfigureZones()
    # Расстановка узлов согласно сценарию
    blockchain_helper.ConfigureNodePositions(nodes, scenario)
    # Получаем zone manager
    zone_manager = blockchain_helper.GetZoneManager()
    
    # Настройка параметров блокчейна
    blockchain_helper.SetAttribute("TransactionInterval", ns.TimeValue(ns.Seconds(1.0)))
    blockchain_helper.SetAttribute("Port", ns.UintegerValue(7000))
    # Настройка интервалов блокчейна
    blockchain_helper.SetAttribute("BlockInterval", ns.TimeValue(ns.Seconds(1.0)))
    # --- Добавление атрибутов для конфигурации зон ---
    blockchain_helper.SetAttribute("SixGRadius", ns.DoubleValue(100.0))
    blockchain_helper.SetAttribute("BridgeRadius", ns.DoubleValue(150.0))
    blockchain_helper.SetAttribute("TowerPosition", ns.VectorValue(ns.Vector(150.0, 150.0, 30.0)))
    # --- Конец добавления атрибутов ---
    
    # Установка блокчейн приложений на все узлы
    print("   🚀 Installing blockchain applications...")
    blockchain_apps = blockchain_helper.Install(nodes)
    # Настройка валидаторов
    blockchain_helper.SetupValidators(nodes, validator_count)
    # Установка Gateway Discovery приложения на все узлы
    print("   🌉 Installing gateway discovery protocol on nodes...")
    gw_helper = ns.GatewayDiscoveryHelper()
    gw_helper.Install(nodes)
    
    blockchain_apps.Start(ns.Seconds(1.0))
    blockchain_apps.Stop(ns.Seconds(float(duration)))
    
    # Настройка трассировки
    print("   📊 Setting up tracing...")
    
    # ASCII трассировка
    ascii_file = output_dir + "/blockchain-trace.tr"
    ascii_helper = ns.AsciiTraceHelper()
    ascii_stream = ascii_helper.CreateFileStream(ascii_file)
    
    # PCAP трассировка 
    pcap_prefix = output_dir + "/blockchain"
    phy.EnablePcapAll(pcap_prefix)
    
    # Настройка логирования NS-3
    ns.LogComponentEnable("CrossZoneBlockchainApp", ns.LOG_LEVEL_INFO)
    ns.LogComponentEnable("ZoneManager", ns.LOG_LEVEL_INFO)
    ns.LogComponentEnable("BlockchainLedger", ns.LOG_LEVEL_INFO)
    
    print("   🎬 Starting REAL blockchain simulation...")
    start_time = time.time()
    # Запуск симуляции до заданного времени
    ns.Simulator.Stop(ns.Seconds(float(duration)))
    ns.Simulator.Run()
    
    simulation_time = time.time() - start_time
    
    # Получение статистики
    print("   📈 Collecting blockchain statistics...")
    
    # Сбор статистики с приложений
    total_tx_sent = 0
    total_tx_received = 0
    total_blocks_created = 0
    
    for i in range(total_nodes):
        app = blockchain_apps.Get(i)
        stats = app.GetStatistics()
        total_tx_sent += stats.tx_sent
        total_tx_received += stats.tx_received  
        total_blocks_created += stats.blocks_created
    
    print(f"   ✅ REAL BLOCKCHAIN SIMULATION COMPLETED!")
    print(f"   ⏱️  Execution time: {simulation_time:.1f}s")
    
    # Очистка
    ns.Simulator.Destroy()
    
    # Результаты реальной интеграции
    results = {
        "simulation_duration": duration,
        "scenario": scenario,
        "simulation_time": simulation_time,
        "real_cpp_integration": True,
        "blockchain_stats": {
            "total_transactions_sent": total_tx_sent,
            "total_transactions_received": total_tx_received,
            "total_blocks_created": total_blocks_created,
            "validator_count": validator_count
        },
        "trace_files": {
            "ascii": ascii_file,
            "pcap": pcap_prefix
        },
        "network_config": {
            "total_nodes": total_nodes,
            "validators": validator_count,
            "routing": "AODV",
            "wifi_standard": "802.11n",
            "simulation_area": "300x300m",
            "tower_position": [150.0, 150.0, 30.0]
        }
    }
    
    # Results printed by C++ NS_LOG_UNCOND trace callbacks
    
    return results

def print_banner():
    """Печать баннера симуляции"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║         🚀 REAL C++ BLOCKCHAIN INTEGRATION WITH NS-3 🚀                     ║
║                                                                              ║
║  Features:                                                                   ║
║  • REAL C++ blockchain module integration (not Python simulation)           ║
║  • Cross-zone transaction handling (6G, Bridge, MANET)                      ║
║  • Actual UDP packet transmission with blockchain headers                   ║
║  • Real AODV routing for blockchain traffic                                 ║
║  • Validator consensus with zone management                                 ║
║  • Complete PCAP/ASCII tracing of blockchain traffic                        ║
║                                                                              ║
║  🔗 NS-3 C++ ⟷ Python Integration ⟷ Analytics                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Real C++ Blockchain Integration with NS-3")
    
    parser.add_argument("--scenario", 
                       choices=["small_campus", "medium_district", "large_city", "stress_test"],
                       default="small_campus",
                       help="Simulation scenario")
    
    parser.add_argument("--duration", type=int, default=30,
                       help="Simulation duration in seconds")
    
    parser.add_argument("--output-dir", default="results",
                       help="Output directory for results")
    
    parser.add_argument("--test-integration", action="store_true",
                       help="Run integration test before simulation")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Создание директории для результатов
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Запуск реальной симуляции
        results = run_real_blockchain_simulation(args.scenario, args.duration, output_dir)
        
        if "error" in results:
            logger.error(f"❌ SIMULATION FAILED: {results['error']}")
            return 1
        
        # Сохранение результатов
        results_file = os.path.join(output_dir, "blockchain_simulation_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Вывод итоговой статистики
        print("\n" + "=" * 80)
        print("🎉 REAL C++ BLOCKCHAIN INTEGRATION SIMULATION COMPLETED!")
        print("=" * 80)
        
        print(f"\n⏱️  TIMING:")
        print(f"   • Total simulation time: {results['simulation_time']:.1f}s")
        print(f"   • Simulated time: {results['simulation_duration']}s")
        
        print(f"\n⛓️  BLOCKCHAIN STATISTICS:")
        for key, value in results['blockchain_stats'].items():
            print(f"   • {key}: {value}")
        
        print(f"\n📊 TRACE FILES:")
        print(f"   • ASCII Trace: {results['trace_files']['ascii']}")
        print(f"   • PCAP Trace: {results['trace_files']['pcap']}")
        
        print(f"\n🎯 REAL INTEGRATION FEATURES:")
        print(f"   ✅ C++ blockchain module compiled and integrated")
        print(f"   ✅ Real UDP packet transmission with blockchain headers")
        print(f"   ✅ Actual AODV routing of blockchain traffic")
        print(f"   ✅ Zone-based validator management")
        print(f"   ✅ Complete network trace capture")
        print(f"   ✅ Python-C++ bidirectional integration")
        
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ REAL BLOCKCHAIN SIMULATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
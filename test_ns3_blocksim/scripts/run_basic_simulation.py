#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска базовой интегрированной симуляции NS-3 и BlockSim.
"""
import os
import sys
import json
import argparse
import time
import logging
import random
import numpy as np
from typing import Dict, Any
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Добавляем каталог моделей в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.integration_interface import IntegrationInterface
from models.ns3_adapter import NS3Adapter
from models.blocksim_adapter import BlockSimAdapter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simulation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Simulation")

def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description='Интегрированная симуляция NS-3 и BlockSim')
    
    parser.add_argument('--config', type=str, default='../config/default.json',
                      help='Путь к файлу конфигурации симуляции')
    parser.add_argument('--duration', type=float, default=100.0,
                      help='Продолжительность симуляции в секундах')
    parser.add_argument('--time-step', type=float, default=1.0,
                      help='Временной шаг симуляции в секундах')
    parser.add_argument('--output-dir', type=str, default='../results',
                      help='Директория для сохранения результатов')
    parser.add_argument('--ns3-path', type=str, default=os.getenv('NS3_DIR'),
                      help='Путь к установленному NS-3')
    parser.add_argument('--debug', action='store_true',
                      help='Включить режим отладки с более подробным логированием')
    parser.add_argument('--animation', action='store_true',
                      help='Включить анимацию NS-3 для визуализации')
    parser.add_argument('--save-interim', action='store_true',
                      help='Сохранять промежуточные результаты симуляции')
    parser.add_argument('--rebuild', action='store_true',
                      help='Пересобрать NS-3 перед запуском')
    return parser.parse_args()

def load_config(config_path):
    """Загрузка конфигурационного файла."""
    try:
        # Проверяем существование файла
        if not os.path.exists(config_path):
            logger.error(f"Файл конфигурации {config_path} не найден. Используются значения по умолчанию.")
            return {}
        
        # Проверяем права на чтение
        if not os.access(config_path, os.R_OK):
            logger.error(f"Ошибка прав доступа: отсутствуют права на чтение файла {config_path}")
            logger.error("Пожалуйста, проверьте права доступа к файлу конфигурации")
            return {}
        
        # Пытаемся открыть файл и прочитать данные
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Файл конфигурации {config_path} не найден. Используются значения по умолчанию.")
        return {}
    except PermissionError:
        logger.error(f"Ошибка прав доступа: невозможно прочитать файл {config_path}")
        logger.error("Пожалуйста, проверьте права доступа к файлу конфигурации")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле {config_path}. Используются значения по умолчанию.")
        return {}
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при чтении файла конфигурации: {e}")
        return {}

def setup_environment(config, ns3_path=None):
    """Настройка окружения для симуляции."""
    # Создаем директорию для результатов, если ещё не существует
    os.makedirs(config.get("output_dir", "../results"), exist_ok=True)
    
    # Настройка NS-3
    if ns3_path:
        os.environ["NS3_DIR"] = ns3_path
    
    # Другие настройки окружения можно добавить здесь
    
    logger.info("Окружение настроено")

def create_network_topology(interface, config):
    """Создание топологии сети на основе конфигурации."""
    # Регистрируем базовую станцию
    interface.register_node(
        "base_station_1",
        (0.0, 0.0, 10.0),
        "base_station",
        {"computational_power": 100, "storage": 1000, "battery": None}
    )
    
    # Регистрируем валидаторов
    for i in range(config.get("num_validators", 3)):
        interface.register_node(
            f"validator_{i+1}",
            (50.0 * (i+1), 50.0 * (i+1), 1.5),
            "validator",
            {"computational_power": 20, "storage": 100, "battery": 0.8}
        )
    
    # Регистрируем обычные узлы
    for i in range(config.get("num_regular_nodes", 10)):
        interface.register_node(
            f"node_{i+1}",
            (100.0 + 20.0 * (i % 5), 100.0 + 20.0 * (i // 5), 1.5),
            "regular",
            {"computational_power": 10, "storage": 50, "battery": 0.9}
        )
    
    # Создаем соединения между узлами
    # Сначала соединяем базовую станцию с валидаторами
    for i in range(config.get("num_validators", 3)):
        interface.register_connection("base_station_1", f"validator_{i+1}", 0.9, 100.0)
    
    # Соединяем валидаторы между собой
    for i in range(config.get("num_validators", 3)):
        for j in range(i+1, config.get("num_validators", 3)):
            interface.register_connection(f"validator_{i+1}", f"validator_{j+1}", 0.8, 50.0)
    
    # Соединяем обычные узлы с ближайшими валидаторами и между собой
    for i in range(config.get("num_regular_nodes", 10)):
        # Соединяем с ближайшим валидатором
        validator_idx = (i % config.get("num_validators", 3)) + 1
        interface.register_connection(f"node_{i+1}", f"validator_{validator_idx}", 0.7, 10.0)
        
        # Соединяем с несколькими соседними узлами
        for j in range(1, 4):  # Соединяем с 3 соседними узлами
            neighbor_idx = (i + j) % config.get("num_regular_nodes", 10) + 1
            interface.register_connection(f"node_{i+1}", f"node_{neighbor_idx}", 0.6, 5.0)
    
    logger.info("Топология сети создана")

def run_simulation(args, config):
    """Выполнение симуляции."""
    # Создаем интерфейс интеграции
    interface = IntegrationInterface()
    
    # Создаем адаптеры для NS-3 и BlockSim
    try:
        ns3_adapter = NS3Adapter(args.ns3_path)
        
        # Если указан флаг --rebuild, перестраиваем NS-3
        if args.rebuild:
            logger.info("Начинаем пересборку NS-3 с оптимизациями...")
            if ns3_adapter.configure_and_build():
                logger.info("NS-3 успешно пересобран")
            else:
                logger.error("Ошибка при сборке NS-3")
                return None
        
        # Создаем скрипт для симуляции MANET с поддержкой блокчейна
        script_path = ns3_adapter.create_ns3_manet_script()
        
        # Компилируем скрипт
        script_name = os.path.basename(script_path).replace('.cc', '')
        if ns3_adapter.compile_ns3_script(script_name):
            logger.info(f"Скрипт {script_name} успешно скомпилирован")
        else:
            logger.warning(f"Не удалось скомпилировать скрипт {script_name}. Используем имеющиеся скрипты.")
            
        logger.info("NS-3 адаптер успешно инициализирован")
    except Exception as e:
        logger.warning(f"Не удалось инициализировать NS-3 адаптер: {e}")
        logger.warning("Будет использоваться эмуляция NS-3")
        ns3_adapter = None
    
    blocksim_adapter = BlockSimAdapter()
    logger.info("BlockSim адаптер инициализирован")
    
    # Создаем топологию сети
    create_network_topology(interface, config)
    
    # Инициализируем блокчейн
    consensus_type = config.get("consensus_type", "PoA")
    num_validators = config.get("num_validators", 3)
    block_interval = config.get("block_interval", 5.0)
    
    blocksim_adapter.initialize_blockchain(consensus_type, num_validators, block_interval)
    
    # Синхронизируем узлы между интерфейсом и BlockSim
    for node_id, node_info in interface.nodes.items():
        node_type = "validator" if node_info["type"] == "validator" else "regular"
        if node_info["type"] == "base_station":
            node_type = "validator"  # Базовая станция считается валидатором
            
        resources = {
            "computational_power": node_info["capabilities"].get("computational_power", 10),
            "storage": node_info["capabilities"].get("storage", 50)
        }
        blocksim_adapter.register_node(node_id, node_type, resources)
    
    # Сценарий симуляции
    total_time = args.duration
    time_step = args.time_step
    current_time = 0.0
    
    # Создаем выходную директорию с временной меткой для текущего запуска
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = os.path.join(args.output_dir, f"simulation_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Генерируем файл сценария для NS-3 (если NS-3 доступен)
    network_params = {
        "simulation_time": total_time,
        "time_step": time_step,
        "wifi_standard": "80211g",
        "propagation_model": "friis",
        "routing_protocol": "aodv"
    }
    
    if ns3_adapter:
        scenario_file = ns3_adapter.create_scenario_file(
            interface.nodes,
            interface.links,
            network_params
        )
        
        # Запускаем NS-3 симуляцию в фоновом режиме
        logger.info("Запуск симуляции NS-3...")
        ns3_results = ns3_adapter.run_simulation(
            scenario_file, 
            total_time, 
            time_step, 
            output_dir
        )
    
    # Основной цикл симуляции
    logger.info(f"Начало симуляции. Продолжительность: {total_time} секунд, шаг: {time_step} секунд")
    node_positions = {}  # Для хранения текущих позиций узлов
    
    # Инициализация начальных позиций
    for node_id, node_info in interface.nodes.items():
        node_positions[node_id] = list(node_info["position"])
    
    while current_time < total_time:
        # Обновляем текущее время
        interface.advance_time(time_step)
        blocksim_adapter.advance_time(time_step)
        current_time += time_step
        
        # Симулируем движение мобильных узлов (кроме базовой станции)
        for node_id, position in node_positions.items():
            if "base_station" not in node_id:  # Не перемещаем базовую станцию
                # Случайное перемещение в пределах небольшого радиуса
                dx = random.uniform(-5, 5) * time_step
                dy = random.uniform(-5, 5) * time_step
                dz = 0  # По умолчанию, движение только в плоскости XY
                
                # Ограничиваем перемещение в пределах разумной области
                new_x = max(0, min(500, position[0] + dx))
                new_y = max(0, min(500, position[1] + dy))
                new_z = position[2]  # Высота не меняется
                
                # Обновляем позицию
                new_position = [new_x, new_y, new_z]
                node_positions[node_id] = new_position
                interface.update_node_position(node_id, tuple(new_position))
                
                # Обновляем качество соединений на основе расстояния
                for other_id, other_pos in node_positions.items():
                    if node_id != other_id:
                        # Рассчитываем расстояние между узлами
                        distance = np.sqrt((new_x - other_pos[0])**2 + 
                                          (new_y - other_pos[1])**2 + 
                                          (new_z - other_pos[2])**2)
                        
                        # Качество связи обратно пропорционально расстоянию
                        # Максимальное расстояние для связи - 100 единиц
                        if distance <= 100:
                            quality = max(0.1, 1.0 - distance / 100.0)
                            # Пропускная способность зависит от качества связи
                            bandwidth = 50.0 * quality
                            
                            # Обновляем соединение между узлами
                            connection_ids = [f"{min(node_id, other_id)}_{max(node_id, other_id)}"]
                            interface.register_connection(node_id, other_id, quality, bandwidth)
                        
        # Генерируем активность узлов каждые 10 секунд
        if int(current_time * 10) % 100 == 0:  # Каждые 10 секунд (с учетом шага симуляции)
            # Создаем несколько транзакций
            for _ in range(5):
                # Выбираем случайные узлы для транзакции
                all_node_ids = list(interface.nodes.keys())
                if len(all_node_ids) >= 2:
                    source_id = random.choice(all_node_ids)
                    target_id = random.choice([n for n in all_node_ids if n != source_id])
                    
                    # Создаем транзакцию через интерфейс
                    tx_data = {
                        "type": "data_transfer",
                        "content": f"Transaction at time {current_time:.2f}",
                        "size": random.randint(1, 1000),
                        "priority": random.choice(["low", "medium", "high"])
                    }
                    tx_id = interface.send_transaction(source_id, target_id, tx_data)
                    
                    # Создаем соответствующую транзакцию в BlockSim
                    if tx_id:
                        blocksim_adapter.create_transaction(source_id, target_id, tx_data)
            
            # Обрабатываем ожидающие транзакции
            processed = interface.process_pending_transactions()
            if processed > 0:
                logger.debug(f"Обработано {processed} транзакций в интерфейсе")
            
            processed_blockchain = blocksim_adapter.process_pending_transactions()
            if processed_blockchain > 0:
                logger.debug(f"Обработано {processed_blockchain} транзакций в блокчейне")
                # Создаем блок с обработанными транзакциями
                block = blocksim_adapter.create_block()
                if block:
                    logger.info(f"Создан новый блок {block['index']} валидатором {block['validator']}")
        
        # Вывод текущего состояния каждые 20 секунд
        if int(current_time * 10) % 200 == 0 or current_time >= total_time - time_step:
            net_state = interface.get_network_state()
            blockchain_state = blocksim_adapter.get_blockchain_state()
            
            logger.info(f"Время симуляции: {current_time:.2f}/{total_time}")
            logger.info(f"Узлов в сети: {len(net_state['nodes'])}")
            logger.info(f"Соединений в сети: {len(net_state['links'])}")
            logger.info(f"Транзакций в сети: {len(net_state['transactions'])}")
            logger.info(f"Блоков в блокчейне: {blockchain_state['blocks_count']}")
            logger.info(f"Ожидающих транзакций: {blockchain_state['pending_transactions']}")
            logger.info(f"Подтвержденных транзакций: {blockchain_state['confirmed_transactions']}")
            
            # Сохраняем промежуточные результаты
            if args.save_interim:
                interim_output = os.path.join(output_dir, f"interim_{int(current_time)}")
                os.makedirs(interim_output, exist_ok=True)
                interface.save_state(os.path.join(interim_output, "network_state.json"))
                blocksim_adapter.save_state(os.path.join(interim_output, "blockchain_state.json"))
    
    logger.info("Симуляция завершена")
    
    # Сохраняем результаты
    network_state_file = os.path.join(output_dir, f"network_state_{timestamp}.json")
    interface.save_state(network_state_file)
    
    # Сохраняем состояние блокчейна
    blockchain_state_file = os.path.join(output_dir, f"blockchain_state_{timestamp}.json")
    blocksim_adapter.save_state(blockchain_state_file)
    
    # Если включена анимация, проверяем файл анимации
    animation_file = None
    if args.animation and ns3_adapter:
        animation_file = os.path.join(output_dir, f"animation_{timestamp}.xml")
        logger.info(f"Файл анимации будет сохранен как: {animation_file}")
        logger.info("Для просмотра анимации запустите NetAnim и откройте файл")
    
    # Сохраняем сводную информацию о симуляции
    summary = {
        "timestamp": timestamp,
        "duration": total_time,
        "time_step": time_step,
        "nodes_count": len(interface.nodes),
        "transactions_processed": len([tx for tx in interface.transactions if tx["status"] in ["processed", "included"]]),
        "blocks_created": blocksim_adapter.get_blockchain_state()["blocks_count"],
        "network_state_file": network_state_file,
        "blockchain_state_file": blockchain_state_file,
        "animation_file": animation_file
    }
    
    with open(os.path.join(output_dir, f"summary_{timestamp}.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    
    return {
        "network_state": interface.get_network_state(),
        "blockchain_state": blocksim_adapter.get_detailed_state(),
        "timestamp": timestamp,
        "animation_file": animation_file
    }

def main():
    """Основная функция."""
    # Парсинг аргументов командной строки
    args = parse_arguments()
    
    # Настройка уровня логирования
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Загрузка конфигурации
    config = load_config(args.config)
    
    # Добавляем аргументы командной строки к конфигурации
    config["duration"] = args.duration
    config["time_step"] = args.time_step
    config["output_dir"] = args.output_dir
    config["animation_enabled"] = args.animation
    
    # Настройка окружения
    setup_environment(config, args.ns3_path)
    
    # Запуск симуляции
    results = run_simulation(args, config)
    
    if results:
        logger.info(f"Результаты симуляции сохранены в {args.output_dir}")
        logger.info(f"Временная метка результатов: {results['timestamp']}")
        if results.get('animation_file'):
            logger.info(f"Файл анимации: {results['animation_file']}")
    else:
        logger.error("Симуляция завершилась с ошибкой")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
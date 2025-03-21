#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования интегрированной симуляции NS-3 и BlockSim.
Запускает симуляцию с минимальными параметрами для проверки работоспособности.
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Добавляем родительский каталог в путь импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("test_simulation.log"), logging.StreamHandler()],
)
logger = logging.getLogger("TestSimulation")


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Тест интегрированной симуляции")

    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Продолжительность симуляции в секундах (по умолчанию: 30)",
    )
    parser.add_argument(
        "--time-step",
        type=float,
        default=0.5,
        help="Временной шаг симуляции в секундах (по умолчанию: 0.5)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="../results/test",
        help="Директория для сохранения результатов",
    )
    parser.add_argument(
        "--ns3-path", type=str, default=None, help="Путь к установленному NS-3"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Включить отладочные сообщения"
    )
    return parser.parse_args()


def create_test_config():
    """Создает тестовую конфигурацию с минимальными параметрами."""
    config = {
        "simulation": {"duration": 30.0, "time_step": 0.5},
        "network": {
            "num_validators": 2,
            "num_regular_nodes": 4,
            "base_station": {
                "position": [0.0, 0.0, 10.0],
                "computational_power": 100,
                "storage": 1000,
            },
            "validator_params": {
                "computational_power": 20,
                "storage": 100,
                "battery": 0.8,
            },
            "node_params": {"computational_power": 10, "storage": 50, "battery": 0.9},
        },
        "blockchain": {
            "consensus_type": "PoA",
            "block_interval": 5.0,
            "transaction_size": 1000,
        },
        "visualization": {"enable_netanim": True, "update_interval": 0.1},
        "output": {"save_network_state": True, "save_blockchain_state": True},
    }

    return config


def main():
    """Основная функция."""
    # Парсинг аргументов командной строки
    args = parse_arguments()

    # Настройка уровня логирования
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Создаем тестовую конфигурацию
    config = create_test_config()
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_config.json"
    )

    # Сохраняем конфигурацию во временный файл
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    logger.info(
        "Создана тестовая конфигурация: %(config_path)s", {config_path: config_path}
    )

    # Обновляем конфигурацию с аргументами командной строки
    if args.duration:
        config["simulation"]["duration"] = args.duration
    if args.time_step:
        config["simulation"]["time_step"] = args.time_step

    # Создаем директорию для результатов
    os.makedirs(args.output_dir, exist_ok=True)

    # Формируем команду для запуска основной симуляции
    cmd_args = [
        sys.executable,
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "run_basic_simulation.py"
        ),
        f"--config={config_path}",
        f"--duration={args.duration}",
        f"--time-step={args.time_step}",
        f"--output-dir={args.output_dir}",
    ]

    if args.ns3_path:
        cmd_args.append(f"--ns3-path={args.ns3_path}")

    if args.debug:
        cmd_args.append("--debug")

    # Добавляем опции сохранения промежуточных результатов и анимации
    cmd_args.append("--save-interim")
    cmd_args.append("--animation")

    # Выводим команду для запуска
    cmd_line = " ".join(cmd_args)
    logger.info(
        "Запуск тестовой симуляции с командой: %(cmd_line)s", {cmd_line: cmd_line}
    )

    # Запускаем процесс
    import subprocess

    try:
        process = subprocess.run(cmd_args, check=True, capture_output=True, text=True)
        logger.info("Симуляция успешно завершена")

        # Проверяем наличие файлов результатов
        result_dir = Path(args.output_dir)
        simulation_dirs = [d for d in result_dir.glob("simulation_*") if d.is_dir()]

        if simulation_dirs:
            latest_dir = max(simulation_dirs, key=lambda p: p.stat().st_mtime)
            logger.info(
                "Результаты симуляции сохранены в: %(latest_dir)s",
                {latest_dir: latest_dir},
            )

            # Проверяем наличие файлов результатов
            network_files = list(latest_dir.glob("network_state_*.json"))
            blockchain_files = list(latest_dir.glob("blockchain_state_*.json"))
            summary_files = list(latest_dir.glob("summary_*.json"))

            if network_files and blockchain_files and summary_files:
                logger.info("Все файлы результатов успешно созданы")

                # Выводим краткую информацию из файла summary
                with open(summary_files[0], "r", encoding="utf-8") as f:
                    summary = json.load(f)
                    logger.info(
                        f"Количество узлов: {summary.get('nodes_count', 'N/A')}"
                    )
                    logger.info(
                        f"Обработано транзакций: {summary.get('transactions_processed', 'N/A')}"
                    )
                    logger.info(
                        f"Создано блоков: {summary.get('blocks_created', 'N/A')}"
                    )
            else:
                logger.warning("Некоторые файлы результатов отсутствуют")
        else:
            logger.warning("Не найдены директории с результатами симуляции")

    except subprocess.CalledProcessError as e:
        logger.error("Ошибка при запуске симуляции: %(e)s", {e: e})
        logger.error("Стандартный вывод: %(e.stdout)s", {e.stdout: e.stdout})
        logger.error("Стандартный вывод ошибок: %(e.stderr)s", {e.stderr: e.stderr})
        return 1

    # Удаляем временный файл конфигурации
    try:
        os.remove(config_path)
    except Exception as e:
        logger.warning("Не удалось удалить временный файл конфигурации: %(e)s", {e: e})

    return 0


if __name__ == "__main__":
    sys.exit(main())

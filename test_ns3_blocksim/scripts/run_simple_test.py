#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска простой тестовой симуляции NS-3.
Предназначен для проверки работоспособности NS-3.
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path
import tempfile
import shutil

# Добавляем путь к моделям
sys.path.append(str(Path(__file__).parent.parent))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ns3_simple_test.log")
    ]
)
logger = logging.getLogger("NS3SimpleTest")

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
            logger.info(f"Автоматически найден путь к NS-3: {path}")
            return str(path)
    
    # Проверяем системные пути
    ns3_cmd = shutil.which("ns3")
    if ns3_cmd:
        # Если ns3 найден в системном PATH, определяем его директорию
        ns3_dir = str(Path(ns3_cmd).parent)
        logger.info(f"Найден NS-3 в системном PATH: {ns3_dir}")
        return ns3_dir
    
    return None

def create_simple_example():
    """
    Создает простой пример симуляции NS-3 для тестирования.
    
    Returns:
        str: Путь к созданному файлу
    """
    # Создаем временный файл
    fd, temp_file = tempfile.mkstemp(suffix=".cc", prefix="ns3_test_")
    os.close(fd)
    
    # Пишем простой пример c++
    example_code = """
/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Простой пример для тестирования NS-3.
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("TestSimulation");

int
main (int argc, char *argv[])
{
  // Включаем логирование для всех компонентов
  LogComponentEnable ("TestSimulation", LOG_LEVEL_INFO);
  NS_LOG_INFO ("Начало тестовой симуляции NS-3");
  
  // Создаем два узла
  NodeContainer nodes;
  nodes.Create (2);

  // Создаем соединение точка-точка
  PointToPointHelper pointToPoint;
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("5Mbps"));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("2ms"));

  // Устанавливаем устройства на узлы
  NetDeviceContainer devices;
  devices = pointToPoint.Install (nodes);

  // Устанавливаем стек интернет-протоколов
  InternetStackHelper stack;
  stack.Install (nodes);

  // Назначаем IP-адреса
  Ipv4AddressHelper address;
  address.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer interfaces = address.Assign (devices);

  // Создаем приложение для отправки данных
  UdpEchoServerHelper echoServer (9);
  ApplicationContainer serverApps = echoServer.Install (nodes.Get (1));
  serverApps.Start (Seconds (1.0));
  serverApps.Stop (Seconds (10.0));

  UdpEchoClientHelper echoClient (interfaces.GetAddress (1), 9);
  echoClient.SetAttribute ("MaxPackets", UintegerValue (1));
  echoClient.SetAttribute ("Interval", TimeValue (Seconds (1.0)));
  echoClient.SetAttribute ("PacketSize", UintegerValue (1024));

  ApplicationContainer clientApps = echoClient.Install (nodes.Get (0));
  clientApps.Start (Seconds (2.0));
  clientApps.Stop (Seconds (10.0));

  // Запускаем симуляцию
  NS_LOG_INFO ("Запуск симуляции...");
  Simulator::Run ();
  Simulator::Destroy ();
  NS_LOG_INFO ("Симуляция завершена.");

  return 0;
}
    """
    
    with open(temp_file, 'w') as f:
        f.write(example_code)
    
    logger.info(f"Создан тестовый файл симуляции: {temp_file}")
    return temp_file

def run_simple_simulation(ns3_path):
    """
    Запускает простую симуляцию NS-3.
    
    Args:
        ns3_path (str): Путь к директории NS-3
        
    Returns:
        bool: True если симуляция успешна, иначе False
    """
    try:
        # Проверяем, есть ли уже готовые примеры
        example_file = None
        example_paths = [
            os.path.join(ns3_path, "examples", "tutorial", "first.cc"),
            os.path.join(ns3_path, "examples", "tutorial", "hello-simulator.cc"),
            os.path.join(ns3_path, "examples", "wireless", "wifi-simple-adhoc.cc")
        ]
        
        for path in example_paths:
            if os.path.exists(path):
                example_file = path
                example_name = os.path.splitext(os.path.basename(path))[0]
                logger.info(f"Найден готовый пример: {example_name}")
                break
        
        # Если не нашли готовый пример, создаем свой
        if example_file is None:
            example_file = create_simple_example()
            # Копируем его в scratch
            scratch_dir = os.path.join(ns3_path, "scratch")
            if os.path.isdir(scratch_dir):
                dst_file = os.path.join(scratch_dir, "test-simulation.cc")
                shutil.copy2(example_file, dst_file)
                example_file = dst_file
                example_name = "scratch/test-simulation"
                logger.info(f"Пример скопирован в scratch: {dst_file}")
            else:
                logger.error(f"Директория scratch не найдена: {scratch_dir}")
                return False
        else:
            # Используем относительный путь для примера
            rel_path = os.path.relpath(example_file, ns3_path)
            example_name = os.path.splitext(rel_path)[0]
        
        # Запускаем симуляцию
        ns3_executable = os.path.join(ns3_path, "ns3")
        cmd = [ns3_executable, "run", example_name]
        
        logger.info(f"Запуск тестовой симуляции: {' '.join(cmd)}")
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=60
        )
        
        if process.returncode == 0:
            logger.info("Тестовая симуляция успешно завершена!")
            logger.info("Вывод симуляции:")
            for line in process.stdout.splitlines():
                logger.info(f"  {line}")
            return True
        else:
            logger.error(f"Тестовая симуляция завершилась с ошибкой: {process.returncode}")
            logger.error(f"Вывод stderr:")
            for line in process.stderr.splitlines():
                logger.error(f"  {line}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Превышено время выполнения симуляции (таймаут)")
        return False
    except Exception as e:
        logger.error(f"Ошибка при запуске тестовой симуляции: {e}", exc_info=True)
        return False

def main():
    """Основная функция для запуска теста."""
    parser = argparse.ArgumentParser(description="Запуск простой тестовой симуляции NS-3")
    parser.add_argument("--ns3-path", type=str, help="Путь к директории NS-3")
    
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
                logger.error("Не удалось автоматически определить путь к NS-3. Используйте --ns3-path или установите переменную окружения NS3_DIR")
                sys.exit(1)
    
    # Проверяем существование директории NS-3
    if not os.path.exists(ns3_path):
        logger.error(f"Директория NS-3 не найдена: {ns3_path}")
        sys.exit(1)
    
    logger.info(f"Используем NS-3 из директории: {ns3_path}")
    
    # Запускаем тестовую симуляцию
    result = run_simple_simulation(ns3_path)
    
    if result:
        logger.info("Тестирование NS-3 успешно завершено!")
        sys.exit(0)
    else:
        logger.error("Тестирование NS-3 завершилось с ошибками")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для быстрой проверки работоспособности NS-3.
Проверяет доступность и базовые возможности NS-3 без запуска полной симуляции.
"""

import os
import sys
import argparse
import subprocess
import logging
import shutil
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NS3Check")

def check_ns3_availability(ns3_path):
    """
    Проверяет доступность NS-3 в указанной директории.
    
    Args:
        ns3_path (str): Путь к директории NS-3
        
    Returns:
        bool: True, если NS-3 доступен, иначе False
    """
    # Проверка наличия директории
    if not os.path.isdir(ns3_path):
        logger.error(f"Директория NS-3 не существует: {ns3_path}")
        return False
    
    # Проверка наличия исполняемого файла ns3
    ns3_executable = os.path.join(ns3_path, "ns3")
    if not os.path.exists(ns3_executable):
        logger.error(f"Исполняемый файл NS-3 не найден: {ns3_executable}")
        return False

    # Проверка прав на выполнение
    if not os.access(ns3_executable, os.X_OK):
        logger.warning(f"Файл NS-3 существует, но не имеет прав на выполнение: {ns3_executable}")
        try:
            logger.info(f"Пытаюсь добавить права на выполнение...")
            os.chmod(ns3_executable, 0o755)  # Добавляем права на выполнение
            logger.info(f"Права на выполнение добавлены успешно")
        except Exception as e:
            logger.error(f"Не удалось добавить права на выполнение: {e}")
            return False
    
    # Проверяем версию NS-3 из файла VERSION
    try:
        version_file = os.path.join(ns3_path, "VERSION")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                version = f.read().strip()
            logger.info(f"Обнаружена версия NS-3: {version}")
        else:
            logger.info("Файл VERSION не найден, продолжаем проверку...")
            
        # Попытка вызова ns3 с минимальными параметрами
        try:
            # Пробуем запустить с минимальным опциями
            result = subprocess.run(
                [ns3_executable, "--help"],
                capture_output=True,
                text=True,
                timeout=10  # Добавляем таймаут
            )
            if result.returncode == 0:
                logger.info("Команда NS-3 запускается успешно")
                return True
            else:
                logger.warning(f"Команда NS-3 завершилась с ошибкой: {result.returncode}")
                logger.warning(f"Вывод stderr: {result.stderr}")
                
                # Пробуем другую команду
                logger.info("Пробуем альтернативную проверку...")
                result = subprocess.run(
                    [ns3_executable],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.returncode == 0
                
        except subprocess.TimeoutExpired:
            logger.error("Таймаут при выполнении команды NS-3")
            return False
        except FileNotFoundError:
            logger.error(f"Файл NS-3 не найден в системном PATH")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке NS-3: {e}")
        return False

def check_ns3_modules(ns3_path):
    """
    Проверяет доступные модули NS-3.
    
    Args:
        ns3_path (str): Путь к директории NS-3
        
    Returns:
        list: Список доступных модулей или пустой список в случае ошибки
    """
    try:
        # Проверка модулей через анализ директорий
        src_dir = os.path.join(ns3_path, "src")
        if os.path.isdir(src_dir):
            # Собираем модули из директорий исходного кода
            modules = []
            for item in os.listdir(src_dir):
                if os.path.isdir(os.path.join(src_dir, item)) and not item.startswith('.'):
                    modules.append(item)
            
            logger.info(f"Найдено {len(modules)} модулей NS-3 в директории src")
            return modules
        
        # Если директория src не найдена, попробуем запустить команду
        ns3_executable = os.path.join(ns3_path, "ns3")
        result = subprocess.run(
            [ns3_executable, "show", "modules"],
            capture_output=True,
            text=True,
            check=False  # Не выбрасываем исключение при ошибке
        )
        
        if result.returncode != 0:
            logger.warning(f"Команда 'show modules' завершилась с ошибкой: {result.returncode}")
            logger.warning(f"Вывод stderr: {result.stderr}")
            return []
        
        modules = []
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('*') and not line.startswith('-') and not line.startswith('='):
                if ':' in line:
                    module_name = line.split(':', 1)[0].strip()
                    modules.append(module_name)
        
        logger.info(f"Обнаружено {len(modules)} модулей NS-3")
        return modules
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке модулей NS-3: {e}")
        return []

def check_build_status(ns3_path):
    """
    Проверяет статус сборки NS-3.
    
    Args:
        ns3_path (str): Путь к директории NS-3
        
    Returns:
        bool: True, если NS-3 успешно собран, иначе False
    """
    try:
        # Проверка наличия различных директорий сборки
        build_dirs = [
            os.path.join(ns3_path, "build"),
            os.path.join(ns3_path, "cmake-build"),
            os.path.join(ns3_path, "cmake-cache")
        ]
        
        build_found = False
        for build_dir in build_dirs:
            if os.path.isdir(build_dir):
                build_found = True
                logger.info(f"Директория сборки найдена: {build_dir}")
                
                # Проверяем наличие библиотек
                library_dirs = [
                    os.path.join(build_dir, "lib"),
                    os.path.join(build_dir, "lib64")
                ]
                
                for lib_dir in library_dirs:
                    if os.path.isdir(lib_dir):
                        libraries = os.listdir(lib_dir)
                        ns_libs = [lib for lib in libraries if lib.startswith("libns3") or lib.startswith("libns-3")]
                        if ns_libs:
                            logger.info(f"Обнаружено {len(ns_libs)} библиотек NS-3 в {lib_dir}")
                            return True
        
        if build_found:
            logger.warning("Директории сборки найдены, но библиотеки NS-3 не обнаружены")
        else:
            logger.warning("Директории сборки NS-3 не найдены")
        
        # Проверка наличия исполняемых файлов в waf-билдах (старый способ сборки)
        waf_build_dir = os.path.join(ns3_path, "build", "bin")
        if os.path.isdir(waf_build_dir):
            executables = os.listdir(waf_build_dir)
            if executables:
                logger.info(f"Найдены исполняемые файлы в старом waf-формате: {len(executables)}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке статуса сборки NS-3: {e}")
        return False

def check_basic_ns3_functionality(ns3_path):
    """
    Проверяет базовую функциональность NS-3.
    
    Args:
        ns3_path (str): Путь к директории NS-3
        
    Returns:
        bool: True, если базовая функциональность работает, иначе False
    """
    try:
        # Проверяем файл примера
        example_path = os.path.join(ns3_path, "examples", "tutorial", "first.cc")
        if not os.path.exists(example_path):
            example_path = os.path.join(ns3_path, "examples", "wireless", "wifi-simple-adhoc.cc")
        
        if os.path.exists(example_path):
            logger.info(f"Пример найден: {example_path}")
            return True
        else:
            logger.warning("Не удалось найти примеры NS-3")
            return False
    except Exception as e:
        logger.error(f"Ошибка при проверке функциональности NS-3: {e}")
        return False

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

def main():
    """Основная функция проверки NS-3."""
    parser = argparse.ArgumentParser(description="Проверка работоспособности NS-3")
    parser.add_argument("--ns3-path", type=str, help="Путь к директории NS-3")
    parser.add_argument("--verbose", action="store_true", help="Подробный вывод")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
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
    
    logger.info(f"Проверка NS-3 по пути: {ns3_path}")
    
    # Проверка доступности NS-3
    if not check_ns3_availability(ns3_path):
        logger.error("NS-3 недоступен или некорректно установлен")
        sys.exit(1)
    
    logger.info("NS-3 успешно обнаружен")
    
    # Проверка статуса сборки
    if not check_build_status(ns3_path):
        logger.warning("NS-3 может быть собран не полностью или сборка повреждена")
    else:
        logger.info("Сборка NS-3 выглядит корректной")
    
    # Проверка базовой функциональности
    if check_basic_ns3_functionality(ns3_path):
        logger.info("Базовые примеры NS-3 найдены")
    
    # Проверка доступных модулей
    modules = check_ns3_modules(ns3_path)
    if modules:
        logger.info(f"Доступные модули NS-3 ({len(modules)}):")
        if args.verbose:
            for i, module in enumerate(modules, 1):
                logger.info(f"{i}. {module}")
        else:
            logger.info(", ".join(modules[:10]) + (", ..." if len(modules) > 10 else ""))
        
        # Проверка наличия необходимых модулей
        required_modules = ['core', 'network', 'internet', 'applications', 'mobility', 'wifi']
        missing_modules = [mod for mod in required_modules if mod not in modules]
        
        if missing_modules:
            logger.warning(f"Отсутствуют необходимые модули: {', '.join(missing_modules)}")
        else:
            logger.info("Все необходимые модули присутствуют")
    else:
        logger.warning("Не удалось получить список модулей NS-3")
    
    logger.info("Проверка NS-3 завершена успешно!")

if __name__ == "__main__":
    main()
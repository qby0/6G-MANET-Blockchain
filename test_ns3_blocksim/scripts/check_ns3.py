#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for quick NS-3 functionality check.
Checks availability and basic NS-3 capabilities without running full simulation.
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("NS3Check")


def check_ns3_availability(ns3_path):
    """
    Checks NS-3 availability in the specified directory.

    Args:
        ns3_path (str): Path to NS-3 directory

    Returns:
        bool: True if NS-3 is available, False otherwise
    """
    # Check directory existence
    if not os.path.isdir(ns3_path):
        logger.error(
            "NS-3 directory does not exist: %s", ns3_path
        )
        return False

    # Check for ns3 executable
    ns3_executable = os.path.join(ns3_path, "ns3")
    if not os.path.exists(ns3_executable):
        logger.error(
            "NS-3 executable not found: %s", ns3_executable,
        )
        return False

    # Check execution permissions
    if not os.access(ns3_executable, os.X_OK):
        logger.warning(
            "NS-3 file exists but is not executable: %s", ns3_executable,
        )
        try:
            logger.info("Trying to add execution permissions...")
            os.chmod(ns3_executable, 0o755)  # Add execution permissions
            logger.info("Execution permissions added successfully")
        except Exception as e:
            logger.error("Failed to add execution permissions: %s", e)
            return False

    # Check NS-3 version from VERSION file
    try:
        version_file = os.path.join(ns3_path, "VERSION")
        if os.path.exists(version_file):
            with open(version_file, "r", encoding="utf-8") as f:
                version = f.read().strip()
            logger.info("Detected NS-3 version: %s", version)
        else:
            logger.info("VERSION file not found, continuing checks...")

        # Try calling ns3 with minimal parameters
        try:
            # Try running with minimal options
            result = subprocess.run(
                [ns3_executable, "--help"],
                capture_output=True,
                text=True,
                timeout=10,  # Add timeout
            )
            if result.returncode == 0:
                logger.info("NS-3 command runs successfully")
                return True
            else:
                logger.warning(
                    f"NS-3 command completed with error: {result.returncode}"
                )
                logger.warning(
                    "Stderr output: %s", result.stderr
                )

                # Try alternative command
                logger.info("Trying alternative check...")
                result = subprocess.run(
                    [ns3_executable], capture_output=True, text=True, timeout=10
                )
                return result.returncode == 0

        except subprocess.TimeoutExpired:
            logger.error("Timeout while executing NS-3 command")
            return False
        except FileNotFoundError:
            logger.error("NS-3 file not found in system PATH")
            return False

        return True
    except Exception as e:
        logger.error("Unexpected error while checking NS-3: %s", e)
        return False


def check_ns3_modules(ns3_path):
    """
    Checks available NS-3 modules.

    Args:
        ns3_path (str): Path to NS-3 directory

    Returns:
        list: List of available modules or empty list on error
    """
    try:
        # Check modules through directory analysis
        src_dir = os.path.join(ns3_path, "src")
        if os.path.isdir(src_dir):
            # Collect modules from source code directories
            modules = []
            for item in os.listdir(src_dir):
                if os.path.isdir(os.path.join(src_dir, item)) and not item.startswith(
                    "."
                ):
                    modules.append(item)

            logger.info(
                "Found %d NS-3 modules in src directory", len(modules)
            )
            return modules

        # If src directory not found, try running command
        ns3_executable = os.path.join(ns3_path, "ns3")
        result = subprocess.run(
            [ns3_executable, "show", "modules"],
            capture_output=True,
            text=True,
            check=False,  # Don't throw exception on error
        )

        if result.returncode != 0:
            logger.warning(
                f"Command 'show modules' completed with error: {result.returncode}"
            )
            logger.warning(
                "Stderr output: %s", result.stderr
            )
            return []

        modules = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if (
                line
                and not line.startswith("*")
                and not line.startswith("-")
                and not line.startswith("=")
            ):
                if ":" in line:
                    module_name = line.split(":", 1)[0].strip()
                    modules.append(module_name)

        logger.info(
            "Detected %d NS-3 modules", len(modules)
        )
        return modules
    except Exception as e:
        logger.error("Unexpected error while checking NS-3 modules: %s", e)
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
            os.path.join(ns3_path, "cmake-cache"),
        ]

        build_found = False
        for build_dir in build_dirs:
            if os.path.isdir(build_dir):
                build_found = True
                logger.info(
                    "Build directory found: %s", build_dir
                )

                # Проверяем наличие библиотек
                library_dirs = [
                    os.path.join(build_dir, "lib"),
                    os.path.join(build_dir, "lib64"),
                ]

                for lib_dir in library_dirs:
                    if os.path.isdir(lib_dir):
                        libraries = os.listdir(lib_dir)
                        ns_libs = [
                            lib
                            for lib in libraries
                            if lib.startswith("libns3") or lib.startswith("libns-3")
                        ]
                        if ns_libs:
                            logger.info(
                                f"Detected {len(ns_libs)} NS-3 libraries in {lib_dir}"
                            )
                            return True

        if build_found:
            logger.warning("Build directories found, but NS-3 libraries not detected")
        else:
            logger.warning("NS-3 build directories not found")

        # Проверка наличия исполняемых файлов в waf-билдах (старый способ сборки)
        waf_build_dir = os.path.join(ns3_path, "build", "bin")
        if os.path.isdir(waf_build_dir):
            executables = os.listdir(waf_build_dir)
            if executables:
                logger.info(
                    f"Found executable files in old waf format: {len(executables)}"
                )
                return True

        return False
    except Exception as e:
        logger.error("Error while checking NS-3 build status: %s", e)
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
            example_path = os.path.join(
                ns3_path, "examples", "wireless", "wifi-simple-adhoc.cc"
            )

        if os.path.exists(example_path):
            logger.info("Example found: %s", example_path)
            return True
        else:
            logger.warning("Could not find NS-3 examples")
            return False
    except Exception as e:
        logger.error("Error while checking NS-3 functionality: %s", e)
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
            logger.info("Automatically found NS-3 path: %s", path)
            return str(path)

    # Проверяем системные пути
    ns3_cmd = shutil.which("ns3")
    if ns3_cmd:
        # Если ns3 найден в системном PATH, определяем его директорию
        ns3_dir = str(Path(ns3_cmd).parent)
        logger.info("Found NS-3 in system PATH: %s", ns3_dir)
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
                logger.error(
                    "Failed to automatically detect NS-3 path. Please use --ns3-path or set the NS3_DIR environment variable"
                )
                sys.exit(1)

    logger.info("Checking NS-3 at path: %s", ns3_path)

    # Проверка доступности NS-3
    if not check_ns3_availability(ns3_path):
        logger.error("NS-3 is unavailable or incorrectly installed")
        sys.exit(1)

    logger.info("NS-3 successfully detected")

    # Проверка статуса сборки
    if not check_build_status(ns3_path):
        logger.warning("NS-3 may not be fully built or the build is corrupted")
    else:
        logger.info("NS-3 build appears correct")

    # Проверка базовой функциональности
    if check_basic_ns3_functionality(ns3_path):
        logger.info("Basic NS-3 examples found")

    # Проверка доступных модулей
    modules = check_ns3_modules(ns3_path)
    if modules:
        logger.info(
            "Available NS-3 modules (%d):", len(modules)
        )
        if args.verbose:
            for i, module in enumerate(modules, 1):
                logger.info("%s. %s", i, module)
        else:
            logger.info(
                ", ".join(modules[:10]) + (", ..." if len(modules) > 10 else "")
            )

        # Проверка наличия необходимых модулей
        required_modules = [
            "core",
            "network",
            "internet",
            "applications",
            "mobility",
            "wifi",
        ]
        missing_modules = [mod for mod in required_modules if mod not in modules]

        if missing_modules:
            logger.warning(
                "Missing required modules: %s", ", ".join(missing_modules)
            )
        else:
            logger.info("All required modules are present")
    else:
        logger.warning("Could not get list of NS-3 modules")

    logger.info("NS-3 check completed successfully!")


if __name__ == "__main__":
    main()

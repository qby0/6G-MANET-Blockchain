#!/usr/bin/env python3
"""
Скрипт для исправления проблемы с распределением случайных чисел в симуляции.
Исправляет некорректное использование secrets.randbelow в файлах симуляции.
"""

import os
import re
import sys
from pathlib import Path


def find_simulation_files(root_dir):
    """Поиск файлов симуляции с использованием secrets.randbelow"""
    simulation_files = []

    # Паттерн для поиска проблемного использования secrets.randbelow
    pattern = r"\(\s*\(\s*[-\d.]+\s*\)\s*\+\s*\(\s*secrets\.randbelow\s*\(\s*int\s*\(\s*\([-\d.]+\s*-\s*[-\d.]+\s*\)\s*\*\s*1000\s*\)\s*\)\s*/\s*1000\.0\s*\)\s*\)"

    for path in Path(root_dir).rglob("*.py"):
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
            if "secrets.randbelow" in content and re.search(pattern, content):
                simulation_files.append(str(path))

    return simulation_files


def fix_randbelow_usage(file_path):
    """Исправляет использование secrets.randbelow в файле"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Паттерн для поиска выражений вида ((min) + (secrets.randbelow(int((max - min) * 1000)) / 1000.0))
    pattern = r"\(\s*\(\s*([-\d.]+)\s*\)\s*\+\s*\(\s*secrets\.randbelow\s*\(\s*int\s*\(\s*\(\s*([-\d.]+)\s*-\s*([-\d.]+)\s*\)\s*\*\s*1000\s*\)\s*\)\s*/\s*1000\.0\s*\)\s*\)"

    def replace_func(match):
        min_val = float(match.group(1))
        max_val = float(match.group(2))
        min_val2 = float(match.group(3))  # Должно совпадать с min_val

        # Проверяем, что min_val == min_val2
        if min_val != min_val2:
            print(
                f"ПРЕДУПРЕЖДЕНИЕ: Несоответствие минимальных значений в {file_path}: {min_val} != {min_val2}"
            )

        # Формируем правильное выражение
        range_size = max_val - min_val
        return f"(min({max_val}, max({min_val}, {min_val} + secrets.randbelow(int({range_size} * 1000)) / 1000.0)))"

    # Исправляем выражения
    new_content = re.sub(pattern, replace_func, content)

    # Проверяем, были ли изменения
    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        return True

    return False


def main():
    # Определяем корневую директорию проекта
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_ns3_blocksim"
        )

    if not os.path.exists(root_dir):
        print(f"Директория {root_dir} не найдена")
        return 1

    print(f"Поиск файлов симуляции в {root_dir}")
    simulation_files = find_simulation_files(root_dir)

    if not simulation_files:
        print("Не найдено файлов с проблемным использованием secrets.randbelow")
        return 0

    print(
        f"Найдено {len(simulation_files)} файлов с проблемным использованием secrets.randbelow:"
    )
    for file_path in simulation_files:
        print(f"  - {file_path}")

    fixed_count = 0
    for file_path in simulation_files:
        if fix_randbelow_usage(file_path):
            print(f"✓ Исправлен файл: {file_path}")
            fixed_count += 1
        else:
            print(f"✗ Не удалось исправить: {file_path}")

    print(f"\nИтого: исправлено {fixed_count} из {len(simulation_files)} файлов")

    return 0


if __name__ == "__main__":
    sys.exit(main())

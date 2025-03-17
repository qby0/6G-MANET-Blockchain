# Интеграция NS-3 и BlockSim для симуляции блокчейн-системы в 6G/MANET сетях
## Обзор
Этот проект демонстрирует интеграцию NS-3 (Network Simulator 3) и BlockSim для симуляции работы блокчейн-системы в условиях гибридной сетевой инфраструктуры 6G и MANET.

## Структура проекта
- `config/` - конфигурационные файлы для различных сценариев симуляции
- `models/` - модели для BlokSim и дополнительные классы для NS-3
- `scripts/` - скрипты для запуска различных симуляций
- `visualization/` - инструменты для визуализации результатов симуляции
- `results/` - директория для сохранения результатов симуляций

## Требования
- NS-3 (рекомендуется версия 3.36 или выше)
- Python 3.8+
- Зависимости из файла requirements.txt
- Qt5 (для NetAnim)
- ccache (для ускорения сборки)

## Быстрая установка и сборка

1. Установите системные зависимости:
   ```bash
   # Ubuntu/Debian
   sudo apt install ccache qt5-default python3-dev cmake ninja-build
   
   # Fedora
   sudo dnf install ccache qt5-devel python3-devel cmake ninja-build
   ```

2. Установите Python-зависимости:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Настройте и соберите NS-3 с оптимизациями:
   ```bash
   cd external/ns-3
   
   # Настройка ccache для ускорения пересборки
   export CCACHE_DIR=$(pwd)/.ccache
   export CCACHE_MAXSIZE=50G
   
   # Конфигурация с оптимизациями
   ./ns3 configure --enable-examples --enable-tests \
                  --enable-python-bindings \
                  --enable-modules='netanim' \
                  --build-profile=optimized \
                  --enable-ccache \
                  --enable-ninja
   
   # Параллельная сборка (используем все доступные ядра)
   ./ns3 build -j$(nproc)
   ```

4. Настройте переменные окружения:
   ```bash
   export NS3_DIR=$(pwd)
   cd ../..
   ```

## Запуск симуляции с визуализацией
1. Базовая симуляция:
   ```bash
   python scripts/run_basic_simulation.py
   ```

2. Запуск NetAnim для визуализации:
   ```bash
   cd $NS3_DIR/netanim
   ./NetAnim
   ```
   Затем откройте сгенерированный XML файл из директории results/

## Сценарии моделирования
1. **baseline_scenario** - базовая симуляция с фиксированными узлами
2. **mobility_scenario** - сценарий с мобильными узлами по модели RandomWalk
3. **urban_scenario** - сценарий городской среды с реалистичным движением узлов

## Визуализация результатов
```bash
python visualization/plot_results.py --input results/simulation_output.json
```

## Примеры
В директории `examples/` находятся детальные примеры использования системы для разных сценариев.

## Советы по производительности
- Используйте ccache для ускорения повторных сборок
- Включайте только необходимые модули при конфигурации NS-3
- Используйте оптимизированный профиль сборки
- При разработке используйте debug профиль только при необходимости
- Используйте ninja вместо make для более быстрой сборки

## Архитектура интеграции
Интеграция NS-3 и BlockSim реализована через промежуточный интерфейс, который синхронизирует события между двумя симуляторами и обеспечивает согласованность данных.
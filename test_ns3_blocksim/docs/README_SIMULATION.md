# Advanced Realistic Cross-Zone Blockchain Simulation

Продвинутая симуляция кросс-зонального блокчейна с реалистичными параметрами устройств и красивой визуализацией статистики.

## 🚀 Быстрый старт

### Простой запуск
```bash
# Запуск с базовыми настройками (10 минут, средний город)
python3 run_simulation.py

# Быстрый тест (1 минута)
python3 run_simulation.py --quick-test

# Полная симуляция с всеми визуализациями
python3 run_simulation.py --scenario large_city --duration 1200 --all-visualizations
```

## 📊 Возможности

### Реалистичные устройства
- **Смартфоны**: 10 GFLOPS, 8GB RAM, батарея 4000mAh
- **IoT сенсоры**: 0.5 GFLOPS, 512MB RAM, батарея 2000mAh  
- **Автомобили**: 30 GFLOPS, 8GB RAM, неограниченное питание
- **5G базовые станции**: 1200 GFLOPS, 64GB RAM
- **Edge серверы**: 2500 GFLOPS, 256GB RAM

### Красивая визуализация
- 📊 **Основной дашборд**: 12 интерактивных графиков
- 👔 **Исполнительный дашборд**: Для руководителей и презентаций
- 🎯 **Интерактивные графики**: HTML дашборды с Plotly
- 📝 **Научные графики**: Готовые для публикаций
- 📋 **Комплексный отчет**: Markdown с полным анализом

### Сбор статистики
- ⚡ Потребление энергии по типам устройств
- 🔋 Анализ батарей мобильных устройств
- 📡 Распределение по зонам (5G, Bridge, MANET)
- 💳 Пропускная способность транзакций
- ⏱️ Производительность консенсуса
- 🌐 Переходы между зонами
- 📈 Производительность валидаторов

## 🎨 Примеры визуализации

### Основной дашборд
![Simulation Dashboard](results/simulation_dashboard.png)

### Исполнительный дашборд  
![Executive Dashboard](results/executive_dashboard.png)

### Интерактивная визуализация
- **HTML файл**: `results/interactive_dashboard.html`
- **Возможности**: Зум, фильтры, анимация, экспорт

## 📋 Параметры командной строки

### Основные параметры
```bash
--scenario SCENARIO        # Сценарий симуляции
  ├── small_campus         # Малый кампус (1 км², 20 устройств)
  ├── medium_district      # Средний район (4 км², 50 устройств) [по умолчанию]
  └── large_city           # Большой город (16 км², 100 устройств)

--duration SECONDS         # Длительность симуляции в секундах [600]
--output-dir PATH          # Папка для результатов [results]
```

### Опции визуализации
```bash
--executive-dashboard      # Создать исполнительный дашборд
--interactive-plots        # Создать интерактивные HTML графики
--publication-plots        # Создать графики для публикаций
--all-visualizations       # Создать все типы визуализации
```

### Отладка
```bash
--verbose                  # Подробное логирование
--quick-test              # Быстрый тест (60 секунд, малый кампус)
```

## 📈 Примеры использования

### 1. Быстрая проверка системы
```bash
python3 run_simulation.py --quick-test --all-visualizations
```

### 2. Стандартная симуляция для исследования
```bash
python3 run_simulation.py --scenario medium_district --duration 600 --executive-dashboard
```

### 3. Полная симуляция для публикации
```bash
python3 run_simulation.py \
  --scenario large_city \
  --duration 1800 \
  --all-visualizations \
  --verbose
```

### 4. Сравнение сценариев
```bash
# Малый кампус
python3 run_simulation.py --scenario small_campus --output-dir results_small

# Средний район  
python3 run_simulation.py --scenario medium_district --output-dir results_medium

# Большой город
python3 run_simulation.py --scenario large_city --output-dir results_large
```

## 📁 Структура результатов

После запуска симуляции создаются следующие файлы:

```
results/
├── 📊 Основные результаты
│   ├── simulation_dashboard.png      # Главный дашборд (12 графиков)
│   ├── simulation_summary.json       # Сырые данные статистики
│   └── comprehensive_report.md       # Полный текстовый отчет
│
├── 🎨 Продвинутая визуализация  
│   ├── executive_dashboard.png       # Исполнительный дашборд
│   ├── interactive_dashboard.html    # Интерактивные графики
│   ├── energy_consumption_detailed.png
│   └── zone_distribution_detailed.png
│
└── 📝 Научные графики
    ├── performance_comparison.png    # Сравнение производительности
    ├── energy_analysis.png          # Анализ энергоэффективности
    └── network_dynamics.png         # Динамика сети
```

## 🔧 Установка зависимостей

### Автоматическая установка
```bash
pip3 install -r requirements.txt
```

### Ручная установка
```bash
pip3 install matplotlib seaborn numpy pandas scipy networkx plotly
```

## 📊 Ключевые метрики

Симуляция отслеживает следующие показатели:

### Энергоэффективность
- Общее потребление энергии (mJ)
- Энергия на транзакцию (mJ/tx)
- Энергия на блок (mJ/block)
- Распределение по типам устройств

### Производительность сети
- Пропускная способность (tx/min)
- Время консенсуса (секунды)
- Успешность транзакций (%)
- Время работы устройств (%)

### Мобильность и зоны
- Распределение по зонам (5G/Bridge/MANET)
- Переходы между зонами
- Уровень батарей мобильных устройств
- Качество сетевого соединения

## 🎯 Сценарии симуляции

### Small Campus (Малый кампус)
- **Площадь**: 1 км²
- **Устройства**: ~20
- **Фокус**: Локальная сеть, высокая плотность
- **Время**: 5-10 минут

### Medium District (Средний район)
- **Площадь**: 4 км²  
- **Устройства**: ~50
- **Фокус**: Смешанная среда, балансировка зон
- **Время**: 10-20 минут

### Large City (Большой город)
- **Площадь**: 16 км²
- **Устройства**: ~100
- **Фокус**: Масштабируемость, множественные зоны
- **Время**: 20-30 минут

## 🔍 Анализ результатов

### Автоматический анализ
Симуляция автоматически генерирует:
- Исполнительное резюме
- Рекомендации по оптимизации
- Сравнение с теоретическими лимитами
- Выявление узких мест

### Ключевые вопросы для анализа
1. **Энергоэффективность**: Какие устройства потребляют больше всего энергии?
2. **Масштабируемость**: Как производительность меняется с увеличением нагрузки?
3. **Мобильность**: Как переходы между зонами влияют на производительность?
4. **Консенсус**: Оптимальны ли параметры консенсуса?

## ⚡ Оптимизация производительности

### Быстрая симуляция
```bash
# Минимальная симуляция (1 минута)
python3 run_simulation.py --duration 60 --scenario small_campus

# Без визуализации (быстрее)
python3 advanced_realistic_simulation.py --duration 300
```

### Детальная симуляция
```bash
# Максимальная детализация (30 минут)
python3 run_simulation.py \
  --duration 1800 \
  --scenario large_city \
  --all-visualizations \
  --verbose
```

## 🐛 Устранение неполадок

### Ошибки импорта
```bash
# Проверить установку зависимостей
pip3 list | grep -E "(matplotlib|seaborn|numpy|pandas)"

# Переустановить зависимости
pip3 install --upgrade -r requirements.txt
```

### Ошибки реалистичного менеджера устройств
```bash
# Запустить тест устройств
python3 scripts/test_realistic_devices.py

# Проверить конфигурацию
ls -la config/realistic_device_config.json
```

### Проблемы с визуализацией
```bash
# Проверить matplotlib backend
python3 -c "import matplotlib; print(matplotlib.get_backend())"

# Для серверной среды без GUI
export MPLBACKEND=Agg
```

## 📚 Дополнительные ресурсы

### Документация
- `DEVICE_PARAMETERS.md` - Параметры устройств
- `STATISTICS_ANALYSIS.md` - Анализ статистики
- `README.md` - Общая документация проекта

### Примеры данных
- `results/simulation_summary.json` - Пример результатов
- `config/realistic_device_config.json` - Конфигурация устройств

### Расширения
- Добавление новых типов устройств
- Кастомные алгоритмы консенсуса
- Интеграция с внешними системами мониторинга

---

## 🎉 Готовые команды для копирования

### Быстрый старт
```bash
python3 run_simulation.py --quick-test --all-visualizations
```

### Стандартная симуляция
```bash
python3 run_simulation.py --scenario medium_district --duration 600 --executive-dashboard
```

### Полная научная симуляция
```bash
python3 run_simulation.py --scenario large_city --duration 1200 --all-visualizations --verbose
```

**🚀 Начните с быстрого теста, а затем переходите к полной симуляции!** 
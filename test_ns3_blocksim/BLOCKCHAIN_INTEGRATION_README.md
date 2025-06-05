# 🚀 Real C++ Blockchain Integration with NS-3

Это реальная интеграция полноценного C++ блокчейн модуля с NS-3, обеспечивающая настоящий сетевой трафик блокчейна в MANET симуляции.

## 🎯 Что это дает

**Это НЕ Python-заглушка**, это настоящая интеграция:

- ✅ **Реальные UDP пакеты** с блокчейн заголовками передаются по сети
- ✅ **Настоящий AODV маршрутинг** блокчейн трафика между зонами
- ✅ **Реальная валидация транзакций** валидаторами в зоне 6G
- ✅ **Фактическое создание блоков** с merkle root и proof-of-work
- ✅ **Полная трассировка PCAP/ASCII** для анализа сетевого трафика
- ✅ **Интеграция C++ ↔ Python** через NS-3 биндинги

## 📁 Структура интеграции

```
test_ns3_blocksim/
├── external/ns-3/src/blockchain/           # 🔥 НОВЫЙ C++ МОДУЛЬ
│   ├── model/
│   │   ├── blockchain-tx-header.{h,cc}     # Заголовки транзакций
│   │   ├── blockchain-ledger.{h,cc}        # Управление блокчейном
│   │   ├── zone-manager.{h,cc}             # Управление зонами
│   │   ├── gateway-discovery-protocol.{h,cc} # Обнаружение шлюзов
│   │   └── cross-zone-blockchain-app.{h,cc}  # Основное приложение
│   ├── helper/
│   │   ├── cross-zone-blockchain-helper.{h,cc} # Helper для настройки
│   │   └── gateway-discovery-helper.{h,cc}     # Helper для шлюзов
│   └── wscript                             # Конфигурация сборки
├── real_sim/scripts/
│   ├── test_blockchain_integration.py      # Тесты интеграции
│   └── real_blockchain_simulation.py       # Реальная симуляция
└── BLOCKCHAIN_INTEGRATION_README.md        # Эта документация
```

## 🔨 Сборка и настройка

### 1. Компиляция блокчейн модуля

```bash
cd test_ns3_blocksim/external/ns-3

# Конфигурация с включением блокчейн модуля
./ns3 configure --enable-examples --enable-python --enable-modules=blockchain,wifi,aodv,applications

# Сборка
./ns3 build
```

### 2. Проверка успешной сборки

```bash
# Проверка что модуль скомпилировался
ls build/lib/*blockchain*

# Должно показать:
# libns3-blockchain.so (или .dylib на macOS)
```

### 3. Тестирование интеграции

```bash
cd ../../real_sim/scripts

# Запуск полных тестов интеграции
python3 test_blockchain_integration.py

# Если все тесты прошли, готово к работе!
```

## 🚀 Использование

### Быстрый старт

```bash
# Запуск с автоматическим тестом интеграции
python3 real_blockchain_simulation.py --test-integration --scenario medium_district --duration 60

# Результаты будут в папке results/
```

### Параметры запуска

```bash
python3 real_blockchain_simulation.py \
    --scenario large_city \        # Сценарий: small_campus, medium_district, large_city, stress_test
    --duration 120 \               # Длительность симуляции в секундах
    --output-dir ./my_results \    # Директория для результатов
    --test-integration             # Опционально: тест перед запуском
```

### Доступные сценарии

| Сценарий | Узлы | Валидаторы | Описание |
|----------|------|------------|----------|
| `small_campus` | 10 | 3 | Небольшой кампус |
| `medium_district` | 15 | 4 | Средний район |
| `large_city` | 25 | 6 | Большой город |
| `stress_test` | 50 | 10 | Стресс-тест |

## 📊 Результаты и аналитика

### Файлы результатов

После симуляции создаются:

```
results/
├── blockchain_simulation_results.json     # JSON с полной статистикой
├── blockchain-trace.tr                    # ASCII трассировка NS-3
├── blockchain-0-0.pcap                   # PCAP файлы для Wireshark
├── blockchain-1-0.pcap                   # (по одному на каждый узел)
└── ...
```

### Анализ PCAP в Wireshark

1. Откройте `blockchain-*.pcap` в Wireshark
2. Фильтр для блокчейн трафика: `udp.port == 7000`
3. Вы увидите реальные UDP пакеты с блокчейн заголовками!

### Пример JSON результатов

```json
{
  "simulation_duration": 60,
  "scenario": "medium_district", 
  "real_cpp_integration": true,
  "blockchain_stats": {
    "total_transactions": 45,
    "total_blocks": 3,
    "total_validators": 4,
    "duplicate_transactions": 2
  },
  "zone_stats": {
    "6g_nodes": 4,
    "bridge_nodes": 6, 
    "manet_nodes": 5,
    "6g_validators": 4
  },
  "trace_files": {
    "ascii": "results/blockchain-trace.tr",
    "pcap": "results/blockchain"
  }
}
```

## 🔧 Архитектура интеграции

### Основные C++ классы

#### 1. `BlockchainTxHeader`
- Заголовок для блокчейн транзакций
- Сериализация/десериализация для передачи по сети
- Поля: txId, zoneSource, zoneDestination, timestamp, etc.

#### 2. `BlockchainLedger` 
- Управление состоянием блокчейна
- Mempool для неподтвержденных транзакций
- Валидация блоков с merkle root
- Обнаружение дубликатов

#### 3. `ZoneManager`
- Управление зонами (6G, Bridge, MANET)
- Отслеживание перемещений узлов между зонами
- Управление валидаторами
- Callback для изменения зон

#### 4. `CrossZoneBlockchainApp`
- Основное NS-3 приложение
- Генерация и обработка транзакций
- Маршрутизация между зонами
- Создание блоков валидаторами

#### 5. `CrossZoneBlockchainHelper`
- Helper для упрощения настройки
- Автоматическая конфигурация зон
- Установка приложений на узлы
- Сбор статистики

### Поток данных

```
Python Script
     ↓
NS-3 Python Bindings  
     ↓
C++ Blockchain Module
     ↓
Real UDP Packets with BlockchainTxHeader
     ↓
AODV Routing (real network simulation)
     ↓ 
Zone-based Validator Processing
     ↓
Block Creation & Consensus
     ↓
PCAP/ASCII Trace Files
     ↓
Python Analytics & Visualization
```

## 🌐 Сетевая топология

### Зонная архитектура

```
     🗼 Central 6G Tower (150,150,30m)
    ╔═══════════════════════════════════╗
    ║           6G Zone (r=100m)        ║  ← Validators here
    ║  📱 6G Nodes (potential validators) ║
    ║     ╔═══════════════════════════╗   ║
    ║     ║    Bridge Zone (r=150m)   ║   ║  ← Bridge coverage
    ║     ║  🌉 Bridge Nodes         ║   ║
    ║     ║                         ║   ║
    ║     ╚═══════════════════════════╝   ║
    ╚═══════════════════════════════════╝
  🌐 MANET Zone (everywhere else)  ← AODV routing
```

### Валидаторы

- **Только узлы в 6G зоне** могут быть валидаторами
- **Автоматическая ротация** валидаторов каждые 30 секунд
- **Мобильность**: если узел покидает 6G зону, теряет статус валидатора

## 🔍 Отладка и устранение неполадок

### Частые проблемы

#### 1. Ошибка компиляции модуля
```bash
# Проверьте зависимости
./ns3 configure --enable-examples --enable-python

# Очистите и пересоберите
./ns3 clean
./ns3 build
```

#### 2. ImportError: No module named 'ns.blockchain'
```bash
# Проверьте что модуль собран
ls build/lib/*blockchain*

# Проверьте Python биндинги
./ns3 build --enable-python
```

#### 3. Нет сетевого трафика в PCAP
```bash
# Увеличьте время симуляции
python3 real_blockchain_simulation.py --duration 120

# Проверьте логи NS-3
export NS_LOG="CrossZoneBlockchainApp=level_all"
```

### Полезные команды отладки

```bash
# Детальные логи NS-3
export NS_LOG="CrossZoneBlockchainApp=level_all:ZoneManager=level_all"

# Проверка сборки модуля
./ns3 show profile

# Тест простой симуляции
./ns3 run blockchain-integration-test
```

## 📈 Метрики для анализа

### Блокчейн метрики
- **Transaction latency**: время от создания до включения в блок
- **Duplicate rate**: процент дублирующихся транзакций
- **Validator efficiency**: блоков создано на валидатора
- **Zone transition rate**: переходы узлов между зонами

### Сетевые метрики
- **Hop count**: среднее количество прыжков для транзакций
- **Packet loss**: потери пакетов при AODV маршрутизации
- **End-to-end delay**: задержка доставки пакетов
- **Network throughput**: пропускная способность блокчейн трафика

## 🎯 Дальнейшее развитие

### Возможные улучшения

1. **Advanced Consensus**: Добавить PBFT или другие алгоритмы консенсуса
2. **Smart Contracts**: Интеграция виртуальной машины для смарт-контрактов  
3. **Sharding**: Разделение блокчейна между зонами
4. **Energy Model**: Модель энергопотребления для blockchain операций
5. **Security**: Добавить криптографическую безопасность

### Интеграция с другими модулями

- **LTE/5G Module**: Реальное 5G/6G моделирование
- **Energy Module**: Анализ энергопотребления
- **Buildings Module**: Моделирование в городской среде
- **Spectrum Module**: Детальное моделирование радиоканала

## 🤝 Как это поможет в защите

Эта реальная интеграция даст вам:

1. **Конкретные цифры**: Реальные метрики сетевого трафика
2. **Визуализацию**: PCAP файлы можно показать в Wireshark
3. **Масштабируемость**: Тестирование на разных размерах сети
4. **Валидность**: Настоящее сетевое моделирование, не заглушки

## 📞 Поддержка

При возникновении проблем:

1. Запустите `test_blockchain_integration.py` для диагностики
2. Проверьте логи NS-3 с включенным NS_LOG
3. Убедитесь что все зависимости установлены
4. Проверьте права доступа к файлам результатов

---

🎉 **Поздравляем! Теперь у вас есть полноценная реальная интеграция C++ блокчейн модуля с NS-3!** 
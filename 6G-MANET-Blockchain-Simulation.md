# 6G-MANET-Blockchain Simulation / Симуляция блокчейна в сетях 6G-MANET

[English](#english) | [Русский](#русский)

## English <a name="english"></a>

# Blockchain System Simulation at the Junction of 6G and MANET Networks

## Overview
This project implements a simulation of a blockchain system operating at the junction of 6G and MANET networks. It integrates NS-3 (Network Simulator 3) with custom blockchain simulation components to model the behavior of a decentralized network with mobile nodes.

## Features
- Realistic simulation of MANET (Mobile Ad-hoc Network) using NS-3
- Integration with blockchain components for distributed ledger functionality
- Support for different node types (base station, validators, regular nodes)
- Dynamic topology changes and node mobility simulation
- Configurable parameters for network and blockchain behavior
- Data visualization and result analysis tools

## Repository Structure
- `/test_ns3_blocksim` - Main simulation framework
  - `/config` - Configuration files for different simulation scenarios
  - `/models` - Core models for the simulation
  - `/scripts` - Scripts for running simulations
  - `/visualization` - Tools for visualizing simulation results
  - `/results` - Directory for storing simulation results
  - `/external` - External dependencies (NS-3)

## Documentation
- [Implementation Status](test_ns3_blocksim/README_IMPLEMENTATION_STATUS_EN.md) - Current state of implementation
- [Technical README](test_ns3_blocksim/README.md) - Technical details and usage instructions

## Getting Started
See the [Technical README](test_ns3_blocksim/README.md) for detailed installation and setup instructions.

## License
[MIT License](LICENSE)

---

## Русский <a name="русский"></a>

# Симуляция блокчейн-системы на стыке сетей 6G и MANET

## Обзор
Этот проект реализует симуляцию блокчейн-системы, работающей на стыке сетей 6G и MANET. Он интегрирует NS-3 (Network Simulator 3) с компонентами симуляции блокчейна для моделирования поведения децентрализованной сети с мобильными узлами.

## Возможности
- Реалистичная симуляция MANET (мобильной ad-hoc сети) с использованием NS-3
- Интеграция с компонентами блокчейна для функциональности распределенного реестра
- Поддержка различных типов узлов (базовая станция, валидаторы, обычные узлы)
- Симуляция динамических изменений топологии и мобильности узлов
- Настраиваемые параметры для поведения сети и блокчейна
- Инструменты визуализации данных и анализа результатов

## Структура репозитория
- `/test_ns3_blocksim` - Основной фреймворк симуляции
  - `/config` - Конфигурационные файлы для различных сценариев симуляции
  - `/models` - Основные модели для симуляции
  - `/scripts` - Скрипты для запуска симуляций
  - `/visualization` - Инструменты для визуализации результатов симуляции
  - `/results` - Директория для хранения результатов симуляции
  - `/external` - Внешние зависимости (NS-3)

## Документация
- [Статус реализации](test_ns3_blocksim/README_IMPLEMENTATION_STATUS_EN.md) - Текущее состояние реализации
- [Технический README](test_ns3_blocksim/README.md) - Технические детали и инструкции по использованию

## Начало работы
См. [Технический README](test_ns3_blocksim/README.md) для подробных инструкций по установке и настройке.

## Лицензия
[Лицензия MIT](LICENSE) 
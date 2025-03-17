#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для визуализации результатов интегрированной симуляции NS-3 и BlockSim.
"""

import os
import sys
import json
import argparse
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.patches import Circle
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple

# Добавляем корневой каталог проекта в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description='Визуализация результатов симуляции')
    
    parser.add_argument('--input', type=str, required=True,
                        help='Путь к файлу с результатами симуляции')
    parser.add_argument('--output-dir', type=str, default='../results',
                        help='Директория для сохранения визуализаций')
    parser.add_argument('--format', type=str, default='png',
                        help='Формат файлов изображений (png, pdf, svg)')
    
    return parser.parse_args()

def load_simulation_data(filepath):
    """Загрузка данных симуляции из файла JSON."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка при загрузке файла {filepath}: {e}")
        sys.exit(1)

def visualize_network_topology(data, output_path):
    """
    Визуализация топологии сети и связей между узлами.
    
    Args:
        data (Dict): Данные о состоянии сети
        output_path (str): Путь для сохранения изображения
    """
    plt.figure(figsize=(12, 10))
    
    # Создаем граф
    G = nx.Graph()
    
    # Добавляем узлы
    for node_id, node_data in data['nodes'].items():
        G.add_node(node_id)
        
    # Добавляем связи
    for link_id, link_data in data['links'].items():
        nodes = link_data.get('nodes', [])
        if len(nodes) >= 2:
            G.add_edge(nodes[0], nodes[1], weight=link_data.get('quality', 0.5))
    
    # Позиционируем узлы
    # В реальном случае, мы могли бы использовать позиции из симуляции
    pos = {}
    for node_id, node_data in data['nodes'].items():
        pos[node_id] = (node_data['position'][0], node_data['position'][1])
    
    # Цвета для разных типов узлов
    color_map = {
        'base_station': 'red',
        'validator': 'green',
        'regular': 'blue'
    }
    
    # Рисуем узлы с разными цветами в зависимости от типа
    for node_type, color in color_map.items():
        node_list = [node_id for node_id, node_data in data['nodes'].items() if node_data.get('type') == node_type]
        nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color=color, 
                             node_size=[300 if node_type == 'base_station' else 
                                       200 if node_type == 'validator' else 100 for _ in node_list], 
                             alpha=0.8, label=node_type)
    
    # Рисуем ребра
    edge_weights = [G[u][v].get('weight', 0.5) for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color=edge_weights, edge_cmap=plt.cm.Blues)
    
    # Рисуем метки узлов
    nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
    
    plt.title("Топология сети")
    plt.axis('off')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Визуализация топологии сети сохранена: {output_path}")

def visualize_transaction_statistics(data, output_path):
    """
    Визуализация статистики транзакций.
    
    Args:
        data (Dict): Данные о транзакциях
        output_path (str): Путь для сохранения изображения
    """
    plt.figure(figsize=(10, 6))
    
    # Собираем транзакции по временной метке
    timestamps = []
    for tx in data.get('transactions', []):
        timestamps.append(tx.get('timestamp', 0))
    
    # Создаем гистограмму
    plt.hist(timestamps, bins=20, alpha=0.7, color='blue', edgecolor='black')
    plt.title("Распределение транзакций по времени")
    plt.xlabel("Время симуляции (секунды)")
    plt.ylabel("Количество транзакций")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Визуализация статистики транзакций сохранена: {output_path}")

def visualize_blockchain_growth(data, output_path):
    """
    Визуализация роста блокчейна.
    
    Args:
        data (Dict): Данные о блокчейне
        output_path (str): Путь для сохранения изображения
    """
    plt.figure(figsize=(10, 6))
    
    # Собираем данные о блоках
    block_indices = []
    block_times = []
    block_sizes = []
    
    for block in data.get('blocks', []):
        block_indices.append(block.get('index', 0))
        block_times.append(block.get('timestamp', 0))
        block_sizes.append(block.get('size', 0))
    
    # Создаем два графика
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # График роста блокчейна по времени
    ax1.plot(block_times, block_indices, marker='o', linestyle='-', color='blue')
    ax1.set_title("Рост блокчейна")
    ax1.set_ylabel("Индекс блока")
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # График размеров блоков по времени
    ax2.bar(block_times, block_sizes, color='green', alpha=0.7)
    ax2.set_title("Размеры блоков")
    ax2.set_xlabel("Время симуляции (секунды)")
    ax2.set_ylabel("Размер блока (транзакции)")
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Визуализация роста блокчейна сохранена: {output_path}")

def visualize_node_activity(network_data, blockchain_data, output_path):
    """
    Визуализация активности узлов.
    
    Args:
        network_data (Dict): Данные о сети
        blockchain_data (Dict): Данные о блокчейне
        output_path (str): Путь для сохранения изображения
    """
    plt.figure(figsize=(12, 8))
    
    # Собираем данные об активности узлов
    node_ids = []
    tx_processed = []
    blocks_created = []
    
    for node_id, node_data in blockchain_data.get('nodes', {}).items():
        node_ids.append(node_id)
        tx_processed.append(node_data.get('transactions_processed', 0))
        blocks_created.append(node_data.get('blocks_created', 0))
    
    # Создаем график 
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(node_ids))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, tx_processed, width, label='Обработано транзакций')
    rects2 = ax.bar(x + width/2, blocks_created, width, label='Создано блоков')
    
    ax.set_title("Активность узлов")
    ax.set_xlabel("Идентификатор узла")
    ax.set_ylabel("Количество")
    ax.set_xticks(x)
    ax.set_xticklabels(node_ids, rotation=45, ha='right')
    ax.legend()
    
    fig.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Визуализация активности узлов сохранена: {output_path}")

def main():
    """Основная функция."""
    args = parse_arguments()
    
    # Создаем директорию для вывода, если не существует
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Определяем суффикс от входного файла
    input_basename = os.path.basename(args.input)
    if "network_state" in input_basename:
        # Обрабатываем файл состояния сети
        data = load_simulation_data(args.input)
        
        # Визуализируем топологию сети
        output_path = os.path.join(args.output_dir, f"network_topology.{args.format}")
        visualize_network_topology(data, output_path)
        
        # Визуализируем статистику транзакций
        output_path = os.path.join(args.output_dir, f"transaction_statistics.{args.format}")
        visualize_transaction_statistics(data, output_path)
        
    elif "blockchain_state" in input_basename:
        # Обрабатываем файл состояния блокчейна
        data = load_simulation_data(args.input)
        
        # Визуализируем рост блокчейна
        output_path = os.path.join(args.output_dir, f"blockchain_growth.{args.format}")
        visualize_blockchain_growth(data, output_path)
        
        # Если есть соответствующий файл с состоянием сети, визуализируем активность узлов
        network_file = args.input.replace("blockchain_state", "network_state")
        if os.path.exists(network_file):
            network_data = load_simulation_data(network_file)
            output_path = os.path.join(args.output_dir, f"node_activity.{args.format}")
            visualize_node_activity(network_data, data, output_path)
    
    else:
        print(f"Неизвестный формат входного файла: {args.input}")
        print("Ожидается файл с префиксом 'network_state' или 'blockchain_state'")
        sys.exit(1)
    
    print(f"Все визуализации сохранены в директории: {args.output_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
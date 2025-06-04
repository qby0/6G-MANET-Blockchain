#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from pathlib import Path

sys.path.append('src')
from dashboard_visualizer import DashboardVisualizer

def main():
    # Загружаем данные аналитики
    with open('results/full_clean_run/simulation_analytics_v2.json', 'r') as f:
        analytics = json.load(f)

    # Создаем визуализатор
    visualizer = DashboardVisualizer('results/full_clean_run')

    # Создаем графики
    try:
        print("🎨 Creating visualizations...")
        
        dashboard_path = visualizer.create_executive_dashboard(analytics)
        print(f'✅ Executive dashboard: {dashboard_path}')
        
        interactive_path = visualizer.create_interactive_dashboard(analytics)
        print(f'✅ Interactive dashboard: {interactive_path}')
        
        heatmap_path = visualizer.create_energy_consumption_heatmap(analytics)
        print(f'✅ Energy heatmap: {heatmap_path}')
        
        topology_path = visualizer.create_network_topology_visualization(analytics)
        print(f'✅ Network topology: {topology_path}')
        
        print("🎉 All visualizations created successfully!")
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
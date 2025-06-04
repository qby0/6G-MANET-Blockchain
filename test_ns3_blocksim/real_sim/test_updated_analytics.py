#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки обновленной системы аналитики
с новой структурой данных зон (5G_Zone, MANET_Zone, Bridge_Zone)
"""

import sys
import json
import logging
from pathlib import Path

# Добавляем пути к модулям
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))
sys.path.insert(0, str(current_dir / "scripts"))

try:
    from executive_dashboard_analyzer import ExecutiveDashboardAnalyzer
    from dashboard_visualizer import DashboardVisualizer
    from generate_executive_analytics import ExecutiveAnalyticsGenerator
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_updated_analytics():
    """Тестирование обновленной системы аналитики"""
    
    print("🚀 Тестирование обновленной системы аналитики")
    print("=" * 60)
    
    # Создаем генератор аналитики
    generator = ExecutiveAnalyticsGenerator(output_dir="results/test_updated")
    
    # Генерируем тестовые данные с новой структурой
    print("📊 Генерация тестовых данных...")
    sample_data = generator._generate_sample_data()
    
    # Проверяем структуру данных
    print(f"✅ Структура данных:")
    print(f"   - Устройства: {len(sample_data['devices'])}")
    print(f"   - Конфигурация симуляции: {len(sample_data['simulation_config'])} параметров")
    
    # Проверяем распределение по зонам
    zone_counts = {}
    for device in sample_data['devices']:
        zone = device['current_zone']
        zone_counts[zone] = zone_counts.get(zone, 0) + 1
    
    print(f"   - Распределение по зонам:")
    for zone, count in zone_counts.items():
        percentage = (count / len(sample_data['devices'])) * 100
        print(f"     * {zone}: {count} устройств ({percentage:.1f}%)")
    
    # Создаем анализатор
    print("\n🔍 Создание анализатора...")
    analyzer = ExecutiveDashboardAnalyzer(sample_data)
    
    # Тестируем анализ зон
    print("\n📍 Тестирование анализа зон...")
    zone_analysis = analyzer.analyze_zone_distribution()
    
    print(f"✅ Анализ зон завершен:")
    print(f"   - Всего устройств: {zone_analysis['total_devices']}")
    print(f"   - Зоны: {list(zone_analysis['zone_counts'].keys())}")
    
    for zone, percentage in zone_analysis['zone_percentages'].items():
        performance = zone_analysis['zone_performance'][zone]
        print(f"   - {zone}: {percentage:.1f}% (Score: {performance['performance_score']:.1f})")
    
    # Тестируем полный анализ
    print("\n📈 Выполнение полного анализа...")
    try:
        summary = analyzer.generate_executive_summary()
        print("✅ Полный анализ завершен успешно")
        
        # Выводим ключевые метрики
        print(f"\n📊 Ключевые метрики:")
        print(f"   - Здоровье сети: {summary['network_health']['score']:.1f}")
        print(f"   - Энергоэффективность: {summary['energy_efficiency']['efficiency_percentage']:.1f}%")
        print(f"   - Успешность транзакций: {summary['key_performance_indicators']['transactions']['success_rate']:.1f}%")
        print(f"   - Общая оценка: {summary['simulation_overview']['overall_performance_rating']}")
        
    except Exception as e:
        print(f"❌ Ошибка при полном анализе: {e}")
        return False
    
    # Тестируем визуализацию
    print("\n🎨 Тестирование визуализации...")
    try:
        visualizer = DashboardVisualizer(output_dir="results/test_updated")
        
        # Создаем дашборд
        dashboard_path = visualizer.create_executive_dashboard(summary)
        print(f"✅ Дашборд создан: {dashboard_path}")
        
        # Создаем интерактивный дашборд
        interactive_path = visualizer.create_interactive_dashboard(summary)
        print(f"✅ Интерактивный дашборд создан: {interactive_path}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании визуализации: {e}")
        return False
    
    # Сохраняем результаты тестирования
    test_results = {
        'test_status': 'SUCCESS',
        'zone_analysis': zone_analysis,
        'summary_metrics': {
            'network_health': summary['network_health']['score'],
            'energy_efficiency': summary['energy_efficiency']['efficiency_percentage'],
            'transaction_success': summary['key_performance_indicators']['transactions']['success_rate'],
            'overall_rating': summary['simulation_overview']['overall_performance_rating']
        },
        'files_created': [
            str(dashboard_path),
            str(interactive_path)
        ]
    }
    
    results_file = Path("results/test_updated/test_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Результаты тестирования сохранены: {results_file}")
    print("\n🎉 Все тесты пройдены успешно!")
    
    return True

def main():
    """Главная функция"""
    try:
        success = test_updated_analytics()
        if success:
            print("\n🚀 Система готова к использованию!")
            print("Запустите: python3 scripts/generate_executive_analytics.py")
        else:
            print("\n❌ Тестирование не пройдено")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
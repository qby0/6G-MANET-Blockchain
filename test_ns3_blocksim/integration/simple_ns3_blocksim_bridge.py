#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple NS-3 BlockSim Bridge
Minimal integration through file exchange
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add BlockSim path
BLOCKSIM_PATH = os.path.join(os.path.dirname(__file__), '..', 'external', 'BlockSim')
if BLOCKSIM_PATH not in sys.path:
    sys.path.insert(0, BLOCKSIM_PATH)

logger = logging.getLogger(__name__)

class SimpleNS3BlockSimBridge:
    """
    Simple bridge between NS-3 and BlockSim through files
    """
    
    def __init__(self, ipc_dir: str = "ns3_blocksim_ipc"):
        """
        Initialize simple bridge
        
        Args:
            ipc_dir: Directory for file exchange
        """
        self.logger = logging.getLogger("SimpleNS3BlockSimBridge")
        
        # Create IPC directory
        self.ipc_dir = Path(ipc_dir)
        self.ipc_dir.mkdir(exist_ok=True)
        
        # Exchange files
        self.ns3_to_blocksim_file = self.ipc_dir / "ns3_to_blocksim.json"
        self.blocksim_to_ns3_file = self.ipc_dir / "blocksim_to_ns3.json"
        self.status_file = self.ipc_dir / "bridge_status.json"
        
        # BlockSim state
        self.blocksim_initialized = False
        self.transaction_counter = 0
        self.processed_transactions = {}
        
        # Initialize BlockSim
        self._initialize_blocksim()
        
        # Create initial files
        self._create_initial_files()
        
        self.logger.info(f"Simple Bridge initialized, IPC dir: {self.ipc_dir}")
    
    def _initialize_blocksim(self):
        """Инициализация BlockSim"""
        try:
            # Переключаемся в директорию BlockSim
            original_cwd = os.getcwd()
            os.chdir(BLOCKSIM_PATH)
            
            # Импортируем BlockSim компоненты
            from InputsConfig import InputsConfig as p
            from Models.AppendableBlock.Node import Node
            from Models.AppendableBlock.Transaction import Transaction
            
            # Сохраняем ссылки
            self.blocksim_config = p
            self.BlockSimNode = Node
            self.BlockSimTransaction = Transaction
            
            # Создаем простые узлы
            self.gateway_node = Node("bridge_gateway", "g", [])
            self.bridge_nodes = {"bridge_gateway": self.gateway_node}
            
            # Возвращаемся в исходную директорию
            os.chdir(original_cwd)
            
            self.blocksim_initialized = True
            self.logger.info("BlockSim initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BlockSim: {e}")
            try:
                os.chdir(original_cwd)
            except:
                pass
            self.blocksim_initialized = False
    
    def _create_initial_files(self):
        """Create initial files for IPC"""
        # Bridge status
        status = {
            "bridge_active": True,
            "blocksim_initialized": self.blocksim_initialized,
            "last_update": time.time(),
            "processed_transactions": 0
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        # Empty file from NS-3 to BlockSim
        with open(self.ns3_to_blocksim_file, 'w') as f:
            json.dump({"transactions": [], "timestamp": time.time()}, f)
        
        # Empty file from BlockSim to NS-3
        with open(self.blocksim_to_ns3_file, 'w') as f:
            json.dump({"results": [], "timestamp": time.time()}, f)
    
    def process_ns3_transactions(self):
        """
        Process transactions from NS-3
        Reads ns3_to_blocksim.json file and processes new transactions
        """
        if not self.blocksim_initialized:
            self.logger.warning("BlockSim not initialized, skipping transaction processing")
            return
        
        try:
            # Read file from NS-3
            if not self.ns3_to_blocksim_file.exists():
                return
            
            with open(self.ns3_to_blocksim_file, 'r') as f:
                data = json.load(f)
            
            transactions = data.get("transactions", [])
            new_transactions = []
            
            # Process new transactions
            for tx in transactions:
                tx_id = tx.get("tx_id")
                if tx_id and tx_id not in self.processed_transactions:
                    result = self._process_single_transaction(tx)
                    new_transactions.append(result)
                    self.processed_transactions[tx_id] = result
            
            # If there are new results, write them
            if new_transactions:
                self._write_results_to_ns3(new_transactions)
                self.logger.info(f"Processed {len(new_transactions)} new transactions")
        
        except Exception as e:
            self.logger.error(f"Error processing NS-3 transactions: {e}")
    
    def _process_single_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка одной транзакции через BlockSim
        
        Args:
            tx: Транзакция от NS-3
            
        Returns:
            Результат обработки
        """
        try:
            # Переключаемся в BlockSim директорию
            original_cwd = os.getcwd()
            os.chdir(BLOCKSIM_PATH)
            
            # Создаем BlockSim транзакцию
            blocksim_tx = self.BlockSimTransaction(previous=-1)
            blocksim_tx.id = self.transaction_counter
            blocksim_tx.timestamp = [time.time()]
            blocksim_tx.sender = tx.get("sender_id", 0)
            blocksim_tx.to = "bridge_gateway"
            
            self.transaction_counter += 1
            
            # Простая валидация (в реальности здесь был бы consensus)
            validation_time = 0.1  # Симулируем время валидации
            time.sleep(validation_time)
            
            # Возвращаемся в исходную директорию
            os.chdir(original_cwd)
            
            # Создаем результат
            result = {
                "tx_id": tx.get("tx_id"),
                "sender_id": tx.get("sender_id"),
                "recipient_id": tx.get("recipient_id"),
                "validated": True,
                "validation_time": validation_time,
                "blocksim_tx_id": blocksim_tx.id,
                "timestamp": time.time(),
                "bridge_signature": f"bridge_sig_{blocksim_tx.id}_{int(time.time())}"
            }
            
            self.logger.debug(f"Processed transaction {tx.get('tx_id')} -> BlockSim ID {blocksim_tx.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing transaction {tx.get('tx_id')}: {e}")
            try:
                os.chdir(original_cwd)
            except:
                pass
            
            return {
                "tx_id": tx.get("tx_id"),
                "validated": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def _write_results_to_ns3(self, new_results: list):
        """Записать результаты для NS-3"""
        try:
            # Читаем существующие результаты
            existing_results = []
            if self.blocksim_to_ns3_file.exists():
                with open(self.blocksim_to_ns3_file, 'r') as f:
                    data = json.load(f)
                    existing_results = data.get("results", [])
            
            # Добавляем новые результаты
            all_results = existing_results + new_results
            
            # Ограничиваем количество результатов (последние 100)
            if len(all_results) > 100:
                all_results = all_results[-100:]
            
            # Записываем обновленные результаты
            output_data = {
                "results": all_results,
                "timestamp": time.time(),
                "total_processed": len(self.processed_transactions)
            }
            
            with open(self.blocksim_to_ns3_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error writing results to NS-3: {e}")
    
    def update_status(self):
        """Обновление файла статуса"""
        try:
            status = {
                "bridge_active": True,
                "blocksim_initialized": self.blocksim_initialized,
                "last_update": time.time(),
                "processed_transactions": len(self.processed_transactions),
                "transaction_counter": self.transaction_counter
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def run_continuous(self, check_interval: float = 0.5):
        """
        Непрерывная работа моста
        
        Args:
            check_interval: Интервал проверки новых транзакций
        """
        self.logger.info("Starting continuous bridge operation")
        
        try:
            while True:
                # Обрабатываем транзакции от NS-3
                self.process_ns3_transactions()
                
                # Обновляем статус
                self.update_status()
                
                # Ждем перед следующей проверкой
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Bridge stopped by user")
        except Exception as e:
            self.logger.error(f"Bridge error: {e}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            # Помечаем мост как неактивный
            status = {
                "bridge_active": False,
                "last_update": time.time(),
                "processed_transactions": len(self.processed_transactions)
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
            
            self.logger.info("Bridge cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def test_simple_bridge():
    """Тест простого моста"""
    logger = logging.getLogger("test")
    logger.info("Testing Simple NS-3 BlockSim Bridge...")
    
    try:
        # Создаем мост
        bridge = SimpleNS3BlockSimBridge("test_ipc")
        
        # Создаем тестовые транзакции от NS-3
        test_transactions = [
            {
                "tx_id": "test_tx_1",
                "sender_id": 1,
                "recipient_id": 2,
                "data": "Hello from NS-3!",
                "timestamp": time.time()
            },
            {
                "tx_id": "test_tx_2",
                "sender_id": 2,
                "recipient_id": 3,
                "data": "Cross-zone message",
                "timestamp": time.time()
            }
        ]
        
        # Записываем транзакции в файл (имитируем NS-3)
        ns3_data = {
            "transactions": test_transactions,
            "timestamp": time.time()
        }
        
        with open(bridge.ns3_to_blocksim_file, 'w') as f:
            json.dump(ns3_data, f, indent=2)
        
        logger.info("Created test transactions from NS-3")
        
        # Обрабатываем транзакции
        bridge.process_ns3_transactions()
        
        # Проверяем результаты
        time.sleep(0.5)
        
        if bridge.blocksim_to_ns3_file.exists():
            with open(bridge.blocksim_to_ns3_file, 'r') as f:
                results = json.load(f)
            
            logger.info(f"BlockSim processed {len(results.get('results', []))} transactions")
            
            for result in results.get('results', []):
                tx_id = result.get('tx_id')
                validated = result.get('validated', False)
                status = "✅ Validated" if validated else "❌ Failed"
                logger.info(f"  Transaction {tx_id}: {status}")
        
        # Очистка
        bridge.cleanup()
        
        logger.info("✅ Simple bridge test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Simple bridge test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_simple_bridge()
    else:
        # Запуск моста
        bridge = SimpleNS3BlockSimBridge()
        try:
            bridge.run_continuous()
        except KeyboardInterrupt:
            bridge.cleanup() 
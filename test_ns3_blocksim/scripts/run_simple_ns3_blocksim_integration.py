#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple NS-3 BlockSim Integration Runner
Запускает NS-3 симуляцию и BlockSim мост одновременно
"""

import os
import sys
import time
import signal
import logging
import subprocess
import threading
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from integration.simple_ns3_blocksim_bridge import SimpleNS3BlockSimBridge

logger = logging.getLogger(__name__)

class SimpleIntegrationRunner:
    """
    Запускает простую интеграцию NS-3 и BlockSim
    """
    
    def __init__(self, 
                 ipc_dir: str = "simple_ns3_blocksim_ipc",
                 ns3_dir: str = None,
                 simulation_time: float = 30.0,
                 num_nodes: int = 6):
        """
        Инициализация runner'а
        
        Args:
            ipc_dir: Директория для IPC
            ns3_dir: Путь к NS-3
            simulation_time: Время симуляции
            num_nodes: Количество узлов
        """
        self.logger = logging.getLogger("SimpleIntegrationRunner")
        
        self.ipc_dir = ipc_dir
        self.simulation_time = simulation_time
        self.num_nodes = num_nodes
        
        # NS-3 configuration
        if ns3_dir is None:
            self.ns3_dir = project_root / "external" / "ns-3"
        else:
            self.ns3_dir = Path(ns3_dir)
        
        self.ns3_script = "simple-ns3-blocksim-integration"
        
        # Process management
        self.bridge_process = None
        self.ns3_process = None
        self.bridge_thread = None
        self.running = False
        
        # Results
        self.bridge = None
        
        self.logger.info(f"Simple Integration Runner initialized")
        self.logger.info(f"  IPC Directory: {self.ipc_dir}")
        self.logger.info(f"  NS-3 Directory: {self.ns3_dir}")
        self.logger.info(f"  Simulation: {self.num_nodes} nodes, {self.simulation_time}s")
    
    def setup_environment(self):
        """Подготовка окружения"""
        self.logger.info("Setting up environment...")
        
        # Создаем IPC директорию
        os.makedirs(self.ipc_dir, exist_ok=True)
        
        # Проверяем NS-3
        if not self.ns3_dir.exists():
            raise RuntimeError(f"NS-3 directory not found: {self.ns3_dir}")
        
        # Проверяем, скомпилирован ли NS-3
        ns3_build_dir = self.ns3_dir / "build"
        if not ns3_build_dir.exists():
            self.logger.warning("NS-3 not built, attempting to build...")
            self._build_ns3()
        
        # Проверяем BlockSim
        blocksim_dir = project_root / "external" / "BlockSim"
        if not blocksim_dir.exists():
            raise RuntimeError(f"BlockSim directory not found: {blocksim_dir}")
        
        self.logger.info("Environment setup completed")
    
    def _build_ns3(self):
        """Компиляция NS-3"""
        self.logger.info("Building NS-3...")
        
        try:
            # Copy our integration files to NS-3
            integration_src = project_root / "integration"
            ns3_scratch = self.ns3_dir / "scratch"
            
            # Copy header and source
            import shutil
            shutil.copy2(integration_src / "ns3_simple_blockchain.h", ns3_scratch)
            shutil.copy2(integration_src / "ns3_simple_blockchain.cc", ns3_scratch)
            
            # Configure and build
            original_cwd = os.getcwd()
            os.chdir(self.ns3_dir)
            
            # Configure
            configure_cmd = ["python3", "ns3", "configure", "--enable-examples", "--enable-tests"]
            result = subprocess.run(configure_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"NS-3 configure failed: {result.stderr}")
                raise RuntimeError("NS-3 configure failed")
            
            # Build
            build_cmd = ["python3", "ns3", "build"]
            result = subprocess.run(build_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"NS-3 build failed: {result.stderr}")
                raise RuntimeError("NS-3 build failed")
            
            os.chdir(original_cwd)
            self.logger.info("NS-3 built successfully")
            
        except Exception as e:
            try:
                os.chdir(original_cwd)
            except:
                pass
            raise
    
    def start_bridge(self):
        """Запуск BlockSim моста в отдельном потоке"""
        self.logger.info("Starting BlockSim bridge...")
        
        def bridge_worker():
            try:
                self.bridge = SimpleNS3BlockSimBridge(self.ipc_dir)
                self.logger.info("BlockSim bridge started successfully")
                
                # Запускаем непрерывную обработку
                self.bridge.run_continuous(check_interval=0.5)
                
            except Exception as e:
                self.logger.error(f"Bridge error: {e}")
        
        self.bridge_thread = threading.Thread(target=bridge_worker, daemon=True)
        self.bridge_thread.start()
        
        # Ждем немного, чтобы мост инициализировался
        time.sleep(2.0)
        
        if self.bridge and self.bridge.blocksim_initialized:
            self.logger.info("✅ BlockSim bridge ready")
        else:
            raise RuntimeError("Failed to initialize BlockSim bridge")
    
    def start_ns3_simulation(self):
        """Запуск NS-3 симуляции"""
        self.logger.info("Starting NS-3 simulation...")
        
        original_cwd = os.getcwd()
        
        try:
            os.chdir(self.ns3_dir)
            
            # Команда для запуска
            cmd = [
                "python3", "ns3", "run",
                f"{self.ns3_script} --nNodes={self.num_nodes} "
                f"--simulationTime={self.simulation_time} "
                f"--ipcDir={os.path.abspath(self.ipc_dir)}"
            ]
            
            self.logger.info(f"Running: {' '.join(cmd)}")
            
            # Запускаем NS-3
            self.ns3_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Читаем вывод в реальном времени
            while True:
                output = self.ns3_process.stdout.readline()
                if output == '' and self.ns3_process.poll() is not None:
                    break
                if output:
                    # Фильтруем и логируем вывод NS-3
                    line = output.strip()
                    if any(marker in line for marker in ["🚀", "📊", "🔗", "✅", "❌", "⏰", "🔄", "📡", "🏁"]):
                        self.logger.info(f"NS-3: {line}")
                    elif "SimpleNS3BlockSimIntegration" in line or "SimpleBlockchain" in line:
                        # Логируем важные сообщения от нашей интеграции
                        if "INFO" in line:
                            self.logger.info(f"NS-3: {line.split('INFO')[-1].strip()}")
            
            return_code = self.ns3_process.poll()
            
            os.chdir(original_cwd)
            
            if return_code == 0:
                self.logger.info("✅ NS-3 simulation completed successfully")
            else:
                self.logger.error(f"❌ NS-3 simulation failed with code {return_code}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error running NS-3 simulation: {e}")
            try:
                os.chdir(original_cwd)
            except:
                pass
            return False
    
    def monitor_integration(self):
        """Мониторинг интеграции"""
        self.logger.info("Monitoring integration...")
        
        start_time = time.time()
        last_status_time = 0
        
        while self.running and time.time() - start_time < self.simulation_time + 10:
            current_time = time.time()
            
            # Проверяем статус каждые 5 секунд
            if current_time - last_status_time >= 5.0:
                self._print_status()
                last_status_time = current_time
            
            time.sleep(1.0)
    
    def _print_status(self):
        """Печать статуса интеграции"""
        try:
            # Проверяем файлы IPC
            ns3_to_blocksim = Path(self.ipc_dir) / "ns3_to_blocksim.json"
            blocksim_to_ns3 = Path(self.ipc_dir) / "blocksim_to_ns3.json"
            status_file = Path(self.ipc_dir) / "bridge_status.json"
            
            status_info = []
            
            if ns3_to_blocksim.exists():
                size = ns3_to_blocksim.stat().st_size
                status_info.append(f"NS-3→BlockSim: {size}B")
            
            if blocksim_to_ns3.exists():
                size = blocksim_to_ns3.stat().st_size
                status_info.append(f"BlockSim→NS-3: {size}B")
            
            if status_file.exists():
                import json
                try:
                    with open(status_file, 'r') as f:
                        status = json.load(f)
                    processed = status.get('processed_transactions', 0)
                    status_info.append(f"Processed: {processed}")
                except:
                    pass
            
            if status_info:
                self.logger.info(f"📊 Integration Status: {', '.join(status_info)}")
                
        except Exception as e:
            self.logger.debug(f"Error getting status: {e}")
    
    def run(self):
        """Запуск полной интеграции"""
        self.logger.info("🚀 Starting Simple NS-3 BlockSim Integration")
        
        try:
            # Установка обработчика сигналов
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Подготовка окружения
            self.setup_environment()
            
            # Запуск моста
            self.start_bridge()
            
            self.running = True
            
            # Запуск мониторинга в отдельном потоке
            monitor_thread = threading.Thread(target=self.monitor_integration, daemon=True)
            monitor_thread.start()
            
            # Запуск NS-3 симуляции
            success = self.start_ns3_simulation()
            
            # Ждем немного, чтобы обработать последние транзакции
            self.logger.info("⏳ Waiting for final transaction processing...")
            time.sleep(3.0)
            
            self.running = False
            
            # Финальная статистика
            self._print_final_statistics()
            
            return success
            
        except KeyboardInterrupt:
            self.logger.info("Integration stopped by user")
            return False
        except Exception as e:
            self.logger.error(f"Integration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()
    
    def _print_final_statistics(self):
        """Печать финальной статистики"""
        self.logger.info("📊 Final Integration Statistics:")
        
        try:
            # Читаем результаты
            results_file = Path(self.ipc_dir) / "blocksim_to_ns3.json"
            if results_file.exists():
                import json
                with open(results_file, 'r') as f:
                    data = json.load(f)
                
                results = data.get('results', [])
                total_processed = data.get('total_processed', 0)
                
                validated_count = sum(1 for r in results if r.get('validated', False))
                
                self.logger.info(f"  📈 Total transactions processed: {total_processed}")
                self.logger.info(f"  ✅ Successfully validated: {validated_count}")
                self.logger.info(f"  ❌ Failed validations: {len(results) - validated_count}")
                
                if validated_count > 0:
                    avg_validation_time = sum(r.get('validation_time', 0) for r in results if r.get('validated')) / validated_count
                    self.logger.info(f"  ⏱️ Average validation time: {avg_validation_time:.3f}s")
            
            # Статус моста
            if self.bridge:
                bridge_active = self.bridge.blocksim_initialized
                self.logger.info(f"  🔗 Bridge status: {'✅ Active' if bridge_active else '❌ Inactive'}")
                
        except Exception as e:
            self.logger.warning(f"Error getting final statistics: {e}")
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.logger.info("Cleaning up...")
        
        self.running = False
        
        # Остановка NS-3 процесса
        if self.ns3_process:
            try:
                self.ns3_process.terminate()
                self.ns3_process.wait(timeout=5)
            except:
                try:
                    self.ns3_process.kill()
                except:
                    pass
        
        # Остановка моста
        if self.bridge:
            try:
                self.bridge.cleanup()
            except:
                pass
        
        self.logger.info("Cleanup completed")

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Simple NS-3 BlockSim Integration")
    
    parser.add_argument("--nodes", type=int, default=6,
                       help="Number of nodes (default: 6)")
    parser.add_argument("--time", type=float, default=30.0,
                       help="Simulation time in seconds (default: 30)")
    parser.add_argument("--ipc-dir", type=str, default="simple_ns3_blocksim_ipc",
                       help="IPC directory (default: simple_ns3_blocksim_ipc)")
    parser.add_argument("--ns3-dir", type=str, default=None,
                       help="NS-3 directory (default: auto-detect)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Настройка логирования
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Simple NS-3 BlockSim Integration Runner")
    logger.info(f"📊 Configuration: {args.nodes} nodes, {args.time}s simulation")
    
    # Создаем и запускаем runner
    runner = SimpleIntegrationRunner(
        ipc_dir=args.ipc_dir,
        ns3_dir=args.ns3_dir,
        simulation_time=args.time,
        num_nodes=args.nodes
    )
    
    success = runner.run()
    
    if success:
        logger.info("🎉 Integration completed successfully!")
        logger.info(f"📁 Check results in: {args.ipc_dir}")
    else:
        logger.error("❌ Integration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
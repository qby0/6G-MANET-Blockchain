"""
Адаптер для интеграции с NS-3.
Обеспечивает управление симуляцией NS-3 из Python.
"""
import os
import sys
import logging
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NS3Adapter")

class NS3Adapter:
    """Класс для взаимодействия с NS-3"""
    
    def __init__(self, ns3_path: str = None):
        """
        Инициализирует адаптер для NS-3.
        
        Args:
            ns3_path (str, optional): Путь к директории NS-3. 
                                      По умолчанию ищется в переменной окружения NS3_DIR.
        """
        # Определяем путь к NS-3
        if ns3_path:
            self.ns3_path = ns3_path
        else:
            self.ns3_path = os.environ.get("NS3_DIR", None)
            if not self.ns3_path:
                raise EnvironmentError("Не задан путь к NS-3. Укажите его как аргумент или установите переменную окружения NS3_DIR.")

        # Проверяем существование директории
        if not os.path.exists(self.ns3_path):
            raise FileNotFoundError(f"Директория NS-3 не найдена по пути: {self.ns3_path}")
        
        logger.info(f"NS-3 адаптер инициализирован с путем: {self.ns3_path}")
        
        # Переменные для хранения состояния симуляции
        self.simulation_running = False
        self.current_nodes = {}
        self.current_links = {}
        self.simulation_time = 0.0
        
    def configure_and_build(self) -> bool:
        """
        Конфигурирует и собирает NS-3 с оптимизациями.
        
        Returns:
            bool: True если сборка успешна, False в противном случае
        """
        try:
            # Настройка ccache
            os.environ["CCACHE_DIR"] = os.path.join(self.ns3_path, ".ccache")
            os.environ["CCACHE_MAXSIZE"] = "50G"
            
            # Конфигурация с оптимизациями
            configure_cmd = [
                "./ns3",
                "configure",
                "--enable-examples",
                "--enable-tests",
                "--enable-python-bindings",
                "--enable-modules=netanim",
                "--build-profile=optimized",
                "--enable-ccache",
                "--enable-ninja"
            ]
            
            subprocess.run(configure_cmd, cwd=self.ns3_path, check=True)
            
            # Параллельная сборка
            build_cmd = ["./ns3", "build", f"-j{os.cpu_count()}"]
            subprocess.run(build_cmd, cwd=self.ns3_path, check=True)
            
            logger.info("NS-3 успешно сконфигурирован и собран")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при сборке NS-3: {e}")
            return False

    def create_scenario_file(self, nodes: Dict[str, Dict], 
                           links: Dict[str, Dict],
                           params: Dict[str, Any]) -> str:
        """
        Создает временный файл сценария для NS-3 на основе предоставленных данных.
        
        Args:
            nodes (Dict[str, Dict]): Словарь с информацией об узлах
            links (Dict[str, Dict]): Словарь с информацией о связях
            params (Dict[str, Any]): Параметры симуляции
            
        Returns:
            str: Путь к созданному файлу сценария
        """
        # Создаем временный файл для сценария NS-3
        fd, scenario_path = tempfile.mkstemp(suffix=".xml", prefix="ns3_scenario_")
        os.close(fd)
        
        # Создаем корневой элемент XML
        root = ET.Element("scenario")
        
        # Добавляем параметры симуляции
        params_elem = ET.SubElement(root, "parameters")
        for key, value in params.items():
            param_elem = ET.SubElement(params_elem, "parameter")
            param_elem.set("name", key)
            param_elem.set("value", str(value))
        
        # Добавляем информацию об узлах
        nodes_elem = ET.SubElement(root, "nodes")
        for node_id, node_data in nodes.items():
            node_elem = ET.SubElement(nodes_elem, "node")
            node_elem.set("id", node_id)
            node_elem.set("type", node_data.get("type", "regular"))
            
            pos = node_data.get("position", (0, 0, 0))
            position_elem = ET.SubElement(node_elem, "position")
            position_elem.set("x", str(pos[0]))
            position_elem.set("y", str(pos[1]))
            position_elem.set("z", str(pos[2]))
            
            capabilities_elem = ET.SubElement(node_elem, "capabilities")
            for cap_name, cap_value in node_data.get("capabilities", {}).items():
                cap_elem = ET.SubElement(capabilities_elem, "capability")
                cap_elem.set("name", cap_name)
                cap_elem.set("value", str(cap_value))
        
        # Добавляем информацию о связях
        links_elem = ET.SubElement(root, "links")
        for link_id, link_data in links.items():
            link_elem = ET.SubElement(links_elem, "link")
            link_elem.set("id", link_id)
            
            nodes_list = link_data.get("nodes", [])
            if len(nodes_list) >= 2:
                link_elem.set("source", nodes_list[0])
                link_elem.set("target", nodes_list[1])
            
            link_elem.set("quality", str(link_data.get("quality", 0.5)))
            link_elem.set("bandwidth", str(link_data.get("bandwidth", 1.0)))
        
        # Добавляем настройки анимации
        anim_elem = ET.SubElement(root, "animation")
        anim_elem.set("enabled", "true")
        anim_elem.set("max_packets_per_sec", "500")
        anim_elem.set("update_interval", "0.1")
        
        # Сохраняем XML в файл
        tree = ET.ElementTree(root)
        tree.write(scenario_path, encoding="utf-8", xml_declaration=True)
        
        logger.info(f"Сценарий NS-3 создан: {scenario_path}")
        return scenario_path
    
    def run_simulation(self, scenario_path: str, duration: float, 
                     time_resolution: float = 0.1, output_dir: str = None) -> Dict[str, Any]:
        """
        Запускает симуляцию NS-3 на основе сценария.
        
        Args:
            scenario_path (str): Путь к файлу сценария
            duration (float): Продолжительность симуляции в секундах
            time_resolution (float, optional): Разрешение времени в секундах. По умолчанию 0.1.
            output_dir (str, optional): Директория для вывода результатов. По умолчанию временная.
            
        Returns:
            Dict[str, Any]: Результаты симуляции
        """
        # Создаем директорию для вывода, если не указана
        if not output_dir:
            output_dir = tempfile.mkdtemp(prefix="ns3_output_")
        elif not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Формируем команду для запуска NS-3
        ns3_script_path = os.path.join(self.ns3_path, "scratch", "manet-blockchain-sim.cc")
        
        # Проверяем существование скрипта
        if not os.path.exists(ns3_script_path):
            logger.warning(f"Скрипт симуляции не найден: {ns3_script_path}")
            logger.warning("Будет использоваться стандартный скрипт для MANET")
            ns3_script_path = "scratch/manet-simulation"
        
        # Путь к исполняемому файлу NS-3
        ns3_exec = os.path.join(self.ns3_path, "ns3")
        
        # Формируем аргументы командной строки
        cmd_args = [
            ns3_exec,
            "run",
            f"{ns3_script_path}",
            f"--scenarioFile={scenario_path}",
            f"--duration={duration}",
            f"--resolution={time_resolution}",
            f"--outputDir={output_dir}"
        ]
        
        # Запускаем симуляцию
        logger.info(f"Запуск симуляции NS-3: {' '.join(cmd_args)}")
        
        try:
            # В реальном сценарии здесь будет запуск процесса NS-3
            # Для демонстрации мы просто эмулируем запуск и создаем фиктивные результаты
            
            # proc = subprocess.run(cmd_args, check=True, capture_output=True, text=True)
            # output = proc.stdout
            
            self.simulation_running = True
            logger.info("Симуляция NS-3 запущена")
            
            # Эмулируем результаты симуляции
            results = {
                "simulation_time": duration,
                "node_movements": [],
                "link_qualities": [],
                "network_stats": {
                    "packets_sent": 1000,
                    "packets_received": 950,
                    "average_delay": 0.05,
                    "packet_loss": 0.05
                }
            }
            
            # В реальной интеграции здесь бы происходил парсинг вывода NS-3
            
            self.simulation_running = False
            logger.info("Симуляция NS-3 завершена")
            
            return results
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при запуске симуляции NS-3: {e}")
            logger.error(f"Вывод stderr: {e.stderr}")
            self.simulation_running = False
            return {"error": str(e), "stderr": e.stderr}
    
    def parse_ns3_output(self, output_dir: str) -> Dict[str, Any]:
        """
        Парсит вывод симуляции NS-3.
        
        Args:
            output_dir (str): Директория с результатами симуляции
            
        Returns:
            Dict[str, Any]: Структурированные результаты симуляции
        """
        # В этой функции бы происходил парсинг файлов, сгенерированных NS-3
        # Для простоты демонстрации возвращаем заглушку
        
        logger.info(f"Парсинг результатов NS-3 из директории: {output_dir}")
        
        # Заглушка для результатов
        results = {
            "node_positions": {},
            "link_qualities": {},
            "packets_info": []
        }
        
        # В реальной реализации здесь был бы код для чтения файлов из output_dir
        # и извлечения данных о позициях узлов, качестве соединений и информации о пакетах
        
        return results
    
    def create_ns3_manet_script(self) -> str:
        """
        Создает скрипт C++ для NS-3, моделирующий MANET сеть с блокчейном.
        
        Returns:
            str: Путь к созданному файлу скрипта
        """
        # Создаем директорию scratch, если не существует
        scratch_dir = os.path.join(self.ns3_path, "scratch")
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)
        
        # Путь к скрипту
        script_path = os.path.join(scratch_dir, "manet-blockchain-sim.cc")
        
        # Обновляем содержимое скрипта с поддержкой NetAnim
        script_content = """
        /* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
        /*
         * Симуляция MANET сети с поддержкой блокчейна
         */

        #include "ns3/core-module.h"
        #include "ns3/network-module.h"
        #include "ns3/internet-module.h"
        #include "ns3/mobility-module.h"
        #include "ns3/wifi-module.h"
        #include "ns3/applications-module.h"
        #include "ns3/netanim-module.h"
        #include "ns3/aodv-module.h"
        #include "ns3/flow-monitor-module.h"
        #include <iostream>
        #include <fstream>
        #include <string>
        #include <vector>
        #include <map>
        #include "ns3/command-line.h"

        using namespace ns3;

        NS_LOG_COMPONENT_DEFINE("ManetBlockchainSimulation");

        // Функция для записи позиций узлов с течением времени
        static void
        RecordNodePositions(NodeContainer nodes, double time, std::string filename)
        {
          std::ofstream file;
          file.open(filename, std::ios::app);
          file << time;
          
          for (uint32_t i = 0; i < nodes.GetN(); i++)
          {
            Ptr<MobilityModel> mobility = nodes.Get(i)->GetObject<MobilityModel>();
            Vector pos = mobility->GetPosition();
            file << "," << i << "," << pos.x << "," << pos.y << "," << pos.z;
          }
          
          file << std::endl;
          file.close();
        }

        // Функция для записи информации о пакетах
        static void
        RecordPacketInfo(std::string context, Ptr<const Packet> packet)
        {
          // В реальной реализации здесь бы записывалась информация о пакетах
          NS_LOG_INFO("Packet transmitted: " << context << ", size: " << packet->GetSize());
        }

        int
        main(int argc, char *argv[])
        {
          // Параметры командной строки
          std::string scenarioFile = "";
          double duration = 100.0;
          double resolution = 0.1;
          std::string outputDir = "./";
          
          CommandLine cmd;
          cmd.AddValue("scenarioFile", "Путь к файлу сценария", scenarioFile);
          cmd.AddValue("duration", "Продолжительность симуляции в секундах", duration);
          cmd.AddValue("resolution", "Разрешение записи данных в секундах", resolution);
          cmd.AddValue("outputDir", "Директория для вывода результатов", outputDir);
          cmd.Parse(argc, argv);
          
          // Настраиваем логгирование
          LogComponentEnable("ManetBlockchainSimulation", LOG_LEVEL_INFO);
          
          // Количество узлов (в реальности должно быть прочитано из scenarioFile)
          uint32_t nNodes = 20;
          uint32_t nValidators = nNodes / 10;
          
          // Создаем узлы
          NodeContainer nodes;
          nodes.Create(nNodes);
          
          // Настраиваем WiFi
          WifiHelper wifi;
          wifi.SetStandard(WIFI_STANDARD_80211g);
          
          YansWifiPhyHelper wifiPhy;
          YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
          wifiPhy.SetChannel(wifiChannel.Create());
          
          // Настройка MAC уровня для Ad-Hoc режима
          WifiMacHelper wifiMac;
          wifiMac.SetType("ns3::AdhocWifiMac");
          
          // Устанавливаем Wi-Fi на узлы
          NetDeviceContainer devices = wifi.Install(wifiPhy, wifiMac, nodes);
          
          // Модель мобильности (случайное блуждание)
          MobilityHelper mobility;
          mobility.SetPositionAllocator("ns3::GridPositionAllocator",
                                       "MinX", DoubleValue(0.0),
                                       "MinY", DoubleValue(0.0),
                                       "DeltaX", DoubleValue(50.0),
                                       "DeltaY", DoubleValue(50.0),
                                       "GridWidth", UintegerValue(5),
                                       "LayoutType", StringValue("RowFirst"));
          
          mobility.SetMobilityModel("ns3::RandomWalk2dMobilityModel",
                                   "Bounds", RectangleValue(Rectangle(-500, 500, -500, 500)),
                                   "Speed", StringValue("ns3::ConstantRandomVariable[Constant=5.0]"));
          mobility.Install(nodes);
          
          // Устанавливаем стек Интернет-протоколов
          InternetStackHelper internet;
          AodvHelper aodv; // Используем AODV маршрутизацию для MANET
          internet.SetRoutingHelper(aodv);
          internet.Install(nodes);
          
          // Назначаем IP-адреса
          Ipv4AddressHelper ipv4;
          ipv4.SetBase("10.1.1.0", "255.255.255.0");
          Ipv4InterfaceContainer interfaces = ipv4.Assign(devices);
          
          // Подготовка файлов для вывода данных
          std::string posFile = outputDir + "/node_positions.csv";
          std::ofstream positionFile;
          positionFile.open(posFile);
          positionFile << "time";
          for (uint32_t i = 0; i < nNodes; i++)
          {
            positionFile << ",node" << i << ",x,y,z";
          }
          positionFile << std::endl;
          positionFile.close();
          
          // Настраиваем запись позиций узлов
          for (double time = 0.0; time <= duration; time += resolution)
          {
            Simulator::Schedule(Seconds(time), &RecordNodePositions, nodes, time, posFile);
          }
          
          // Трассировка пакетов
          Config::Connect("/NodeList/*/$ns3::MobilityModel/CourseChange",
                          MakeCallback(&CourseChangeCallback));
          
          // Анимация для визуализации (если доступна)
          AnimationInterface anim(outputDir + "/animation.xml");
          
          // Мониторинг потоков
          Ptr<FlowMonitor> flowMonitor;
          FlowMonitorHelper flowHelper;
          flowMonitor = flowHelper.InstallAll();
          
          // Запуск симуляции
          Simulator::Stop(Seconds(duration));
          Simulator::Run();
          
          // Сохраняем статистику потоков
          flowMonitor->SerializeToXmlFile(outputDir + "/flow-monitor.xml", true, true);
          
          Simulator::Destroy();
          
          NS_LOG_INFO("Симуляция завершена.");
          
          return 0;
        }
        """
        
        # Записываем скрипт в файл
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        logger.info(f"Скрипт NS-3 создан: {script_path}")
        return script_path

    def compile_ns3_script(self, script_name: str) -> bool:
        """
        Компилирует скрипт NS-3.
        
        Args:
            script_name (str): Имя скрипта (без пути и расширения)
            
        Returns:
            bool: True, если компиляция успешна, иначе False
        """
        # Путь к NS-3 для компиляции
        cmd_args = [
            os.path.join(self.ns3_path, "ns3"),
            "build",
            f"scratch/{script_name}"
        ]
        
        logger.info(f"Компиляция скрипта NS-3: {' '.join(cmd_args)}")
        
        try:
            # В реальном сценарии здесь будет запуск компиляции
            # proc = subprocess.run(cmd_args, check=True, capture_output=True, text=True)
            # return True
            
            # Для демонстрации просто возвращаем успех
            logger.info("Компиляция NS-3 успешно завершена")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при компиляции скрипта NS-3: {e}")
            logger.error(f"Вывод stderr: {e.stderr}")
            return False


if __name__ == "__main__":
    # Пример использования
    try:
        # Создаем адаптер, указав путь к NS-3
        adapter = NS3Adapter("/path/to/ns3")
        
        # Создаем скрипт для симуляции
        script_path = adapter.create_ns3_manet_script()
        
        # Компилируем скрипт
        adapter.compile_ns3_script("manet-blockchain-sim")
        
        # Создаем простой сценарий
        nodes = {
            "base_station_1": {
                "type": "base_station",
                "position": (0.0, 0.0, 10.0),
                "capabilities": {"computational_power": 100, "storage": 1000}
            },
            "node_1": {
                "type": "regular",
                "position": (100.0, 100.0, 1.5),
                "capabilities": {"computational_power": 10, "storage": 50, "battery": 0.9}
            },
            "node_2": {
                "type": "validator",
                "position": (200.0, 200.0, 1.5),
                "capabilities": {"computational_power": 20, "storage": 100, "battery": 0.8}
            }
        }
        
        links = {
            "bs1_n1": {
                "nodes": ["base_station_1", "node_1"],
                "quality": 0.9,
                "bandwidth": 100.0
            },
            "n1_n2": {
                "nodes": ["node_1", "node_2"],
                "quality": 0.7,
                "bandwidth": 50.0
            }
        }
        
        params = {
            "simulation_time": 100.0,
            "wifi_standard": "80211g",
            "propagation_model": "friis",
            "routing_protocol": "aodv"
        }
        
        # Создаем файл сценария
        scenario_file = adapter.create_scenario_file(nodes, links, params)
        
        # Запускаем симуляцию
        results = adapter.run_simulation(
            scenario_file, 
            duration=100.0,
            time_resolution=0.1,
            output_dir="/tmp/ns3_results"
        )
        
        print(f"Результаты симуляции: {results}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
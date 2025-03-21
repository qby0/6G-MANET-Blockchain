#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Интерфейс для интеграции между NS-3 и BlockSim.
Обеспечивает передачу данных и синхронизацию между симуляторами.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("IntegrationInterface")


class IntegrationInterface:
    """Класс для интеграции NS-3 и BlockSim"""

    def __init__(self, config_path: Optional[Any] = None):
        """
        Инициализирует интерфейс интеграции.

        Args:
            config_path (str, optional): Путь к файлу конфигурации. По умолчанию None.
        """
        self.nodes: Dict[str, Any] = {}  # Словарь для хранения информации об узлах
        self.links: Dict[
            str, Any
        ] = {}  # Словарь для хранения информации о связях между узлами
        self.transactions: List[Any] = []  # Список транзакций
        self.simulation_time = 0.0  # Текущее время симуляции
        self.config: Dict[str, Any] = {}  # Конфигурация симуляции

        # Загружаем конфигурацию, если указана
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
                logger.info(
                    "Конфигурация загружена из %(config_path)s",
                    {config_path: config_path},
                )

    def register_node(
        self,
        node_id: str,
        position: Tuple[float, float, float],
        node_type: str,
        capabilities: Dict[str, Any],
    ) -> bool:
        """
        Регистрирует новый узел в системе.

        Args:
            node_id (str): Уникальный идентификатор узла
            position (Tuple[float, float, float]): Координаты узла (x, y, z)
            node_type (str): Тип узла (base_station, validator, regular)
            capabilities (Dict[str, Any]): Параметры возможностей узла

        Returns:
            bool: True, если узел успешно зарегистрирован, иначе False
        """
        if node_id in self.nodes:
            logger.warning("Узел %(node_id)s уже зарегистрирован", {node_id: node_id})
            return False

        self.nodes[node_id] = {
            "position": position,
            "type": node_type,
            "capabilities": capabilities,
            "connections": [],
            "active": True,
            "trust_rating": 0.5 if node_type != "base_station" else 1.0,
            "registered_time": self.simulation_time,
        }

        logger.info("Узел %(node_id)s успешно зарегистрирован", {node_id: node_id})
        return True

    def update_node_position(
        self, node_id: str, position: Tuple[float, float, float]
    ) -> bool:
        """
        Обновляет позицию узла.

        Args:
            node_id (str): Идентификатор узла
            position (Tuple[float, float, float]): Новые координаты (x, y, z)

        Returns:
            bool: True, если позиция успешно обновлена, иначе False
        """
        if node_id not in self.nodes:
            logger.error("Узел %(node_id)s не найден", {node_id: node_id})
            return False

        old_position = self.nodes[node_id]["position"]
        self.nodes[node_id]["position"] = position

        logger.debug(
            "Узел %(node_id)s переместился из %(old_position)s в %(position)s",
            {node_id: node_id, old_position: old_position, position: position},
        )
        return True

    def register_connection(
        self, node1_id: str, node2_id: str, quality: float, bandwidth: float
    ) -> bool:
        """
        Регистрирует соединение между двумя узлами.

        Args:
            node1_id (str): Идентификатор первого узла
            node2_id (str): Идентификатор второго узла
            quality (float): Качество соединения (0.0-1.0)
            bandwidth (float): Пропускная способность (Mbps)

        Returns:
            bool: True, если соединение успешно зарегистрировано, иначе False
        """
        if node1_id not in self.nodes or node2_id not in self.nodes:
            logger.error(
                "Один или оба узла не найдены: %(node1_id)s, %(node2_id)s",
                {node1_id: node1_id, node2_id: node2_id},
            )
            return False

        connection_id = f"{min(node1_id, node2_id)}_{max(node1_id, node2_id)}"

        if connection_id in self.links:
            # Обновляем существующее соединение
            self.links[connection_id]["quality"] = quality
            self.links[connection_id]["bandwidth"] = bandwidth
            logger.debug(
                "Соединение %(connection_id)s обновлено", {connection_id: connection_id}
            )
        else:
            # Создаем новое соединение
            self.links[connection_id] = {
                "nodes": [node1_id, node2_id],
                "quality": quality,
                "bandwidth": bandwidth,
                "established_time": self.simulation_time,
                "active": True,
            }

            # Обновляем список соединений для обоих узлов
            self.nodes[node1_id]["connections"].append(node2_id)
            self.nodes[node2_id]["connections"].append(node1_id)

            logger.info(
                "Соединение между узлами %(node1_id)s и %(node2_id)s установлено",
                {node1_id: node1_id, node2_id: node2_id},
            )

        return True

    def send_transaction(
        self, source_id: str, target_id: str, transaction_data: Dict[str, Any]
    ) -> str:
        """
        Отправляет транзакцию от одного узла к другому.

        Args:
            source_id (str): Идентификатор узла-отправителя
            target_id (str): Идентификатор узла-получателя
            transaction_data (Dict[str, Any]): Данные транзакции

        Returns:
            str: Идентификатор транзакции или пустая строка в случае ошибки
        """
        if source_id not in self.nodes:
            logger.error(
                "Узел-отправитель %(source_id)s не найден", {source_id: source_id}
            )
            return ""

        if target_id not in self.nodes:
            logger.error(
                "Узел-получатель %(target_id)s не найден", {target_id: target_id}
            )
            return ""

        # Проверяем, есть ли прямое соединение или путь между узлами
        if not self._check_path_exists(source_id, target_id):
            logger.error(
                "Нет доступного пути между узлами %(source_id)s и %(target_id)s",
                {source_id: source_id, target_id: target_id},
            )
            return ""

        # Генерируем уникальный идентификатор транзакции
        import uuid

        tx_id = f"tx_{uuid.uuid4().hex[:8]}"

        # Создаем транзакцию
        transaction = {
            "id": tx_id,
            "source": source_id,
            "target": target_id,
            "data": transaction_data,
            "timestamp": self.simulation_time,
            "status": "pending",
            "path": self._find_shortest_path(source_id, target_id),
        }

        self.transactions.append(transaction)
        logger.info("Транзакция %(tx_id)s создана и отправлена", {tx_id: tx_id})

        return tx_id

    def process_pending_transactions(self) -> int:
        """
        Обрабатывает ожидающие транзакции.

        Returns:
            int: Количество обработанных транзакций
        """
        count = 0
        for tx in self.transactions:
            if tx["status"] == "pending":
                # Симулируем прохождение транзакции через сеть
                # В реальной интеграции здесь будет связь с BlockSim
                tx["status"] = "processed"
                count += 1

        logger.info("Обработано %(count)s транзакций", {count: count})
        return count

    def advance_time(self, time_delta: float) -> None:
        """
        Продвигает время симуляции вперед.

        Args:
            time_delta (float): Величина времени для продвижения (в секундах)
        """
        self.simulation_time += time_delta
        logger.debug(
            "Время симуляции продвинуто до %(self.simulation_time)s",
            {self.simulation_time: self.simulation_time},
        )

    def get_network_state(self) -> Dict[str, Any]:
        """
        Возвращает текущее состояние сети.

        Returns:
            Dict[str, Any]: Словарь с состоянием сети
        """
        return {
            "simulation_time": self.simulation_time,
            "nodes": self.nodes,
            "links": self.links,
            "transactions": self.transactions,
        }

    def save_state(self, filepath: str) -> bool:
        """
        Сохраняет текущее состояние интерфейса в файл JSON.

        Args:
            filepath (str): Путь для сохранения состояния

        Returns:
            bool: True, если состояние успешно сохранено, иначе False
        """
        try:
            # Проверяем, существует ли директория, и создаем её, если нет
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(
                        "Создана директория %(directory)s", {directory: directory}
                    )
                except PermissionError:
                    logger.error(
                        f"Ошибка прав доступа: невозможно создать директорию {directory}"
                    )
                    logger.error(
                        "Пожалуйста, проверьте права доступа к файловой системе"
                    )
                    return False
                except Exception as e:
                    logger.error(
                        "Ошибка при создании директории %(directory)s: %(e)s",
                        {directory: directory, e: e},
                    )
                    return False

            # Проверяем права на запись, если файл уже существует
            if os.path.exists(filepath):
                if not os.access(filepath, os.W_OK):
                    logger.error(
                        f"Ошибка прав доступа: отсутствуют права на запись файла {filepath}"
                    )
                    logger.error("Пожалуйста, проверьте права доступа к файлу")
                    return False

            # Пытаемся открыть файл и записать данные
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.get_network_state(), f, indent=2)
            logger.info(
                "Состояние симуляции сохранено в %(filepath)s", {filepath: filepath}
            )
            return True
        except PermissionError:
            logger.error(
                "Ошибка прав доступа: невозможно записать в файл %(filepath)s",
                {filepath: filepath},
            )
            logger.error("Пожалуйста, проверьте права доступа к файлу и директории")
            return False
        except Exception as e:
            logger.error("Ошибка при сохранении состояния: %(e)s", {e: e})
            return False

    def load_state(self, filepath: str) -> bool:
        """
        Загружает состояние интерфейса из файла JSON.

        Args:
            filepath (str): Путь к файлу состояния

        Returns:
            bool: True, если состояние успешно загружено, иначе False
        """
        try:
            # Проверяем существование файла
            if not os.path.exists(filepath):
                logger.error(
                    "Файл состояния %(filepath)s не существует", {filepath: filepath}
                )
                return False

            # Проверяем права на чтение
            if not os.access(filepath, os.R_OK):
                logger.error(
                    f"Ошибка прав доступа: отсутствуют права на чтение файла {filepath}"
                )
                logger.error("Пожалуйста, проверьте права доступа к файлу")
                return False

            # Пытаемся открыть файл и прочитать данные
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)

            # Загружаем состояние
            self.nodes = state.get("nodes", {})
            self.links = state.get("links", {})
            self.transactions = state.get("transactions", [])
            self.simulation_time = state.get("time", 0.0)

            logger.info(
                "Состояние симуляции загружено из %(filepath)s", {filepath: filepath}
            )
            return True
        except PermissionError:
            logger.error(
                "Ошибка прав доступа: невозможно прочитать файл %(filepath)s",
                {filepath: filepath},
            )
            logger.error("Пожалуйста, проверьте права доступа к файлу")
            return False
        except json.JSONDecodeError:
            logger.error(
                "Ошибка декодирования JSON в файле %(filepath)s", {filepath: filepath}
            )
            return False
        except Exception as e:
            logger.error("Ошибка при загрузке состояния: %(e)s", {e: e})
            return False

    def _check_path_exists(self, source_id: str, target_id: str) -> bool:
        """
        Проверяет наличие пути между двумя узлами.

        Args:
            source_id (str): Идентификатор узла-отправителя
            target_id (str): Идентификатор узла-получателя

        Returns:
            bool: True, если путь существует, иначе False
        """
        # В простейшем случае используем поиск в ширину
        visited = set()
        queue = [source_id]

        while queue:
            node_id = queue.pop(0)

            if node_id == target_id:
                return True

            if node_id in visited:
                continue

            visited.add(node_id)

            if node_id in self.nodes:
                for connected_node in self.nodes[node_id].get("connections", []):
                    if connected_node not in visited:
                        queue.append(connected_node)

        return False

    def _find_shortest_path(self, source_id: str, target_id: str) -> List[str]:
        """
        Находит кратчайший путь между двумя узлами.

        Args:
            source_id (str): Идентификатор узла-отправителя
            target_id (str): Идентификатор узла-получателя

        Returns:
            List[str]: Список идентификаторов узлов, составляющих путь
        """
        # Реализуем простой алгоритм поиска в ширину
        visited = set()
        queue = [(source_id, [source_id])]

        while queue:
            node_id, path = queue.pop(0)

            if node_id == target_id:
                return path

            if node_id in visited:
                continue

            visited.add(node_id)

            if node_id in self.nodes:
                for connected_node in self.nodes[node_id].get("connections", []):
                    if connected_node not in visited:
                        new_path = path + [connected_node]
                        queue.append((connected_node, new_path))

        return []  # Путь не найден


if __name__ == "__main__":
    # Пример использования
    interface = IntegrationInterface()

    # Регистрируем базовую станцию
    interface.register_node(
        "base_station_1",
        (0.0, 0.0, 10.0),
        "base_station",
        {"computational_power": 100, "storage": 1000, "battery": None},
    )

    # Регистрируем два мобильных узла
    interface.register_node(
        "node_1",
        (10.0, 10.0, 1.5),
        "regular",
        {"computational_power": 10, "storage": 50, "battery": 0.9},
    )

    interface.register_node(
        "node_2",
        (20.0, 20.0, 1.5),
        "validator",
        {"computational_power": 20, "storage": 100, "battery": 0.8},
    )

    # Устанавливаем соединения
    interface.register_connection("base_station_1", "node_1", 0.9, 100.0)
    interface.register_connection("node_1", "node_2", 0.7, 50.0)

    # Отправляем транзакцию
    tx_id = interface.send_transaction(
        "node_1", "node_2", {"type": "data_transfer", "size": 1024, "priority": "high"}
    )

    # Продвигаем время и обрабатываем транзакции
    interface.advance_time(1.0)
    interface.process_pending_transactions()

    # Сохраняем состояние
    interface.save_state(os.path.join(tempfile.gettempdir(), "simulation_state.json"))

    print("Пример выполнен успешно.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Адаптер для интеграции с BlockSim.
Обеспечивает управление симуляцией блокчейна.
"""

import json
import logging
import os
import random
import secrets
import sys
from typing import Any, Dict, List, Optional, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("BlockSimAdapter")


class BlockSimAdapter:
    """Класс для взаимодействия с BlockSim"""

    def __init__(self, config_path: Optional[Any] = None):
        """
        Инициализирует адаптер для BlockSim.

        Args:
            config_path (str, optional): Путь к файлу конфигурации.
        """
        self.config: Dict[str, Any] = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
                logger.info(
                    "Конфигурация загружена из %s", config_path
                )

        # BlockSim должен быть установлен
        try:
            # В реальном использовании проверяем наличие BlockSim
            # from blocksim.models.blockchain import Blockchain
            # from blocksim.models.consensus import ProofOfAuthority
            logger.info("Проверка импорта модулей BlockSim выполнена")
        except ImportError as e:
            logger.warning("Не удалось импортировать модули BlockSim: %s", e)
            logger.warning("Будет использоваться эмуляция BlockSim")

        # Внутренние переменные для отслеживания состояния симуляции
        self.blockchain = None
        self.nodes: Dict[str, Any] = {}
        self.blocks: List[Any] = []
        self.transactions: List[Any] = []
        self.current_time = 0.0

    def initialize_blockchain(
        self, consensus_type: str, num_validators: int, block_interval: float
    ) -> bool:
        """
        Инициализирует блокчейн с указанными параметрами.

        Args:
            consensus_type (str): Тип консенсуса ('PoW', 'PoA', 'PBFT')
            num_validators (int): Количество узлов-валидаторов
            block_interval (float): Интервал создания блока в секундах

        Returns:
            bool: True, если инициализация успешна, иначе False
        """
        try:
            # В реальной интеграции здесь был бы код инициализации BlockSim
            # self.blockchain = Blockchain(consensus_type=consensus_type, ...)

            # Эмулируем создание блокчейна
            self.blockchain = {
                "consensus_type": consensus_type,
                "num_validators": num_validators,
                "block_interval": block_interval,
                "genesis_block": {
                    "index": 0,
                    "timestamp": self.current_time,
                    "transactions": [],
                    "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000",
                    "validator": "genesis",
                },
            }

            # Добавляем первый блок
            self.blocks.append(self.blockchain["genesis_block"])

            logger.info(
                f"Блокчейн инициализирован с консенсусом {consensus_type}, {num_validators} валидаторами"
            )
            return True

        except Exception as e:
            logger.error("Ошибка инициализации блокчейна: %s", e)
            return False

    def register_node(
        self, node_id: str, node_type: str, resources: Dict[str, Any]
    ) -> bool:
        """
        Регистрирует новый узел в блокчейне.

        Args:
            node_id (str): Идентификатор узла
            node_type (str): Тип узла ('validator', 'regular')
            resources (Dict[str, Any]): Ресурсы узла (вычислительная мощность и пр.)

        Returns:
            bool: True, если узел успешно зарегистрирован, иначе False
        """
        if node_id in self.nodes:
            logger.warning("Узел %s уже зарегистрирован", node_id)
            return False

        # Создаем запись узла
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "resources": resources,
            "registered_time": self.current_time,
            "transactions_processed": 0,
            "blocks_created": 0,
            "is_active": True,
        }

        logger.info(
            "Узел %s зарегистрирован как %s", node_id, node_type
        )
        return True

    def update_node_status(self, node_id: str, is_active: bool) -> bool:
        """
        Обновляет статус активности узла.

        Args:
            node_id (str): Идентификатор узла
            is_active (bool): Активен ли узел

        Returns:
            bool: True, если статус успешно обновлен, иначе False
        """
        if node_id not in self.nodes:
            logger.error("Узел %s не найден", node_id)
            return False

        self.nodes[node_id]["is_active"] = is_active

        status_text = "активен" if is_active else "неактивен"
        logger.info(
            "Статус узла %s обновлен: %s", node_id, status_text
        )
        return True

    def create_transaction(
        self,
        source_id: str,
        target_id: str,
        data: Dict[str, Any],
        tx_type: str = "data",
    ) -> str:
        """
        Создает новую транзакцию.

        Args:
            source_id (str): Идентификатор узла-отправителя
            target_id (str): Идентификатор узла-получателя
            data (Dict[str, Any]): Данные транзакции
            tx_type (str, optional): Тип транзакции. По умолчанию "data".

        Returns:
            str: Идентификатор транзакции или пустая строка в случае ошибки
        """
        if source_id not in self.nodes:
            logger.error(
                "Узел-отправитель %s не найден", source_id
            )
            return ""

        if target_id not in self.nodes:
            logger.error(
                "Узел-получатель %s не найден", target_id
            )
            return ""

        # Генерируем идентификатор транзакции
        import hashlib
        import time

        tx_id = hashlib.sha256(
            f"{source_id}{target_id}{str(data)}{time.time()}".encode()
        ).hexdigest()[:16]

        # Создаем транзакцию
        transaction = {
            "id": tx_id,
            "source": source_id,
            "target": target_id,
            "data": data,
            "type": tx_type,
            "timestamp": self.current_time,
            "status": "pending",
        }

        self.transactions.append(transaction)

        logger.info(
            "Транзакция %s создана между %s и %s", tx_id, source_id, target_id
        )
        return tx_id

    def process_pending_transactions(self) -> int:
        """
        Обрабатывает ожидающие транзакции.

        Returns:
            int: Количество обработанных транзакций
        """
        if not self.blockchain:
            logger.error("Блокчейн не инициализирован")
            return 0

        count = 0
        for tx in self.transactions:
            if tx["status"] == "pending":
                # Обрабатываем транзакцию
                tx["status"] = "confirmed"

                # Обновляем счетчик транзакций для узла
                if tx["source"] in self.nodes:
                    self.nodes[tx["source"]]["transactions_processed"] += 1

                count += 1

        logger.info("Обработано %s транзакций", count)
        return count

    def create_block(self) -> Dict[str, Any]:
        """
        Создает новый блок с ожидающими транзакциями.

        Returns:
            Dict[str, Any]: Информация о созданном блоке или пустой словарь в случае ошибки
        """
        if not self.blockchain:
            logger.error("Блокчейн не инициализирован")
            return {}

        # Получаем ожидающие транзакции
        pending_txs = [tx for tx in self.transactions if tx["status"] == "confirmed"]

        if not pending_txs:
            logger.warning("Нет транзакций для создания блока")
            return {}

        # Выбираем случайного активного валидатора
        validators = [
            node_id
            for node_id, node in self.nodes.items()
            if node["type"] == "validator" and node["is_active"]
        ]

        if not validators:
            logger.error("Нет активных валидаторов для создания блока")
            return {}

        validator = secrets.choice(validators)

        # Создаем блок
        block_index = len(self.blocks)
        previous_hash = self.blocks[-1]["previous_hash"] if self.blocks else "0" * 64

        import hashlib

        # Создаем хеш нового блока
        block_data = f"{block_index}{previous_hash}{str(pending_txs)}{validator}{self.current_time}"
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()

        block = {
            "index": block_index,
            "timestamp": self.current_time,
            "transactions": [tx["id"] for tx in pending_txs],
            "previous_hash": previous_hash,
            "hash": block_hash,
            "validator": validator,
            "size": len(pending_txs),
        }

        self.blocks.append(block)

        # Обновляем статус транзакций
        for tx in pending_txs:
            tx["status"] = "included"
            tx["block_index"] = block_index

        # Обновляем счетчик блоков для валидатора
        self.nodes[validator]["blocks_created"] += 1

        logger.info(
            f"Блок {block_index} создан валидатором {validator} с {len(pending_txs)} транзакциями"
        )
        return block

    def advance_time(self, time_delta: float) -> None:
        """
        Продвигает время симуляции вперед.

        Args:
            time_delta (float): Количество секунд для продвижения времени
        """
        old_time = self.current_time
        self.current_time += time_delta

        logger.debug(
            "Время симуляции продвинуто с %s до %s", old_time, self.current_time
        )

        # Проверяем, нужно ли создавать новые блоки
        if self.blockchain:
            # Интервал между блоками
            block_interval = self.blockchain.get("block_interval", 10.0)

            # Количество блоков, которые должны были быть созданы
            blocks_to_create = int((self.current_time - old_time) / block_interval)

            # Создаем блоки
            for _ in range(blocks_to_create):
                if self.process_pending_transactions() > 0:
                    self.create_block()

    def get_blockchain_state(self) -> Dict[str, Any]:
        """
        Возвращает текущее состояние блокчейна.

        Returns:
            Dict[str, Any]: Текущее состояние блокчейна
        """
        return {
            "current_time": self.current_time,
            "blockchain_config": self.blockchain if self.blockchain else {},
            "blocks_count": len(self.blocks),
            "transactions_count": len(self.transactions),
            "pending_transactions": len(
                [tx for tx in self.transactions if tx["status"] == "pending"]
            ),
            "confirmed_transactions": len(
                [
                    tx
                    for tx in self.transactions
                    if tx["status"] in ["confirmed", "included"]
                ]
            ),
            "nodes": {
                "total": len(self.nodes),
                "validators": len(
                    [n for n in self.nodes.values() if n["type"] == "validator"]
                ),
                "active": len([n for n in self.nodes.values() if n["is_active"]]),
            },
        }

    def get_detailed_state(self) -> Dict[str, Any]:
        """
        Возвращает детальное текущее состояние симуляции.

        Returns:
            Dict[str, Any]: Детальное состояние симуляции
        """
        return {
            "current_time": self.current_time,
            "blockchain": self.blockchain,
            "nodes": self.nodes,
            "blocks": self.blocks,
            "transactions": self.transactions,
        }

    def save_state(self, filepath: str) -> bool:
        """
        Сохраняет текущее состояние в файл JSON.

        Args:
            filepath (str): Путь для сохранения

        Returns:
            bool: True, если состояние успешно сохранено, иначе False
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.get_detailed_state(), f, indent=2)
            logger.info("Состояние сохранено в %s", filepath)
            return True
        except Exception as e:
            logger.error("Ошибка при сохранении состояния: %s", e)
            return False

    def load_state(self, filepath: str) -> bool:
        """
        Загружает состояние из файла JSON.

        Args:
            filepath (str): Путь к файлу состояния

        Returns:
            bool: True, если состояние успешно загружено, иначе False
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)

            self.current_time = state.get("current_time", 0.0)
            self.blockchain = state.get("blockchain", None)
            self.nodes = state.get("nodes", {})
            self.blocks = state.get("blocks", [])
            self.transactions = state.get("transactions", [])

            logger.info("Состояние загружено из %s", filepath)
            return True
        except Exception as e:
            logger.error("Ошибка при загрузке состояния: %s", e)
            return False


if __name__ == "__main__":
    # Пример использования
    adapter = BlockSimAdapter()

    # Инициализируем блокчейн
    adapter.initialize_blockchain("PoA", 3, 5.0)

    # Регистрируем узлы
    adapter.register_node("node1", "validator", {"computing_power": 10})
    adapter.register_node("node2", "validator", {"computing_power": 8})
    adapter.register_node("node3", "validator", {"computing_power": 12})
    adapter.register_node("node4", "regular", {"computing_power": 5})
    adapter.register_node("node5", "regular", {"computing_power": 4})

    # Создаем несколько транзакций
    adapter.create_transaction(
        "node4", "node5", {"data": "Hello, BlockSim!"}, "message"
    )
    adapter.create_transaction(
        "node5", "node4", {"data": "Response from BlockSim"}, "message"
    )

    # Продвигаем время симуляции
    adapter.advance_time(10.0)

    # Смотрим состояние блокчейна
    state = adapter.get_blockchain_state()
    print("Состояние блокчейна:", state)

    # Сохраняем состояние
    adapter.save_state(os.path.join(tempfile.gettempdir(), "blocksim_state.json"))

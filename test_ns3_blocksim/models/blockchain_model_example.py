#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Blockchain model for 6G-MANET network simulation.
Модель блокчейна для симуляции сети 6G-MANET.
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, List, Any, Optional

# Setup logging / Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BlockchainModel")

class Block:
    """
    Block in the blockchain.
    Блок в блокчейне.
    """
    
    def __init__(self, index: int, timestamp: float, transactions: List[Dict[str, Any]], 
               previous_hash: str, nonce: int = 0):
        """
        Initialize a new block.
        Инициализация нового блока.
        
        Args:
            index (int): Block index / Индекс блока
            timestamp (float): Block creation timestamp / Временная метка создания блока
            transactions (List[Dict[str, Any]]): List of transactions / Список транзакций
            previous_hash (str): Hash of previous block / Хеш предыдущего блока
            nonce (int, optional): Nonce for PoW. Defaults to 0. / Nonce для PoW. По умолчанию 0.
        """
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Calculate the hash of this block.
        Вычисление хеша этого блока.
        
        Returns:
            str: Block hash / Хеш блока
        """
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """
        Mine the block (find a hash with the required number of leading zeros).
        Майнинг блока (поиск хеша с требуемым количеством начальных нулей).
        
        Args:
            difficulty (int): The number of leading zeros required / Требуемое количество начальных нулей
        """
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
            
        logger.info(f"Block #{self.index} mined: {self.hash}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert block to dictionary.
        Преобразование блока в словарь.
        
        Returns:
            Dict[str, Any]: Block as dictionary / Блок в виде словаря
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }

class Blockchain:
    """
    Blockchain implementation for 6G-MANET network.
    Реализация блокчейна для сети 6G-MANET.
    """
    
    def __init__(self, difficulty: int = 4):
        """
        Initialize the blockchain with the genesis block.
        Инициализация блокчейна с генезис-блоком.
        
        Args:
            difficulty (int, optional): Mining difficulty. Defaults to 4. 
                                       / Сложность майнинга. По умолчанию 4.
        """
        self.difficulty = difficulty
        self.pending_transactions = []
        self.chain = [self.create_genesis_block()]
        self.nodes = {}  # node_id -> node_info
        
        logger.info("Blockchain initialized with genesis block")
    
    def create_genesis_block(self) -> Block:
        """
        Create the first block in the chain (genesis block).
        Создание первого блока в цепи (генезис-блок).
        
        Returns:
            Block: Genesis block / Генезис-блок
        """
        return Block(0, time.time(), [], "0")
    
    def get_latest_block(self) -> Block:
        """
        Get the most recent block in the chain.
        Получение самого последнего блока в цепи.
        
        Returns:
            Block: The latest block / Последний блок
        """
        return self.chain[-1]
    
    def add_transaction(self, sender: str, recipient: str, data: Dict[str, Any]) -> int:
        """
        Add a new transaction to pending transactions.
        Добавление новой транзакции в список ожидающих транзакций.
        
        Args:
            sender (str): Sender's ID / ID отправителя
            recipient (str): Recipient's ID / ID получателя
            data (Dict[str, Any]): Transaction data / Данные транзакции
            
        Returns:
            int: Index of the block that will hold this transaction / Индекс блока, который будет содержать эту транзакцию
        """
        self.pending_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "timestamp": time.time(),
            "data": data
        })
        
        return self.get_latest_block().index + 1
    
    def mine_pending_transactions(self, miner_reward_address: str) -> Optional[Block]:
        """
        Mine pending transactions and add them to the blockchain.
        Майнинг ожидающих транзакций и добавление их в блокчейн.
        
        Args:
            miner_reward_address (str): Address to send mining rewards / Адрес для отправки вознаграждения за майнинг
            
        Returns:
            Optional[Block]: The newly created block, or None if no transactions to mine / Новый созданный блок или None, если нет транзакций для майнинга
        """
        if not self.pending_transactions:
            logger.info("No pending transactions to mine")
            return None
        
        # Create reward transaction for miner / Создание транзакции вознаграждения для майнера
        reward_transaction = {
            "sender": "0",  # "0" means system / "0" означает систему
            "recipient": miner_reward_address,
            "timestamp": time.time(),
            "data": {"type": "reward", "amount": 1}  # Simple reward of 1 token / Простое вознаграждение в 1 токен
        }
        
        # Add reward transaction to pending transactions / Добавление транзакции вознаграждения в ожидающие транзакции
        transactions_to_mine = self.pending_transactions + [reward_transaction]
        
        # Create and mine new block / Создание и майнинг нового блока
        latest_block = self.get_latest_block()
        new_block = Block(latest_block.index + 1, time.time(), transactions_to_mine, latest_block.hash)
        new_block.mine_block(self.difficulty)
        
        # Add new block to chain and clear pending transactions / Добавление нового блока в цепочку и очистка ожидающих транзакций
        self.chain.append(new_block)
        self.pending_transactions = []
        
        logger.info(f"Block #{new_block.index} with {len(transactions_to_mine)} transactions added to the chain")
        return new_block
    
    def is_chain_valid(self) -> bool:
        """
        Check if the blockchain is valid.
        Проверка корректности блокчейна.
        
        Returns:
            bool: True if the chain is valid, False otherwise / True, если цепь корректна, иначе False
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if the block's hash is valid / Проверка корректности хеша блока
            if current_block.hash != current_block.calculate_hash():
                logger.error(f"Invalid hash for block #{current_block.index}")
                return False
            
            # Check if the block points to the correct previous block / Проверка указания на правильный предыдущий блок
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Invalid previous_hash for block #{current_block.index}")
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert blockchain to dictionary.
        Преобразование блокчейна в словарь.
        
        Returns:
            Dict[str, Any]: Blockchain as dictionary / Блокчейн в виде словаря
        """
        return {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": self.pending_transactions,
            "difficulty": self.difficulty,
            "nodes": self.nodes
        }
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save blockchain state to file.
        Сохранение состояния блокчейна в файл.
        
        Args:
            filepath (str): Path to save the blockchain / Путь для сохранения блокчейна
            
        Returns:
            bool: True if successful, False otherwise / True в случае успеха, иначе False
        """
        try:
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            
            logger.info(f"Blockchain saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving blockchain: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'Blockchain':
        """
        Load blockchain state from file.
        Загрузка состояния блокчейна из файла.
        
        Args:
            filepath (str): Path to load the blockchain from / Путь для загрузки блокчейна
            
        Returns:
            Blockchain: Loaded blockchain / Загруженный блокчейн
            
        Raises:
            FileNotFoundError: If file does not exist / Если файл не существует
            json.JSONDecodeError: If file is not valid JSON / Если файл не является корректным JSON
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        blockchain = cls(difficulty=data.get('difficulty', 4))
        blockchain.pending_transactions = data.get('pending_transactions', [])
        blockchain.nodes = data.get('nodes', {})
        
        # Clear existing chain and rebuild it / Очистка существующей цепи и ее восстановление
        blockchain.chain = []
        for block_data in data.get('chain', []):
            block = Block(
                block_data['index'],
                block_data['timestamp'],
                block_data['transactions'],
                block_data['previous_hash'],
                block_data['nonce']
            )
            block.hash = block_data['hash']
            blockchain.chain.append(block)
        
        logger.info(f"Blockchain loaded from {filepath} with {len(blockchain.chain)} blocks")
        return blockchain


# Example usage / Пример использования
if __name__ == "__main__":
    # Create a new blockchain / Создание нового блокчейна
    blockchain = Blockchain(difficulty=2)
    
    # Add some transactions / Добавление нескольких транзакций
    blockchain.add_transaction("node_1", "node_2", {"message": "Hello from node 1!", "type": "data"})
    blockchain.add_transaction("node_3", "node_1", {"message": "Response from node 3", "type": "ack"})
    
    # Mine the transactions / Майнинг транзакций
    blockchain.mine_pending_transactions("node_validator_1")
    
    # Add more transactions / Добавление еще транзакций
    blockchain.add_transaction("node_2", "node_3", {"message": "Forwarded data", "type": "data"})
    blockchain.mine_pending_transactions("node_validator_2")
    
    # Verify the chain / Проверка цепи
    print(f"Is blockchain valid? {blockchain.is_chain_valid()}")
    
    # Save and load / Сохранение и загрузка
    blockchain.save_to_file("example_blockchain.json")
    loaded_blockchain = Blockchain.load_from_file("example_blockchain.json")
    
    print(f"Original blockchain has {len(blockchain.chain)} blocks")
    print(f"Loaded blockchain has {len(loaded_blockchain.chain)} blocks") 
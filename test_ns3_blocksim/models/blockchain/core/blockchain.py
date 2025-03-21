import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from ..network.node import Node
from .block import Block


class Blockchain:
    """
    Core blockchain implementation that can be initialized on any node
    """

    def __init__(self, node_id: str):
        self.chain: List[Block] = []
        self.node_id = node_id
        self.pending_transactions: List[Dict] = []

        # Initialize with genesis block
        if not self.chain:
            self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            previous_hash="0" * 64,
            timestamp=time.time(),
            data={
                "message": "Genesis Block",
                "creator": self.node_id,
                "timestamp": time.time(),
            },
        )
        self.chain.append(genesis_block)

    def add_block(self, data: Dict) -> Optional[Block]:
        """Add a new block to the chain with the given data"""
        if not self.chain:
            self._create_genesis_block()

        previous_block = self.chain[-1]
        new_block = Block(
            index=previous_block.index + 1,
            previous_hash=previous_block.hash,
            timestamp=time.time(),
            data=data,
        )

        if new_block.is_valid(previous_block):
            self.chain.append(new_block)
            return new_block
        return None

    def add_transaction(self, transaction: Dict) -> int:
        """Add a transaction to pending transactions"""
        self.pending_transactions.append(transaction)
        return self.last_block.index + 1

    def create_block_from_transactions(self) -> Optional[Block]:
        """Create a new block from pending transactions"""
        if not self.pending_transactions:
            return None

        data = {
            "transactions": self.pending_transactions,
            "creator": self.node_id,
            "timestamp": time.time(),
        }

        self.pending_transactions: List[Any] = []
        return self.add_block(data)

    @property
    def last_block(self) -> Block:
        """Get the last block in the chain"""
        return self.chain[-1]

    def is_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if not current_block.is_valid(previous_block):
                return False

        return True

    def to_dict(self) -> Dict:
        """Convert the blockchain to a dictionary for serialization"""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "node_id": self.node_id,
            "pending_transactions": self.pending_transactions,
        }

    @classmethod
    def from_dict(cls, blockchain_dict: Dict) -> "Blockchain":
        """Create a Blockchain instance from a dictionary"""
        blockchain = cls(blockchain_dict["node_id"])
        blockchain.chain = [
            Block.from_dict(block_dict) for block_dict in blockchain_dict["chain"]
        ]
        blockchain.pending_transactions = blockchain_dict["pending_transactions"]
        return blockchain

    def save_to_file(self, filepath: str) -> None:
        """Save the blockchain to a file"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filepath: str) -> Optional["Blockchain"]:
        """Load a blockchain from a file"""
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            blockchain_dict = json.load(f)

        return cls.from_dict(blockchain_dict)

    def merge_chains(self, other_chain: List[Block]) -> Tuple[bool, str]:
        """
        Merge with another blockchain if it's valid and longer
        Returns (success, message)
        """
        # Validate the other chain
        for i in range(1, len(other_chain)):
            if not other_chain[i].is_valid(other_chain[i - 1]):
                return False, "Invalid chain structure"

        # Check if the other chain is longer
        if len(other_chain) <= len(self.chain):
            return False, "Current chain is longer or equal"

        # Check if the chains share the same genesis block
        if other_chain[0].hash != self.chain[0].hash:
            return False, "Different genesis blocks"

        # Find the fork point
        fork_point = 0
        for i in range(min(len(self.chain), len(other_chain))):
            if self.chain[i].hash != other_chain[i].hash:
                fork_point = i - 1
                break

        # If fork point is valid, replace the chain after that point
        if fork_point >= 0:
            self.chain = self.chain[: fork_point + 1] + other_chain[fork_point + 1 :]
            return True, f"Chain merged at block {fork_point}"

        return False, "Invalid fork point"

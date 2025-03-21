import hashlib
import json
import time
from typing import Any, Dict, List, Optional


class Block:
    """
    Basic block structure for the blockchain
    """

    def __init__(
        self,
        index: int,
        previous_hash: str,
        timestamp: Optional[Any] = None,
        data: Any = None,
        hash: str = None,
    ):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp if timestamp else time.time()
        self.data = data if data else {}
        self.hash = hash if hash else self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate the hash of the block based on its contents"""
        block_string = json.dumps(
            {
                "index": self.index,
                "previous_hash": self.previous_hash,
                "timestamp": self.timestamp,
                "data": self.data,
            },
            sort_keys=True,
        ).encode()

        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict:
        """Convert block to dictionary for serialization"""
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, block_dict: Dict) -> "Block":
        """Create a Block instance from a dictionary"""
        return cls(
            index=block_dict["index"],
            previous_hash=block_dict["previous_hash"],
            timestamp=block_dict["timestamp"],
            data=block_dict["data"],
            hash=block_dict["hash"],
        )

    def is_valid(self, previous_block: Optional["Block"] = None) -> bool:
        """Validate block integrity and link to previous block"""
        # Check hash validity
        if self.hash != self.calculate_hash():
            return False

        # If previous block is provided, check the link
        if previous_block:
            if self.previous_hash != previous_block.hash:
                return False
            if self.index != previous_block.index + 1:
                return False

        return True

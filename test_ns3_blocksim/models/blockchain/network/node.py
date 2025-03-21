import hashlib
import json
import random
import secrets
import time
import uuid
from typing import Any, Dict, List, Optional, Set


class Node:
    """
    Node class representing a participant in the blockchain network
    """

    def __init__(
        self,
        node_id: Optional[Any] = None,
        node_type: str = "regular",
        position: tuple = (0, 0, 0),
        public_key: str = None,
        private_key: str = None,
        coverage_radius: float = 100.0,
    ):
        self.node_id = node_id if node_id else str(uuid.uuid4())
        self.node_type = node_type  # 'regular', 'validator', 'base_station'
        self.position = position
        self.coverage_radius = coverage_radius
        self.neighbors: Set[str] = set()
        self.is_active = True
        self.rating = 100.0  # Initial trust rating
        self.last_active = time.time()

        # Generate keys if not provided
        if not public_key or not private_key:
            self._generate_keys()
        else:
            self.public_key = public_key
            self.private_key = private_key

        # Track blockchain state
        self.has_blockchain = False
        self.blockchain_height = 0

    def _generate_keys(self) -> None:
        """Generate public and private keys for the node"""
        # This is a simplified version - in a real system use proper cryptography
        seed = f"{self.node_id}_{time.time()}_{int.from_bytes(secrets.token_bytes(4), 'big') / 2**32}"

        self.private_key = hashlib.sha256(f"private_{seed}".encode()).hexdigest()
        self.public_key = hashlib.sha256(f"public_{seed}".encode()).hexdigest()

    def update_position(self, new_position: tuple) -> None:
        """Update the node's position"""
        self.position = new_position
        self.last_active = time.time()

    def update_neighbors(self, node_ids: List[str]) -> None:
        """Update the node's neighbors list"""
        self.neighbors = set(node_ids)

    def add_neighbor(self, node_id: str) -> None:
        """Add a node as a neighbor"""
        self.neighbors.add(node_id)

    def remove_neighbor(self, node_id: str) -> None:
        """Remove a node from neighbors"""
        if node_id in self.neighbors:
            self.neighbors.remove(node_id)

    def is_within_range(self, other_node: "Node") -> bool:
        """Check if another node is within this node's coverage radius"""
        x1, y1, z1 = self.position
        x2, y2, z2 = other_node.position

        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5
        return distance <= self.coverage_radius

    def sign_message(self, message: Dict) -> str:
        """Sign a message with the node's private key"""
        # In a real implementation, use proper cryptographic signing
        message_str = json.dumps(message, sort_keys=True)
        signature = hashlib.sha256(
            f"{message_str}_{self.private_key}".encode()
        ).hexdigest()
        return signature

    def verify_signature(self, message: Dict, signature: str, public_key: str) -> bool:
        """Verify a signature using the provided public key"""
        # In a real implementation, use proper cryptographic verification
        message_str = json.dumps(message, sort_keys=True)
        expected = hashlib.sha256(
            f"{message_str}_{self.private_key}".encode()
        ).hexdigest()
        return signature == expected and self.public_key == public_key

    def ping(self) -> Dict:
        """Generate a heartbeat/ping message"""
        timestamp = time.time()
        message = {
            "node_id": self.node_id,
            "timestamp": timestamp,
            "position": self.position,
            "neighbors": list(self.neighbors),
            "blockchain_height": self.blockchain_height,
        }

        signature = self.sign_message(message)
        message["signature"] = signature

        self.last_active = timestamp
        return message

    def update_blockchain_status(self, has_blockchain: bool, height: int) -> None:
        """Update the node's blockchain status"""
        self.has_blockchain = has_blockchain
        self.blockchain_height = height

    def to_dict(self) -> Dict:
        """Convert node to dictionary for serialization"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "position": self.position,
            "coverage_radius": self.coverage_radius,
            "neighbors": list(self.neighbors),
            "is_active": self.is_active,
            "rating": self.rating,
            "last_active": self.last_active,
            "public_key": self.public_key,
            "has_blockchain": self.has_blockchain,
            "blockchain_height": self.blockchain_height,
        }

    @classmethod
    def from_dict(cls, node_dict: Dict) -> "Node":
        """Create a Node instance from a dictionary"""
        node = cls(
            node_id=node_dict["node_id"],
            node_type=node_dict["node_type"],
            position=node_dict["position"],
            public_key=node_dict["public_key"],
            coverage_radius=node_dict["coverage_radius"],
        )

        node.neighbors = set(node_dict["neighbors"])
        node.is_active = node_dict["is_active"]
        node.rating = node_dict["rating"]
        node.last_active = node_dict["last_active"]
        node.has_blockchain = node_dict.get("has_blockchain", False)
        node.blockchain_height = node_dict.get("blockchain_height", 0)

        return node

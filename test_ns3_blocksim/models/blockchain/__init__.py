# Blockchain integration components
from .blocksim_bridge import BlockSimBridge
from .crypto_manager import CrossZoneCrypto
from .transaction_handler import CrossZoneTransactionHandler

# Legacy blockchain components (keep for compatibility)
try:
    from .consensus import DistributedInitialization
    from .core import Block, Blockchain
    from .network import Node
    
    __all__ = [
        "BlockSimBridge", 
        "CrossZoneCrypto", 
        "CrossZoneTransactionHandler",
        "Block", 
        "Blockchain", 
        "Node", 
        "DistributedInitialization"
    ]
except ImportError:
    # If legacy components don't exist, only export new ones
    __all__ = [
        "BlockSimBridge", 
        "CrossZoneCrypto", 
        "CrossZoneTransactionHandler"
    ]

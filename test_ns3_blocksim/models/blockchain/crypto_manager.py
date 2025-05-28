#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crypto Manager for Cross-Zone Authentication
Handles cryptographic signing and verification of transactions
crossing zone boundaries in the 6G MANET blockchain system.
"""

import hashlib
import json
import logging
import os
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import ecdsa
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class NodeKeys:
    """Key pair for a network node"""
    node_id: int
    private_key: Any
    public_key: Any
    key_type: str  # "ecdsa" or "rsa"
    created_at: float

@dataclass
class TransactionSignature:
    """Digital signature for a transaction"""
    signature: str
    public_key_hash: str
    algorithm: str
    timestamp: float
    signer_id: int

class CrossZoneCrypto:
    """
    Cryptographic manager for cross-zone transactions
    Handles key generation, signing, and verification
    """
    
    def __init__(self, key_type: str = "ecdsa", key_size: int = 256):
        """
        Initialize crypto manager
        
        Args:
            key_type: Type of cryptographic keys ("ecdsa" or "rsa")
            key_size: Key size (256 for ECDSA, 2048+ for RSA)
        """
        self.logger = logging.getLogger("CrossZoneCrypto")
        
        if not CRYPTO_AVAILABLE:
            self.logger.warning("Cryptographic libraries not available. Using mock signatures.")
        
        self.key_type = key_type.lower()
        self.key_size = key_size
        self.node_keys: Dict[int, NodeKeys] = {}
        self.signature_cache: Dict[str, TransactionSignature] = {}
        
        # Validation settings
        self.signature_timeout = 300.0  # 5 minutes
        self.max_signature_age = 3600.0  # 1 hour
        
        self.logger.info(f"Crypto manager initialized with {key_type} keys")
    
    def generate_node_keys(self, node_id: int) -> bool:
        """
        Generate cryptographic keys for a node
        
        Args:
            node_id: Network node ID
            
        Returns:
            True if successful
        """
        try:
            if not CRYPTO_AVAILABLE:
                # Mock keys for testing
                self.node_keys[node_id] = NodeKeys(
                    node_id=node_id,
                    private_key=f"mock_private_{node_id}",
                    public_key=f"mock_public_{node_id}",
                    key_type="mock",
                    created_at=time.time()
                )
                self.logger.debug(f"Generated mock keys for node {node_id}")
                return True
            
            if self.key_type == "ecdsa":
                private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
                public_key = private_key.get_verifying_key()
                
                self.node_keys[node_id] = NodeKeys(
                    node_id=node_id,
                    private_key=private_key,
                    public_key=public_key,
                    key_type="ecdsa",
                    created_at=time.time()
                )
                
            elif self.key_type == "rsa":
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=max(self.key_size, 2048)
                )
                public_key = private_key.public_key()
                
                self.node_keys[node_id] = NodeKeys(
                    node_id=node_id,
                    private_key=private_key,
                    public_key=public_key,
                    key_type="rsa",
                    created_at=time.time()
                )
            
            else:
                raise ValueError(f"Unsupported key type: {self.key_type}")
            
            self.logger.debug(f"Generated {self.key_type} keys for node {node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate keys for node {node_id}: {e}")
            return False
    
    def sign_transaction(self, transaction_data: Dict[str, Any], signer_id: int) -> Optional[TransactionSignature]:
        """
        Sign a transaction with node's private key
        
        Args:
            transaction_data: Transaction data to sign
            signer_id: ID of the signing node
            
        Returns:
            Transaction signature or None if failed
        """
        try:
            if signer_id not in self.node_keys:
                self.logger.error(f"No keys found for node {signer_id}")
                return None
            
            node_keys = self.node_keys[signer_id]
            
            # Create canonical transaction string
            tx_string = self._canonicalize_transaction(transaction_data)
            tx_hash = hashlib.sha256(tx_string.encode()).digest()
            
            if not CRYPTO_AVAILABLE or node_keys.key_type == "mock":
                # Mock signature
                signature_hex = hashlib.md5(f"{signer_id}_{tx_string}".encode()).hexdigest()
                public_key_hash = hashlib.md5(f"public_{signer_id}".encode()).hexdigest()
                
            elif node_keys.key_type == "ecdsa":
                signature = node_keys.private_key.sign(tx_hash)
                signature_hex = signature.hex()
                public_key_hash = hashlib.sha256(
                    node_keys.public_key.to_string()
                ).hexdigest()
                
            elif node_keys.key_type == "rsa":
                signature = node_keys.private_key.sign(
                    tx_hash,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                signature_hex = signature.hex()
                public_key_hash = hashlib.sha256(
                    node_keys.public_key.public_bytes(
                        encoding=serialization.Encoding.DER,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                ).hexdigest()
            
            else:
                raise ValueError(f"Unknown key type: {node_keys.key_type}")
            
            # Create signature object
            tx_signature = TransactionSignature(
                signature=signature_hex,
                public_key_hash=public_key_hash,
                algorithm=node_keys.key_type,
                timestamp=time.time(),
                signer_id=signer_id
            )
            
            # Cache signature
            cache_key = f"{signer_id}_{tx_signature.public_key_hash[:16]}"
            self.signature_cache[cache_key] = tx_signature
            
            self.logger.debug(f"Transaction signed by node {signer_id}")
            return tx_signature
            
        except Exception as e:
            self.logger.error(f"Failed to sign transaction for node {signer_id}: {e}")
            return None
    
    def verify_signature(self, 
                        transaction_data: Dict[str, Any], 
                        signature: TransactionSignature) -> bool:
        """
        Verify a transaction signature
        
        Args:
            transaction_data: Original transaction data
            signature: Signature to verify
            
        Returns:
            True if signature is valid
        """
        try:
            # Check signature age
            if time.time() - signature.timestamp > self.max_signature_age:
                self.logger.warning(f"Signature from node {signature.signer_id} is too old")
                return False
            
            # Get signer's keys
            if signature.signer_id not in self.node_keys:
                self.logger.error(f"No keys found for signer {signature.signer_id}")
                return False
            
            node_keys = self.node_keys[signature.signer_id]
            
            # Create canonical transaction string
            tx_string = self._canonicalize_transaction(transaction_data)
            tx_hash = hashlib.sha256(tx_string.encode()).digest()
            
            if not CRYPTO_AVAILABLE or signature.algorithm == "mock":
                # Mock verification
                expected_signature = hashlib.md5(
                    f"{signature.signer_id}_{tx_string}".encode()
                ).hexdigest()
                is_valid = signature.signature == expected_signature
                
            elif signature.algorithm == "ecdsa":
                try:
                    signature_bytes = bytes.fromhex(signature.signature)
                    node_keys.public_key.verify(signature_bytes, tx_hash)
                    is_valid = True
                except ecdsa.BadSignatureError:
                    is_valid = False
                    
            elif signature.algorithm == "rsa":
                try:
                    signature_bytes = bytes.fromhex(signature.signature)
                    node_keys.public_key.verify(
                        signature_bytes,
                        tx_hash,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    is_valid = True
                except Exception:
                    is_valid = False
            
            else:
                self.logger.error(f"Unknown signature algorithm: {signature.algorithm}")
                return False
            
            if is_valid:
                self.logger.debug(f"Signature verified for node {signature.signer_id}")
            else:
                self.logger.warning(f"Invalid signature from node {signature.signer_id}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False
    
    def generate_cross_zone_proof(self, 
                                 transaction_data: Dict[str, Any], 
                                 bridge_id: int,
                                 from_zone: str,
                                 to_zone: str) -> Optional[Dict[str, Any]]:
        """
        Generate cross-zone proof by bridge validator
        
        Args:
            transaction_data: Transaction crossing zones
            bridge_id: ID of bridge validator
            from_zone: Source zone
            to_zone: Destination zone
            
        Returns:
            Cross-zone proof or None if failed
        """
        try:
            # Create proof data
            proof_data = {
                "transaction": transaction_data,
                "bridge_validator": bridge_id,
                "from_zone": from_zone,
                "to_zone": to_zone,
                "timestamp": time.time(),
                "zone_transition_valid": True  # In real implementation, validate this
            }
            
            # Sign the proof
            proof_signature = self.sign_transaction(proof_data, bridge_id)
            if not proof_signature:
                return None
            
            # Create final proof
            cross_zone_proof = {
                "proof_data": proof_data,
                "bridge_signature": {
                    "signature": proof_signature.signature,
                    "public_key_hash": proof_signature.public_key_hash,
                    "algorithm": proof_signature.algorithm,
                    "timestamp": proof_signature.timestamp,
                    "bridge_id": bridge_id
                },
                "proof_hash": hashlib.sha256(
                    json.dumps(proof_data, sort_keys=True).encode()
                ).hexdigest()
            }
            
            self.logger.info(f"Cross-zone proof generated by bridge {bridge_id}")
            return cross_zone_proof
            
        except Exception as e:
            self.logger.error(f"Failed to generate cross-zone proof: {e}")
            return None
    
    def verify_cross_zone_proof(self, proof: Dict[str, Any]) -> bool:
        """
        Verify a cross-zone proof
        
        Args:
            proof: Cross-zone proof to verify
            
        Returns:
            True if proof is valid
        """
        try:
            # Extract components
            proof_data = proof.get("proof_data", {})
            bridge_signature = proof.get("bridge_signature", {})
            proof_hash = proof.get("proof_hash", "")
            
            # Verify proof hash
            expected_hash = hashlib.sha256(
                json.dumps(proof_data, sort_keys=True).encode()
            ).hexdigest()
            
            if proof_hash != expected_hash:
                self.logger.warning("Cross-zone proof hash mismatch")
                return False
            
            # Verify bridge signature
            bridge_id = bridge_signature.get("bridge_id")
            if not bridge_id:
                self.logger.error("No bridge ID in proof")
                return False
            
            # Create signature object
            signature = TransactionSignature(
                signature=bridge_signature["signature"],
                public_key_hash=bridge_signature["public_key_hash"],
                algorithm=bridge_signature["algorithm"],
                timestamp=bridge_signature["timestamp"],
                signer_id=bridge_id
            )
            
            # Verify signature
            is_valid = self.verify_signature(proof_data, signature)
            
            if is_valid:
                self.logger.info(f"Cross-zone proof verified from bridge {bridge_id}")
            else:
                self.logger.warning(f"Invalid cross-zone proof from bridge {bridge_id}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Error verifying cross-zone proof: {e}")
            return False
    
    def _canonicalize_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """
        Create canonical string representation of transaction
        
        Args:
            transaction_data: Transaction data
            
        Returns:
            Canonical string
        """
        # Remove signature-related fields and sort keys
        clean_data = {k: v for k, v in transaction_data.items() 
                     if k not in ['signature', 'bridge_proof', 'validated']}
        
        return json.dumps(clean_data, sort_keys=True, separators=(',', ':'))
    
    def get_public_key(self, node_id: int) -> Optional[str]:
        """
        Get public key for a node
        
        Args:
            node_id: Node ID
            
        Returns:
            Public key as hex string or None
        """
        if node_id not in self.node_keys:
            return None
        
        node_keys = self.node_keys[node_id]
        
        try:
            if not CRYPTO_AVAILABLE or node_keys.key_type == "mock":
                return f"mock_public_{node_id}"
            elif node_keys.key_type == "ecdsa":
                return node_keys.public_key.to_string().hex()
            elif node_keys.key_type == "rsa":
                return node_keys.public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).hex()
        except Exception as e:
            self.logger.error(f"Error getting public key for node {node_id}: {e}")
        
        return None
    
    def get_crypto_statistics(self) -> Dict[str, Any]:
        """Get cryptographic statistics"""
        return {
            "total_keys": len(self.node_keys),
            "key_type": self.key_type,
            "key_size": self.key_size,
            "signatures_cached": len(self.signature_cache),
            "crypto_available": CRYPTO_AVAILABLE,
            "signature_timeout": self.signature_timeout,
            "max_signature_age": self.max_signature_age
        }
    
    def export_public_keys(self) -> Dict[int, str]:
        """
        Export all public keys for sharing
        
        Returns:
            Dictionary mapping node ID to public key hex
        """
        public_keys = {}
        for node_id in self.node_keys:
            pub_key = self.get_public_key(node_id)
            if pub_key:
                public_keys[node_id] = pub_key
        
        return public_keys
    
    def cleanup_old_signatures(self):
        """Remove old signatures from cache"""
        current_time = time.time()
        old_keys = []
        
        for key, signature in self.signature_cache.items():
            if current_time - signature.timestamp > self.max_signature_age:
                old_keys.append(key)
        
        for key in old_keys:
            del self.signature_cache[key]
        
        if old_keys:
            self.logger.debug(f"Cleaned up {len(old_keys)} old signatures")


# Testing functions
def test_crypto_manager():
    """Test the crypto manager"""
    logger = logging.getLogger("test")
    logger.info("Testing Cross-Zone Crypto Manager...")
    
    try:
        # Create crypto manager
        crypto = CrossZoneCrypto(key_type="ecdsa" if CRYPTO_AVAILABLE else "mock")
        
        # Generate keys for test nodes
        node_ids = [1, 10, 11]  # MANET node, Bridge validators
        for node_id in node_ids:
            success = crypto.generate_node_keys(node_id)
            if not success:
                raise RuntimeError(f"Failed to generate keys for node {node_id}")
        
        # Test transaction signing
        test_transaction = {
            "tx_id": "test_tx_123",
            "sender_id": 1,
            "recipient_id": 10,
            "data": "test_cross_zone_data",
            "timestamp": time.time()
        }
        
        signature = crypto.sign_transaction(test_transaction, 1)
        if not signature:
            raise RuntimeError("Failed to sign transaction")
        
        logger.info(f"Transaction signed: {signature.signature[:32]}...")
        
        # Test signature verification
        is_valid = crypto.verify_signature(test_transaction, signature)
        logger.info(f"Signature verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Test cross-zone proof
        proof = crypto.generate_cross_zone_proof(
            test_transaction, 10, "manet", "5g"
        )
        if not proof:
            raise RuntimeError("Failed to generate cross-zone proof")
        
        logger.info(f"Cross-zone proof generated: {proof['proof_hash'][:16]}...")
        
        # Test proof verification
        proof_valid = crypto.verify_cross_zone_proof(proof)
        logger.info(f"Proof verification: {'✅ Valid' if proof_valid else '❌ Invalid'}")
        
        # Get statistics
        stats = crypto.get_crypto_statistics()
        logger.info(f"Crypto statistics: {stats}")
        
        logger.info("✅ Crypto Manager test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Crypto Manager test failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_crypto_manager() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive Test for Real BlockSim Integration
Tests all components of the BlockSim bridge, crypto manager, and transaction handler
"""

import logging
import sys
import time
import json
from pathlib import Path

# Add models to path
sys.path.append(str(Path(__file__).parent))

from models.blockchain.blocksim_bridge import BlockSimBridge, test_blocksim_bridge
from models.blockchain.crypto_manager import CrossZoneCrypto, test_crypto_manager
from models.blockchain.transaction_handler import CrossZoneTransactionHandler, TransactionType

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("RealBlockSimIntegration")

def test_full_integration():
    """Test full integration pipeline"""
    logger.info("🧪 Testing Full BlockSim Integration Pipeline...")
    logger.info("=" * 60)
    
    try:
        # Step 1: Create and test BlockSim Bridge
        logger.info("📊 Step 1: Testing BlockSim Bridge...")
        bridge = BlockSimBridge(
            bridge_node_ids=[10, 11, 12],  # 3 bridge validators
            manet_node_ids=[1, 2, 3, 4],   # 4 MANET nodes
            fiveg_node_ids=[5, 6, 7, 8]    # 4 5G nodes
        )
        
        bridge_stats = bridge.get_bridge_statistics()
        logger.info(f"   ✅ Bridge initialized: {bridge_stats}")
        
        # Step 2: Create and test Crypto Manager
        logger.info("🔐 Step 2: Testing Crypto Manager...")
        crypto = CrossZoneCrypto()
        
        # Generate keys for all nodes
        all_nodes = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12]
        for node_id in all_nodes:
            success = crypto.generate_node_keys(node_id)
            if not success:
                raise RuntimeError(f"Failed to generate keys for node {node_id}")
        
        crypto_stats = crypto.get_crypto_statistics()
        logger.info(f"   ✅ Crypto keys generated: {crypto_stats}")
        
        # Step 3: Create and test Transaction Handler
        logger.info("🔄 Step 3: Testing Transaction Handler...")
        handler = CrossZoneTransactionHandler(bridge, crypto)
        
        # Step 4: Test Cross-Zone Transactions
        logger.info("🌐 Step 4: Testing Cross-Zone Transactions...")
        
        # Test Case 1: MANET -> 5G transaction
        logger.info("   📡 Test Case 1: MANET -> 5G")
        tx1_id = handler.create_transaction(
            sender_id=1,      # MANET node
            recipient_id=5,   # 5G node
            data="Hello from MANET to 5G!",
            transaction_type=TransactionType.DATA_TRANSFER,
            metadata={"test_case": 1, "priority": "high"}
        )
        
        # Test Case 2: 5G -> MANET transaction
        logger.info("   📱 Test Case 2: 5G -> MANET")
        tx2_id = handler.create_transaction(
            sender_id=6,      # 5G node
            recipient_id=3,   # MANET node
            data="Response from 5G to MANET!",
            transaction_type=TransactionType.DATA_TRANSFER,
            metadata={"test_case": 2, "response_to": tx1_id}
        )
        
        # Test Case 3: Zone transition notification
        logger.info("   🔄 Test Case 3: Zone Transition")
        tx3_id = handler.create_transaction(
            sender_id=2,      # MANET node
            recipient_id=10,  # Bridge validator
            data="Node entering 5G zone",
            transaction_type=TransactionType.ZONE_TRANSITION,
            metadata={"test_case": 3, "new_zone": "5g"}
        )
        
        logger.info(f"   Created transactions: {tx1_id[:16]}, {tx2_id[:16]}, {tx3_id[:16]}")
        
        # Step 5: Monitor transaction processing
        logger.info("⏱️  Step 5: Monitoring Transaction Processing...")
        
        transactions = [tx1_id, tx2_id, tx3_id]
        processing_timeout = 10.0
        start_time = time.time()
        
        while time.time() - start_time < processing_timeout:
            completed = 0
            failed = 0
            
            for tx_id in transactions:
                status = handler.get_transaction_status(tx_id)
                if status:
                    if status["status"] == "completed":
                        completed += 1
                    elif status["status"] == "failed":
                        failed += 1
            
            logger.info(f"   Status: {completed} completed, {failed} failed, {len(transactions)-completed-failed} active")
            
            if completed + failed == len(transactions):
                break
            
            time.sleep(1.0)
        
        # Step 6: Analyze results
        logger.info("📈 Step 6: Analyzing Results...")
        
        for i, tx_id in enumerate(transactions, 1):
            status = handler.get_transaction_status(tx_id)
            if status:
                tx_status = status.get("current_status") or status.get("final_status")
                events_count = len(status.get("events", []))
                logger.info(f"   Transaction {i}: {tx_status} ({events_count} events)")
                
                # Show detailed events for first transaction
                if i == 1 and status.get("events"):
                    logger.info("   Event timeline:")
                    for event in status["events"][-3:]:  # Show last 3 events
                        logger.info(f"     • {event['event_type']} at node {event['node_id']} ({event['zone']})")
        
        # Step 7: Get final statistics
        logger.info("📊 Step 7: Final Statistics...")
        
        handler_stats = handler.get_handler_statistics()
        bridge_final_stats = bridge.get_bridge_statistics()
        crypto_final_stats = crypto.get_crypto_statistics()
        
        logger.info("   Handler Statistics:")
        logger.info(f"     • Active: {handler_stats['active_transactions']}")
        logger.info(f"     • Completed: {handler_stats['completed_transactions']}")
        logger.info(f"     • Failed: {handler_stats['failed_transactions']}")
        logger.info(f"     • Average latency: {handler_stats['metrics']['average_latency']:.3f}s")
        
        logger.info("   Bridge Statistics:")
        logger.info(f"     • Total nodes: {bridge_final_stats['total_nodes']}")
        logger.info(f"     • Bridge validators: {bridge_final_stats['bridge_validators']}")
        logger.info(f"     • Validated transactions: {bridge_final_stats['validated_transactions']}")
        
        logger.info("   Crypto Statistics:")
        logger.info(f"     • Total keys: {crypto_final_stats['total_keys']}")
        logger.info(f"     • Key type: {crypto_final_stats['key_type']}")
        logger.info(f"     • Signatures cached: {crypto_final_stats['signatures_cached']}")
        
        # Step 8: Test cleanup
        logger.info("🧹 Step 8: Cleanup...")
        
        handler.shutdown()
        bridge.shutdown()
        
        logger.info("✅ Full integration test completed successfully!")
        logger.info("🎉 All components working together!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Full integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual components separately"""
    logger.info("🔧 Testing Individual Components...")
    logger.info("=" * 40)
    
    results = {}
    
    # Test BlockSim Bridge
    logger.info("1️⃣  Testing BlockSim Bridge...")
    results["bridge"] = test_blocksim_bridge()
    
    # Test Crypto Manager
    logger.info("2️⃣  Testing Crypto Manager...")
    results["crypto"] = test_crypto_manager()
    
    # Test Transaction Handler (requires bridge and crypto)
    logger.info("3️⃣  Testing Transaction Handler...")
    try:
        bridge = BlockSimBridge([10], [1, 2], [3, 4])
        crypto = CrossZoneCrypto()
        
        for node_id in [1, 2, 3, 4, 10]:
            crypto.generate_node_keys(node_id)
        
        handler = CrossZoneTransactionHandler(bridge, crypto)
        
        # Quick test
        tx_id = handler.create_transaction(1, 3, "test")
        time.sleep(2.0)
        
        status = handler.get_transaction_status(tx_id)
        results["handler"] = status is not None
        
        handler.shutdown()
        bridge.shutdown()
        
    except Exception as e:
        logger.error(f"Transaction handler test failed: {e}")
        results["handler"] = False
    
    # Summary
    logger.info("📊 Component Test Results:")
    for component, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {component.capitalize()}: {status}")
    
    all_passed = all(results.values())
    logger.info(f"Overall: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    
    return all_passed

def test_performance():
    """Test performance with multiple transactions"""
    logger.info("⚡ Testing Performance...")
    logger.info("=" * 30)
    
    try:
        # Create larger system
        bridge = BlockSimBridge(
            bridge_node_ids=[10, 11, 12],
            manet_node_ids=list(range(1, 11)),   # 10 MANET nodes
            fiveg_node_ids=list(range(21, 31))   # 10 5G nodes
        )
        
        crypto = CrossZoneCrypto()
        
        # Generate keys for all nodes
        all_nodes = list(range(1, 11)) + list(range(21, 31)) + [10, 11, 12]
        for node_id in all_nodes:
            crypto.generate_node_keys(node_id)
        
        handler = CrossZoneTransactionHandler(bridge, crypto)
        
        # Create multiple transactions
        transaction_count = 5
        transaction_ids = []
        
        start_time = time.time()
        
        for i in range(transaction_count):
            tx_id = handler.create_transaction(
                sender_id=1 + (i % 10),      # Rotate through MANET nodes
                recipient_id=21 + (i % 10),  # Rotate through 5G nodes
                data=f"Performance test transaction {i+1}",
                transaction_type=TransactionType.DATA_TRANSFER
            )
            transaction_ids.append(tx_id)
        
        creation_time = time.time() - start_time
        logger.info(f"Created {transaction_count} transactions in {creation_time:.3f}s")
        
        # Wait for processing
        processing_start = time.time()
        completed = 0
        
        while time.time() - processing_start < 15.0 and completed < transaction_count:
            completed = 0
            for tx_id in transaction_ids:
                status = handler.get_transaction_status(tx_id)
                if status and status["status"] in ["completed", "failed"]:
                    completed += 1
            
            if completed > 0:
                logger.info(f"Progress: {completed}/{transaction_count} transactions processed")
            
            time.sleep(1.0)
        
        processing_time = time.time() - processing_start
        
        # Get final statistics
        stats = handler.get_handler_statistics()
        
        logger.info("Performance Results:")
        logger.info(f"   • Transaction creation: {creation_time:.3f}s")
        logger.info(f"   • Processing time: {processing_time:.3f}s")
        logger.info(f"   • Throughput: {completed / processing_time:.2f} tx/s")
        logger.info(f"   • Average latency: {stats['metrics']['average_latency']:.3f}s")
        logger.info(f"   • Success rate: {stats['completed_transactions']}/{transaction_count}")
        
        handler.shutdown()
        bridge.shutdown()
        
        return completed >= transaction_count * 0.8  # 80% success rate
        
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Real BlockSim Integration Test Suite")
    logger.info("=" * 80)
    
    test_results = {}
    
    # Run individual component tests
    test_results["components"] = test_individual_components()
    
    print()  # Separator
    
    # Run full integration test
    test_results["integration"] = test_full_integration()
    
    print()  # Separator
    
    # Run performance test
    test_results["performance"] = test_performance()
    
    print()  # Separator
    
    # Final summary
    logger.info("🏁 Test Suite Summary")
    logger.info("=" * 40)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name.capitalize()}: {status}")
    
    all_passed = all(test_results.values())
    
    if all_passed:
        logger.info("")
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("✅ Real BlockSim integration is working correctly!")
        logger.info("🔗 Bridge Zone Template can now use real blockchain!")
    else:
        logger.info("")
        logger.info("❌ Some tests failed.")
        logger.info("🔧 Check the logs above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
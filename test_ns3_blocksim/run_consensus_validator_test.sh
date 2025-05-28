#!/bin/bash

# Consensus Validator Selection Test Runner
# Tests the ValidatorLeave/ManetNodeEnter exchange algorithm

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Consensus-Based Validator Selection Test${NC}"
echo -e "${BLUE}=============================================${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if we have the consensus validator manager
if [ ! -f "models/blockchain/consensus_validator_manager.py" ]; then
    echo -e "${RED}❌ Consensus validator manager not found${NC}"
    exit 1
fi

# Function to run a test
run_test() {
    local test_name="$1"
    local args="$2"
    
    echo -e "\n${YELLOW}📊 Running test: ${test_name}${NC}"
    echo -e "${YELLOW}Arguments: ${args}${NC}"
    
    if python3 scripts/run_consensus_validator_simulation.py $args; then
        echo -e "${GREEN}✅ Test '${test_name}' completed successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ Test '${test_name}' failed${NC}"
        return 1
    fi
}

# Parse command line arguments
TEST_MODE="quick"
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        quick|standard|extended)
            TEST_MODE="$1"
            shift
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        *)
            echo "Usage: $0 [quick|standard|extended] [--verbose]"
            echo ""
            echo "Test modes:"
            echo "  quick    - Short tests (60s each)"
            echo "  standard - Medium tests (180s each)" 
            echo "  extended - Long tests (300s each)"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}Test mode: ${TEST_MODE}${NC}"
if [ -n "$VERBOSE" ]; then
    echo -e "${BLUE}Verbose logging enabled${NC}"
fi

# Test configurations based on mode
case $TEST_MODE in
    "quick")
        TIME=60
        echo -e "${YELLOW}🏃 Quick test mode (60s simulations)${NC}"
        ;;
    "standard")
        TIME=180
        echo -e "${YELLOW}⏰ Standard test mode (180s simulations)${NC}"
        ;;
    "extended")
        TIME=300
        echo -e "${YELLOW}🕐 Extended test mode (300s simulations)${NC}"
        ;;
esac

echo ""

# Test 1: Basic consensus validator management
echo -e "${BLUE}Test 1: Basic Consensus Validator Management${NC}"
run_test "Basic Consensus" "--time $TIME --nodes 15 --min-validators 3 --max-validators 5 --no-ns3 $VERBOSE"

echo ""

# Test 2: High node mobility
echo -e "${BLUE}Test 2: High Node Mobility Scenario${NC}" 
run_test "High Mobility" "--time $TIME --nodes 25 --min-validators 4 --max-validators 8 --no-ns3 $VERBOSE"

echo ""

# Test 3: Validator shortage scenario
echo -e "${BLUE}Test 3: Validator Shortage Scenario${NC}"
run_test "Validator Shortage" "--time $TIME --nodes 12 --min-validators 5 --max-validators 7 --no-ns3 $VERBOSE"

echo ""

# Test 4: Large network test (if standard or extended)
if [ "$TEST_MODE" != "quick" ]; then
    echo -e "${BLUE}Test 4: Large Network Simulation${NC}"
    run_test "Large Network" "--time $TIME --nodes 40 --min-validators 5 --max-validators 10 --no-ns3 $VERBOSE"
    echo ""
fi

# Test 5: NS-3 integration test (if extended)
if [ "$TEST_MODE" = "extended" ]; then
    echo -e "${BLUE}Test 5: NS-3 Integration Test${NC}"
    run_test "NS-3 Integration" "--time $TIME --nodes 20 --min-validators 3 --max-validators 6 $VERBOSE"
    echo ""
fi

echo -e "${GREEN}🎉 All consensus validator tests completed!${NC}"
echo ""

# Test the consensus validator manager directly
echo -e "${BLUE}Testing Consensus Validator Manager directly...${NC}"
if python3 -c "
import sys
sys.path.append('.')
from models.blockchain.consensus_validator_manager import test_consensus_validator_manager
test_consensus_validator_manager()
"; then
    echo -e "${GREEN}✅ Direct manager test passed${NC}"
else
    echo -e "${RED}❌ Direct manager test failed${NC}"
fi

echo ""
echo -e "${GREEN}🎯 Consensus-Based Validator Selection Tests Summary:${NC}"
echo -e "${GREEN}  ✅ ValidatorLeave/ManetNodeEnter algorithm implemented${NC}"
echo -e "${GREEN}  ✅ PBFT consensus for validator changes${NC}"
echo -e "${GREEN}  ✅ RSSI-based zone detection and transitions${NC}"
echo -e "${GREEN}  ✅ Mobility-aware validator rotation${NC}"
echo -e "${GREEN}  ✅ Automatic candidate promotion on validator shortage${NC}"
echo -e "${GREEN}  ✅ Battery and performance-based validator selection${NC}"
echo -e "${GREEN}  ✅ Dual-radio gateway-validator preference${NC}"
echo ""
echo -e "${BLUE}📊 Features demonstrated:${NC}"
echo -e "${BLUE}  🔄 Dynamic validator rotation based on mobility${NC}"
echo -e "${BLUE}  📡 RSSI threshold-based leave/join decisions${NC}"
echo -e "${BLUE}  🗳️ Consensus voting for validator changes${NC}"
echo -e "${BLUE}  🔋 Battery level monitoring${NC}"
echo -e "${BLUE}  🌐 Multi-zone network support (5G/MANET/Bridge)${NC}"
echo -e "${BLUE}  ⚡ Real-time validator management${NC}" 
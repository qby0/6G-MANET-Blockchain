#!/bin/bash

# Enhanced Advanced Cross-Zone Blockchain Simulation with Consensus Validators
# Supports ValidatorLeave/ManetNodeEnter algorithm with mobility and PBFT consensus

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 Enhanced Cross-Zone Blockchain with Consensus Validators${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Default parameters
SIMULATION_TYPE="enhanced"
MANET_NODES=8
FG_NODES=6
BRIDGE_NODES=3
TIME=180
FG_RADIUS=100
MIN_VALIDATORS=3
MAX_VALIDATORS=7
MODE="standard"
VERBOSE=""
DISABLE_CONSENSUS=false

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS] [MODE]"
    echo ""
    echo "Simulation Types:"
    echo "  enhanced     - Enhanced cross-zone with consensus validators (DEFAULT)"
    echo "  cross-zone   - Basic cross-zone without consensus"
    echo "  consensus    - Standalone consensus validator simulation"
    echo "  all          - Run all simulation types"
    echo ""
    echo "Modes:"
    echo "  quick       - Quick test (60s, small network)"
    echo "  standard    - Standard simulation (180s, medium network)"
    echo "  large       - Large network simulation (300s, many nodes)"
    echo "  demo        - Demo with visualization focus (120s)"
    echo ""
    echo "Network Options:"
    echo "  --manet-nodes N      Number of MANET nodes (default: 8)"
    echo "  --5g-nodes N         Number of 5G nodes (default: 6)"
    echo "  --bridge-nodes N     Number of bridge validators (default: 3)"
    echo "  --time T             Simulation time in seconds (default: 180)"
    echo "  --5g-radius R        5G coverage radius in meters (default: 100)"
    echo ""
    echo "Consensus Validator Options:"
    echo "  --min-validators N   Minimum validators (default: 3)"
    echo "  --max-validators N   Maximum validators (default: 7)"
    echo "  --disable-consensus  Disable consensus validator management"
    echo ""
    echo "General Options:"
    echo "  --verbose           Enable verbose output"
    echo "  --list              List available simulation types"
    echo "  --help              Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                                          # Enhanced simulation (default)"
    echo "  $0 enhanced quick --verbose                 # Quick enhanced test"
    echo "  $0 consensus --time 300                     # Standalone consensus simulation"
    echo "  $0 cross-zone large --disable-consensus     # Large cross-zone without consensus"
    echo "  $0 all                                      # Run all simulation types"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        enhanced|cross-zone|consensus|all)
            SIMULATION_TYPE="$1"
            shift
            ;;
        quick|standard|large|demo)
            MODE="$1"
            shift
            ;;
        --manet-nodes)
            MANET_NODES="$2"
            shift 2
            ;;
        --5g-nodes)
            FG_NODES="$2"
            shift 2
            ;;
        --bridge-nodes)
            BRIDGE_NODES="$2"
            shift 2
            ;;
        --time)
            TIME="$2"
            shift 2
            ;;
        --5g-radius)
            FG_RADIUS="$2"
            shift 2
            ;;
        --min-validators)
            MIN_VALIDATORS="$2"
            shift 2
            ;;
        --max-validators)
            MAX_VALIDATORS="$2"
            shift 2
            ;;
        --disable-consensus)
            DISABLE_CONSENSUS=true
            shift
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --list)
            echo -e "${CYAN}📋 Available Simulation Types:${NC}"
            echo "  🏆 enhanced     - Enhanced cross-zone with consensus validators"
            echo "  🌐 cross-zone   - Advanced cross-zone with mobility"
            echo "  🗳️ consensus    - Consensus validator selection (standalone)"
            echo "  🎯 all          - Run all simulation types sequentially"
            echo ""
            echo -e "${CYAN}📋 Available Modes:${NC}"
            echo "  ⚡ quick        - Quick test (60s, small network)"
            echo "  📊 standard     - Standard simulation (180s, medium network)"
            echo "  🌐 large        - Large network simulation (300s, many nodes)"
            echo "  🎬 demo         - Demo with visualization focus (120s)"
            exit 0
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Apply mode presets
case $MODE in
    quick)
        MANET_NODES=4
        FG_NODES=3
        BRIDGE_NODES=2
        TIME=60
        FG_RADIUS=80
        MIN_VALIDATORS=2
        MAX_VALIDATORS=4
        echo -e "${YELLOW}⚡ Quick mode: Small network, 60s simulation${NC}"
        ;;
    standard)
        # Use defaults
        echo -e "${GREEN}📊 Standard mode: Medium network, 180s simulation${NC}"
        ;;
    large)
        MANET_NODES=12
        FG_NODES=10
        BRIDGE_NODES=5
        TIME=300
        FG_RADIUS=120
        MIN_VALIDATORS=4
        MAX_VALIDATORS=10
        echo -e "${PURPLE}🌐 Large mode: Big network, 300s simulation${NC}"
        ;;
    demo)
        MANET_NODES=6
        FG_NODES=4
        BRIDGE_NODES=3
        TIME=120
        FG_RADIUS=100
        MIN_VALIDATORS=3
        MAX_VALIDATORS=6
        echo -e "${CYAN}🎬 Demo mode: Visualization-focused, 120s simulation${NC}"
        ;;
    *)
        echo -e "${RED}❌ Unknown mode: $MODE${NC}"
        show_help
        exit 1
        ;;
esac

TOTAL_NODES=$((1 + MANET_NODES + FG_NODES + BRIDGE_NODES))

echo -e "${BLUE}📊 Configuration:${NC}"
echo -e "  Simulation Type: ${YELLOW}$SIMULATION_TYPE${NC}"
echo -e "  Mode: ${YELLOW}$MODE${NC}"
echo -e "  MANET nodes: ${YELLOW}$MANET_NODES${NC}"
echo -e "  5G nodes: ${YELLOW}$FG_NODES${NC}"
echo -e "  Bridge validators: ${YELLOW}$BRIDGE_NODES${NC}"
echo -e "  Total nodes: ${YELLOW}$TOTAL_NODES${NC} (including 1 base station)"
echo -e "  Simulation time: ${YELLOW}${TIME}s${NC}"
echo -e "  5G coverage: ${YELLOW}${FG_RADIUS}m${NC} radius"

if [[ "$SIMULATION_TYPE" == "enhanced" || "$SIMULATION_TYPE" == "consensus" ]] && [[ "$DISABLE_CONSENSUS" == "false" ]]; then
    echo -e "  Min validators: ${YELLOW}$MIN_VALIDATORS${NC}"
    echo -e "  Max validators: ${YELLOW}$MAX_VALIDATORS${NC}"
    echo -e "  Consensus: ${GREEN}Enabled${NC}"
elif [[ "$DISABLE_CONSENSUS" == "true" ]]; then
    echo -e "  Consensus: ${RED}Disabled${NC}"
fi

echo ""

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found! Please install Python 3.${NC}"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "main_sim.py" ]]; then
    echo -e "${RED}❌ main_sim.py not found!${NC}"
    echo -e "${RED}   Please run this script from the project root directory.${NC}"
    exit 1
fi

# Function to run the simulation
run_simulation() {
    echo -e "${BLUE}🚀 Starting Enhanced Cross-Zone Blockchain Simulation...${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    
    cd "$SCRIPT_DIR"
    
    # Build command using main_sim.py
    cmd="python3 main_sim.py $SIMULATION_TYPE"
    
    # Add network parameters
    cmd="$cmd --manet-nodes $MANET_NODES"
    cmd="$cmd --5g-nodes $FG_NODES"
    cmd="$cmd --bridge-nodes $BRIDGE_NODES"
    cmd="$cmd --time $TIME"
    cmd="$cmd --5g-radius $FG_RADIUS"
    
    # Add consensus parameters if applicable
    if [[ "$SIMULATION_TYPE" == "enhanced" || "$SIMULATION_TYPE" == "consensus" ]]; then
        cmd="$cmd --min-validators $MIN_VALIDATORS"
        cmd="$cmd --max-validators $MAX_VALIDATORS"
        
        if [[ "$DISABLE_CONSENSUS" == "true" ]]; then
            cmd="$cmd --disable-consensus"
        fi
    fi
    
    # Add verbose flag if requested
    if [[ -n "$VERBOSE" ]]; then
        cmd="$cmd $VERBOSE"
    fi
    
    echo -e "${BLUE}📋 Running: ${YELLOW}$cmd${NC}"
    echo ""
    
    # Show what will happen based on simulation type
    case $SIMULATION_TYPE in
        enhanced)
            echo -e "${CYAN}🎯 Enhanced Features:${NC}"
            echo -e "  🚶 All nodes mobile except base station"
            echo -e "  🔄 Dynamic zone transitions (5G ↔ MANET ↔ Bridge)"
            echo -e "  🛡️ Consensus-based validator management"
            echo -e "  🗳️ PBFT consensus for validator changes"
            echo -e "  📡 RSSI-based automatic validator rotation"
            echo -e "  🔗 Cross-zone transaction validation"
            echo -e "  ✍️ Cryptographic signatures for transactions"
            echo -e "  📡 AODV routing for MANET zone"
            echo -e "  📊 Real-time statistics and NetAnim visualization"
            ;;
        cross-zone)
            echo -e "${CYAN}🎯 Cross-Zone Features:${NC}"
            echo -e "  🚶 All nodes mobile except base station"
            echo -e "  🔄 Dynamic zone transitions (5G ↔ MANET ↔ Bridge)"
            echo -e "  🔁 Basic validator rotation"
            echo -e "  🔗 Cross-zone transaction validation"
            echo -e "  ✍️ Cryptographic signatures"
            echo -e "  📡 AODV routing for MANET zone"
            ;;
        consensus)
            echo -e "${CYAN}🎯 Consensus Features:${NC}"
            echo -e "  🛡️ ValidatorLeave/ManetNodeEnter algorithm"
            echo -e "  🗳️ PBFT consensus voting"
            echo -e "  📡 RSSI-based zone detection"
            echo -e "  🔋 Battery level monitoring"
            echo -e "  🚶 Mobility-aware validator rotation"
            echo -e "  ⚡ Automatic candidate promotion"
            ;;
        all)
            echo -e "${CYAN}🎯 Running All Simulation Types:${NC}"
            echo -e "  🔧 Basic NS-3 + BlockSim integration"
            echo -e "  📡 5G base station simulation"
            echo -e "  🌐 Cross-zone blockchain"
            echo -e "  🗳️ Consensus validator selection"
            echo -e "  🏆 Enhanced cross-zone with consensus"
            ;;
    esac
    
    echo ""
    
    if eval $cmd; then
        echo ""
        echo -e "${GREEN}✅ Enhanced Cross-Zone simulation completed successfully!${NC}"
        echo -e "${GREEN}🎉 Great job! The simulation ran without errors.${NC}"
        echo ""
        
        if [[ "$SIMULATION_TYPE" != "consensus" && "$SIMULATION_TYPE" != "all" ]]; then
            echo -e "${CYAN}📁 Generated files:${NC}"
            echo -e "  📊 ${YELLOW}advanced-cross-zone-blockchain-fixed.xml${NC} - NetAnim visualization"
            echo -e "     Open in NetAnim to see node movements and zone transitions"
            echo ""
        fi
        
        echo -e "${CYAN}🎯 What happened in the simulation:${NC}"
        case $SIMULATION_TYPE in
            enhanced)
                echo -e "  🏗️ Network initialized with 3 zones (5G, MANET, Bridge)"
                echo -e "  🛡️ Consensus validator management activated"
                echo -e "  🗳️ PBFT consensus for validator changes"
                echo -e "  🚶 Mobile nodes moved and changed zones dynamically"
                echo -e "  📡 RSSI-based automatic validator rotation"
                echo -e "  🔗 Cross-zone transactions validated cryptographically"
                echo -e "  📊 Live consensus statistics displayed"
                ;;
            cross-zone)
                echo -e "  🏗️ Network initialized with 3 zones (5G, MANET, Bridge)"
                echo -e "  🚶 Mobile nodes moved and changed zones dynamically"
                echo -e "  🔄 Basic validators rotated automatically"
                echo -e "  🔗 Cross-zone transactions validated cryptographically"
                ;;
            consensus)
                echo -e "  🛡️ Consensus validator system demonstrated"
                echo -e "  🗳️ PBFT voting for validator changes"
                echo -e "  📡 RSSI-based mobility detection"
                echo -e "  🔋 Battery level monitoring"
                ;;
            all)
                echo -e "  🎯 All simulation types executed successfully"
                echo -e "  📊 Comprehensive feature demonstration"
                ;;
        esac
        
        echo -e "  📊 Statistics collected throughout the simulation"
        echo ""
        return 0
    else
        echo ""
        echo -e "${RED}❌ Enhanced Cross-Zone simulation failed!${NC}"
        echo -e "${RED}💥 Something went wrong during the simulation.${NC}"
        echo ""
        echo -e "${YELLOW}🔍 Troubleshooting tips:${NC}"
        echo -e "  📋 Check the logs above for specific error messages"
        echo -e "  🔧 Try rebuilding NS-3: cd external/ns-3 && python3 ns3 clean && python3 ns3 build"
        echo -e "  📝 Run with --verbose for more detailed output"
        echo -e "  ⚡ Try 'quick' mode first to test basic functionality"
        echo -e "  🛑 Check if consensus validator dependencies are installed"
        echo ""
        return 1
    fi
}

# Main execution
echo -e "${CYAN}⏰ Starting in 3 seconds... Press Ctrl+C to cancel${NC}"
sleep 1
echo -e "${CYAN}⏰ Starting in 2 seconds...${NC}"
sleep 1
echo -e "${CYAN}⏰ Starting in 1 second...${NC}"
sleep 1

run_simulation
exit_code=$?

echo ""
if [[ $exit_code -eq 0 ]]; then
    echo -e "${GREEN}🚀 Mission accomplished! Enhanced cross-zone blockchain ready!${NC}"
    case $SIMULATION_TYPE in
        enhanced)
            echo -e "${GREEN}🏆 Consensus-based validator management successfully demonstrated!${NC}"
            echo -e "${GREEN}🛡️ ValidatorLeave/ManetNodeEnter algorithm working perfectly!${NC}"
            ;;
        consensus)
            echo -e "${GREEN}🗳️ PBFT consensus validator selection completed!${NC}"
            ;;
        all)
            echo -e "${GREEN}🎯 All simulation types completed successfully!${NC}"
            ;;
    esac
    if [[ "$SIMULATION_TYPE" != "consensus" && "$SIMULATION_TYPE" != "all" ]]; then
        echo -e "${GREEN}📊 Check the NetAnim file for cool visualization!${NC}"
    fi
    echo -e "${GREEN}🎮 Try different modes: quick, standard, large, demo${NC}"
else
    echo -e "${RED}💥 Mission failed! Check the troubleshooting tips above.${NC}"
fi

exit $exit_code 
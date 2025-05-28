#!/bin/bash
# 
# Convenient script for running NS-3 5G base station simulation
# 

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎬 5G Base Station + MANET + Blockchain Simulation${NC}"
echo -e "${BLUE}=================================================${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}📂 Project root: ${PROJECT_ROOT}${NC}"

# Change to project root directory
cd "$PROJECT_ROOT"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Activating virtual environment${NC}"
    source venv/bin/activate
fi

# Check for NS-3
NS3_PATH="$PROJECT_ROOT/external/ns-3"
if [ ! -d "$NS3_PATH" ]; then
    echo -e "${RED}❌ NS-3 not found at: $NS3_PATH${NC}"
    echo -e "${YELLOW}💡 Please install NS-3 in external/ns-3${NC}"
    exit 1
fi

echo -e "${GREEN}✅ NS-3 found at: $NS3_PATH${NC}"

# Check for simulation file
SIM_FILE="$NS3_PATH/scratch/simple-manet-5g-basestation.cc"
if [ ! -f "$SIM_FILE" ]; then
    echo -e "${RED}❌ Simulation file not found: $SIM_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Simulation file found${NC}"

# Run Python script with passed arguments
echo -e "${BLUE}🚀 Starting simulation...${NC}"
python3 scripts/run_5g_basestation_simulation.py "$@"

# Check result
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}🎉 Simulation completed successfully!${NC}"
    echo -e "${YELLOW}💡 To view animation, install NetAnim and open the generated .xml file${NC}"
else
    echo -e "\n${RED}❌ Simulation failed!${NC}"
    exit 1
fi 
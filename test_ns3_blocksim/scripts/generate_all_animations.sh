#!/bin/bash

echo "🎬 Generating All NetAnim Visualizations"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Setup
WORK_DIR=$(pwd)
NS3_DIR="$WORK_DIR/external/ns-3"
NETANIM_BIN="$WORK_DIR/netanim/build/bin/netanim"
OUTPUT_DIR="$WORK_DIR/animations"

# Create output directory
mkdir -p "$OUTPUT_DIR"

cd "$NS3_DIR"

echo -e "${BLUE}📁 Building simulation scripts...${NC}"

# Build all scripts
./ns3 build enhanced-manet-blockchain-netanim
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to build enhanced blockchain script${NC}"
    exit 1
fi

./ns3 build radio-range-visualizer
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to build radio range script${NC}"
    exit 1
fi

./ns3 build manet-blockchain-netanim
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Original script not available, skipping${NC}"
fi

echo -e "${GREEN}✅ All scripts built successfully${NC}"
echo ""

# Generate animations
echo -e "${BLUE}🚀 Generating animations...${NC}"

# 1. Enhanced Blockchain with Energy
echo -e "${YELLOW}1. Enhanced Blockchain + Energy Tracking...${NC}"
./ns3 run "enhanced-manet-blockchain-netanim --nNodes=15 --simulationTime=30 --outputFile=$OUTPUT_DIR/blockchain-energy.xml"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Blockchain energy animation generated${NC}"
else
    echo -e "${RED}❌ Failed to generate blockchain energy animation${NC}"
fi

# 2. Radio Range Visualization
echo -e "${YELLOW}2. Radio Range + Connectivity...${NC}"
./ns3 run "radio-range-visualizer --nNodes=12 --simulationTime=25 --outputFile=$OUTPUT_DIR/radio-connectivity.xml"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Radio connectivity animation generated${NC}"
else
    echo -e "${RED}❌ Failed to generate radio connectivity animation${NC}"
fi

# 3. High-density network
echo -e "${YELLOW}3. High-Density Network...${NC}"
./ns3 run "enhanced-manet-blockchain-netanim --nNodes=20 --simulationTime=20 --outputFile=$OUTPUT_DIR/high-density.xml"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ High-density animation generated${NC}"
else
    echo -e "${RED}❌ Failed to generate high-density animation${NC}"
fi

# 4. Extended simulation
echo -e "${YELLOW}4. Extended Simulation...${NC}"
./ns3 run "radio-range-visualizer --nNodes=8 --simulationTime=60 --outputFile=$OUTPUT_DIR/extended-network.xml"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Extended simulation animation generated${NC}"
else
    echo -e "${RED}❌ Failed to generate extended animation${NC}"
fi

# Copy routing files
cp enhanced-blockchain-routing.xml "$OUTPUT_DIR/" 2>/dev/null
cp radio-range-routing.xml "$OUTPUT_DIR/" 2>/dev/null
cp enhanced-blockchain-flowmon.xml "$OUTPUT_DIR/" 2>/dev/null

cd "$WORK_DIR"

echo ""
echo -e "${GREEN}🎉 All animations generated!${NC}"
echo ""
echo -e "${BLUE}📋 Generated Files:${NC}"
ls -la "$OUTPUT_DIR"/*.xml | while read line; do
    echo -e "  ${GREEN}•${NC} $line"
done

# Create launcher script
echo -e "${BLUE}📱 Creating launcher script...${NC}"

cat > "$OUTPUT_DIR/launch_netanim.sh" << 'EOF'
#!/bin/bash

# NetAnim Launcher for WSL
# Automatically sets up DISPLAY and launches animations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NETANIM_BIN="$(dirname "$SCRIPT_DIR")/netanim/build/bin/netanim"

# Setup DISPLAY for WSL
if [[ -z "$DISPLAY" ]]; then
    export DISPLAY=$(grep nameserver /etc/resolv.conf | awk '{print $2}'):0.0
    echo "DISPLAY set to: $DISPLAY"
fi

# Check if NetAnim exists
if [[ ! -f "$NETANIM_BIN" ]]; then
    echo "❌ NetAnim not found at: $NETANIM_BIN"
    exit 1
fi

echo "🎬 Available Animations:"
echo "========================"
echo "1. Blockchain + Energy Tracking (15 nodes, 30s)"
echo "2. Radio Range + Connectivity (12 nodes, 25s)"  
echo "3. High-Density Network (20 nodes, 20s)"
echo "4. Extended Simulation (8 nodes, 60s)"
echo "5. All animations (opens multiple windows)"
echo ""

read -p "Select animation (1-5): " choice

case $choice in
    1)
        echo "🔋 Launching Blockchain Energy Animation..."
        "$NETANIM_BIN" "$SCRIPT_DIR/blockchain-energy.xml"
        ;;
    2)
        echo "📡 Launching Radio Connectivity Animation..."
        "$NETANIM_BIN" "$SCRIPT_DIR/radio-connectivity.xml"
        ;;
    3)
        echo "🏙️ Launching High-Density Animation..."
        "$NETANIM_BIN" "$SCRIPT_DIR/high-density.xml"
        ;;
    4)
        echo "⏱️ Launching Extended Animation..."
        "$NETANIM_BIN" "$SCRIPT_DIR/extended-network.xml"
        ;;
    5)
        echo "🚀 Launching all animations..."
        for file in "$SCRIPT_DIR"/*.xml; do
            if [[ -f "$file" && "$file" != *"routing"* && "$file" != *"flowmon"* ]]; then
                echo "Opening: $(basename "$file")"
                "$NETANIM_BIN" "$file" &
                sleep 2
            fi
        done
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
EOF

chmod +x "$OUTPUT_DIR/launch_netanim.sh"

echo -e "${GREEN}✅ Launcher created: $OUTPUT_DIR/launch_netanim.sh${NC}"
echo ""
echo -e "${PURPLE}🖥️  To run animations:${NC}"
echo -e "  ${GREEN}1.${NC} cd animations"
echo -e "  ${GREEN}2.${NC} ./launch_netanim.sh"
echo -e "  ${GREEN}3.${NC} Select animation number"
echo ""
echo -e "${BLUE}📊 Animation Features:${NC}"
echo -e "  ${GREEN}•${NC} Energy tracking with visual feedback"
echo -e "  ${GREEN}•${NC} Radio range circles and connectivity"
echo -e "  ${GREEN}•${NC} Dynamic color coding (validators vs nodes)"
echo -e "  ${GREEN}•${NC} Real-time counters (Energy, Blocks, Transactions)"
echo -e "  ${GREEN}•${NC} Packet flow visualization"
echo -e "  ${GREEN}•${NC} Network statistics and routing info"
echo ""
echo -e "${YELLOW}💡 Pro tips:${NC}"
echo -e "  • Use 0.5x playback speed for better visibility"
echo -e "  • Enable Node Statistics panel in NetAnim"
echo -e "  • Watch energy levels decrease over time"
echo -e "  • Observe connectivity changes in radio visualization"
EOF 
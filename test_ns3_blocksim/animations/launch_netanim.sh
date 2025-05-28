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

#!/bin/bash

# MANET Blockchain NetAnim Setup Script
# This script installs and configures NetAnim for visualization

echo "🎯 Setting up NetAnim for MANET Blockchain Visualization"

# Check if running on WSL
if grep -q Microsoft /proc/version; then
    echo "⚠️  WSL detected. NetAnim requires X11 forwarding for GUI."
    echo "Please ensure you have:"
    echo "1. X11 server running on Windows (VcXsrv, Xming, etc.)"
    echo "2. DISPLAY environment variable set"
    echo ""
fi

# Install dependencies
echo "📦 Installing NetAnim dependencies..."
sudo apt update
sudo apt install -y build-essential qt5-default qt5-qmake qtbase5-dev-tools

# Download and build NetAnim
NETANIM_VERSION="3.109"
NETANIM_DIR="netanim-${NETANIM_VERSION}"

if [ ! -d "$NETANIM_DIR" ]; then
    echo "⬇️  Downloading NetAnim..."
    wget https://www.nsnam.org/releases/netanim-${NETANIM_VERSION}.tar.bz2
    tar -xf netanim-${NETANIM_VERSION}.tar.bz2
    rm netanim-${NETANIM_VERSION}.tar.bz2
fi

cd $NETANIM_DIR
echo "🔨 Building NetAnim..."
make clean
qmake NetAnim.pro
make

if [ -f "NetAnim" ]; then
    echo "✅ NetAnim built successfully!"
    
    # Create desktop entry
    cat > NetAnim.desktop << EOF
[Desktop Entry]
Version=1.0
Name=NetAnim
Comment=Network Animator for NS-3
Exec=$(pwd)/NetAnim
Icon=applications-multimedia
Terminal=false
Type=Application
Categories=Development;
EOF
    
    echo "🎮 NetAnim executable: $(pwd)/NetAnim"
    echo ""
    echo "🎨 To view your animation:"
    echo "1. Run: ./NetAnim"
    echo "2. Open: manet-blockchain-visualization.xml"
    echo ""
    
    # Copy animation files to NetAnim directory
    cp ../external/ns-3/manet-blockchain-visualization.xml .
    cp ../external/ns-3/blockchain-routing.xml .
    
    echo "📁 Animation files copied to NetAnim directory"
    
else
    echo "❌ Failed to build NetAnim"
    exit 1
fi

cd ..

echo ""
echo "🎯 NetAnim Setup Complete!"
echo ""
echo "📋 Available animation files:"
echo "   • manet-blockchain-visualization.xml (Main animation)"
echo "   • blockchain-routing.xml (Routing table tracking)"
echo ""
echo "🚀 To start visualization:"
echo "   cd $NETANIM_DIR && ./NetAnim"
echo ""
echo "🎪 Animation Features:"
echo "   • 15 MANET nodes (3 validators in blue, 12 regular in red)"
echo "   • 30 seconds of network simulation"
echo "   • Random mobility with AODV routing"
echo "   • Packet transmission visualization"
echo "   • Energy and routing tracking" 
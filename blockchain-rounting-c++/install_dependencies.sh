#!/bin/bash
# Install Python dependencies for analysis script

echo "Installing Python dependencies for analysis..."

# Try pip3 with user flag first
echo "Attempting: pip3 install --user pandas matplotlib numpy seaborn"
pip3 install --user pandas matplotlib numpy seaborn 2>&1 | tail -5

# Check if successful
if python3 -c "import pandas, matplotlib, numpy" 2>/dev/null; then
    echo ""
    echo "✓ Dependencies installed successfully!"
    exit 0
fi

# If that fails, try system packages (Ubuntu/Debian)
if command -v apt-get > /dev/null 2>&1; then
    echo ""
    echo "Trying system package manager..."
    echo "Run this command manually (requires sudo):"
    echo "  sudo apt-get install -y python3-pandas python3-matplotlib python3-numpy python3-seaborn"
    echo ""
    echo "Or create a virtual environment:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install pandas matplotlib numpy seaborn"
fi

echo ""
echo "If installation fails, you can:"
echo "1. Use system package manager (requires sudo)"
echo "2. Create a Python virtual environment"
echo "3. Install manually: pip3 install pandas matplotlib numpy seaborn"


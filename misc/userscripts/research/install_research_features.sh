#!/bin/bash

# Install Research & OSINT Features for qutebrowser
# This script installs advanced research capabilities including:
# - Public records databases
# - Academic research tools
# - Financial intelligence
# - OSINT capabilities

set -e

echo "======================================"
echo "qutebrowser Research Features Installer"
echo "======================================"
echo ""

# Detect config directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/.config/qutebrowser"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/qutebrowser"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

USERSCRIPTS_DIR="$CONFIG_DIR/userscripts"

echo "Configuration directory: $CONFIG_DIR"
echo "Userscripts directory: $USERSCRIPTS_DIR"
echo ""

# Create directories if they don't exist
mkdir -p "$CONFIG_DIR"
mkdir -p "$USERSCRIPTS_DIR"

# Copy research configuration
echo "Installing research configuration..."
cp research_config.py "$CONFIG_DIR/"
echo "  ✓ research_config.py installed"

# Copy userscripts
echo ""
echo "Installing userscripts..."
for script in multi_search.py earnings_analysis.py deep_search.py financial_analysis.py osint_search.py; do
    cp "$script" "$USERSCRIPTS_DIR/"
    chmod +x "$USERSCRIPTS_DIR/$script"
    echo "  ✓ $script installed and made executable"
done

# Check if config.py exists
if [ -f "$CONFIG_DIR/config.py" ]; then
    echo ""
    echo "Checking existing config.py..."
    
    # Check if research features are already configured
    if grep -q "research_config import setup_research_features" "$CONFIG_DIR/config.py"; then
        echo "  ✓ Research features already configured in config.py"
    else
        echo "  Adding research features to config.py..."
        
        # Create backup
        cp "$CONFIG_DIR/config.py" "$CONFIG_DIR/config.py.backup"
        echo "  ✓ Backup created: config.py.backup"
        
        # Add import statement after the sys.path configuration
        cat >> "$CONFIG_DIR/config.py" << 'EOF'

# Import Research Features Configuration
try:
    import sys
    import os
    config_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, config_dir)
    from research_config import setup_research_features
    setup_research_features(config)
    print("Research features loaded successfully!")
except ImportError as e:
    print(f"Warning: Could not load research features: {e}")
EOF
        echo "  ✓ Research features added to config.py"
    fi
else
    echo ""
    echo "Creating new config.py with research features..."
    cat > "$CONFIG_DIR/config.py" << 'EOF'
#!/usr/bin/env python3
# qutebrowser configuration with Research & OSINT features

import os
import sys

# Load default configuration
config.load_autoconfig(False)

# Basic settings
c.auto_save.session = True
c.content.javascript.enabled = True
c.downloads.location.directory = '~/Downloads/'

# Import Research Features Configuration
try:
    config_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, config_dir)
    from research_config import setup_research_features
    setup_research_features(config)
    print("Research features loaded successfully!")
except ImportError as e:
    print(f"Warning: Could not load research features: {e}")

print("Configuration loaded!")
EOF
    echo "  ✓ config.py created with research features"
fi

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Research features have been installed successfully!"
echo ""
echo "Available commands:"
echo "  :biz-search <company>    - Search business registries"
echo "  :acad-search <topic>     - Search academic databases"
echo "  :earnings <ticker>       - Get earnings data"
echo "  :deep-search <query>     - Comprehensive OSINT search"
echo "  :reddit-user <username>  - Reddit user analysis"
echo "  :find-forum <topic>      - Find specialized forums"
echo ""
echo "Keybindings:"
echo "  ,bs - Business search      ,as - Academic search"
echo "  ,ls - Legal search         ,gs - Government data"
echo "  ,ps - Property search      ,ru - Reddit user"
echo "  ,is - IP search            ,ff - Find forums"
echo "  ,ea - Earnings analysis    ,ds - Deep search"
echo ""
echo "To test the installation, restart qutebrowser and try:"
echo "  :biz-search 'Apple Inc'"
echo ""
echo "For more information, see README_RESEARCH_FEATURES.md"
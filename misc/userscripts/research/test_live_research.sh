#!/bin/bash

# Test Research Features in qutebrowser
# This script tests the research features by sending commands to a running qutebrowser instance

echo "================================"
echo "Research Features Live Test"
echo "================================"
echo ""
echo "This test requires qutebrowser to be running."
echo "Start qutebrowser first, then run this script."
echo ""
read -p "Is qutebrowser running? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please start qutebrowser and run this script again."
    exit 1
fi

# Get the qutebrowser FIFO
QUTE_FIFO=$(ls /tmp/qutebrowser-*/ipc-* 2>/dev/null | head -1)

if [ -z "$QUTE_FIFO" ]; then
    echo "Error: Could not find qutebrowser IPC socket."
    echo "Make sure qutebrowser is running."
    exit 1
fi

echo "Found qutebrowser IPC: $QUTE_FIFO"
echo ""

# Function to send command to qutebrowser
send_command() {
    echo "$1" | socat - UNIX-CONNECT:"$QUTE_FIFO"
    sleep 1
}

# Test search engines
echo "Testing Search Engines..."
echo "========================="
echo ""

echo "1. Testing Google Scholar search engine..."
send_command ":open -t scholar quantum computing"
echo "   ✓ Google Scholar search sent"

echo "2. Testing SEC EDGAR search..."
send_command ":open -t sec Apple Inc"
echo "   ✓ SEC EDGAR search sent"

echo "3. Testing Patent search..."
send_command ":open -t gpatent artificial intelligence"
echo "   ✓ Patent search sent"

echo ""
echo "Testing Master Commands..."
echo "=========================="
echo ""

echo "4. Testing business search (will open multiple tabs)..."
send_command ":biz-search Microsoft Corporation"
echo "   ✓ Business search command sent"
sleep 2

echo "5. Testing academic search (will open multiple tabs)..."
send_command ":acad-search machine learning"
echo "   ✓ Academic search command sent"
sleep 2

echo "6. Testing Reddit user analysis..."
send_command ":reddit-user spez"
echo "   ✓ Reddit user search sent"

echo "7. Testing forum discovery..."
send_command ":find-forum vintage fountain pens"
echo "   ✓ Forum discovery search sent"

echo "8. Testing earnings analysis..."
send_command ":earnings AAPL"
echo "   ✓ Earnings analysis sent"
sleep 2

echo "9. Testing deep OSINT search..."
send_command ":deep-search john.doe@example.com"
echo "   ✓ Deep OSINT search sent"
sleep 2

echo "10. Testing financial analysis..."
send_command ":financials GOOGL"
echo "   ✓ Financial analysis sent"

echo ""
echo "================================"
echo "Test Complete!"
echo "================================"
echo ""
echo "Check qutebrowser for the opened tabs."
echo "You should see:"
echo "  - Individual search tabs for scholar, SEC, patents"
echo "  - Multiple tabs for business and academic searches"
echo "  - Reddit user search results"
echo "  - Forum discovery results"
echo "  - Financial/earnings data tabs"
echo "  - OSINT search results"
echo ""
echo "If tabs didn't open, check:"
echo "  1. qutebrowser console for errors (press : then 'messages')"
echo "  2. Userscripts are executable"
echo "  3. Config is loaded (check startup messages)"
echo ""
echo "To manually test keybindings, try:"
echo "  ,bs - Business search"
echo "  ,ls - Legal search"
echo "  ,as - Academic search"
echo "  ,ea - Earnings analysis"
echo "  ,ds - Deep search"
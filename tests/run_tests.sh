#!/bin/bash

# Qutebrowser Advanced Search Test Runner
# Run all tests for the advanced search features

echo "=========================================="
echo "QUTEBROWSER ADVANCED SEARCH TEST RUNNER"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -n "Running $test_name... "
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval $test_command > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Change to tests directory
cd "$(dirname "$0")"

# Run comprehensive test suite
echo "🧪 Running Comprehensive Test Suite"
echo "-----------------------------------"
python test_advanced_search_all.py

echo ""
echo "=========================================="
echo "TEST RESULTS"
echo "=========================================="

# Check if all core files exist
echo ""
echo "📁 File Structure Check:"
run_test "Config file" "test -f '$HOME/Library/Application Support/qutebrowser/config.py'"
run_test "Search script" "test -f '$HOME/Library/Application Support/qutebrowser/scripts/cross_search.py'"
run_test "Userscript" "test -f '$HOME/Library/Application Support/qutebrowser/userscripts/cross_search'"
run_test "Userscript executable" "test -x '$HOME/Library/Application Support/qutebrowser/userscripts/cross_search'"

# Summary
echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed!${NC}"
    exit 1
fi
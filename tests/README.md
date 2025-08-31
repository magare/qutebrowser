# Qutebrowser Advanced Search - Test Suite

## Overview

Comprehensive test suite for qutebrowser advanced search features including unit tests, integration tests, and visual browser tests.

## Test Structure

```
tests/
├── unit/scripts/                        # Original unit tests
│   └── test_cross_search.py            # Core search functionality tests
├── integration/                         # Original integration tests
│   └── test_cross_search_integration.py # Config and script integration
├── test_advanced_search_all.py         # Consolidated test suite (all tests in one)
└── run_tests.sh                        # Simple test runner
```

## Running Tests

### Quick Test (All Tests)
```bash
cd tests
./run_tests.sh
```

### Comprehensive Test Suite
```bash
python test_advanced_search_all.py
```

### Individual Test Files (if needed)
```bash
# Unit tests only
python unit/scripts/test_cross_search.py

# Integration tests only
python integration/test_cross_search_integration.py
```

## Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| Cross-engine search | 13 unit tests | ✅ Passing |
| Search operators | 11 operator tests | ✅ Passing |
| Configuration | 16 integration tests | ✅ Passing |
| User journeys | 4 workflow tests | ✅ Passing |
| Visual browser | 5 browser tests | ✅ Passing |

## Visual Test Details

### 1. Framework Test
Verifies qutebrowser installation and environment setup.

### 2. End-to-End Test
Tests complete user workflows:
- Researcher journey (academic searches)
- Developer journey (code searches)
- Student journey (research tasks)

### 3. Headless Browser Test
CI/CD compatible tests without GUI requirements.

### 4. Final Verification
Quick validation of all features.

### 5. Master Test Runner
Orchestrates all tests and generates HTML reports.

## Test Results

Latest test run: **100% Pass Rate**
- Total tests: 49
- Passed: 49
- Failed: 0

## Browser Launch Test

To test features in actual browser:

```bash
/Users/vilasmagare/Documents/qutebrowser/qute-venv/bin/qutebrowser \
  --config-py "$HOME/Library/Application Support/qutebrowser/config.py"
```

Then test:
- `:xs python tutorial` - Cross-engine search
- `,ss github.com python` - Site search
- `,sf pdf tutorial` - File type search

## Continuous Testing

The test suite supports:
- Unit testing for individual components
- Integration testing for configuration
- Visual testing for actual browser behavior
- CI/CD integration via headless tests
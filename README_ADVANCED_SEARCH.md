# Qutebrowser Advanced Search Features

## Overview

Advanced search enhancements for qutebrowser that add cross-engine search capabilities and advanced search operators while maintaining qutebrowser's minimalist, keyboard-driven philosophy.

## Features

### 1. Cross-Engine Triangulation
Search multiple engines simultaneously with a single command.

**Usage:** `:xs <query>` or `,x <query>`

**Example:** `:xs python tutorial` opens tabs in Google, Bing, and DuckDuckGo

### 2. Advanced Search Operators

| Operator | Shortcut | Description | Example |
|----------|----------|-------------|---------|
| Site Search | `,ss` | Limit to specific site | `,ss github.com python` |
| File Type | `,sf` | Search specific file types | `,sf pdf machine learning` |
| PDF Search | `,sp` | Quick PDF search | `,sp python tutorial` |
| Exact Phrase | `,se` | Add quotes automatically | `,se machine learning` |
| Exclusion | `,s-` | Exclude terms | `,s- python -django` |
| Inclusion | `,s+` | Force include terms | `,s+ python +flask` |
| Boolean OR | `,so` | OR operator | `,so python OR ruby` |
| Grouping | `,s(` | Group terms | `,s( (python OR ruby)` |
| In Title | `,st` | Search in page titles | `,st tutorial python` |
| In URL | `,su` | Search in URLs | `,su api documentation` |
| In Text | `,si` | Search in page text | `,si python examples` |
| In Anchor | `,sa` | Search in link text | `,sa download` |
| Wildcard | `,s*` | Wildcard search | `,s* python * tutorial` |

### 3. Quick Search Macros

- `,sA` - Academic search (Google Scholar, arXiv, PubMed)
- `,sN` - News search (NYTimes, BBC, Reuters)
- `,sD` - Documentation search (Python docs, MDN, Stack Overflow)

### 4. Direct Engine Selection

- `sg` - Search selected text in Google
- `sb` - Search selected text in Bing
- `sd` - Search selected text in DuckDuckGo
- `gx` - Search selected text across all engines

## Installation

### Required Files

```
~/Library/Application Support/qutebrowser/
├── config.py                    # Main configuration with keybindings
├── scripts/
│   └── cross_search.py          # Cross-engine search script
└── userscripts/
    └── cross_search             # Qutebrowser userscript wrapper
```

### Configuration

The configuration is automatically loaded when qutebrowser starts. All keybindings are defined in `config.py`.

## Testing

### Quick Test
```bash
cd tests
./run_all_tests.sh
```

### Test Structure
```
tests/
├── unit/scripts/                        # Unit tests
│   └── test_cross_search.py            # Core functionality tests
├── integration/                         # Integration tests
│   └── test_cross_search_integration.py # Config and script integration
├── visual/                              # Visual browser tests
│   ├── visual_test_framework.py        # Test framework
│   ├── visual_tests.py                 # Browser automation tests
│   ├── headless_browser_test.py        # CI/CD compatible tests
│   ├── end_to_end_test.py             # User journey tests
│   ├── final_verification.py          # Quick verification
│   ├── master_test_runner.py          # Test orchestrator
│   └── run_all_visual_tests.sh        # Visual test runner
├── test_advanced_search_complete.py    # Comprehensive test suite
└── run_all_tests.sh                    # Main test runner
```

### Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| Cross-engine search | 13 unit tests | ✅ Passing |
| Search operators | 11 operator tests | ✅ Passing |
| Configuration | 16 integration tests | ✅ Passing |
| User journeys | 4 workflow tests | ✅ Passing |
| Visual browser | 5 browser tests | ✅ Passing |

**Total:** 49 tests, 100% passing

## Browser Launch

To test features in the actual browser:

```bash
/Users/vilasmagare/Documents/qutebrowser/qute-venv/bin/qutebrowser \
  --config-py "$HOME/Library/Application Support/qutebrowser/config.py"
```

Then test:
- `:xs python tutorial` - Cross-engine search
- `,ss github.com python` - Site search
- `,sf pdf tutorial` - File type search

## Usage Examples

### Basic Usage

1. **Cross-Engine Search**
   ```
   :xs python tutorial
   ```
   Opens 3 tabs with search results from different engines

2. **Site-Specific Search**
   ```
   ,ss stackoverflow.com python error
   ```
   Searches only on Stack Overflow

3. **File Type Search**
   ```
   ,sf pdf machine learning
   ```
   Finds PDF files about machine learning

### Advanced Examples

```bash
# Complex query with multiple operators
:open site:github.com "python api" -deprecated filetype:md

# Academic research
,sA quantum computing

# News search
,sN climate change

# Selected text search across engines
# Select text and press:
gx
```

## Philosophy Alignment

The implementation follows qutebrowser's core principles:

- **Keyboard-driven**: All features accessible via keyboard shortcuts
- **Minimalist**: No GUI additions, uses existing command interface
- **Vim-like**: Consistent with vim conventions (leader keys, mnemonics)
- **Extensible**: Uses userscripts without modifying core browser
- **Privacy-respecting**: No tracking or data collection

## Troubleshooting

1. **Commands not working**: Restart qutebrowser after configuration changes
2. **Userscript errors**: Check file permissions (should be executable)
3. **Missing features**: Ensure config.py is loaded (check :messages)

## Support

For issues or questions, check the test files for examples or refer to the qutebrowser documentation.
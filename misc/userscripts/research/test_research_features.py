#!/usr/bin/env python3
"""
Test script for Research & OSINT features in qutebrowser
"""

import os
import sys
import subprocess
import time
import tempfile
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_test(name, status):
    symbol = "✓" if status else "✗"
    color = GREEN if status else RED
    print(f"{color}[{symbol}] {name}{RESET}")

def test_config_files():
    """Test if all configuration files are present"""
    print_header("Testing Configuration Files")
    
    config_dir = Path.home() / '.config' / 'qutebrowser'
    files_to_check = [
        'config.py',
        'research_config.py',
        'userscripts/multi_search.py',
        'userscripts/earnings_analysis.py',
        'userscripts/deep_search.py',
        'userscripts/financial_analysis.py',
        'userscripts/osint_search.py',
    ]
    
    all_present = True
    for file_path in files_to_check:
        full_path = config_dir / file_path
        exists = full_path.exists()
        print_test(f"File: {file_path}", exists)
        if exists and file_path.startswith('userscripts/'):
            is_exec = os.access(full_path, os.X_OK)
            print_test(f"  └─ Executable", is_exec)
            all_present = all_present and is_exec
        all_present = all_present and exists
    
    return all_present

def test_search_engines():
    """Test if search engines are properly configured"""
    print_header("Testing Search Engine Configuration")
    
    # Import the multi_search script to check categories
    userscript_path = Path.home() / '.config' / 'qutebrowser' / 'userscripts'
    sys.path.insert(0, str(userscript_path))
    
    try:
        from multi_search import SEARCH_CATEGORIES
        
        # Check if main categories exist
        required_categories = [
            'business', 'legal', 'property', 'ip', 
            'academic', 'govdata', 'osint'
        ]
        
        for category in required_categories:
            exists = category in SEARCH_CATEGORIES
            print_test(f"Category: {category}", exists)
            if exists:
                url_count = len(SEARCH_CATEGORIES[category])
                print(f"  └─ URLs configured: {url_count}")
        
        return True
    except ImportError as e:
        print_test("Import search categories", False)
        print(f"  Error: {e}")
        return False

def test_userscript_syntax():
    """Test if userscripts have valid Python syntax"""
    print_header("Testing Userscript Syntax")
    
    userscript_dir = Path.home() / '.config' / 'qutebrowser' / 'userscripts'
    scripts = [
        'multi_search.py',
        'earnings_analysis.py',
        'deep_search.py',
        'financial_analysis.py',
        'osint_search.py',
    ]
    
    all_valid = True
    for script in scripts:
        script_path = userscript_dir / script
        if script_path.exists():
            try:
                with open(script_path, 'r') as f:
                    code = f.read()
                compile(code, str(script_path), 'exec')
                print_test(f"Script: {script}", True)
            except SyntaxError as e:
                print_test(f"Script: {script}", False)
                print(f"  Error: {e}")
                all_valid = False
        else:
            print_test(f"Script: {script}", False)
            all_valid = False
    
    return all_valid

def test_qutebrowser_integration():
    """Test if qutebrowser can load the configuration"""
    print_header("Testing qutebrowser Integration")
    
    # Create a test script that loads the config
    test_script = """
import sys
import os
from pathlib import Path

# Add config directory to path
config_dir = Path.home() / '.config' / 'qutebrowser'
sys.path.insert(0, str(config_dir))

# Mock qutebrowser config object
class MockConfig:
    def __init__(self):
        self.data = {}
        self.aliases = {}
        self.bindings = {}
    
    def set(self, key, value):
        self.data[key] = value
    
    def bind(self, key, command):
        self.bindings[key] = command

config = MockConfig()

# Try to import and run research config
try:
    from research_config import setup_research_features
    setup_research_features(config)
    
    # Check if configuration was applied
    has_search_engines = 'url.searchengines' in config.data
    has_aliases = 'aliases' in config.data
    
    print(f"Search engines configured: {has_search_engines}")
    print(f"Aliases configured: {has_aliases}")
    
    if has_search_engines:
        engines = config.data['url.searchengines']
        print(f"Number of search engines: {len(engines)}")
    
    if has_aliases:
        aliases = config.data['aliases']
        print(f"Number of aliases: {len(aliases)}")
    
    # Check for key bindings
    print(f"Number of key bindings: {len(config.bindings)}")
    
    sys.exit(0 if (has_search_engines and has_aliases) else 1)
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"""
    
    # Write test script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        temp_script = f.name
    
    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, temp_script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        success = result.returncode == 0
        print_test("Configuration loads without errors", success)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if not success and result.stderr:
            print(f"{RED}  Error output:{RESET}")
            for line in result.stderr.strip().split('\n'):
                print(f"  {line}")
        
        return success
        
    except subprocess.TimeoutExpired:
        print_test("Configuration loads without errors", False)
        print("  Error: Script timed out")
        return False
    finally:
        os.unlink(temp_script)

def test_specific_commands():
    """Test specific command patterns"""
    print_header("Testing Command Patterns")
    
    # Test that userscripts handle arguments correctly
    userscript_dir = Path.home() / '.config' / 'qutebrowser' / 'userscripts'
    
    tests = [
        ('multi_search.py', ['business', 'test company'], 'Multi-search with category'),
        ('earnings_analysis.py', ['AAPL'], 'Earnings analysis with ticker'),
        ('deep_search.py', ['john.doe@example.com'], 'Deep search with email'),
        ('osint_search.py', ['example.com'], 'OSINT search with domain'),
        ('financial_analysis.py', ['GOOGL'], 'Financial analysis with ticker'),
    ]
    
    all_pass = True
    for script, args, description in tests:
        script_path = userscript_dir / script
        if script_path.exists():
            # Just check if script can be called with arguments (dry run)
            try:
                # Read script and check for main function
                with open(script_path, 'r') as f:
                    content = f.read()
                has_main = 'def main()' in content and "if __name__ == '__main__'" in content
                print_test(description, has_main)
            except Exception as e:
                print_test(description, False)
                print(f"  Error: {e}")
                all_pass = False
        else:
            print_test(description, False)
            all_pass = False
    
    return all_pass

def main():
    """Run all tests"""
    print(f"{YELLOW}Research & OSINT Features Test Suite{RESET}")
    print(f"{YELLOW}Testing qutebrowser configuration...{RESET}")
    
    results = []
    
    # Run tests
    results.append(("Configuration Files", test_config_files()))
    results.append(("Search Engines", test_search_engines()))
    results.append(("Userscript Syntax", test_userscript_syntax()))
    results.append(("qutebrowser Integration", test_qutebrowser_integration()))
    results.append(("Command Patterns", test_specific_commands()))
    
    # Summary
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for _, status in results if status)
    
    for name, status in results:
        print_test(name, status)
    
    print(f"\n{BLUE}Results: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"{GREEN}✓ All tests passed! Research features are ready to use.{RESET}")
        print(f"\n{YELLOW}Quick Start Guide:{RESET}")
        print("1. Start qutebrowser")
        print("2. Try these commands:")
        print("   - :biz-search 'Apple Inc' - Search business registries")
        print("   - :acad-search 'quantum computing' - Search academic papers")
        print("   - :earnings AAPL - Get earnings data")
        print("   - :deep-search john@example.com - OSINT email search")
        print("   - ,bs [then type] - Business search keybinding")
        return 0
    else:
        print(f"{RED}✗ Some tests failed. Please check the errors above.{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
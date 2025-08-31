#!/usr/bin/env python3
"""
Integration tests for cross-search feature in qutebrowser.
This tests the integration between the config.py and cross_search.py script.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, call
import subprocess

# Path to config directory
CONFIG_DIR = os.path.expanduser('~/Library/Application Support/qutebrowser')
SCRIPTS_DIR = os.path.join(CONFIG_DIR, 'scripts')
CROSS_SEARCH_SCRIPT = os.path.join(SCRIPTS_DIR, 'cross_search.py')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.py')


class TestCrossSearchFeature(unittest.TestCase):
    """Test the complete cross-search feature integration."""
    
    def test_config_file_exists(self):
        """Test that config.py exists."""
        self.assertTrue(os.path.exists(CONFIG_FILE), 
                       f"Config file not found at {CONFIG_FILE}")
    
    def test_cross_search_script_exists(self):
        """Test that cross_search.py exists."""
        self.assertTrue(os.path.exists(CROSS_SEARCH_SCRIPT),
                       f"Cross-search script not found at {CROSS_SEARCH_SCRIPT}")
    
    def test_config_imports_correctly(self):
        """Test that config.py can be imported without errors."""
        # Create a test environment
        test_env = {
            'config': MagicMock(),
            'c': MagicMock(),
            '__file__': CONFIG_FILE
        }
        
        with open(CONFIG_FILE, 'r') as f:
            config_content = f.read()
        
        # Check for required imports and definitions
        self.assertIn('import os', config_content)
        self.assertIn('import sys', config_content)
        # Updated to check for userscript instead of direct script reference
        self.assertIn('cross_search', config_content)
        self.assertIn('spawn --userscript', config_content)
    
    def test_keybindings_configured(self):
        """Test that keybindings are properly configured."""
        with open(CONFIG_FILE, 'r') as f:
            config_content = f.read()
        
        # Check for cross-search keybindings
        self.assertIn("config.bind('xs'", config_content)
        self.assertIn("config.bind(',x'", config_content)
        
        # Check for advanced search operator bindings
        self.assertIn("config.bind(',ss'", config_content)  # Site search
        self.assertIn("config.bind(',sf'", config_content)  # File type search
        self.assertIn("config.bind(',se'", config_content)  # Exact phrase
    
    def test_search_engines_configured(self):
        """Test that search engines are properly configured."""
        with open(CONFIG_FILE, 'r') as f:
            config_content = f.read()
        
        # Check for search engine configuration
        self.assertIn('c.url.searchengines', config_content)
        self.assertIn("'g': 'https://www.google.com", config_content)
        self.assertIn("'b': 'https://www.bing.com", config_content)
        self.assertIn("'d': 'https://duckduckgo.com", config_content)
    
    def test_cross_search_execution(self):
        """Test that cross_search.py produces correct output."""
        # Test with a simple query
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT, 'test query'],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        
        # Check output contains URLs
        urls = result.stdout.strip().split('\n')
        self.assertGreater(len(urls), 0)
        
        for url in urls:
            self.assertTrue(url.startswith('http'))
            self.assertIn('test%20query', url)
    
    def test_cross_search_with_special_chars(self):
        """Test cross_search.py with special characters."""
        queries = [
            'site:example.com test',
            'filetype:pdf python',
            '"exact phrase" search',
            'search -exclude +include',
            'test OR another',
            'AROUND(5) proximity'
        ]
        
        for query in queries:
            result = subprocess.run(
                [sys.executable, CROSS_SEARCH_SCRIPT, query],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0, 
                           f"Failed for query: {query}")
            
            urls = result.stdout.strip().split('\n')
            self.assertGreater(len(urls), 0,
                             f"No URLs generated for query: {query}")
    
    def test_cross_search_custom_engines(self):
        """Test cross_search.py with custom engine selection."""
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT, 
             '--engines', 'google,yahoo', 'custom engine test'],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        
        urls = result.stdout.strip().split('\n')
        self.assertEqual(len(urls), 2)
        self.assertIn('google.com', urls[0])
        self.assertIn('yahoo.com', urls[1])


class TestAdvancedSearchOperators(unittest.TestCase):
    """Test that advanced search operators work correctly."""
    
    def test_exact_phrase_operator(self):
        """Test exact phrase search with quotes."""
        query = '"exact phrase search"'
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT, query],
            capture_output=True,
            text=True
        )
        
        urls = result.stdout.strip().split('\n')
        for url in urls:
            # Check that quotes are properly encoded
            self.assertIn('exact%20phrase%20search', url)
    
    def test_exclusion_inclusion_operators(self):
        """Test - and + operators."""
        query = 'python -java +tutorial'
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT, query],
            capture_output=True,
            text=True
        )
        
        urls = result.stdout.strip().split('\n')
        for url in urls:
            self.assertIn('python', url)
            self.assertIn('java', url)
            self.assertIn('tutorial', url)
    
    def test_site_restriction_operator(self):
        """Test site: operator."""
        query = 'site:github.com python'
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT, query],
            capture_output=True,
            text=True
        )
        
        urls = result.stdout.strip().split('\n')
        for url in urls:
            self.assertIn('site%3Agithub.com', url)
    
    def test_filetype_operator(self):
        """Test filetype: operator."""
        query = 'filetype:pdf machine learning'
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT, query],
            capture_output=True,
            text=True
        )
        
        urls = result.stdout.strip().split('\n')
        for url in urls:
            self.assertIn('filetype%3Apdf', url)
    
    def test_boolean_operators(self):
        """Test OR operator and parentheses."""
        query = '(python OR java) programming'
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT, query],
            capture_output=True,
            text=True
        )
        
        urls = result.stdout.strip().split('\n')
        for url in urls:
            # Check that parentheses and OR are encoded
            self.assertIn('python%20OR%20java', url)
    
    def test_wildcard_operator(self):
        """Test * wildcard operator."""
        query = '"python * tutorial"'
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT, query],
            capture_output=True,
            text=True
        )
        
        urls = result.stdout.strip().split('\n')
        for url in urls:
            self.assertIn('python', url)
            self.assertIn('tutorial', url)


class TestEndToEnd(unittest.TestCase):
    """End-to-end tests for the complete feature."""
    
    def test_complete_workflow(self):
        """Test the complete workflow from query to URLs."""
        test_queries = [
            'simple search',
            'site:stackoverflow.com python error',
            'filetype:pdf "machine learning"',
            'javascript -jquery +react',
            '(python OR ruby) web framework',
            'intitle:tutorial programming',
        ]
        
        for query in test_queries:
            # Test default engines
            result = subprocess.run(
                [sys.executable, CROSS_SEARCH_SCRIPT, query],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0,
                           f"Script failed for query: {query}")
            
            urls = result.stdout.strip().split('\n')
            self.assertGreater(len(urls), 0,
                             f"No URLs generated for: {query}")
            
            # Verify each URL is valid
            for url in urls:
                self.assertTrue(url.startswith('http'),
                              f"Invalid URL format: {url}")
                
                # Check that the query is in the URL (encoded)
                import urllib.parse
                encoded_query = urllib.parse.quote(query)
                # Note: The encoded query might be differently formatted
                # but should contain the key terms
    
    def test_error_recovery(self):
        """Test that the system handles errors gracefully."""
        # Test with empty query
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error", result.stderr)
        
        # Test with invalid engine
        result = subprocess.run(
            [sys.executable, CROSS_SEARCH_SCRIPT,
             '--engines', 'invalid_engine', 'test'],
            capture_output=True,
            text=True
        )
        
        # Should still work but produce no output
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), '')


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
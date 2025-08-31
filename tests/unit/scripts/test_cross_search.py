#!/usr/bin/env python3
"""
Unit tests for the cross-engine search functionality.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import subprocess

# Add the scripts directory to the path
sys.path.insert(0, os.path.expanduser('~/Library/Application Support/qutebrowser/scripts'))

# Import the cross_search module
import cross_search


class TestCrossSearch(unittest.TestCase):
    """Test cases for cross-engine search functionality."""
    
    def test_get_search_urls_default_engines(self):
        """Test URL generation with default engines."""
        query = "test query"
        urls = cross_search.get_search_urls(query)
        
        # Check we have the right number of URLs
        self.assertEqual(len(urls), len(cross_search.DEFAULT_ENGINES))
        
        # Check URLs are properly formatted
        for url in urls:
            self.assertIn("test%20query", url)
            self.assertTrue(url.startswith("http"))
    
    def test_get_search_urls_custom_engines(self):
        """Test URL generation with custom engines."""
        query = "python programming"
        engines = ['google', 'yahoo']
        urls = cross_search.get_search_urls(query, engines)
        
        self.assertEqual(len(urls), 2)
        self.assertIn("google.com", urls[0])
        self.assertIn("yahoo.com", urls[1])
        self.assertIn("python%20programming", urls[0])
    
    def test_get_search_urls_special_characters(self):
        """Test URL encoding of special characters."""
        query = "test & query + special #chars"
        urls = cross_search.get_search_urls(query)
        
        for url in urls:
            # Check that special characters are properly encoded
            self.assertNotIn("&", url.split("?q=")[1])
            self.assertNotIn("#", url.split("?q=")[1])
            self.assertIn("test%20%26%20query%20%2B%20special%20%23chars", url)
    
    def test_get_search_urls_empty_query(self):
        """Test behavior with empty query."""
        query = ""
        urls = cross_search.get_search_urls(query)
        
        # Should still generate URLs, even if empty
        self.assertEqual(len(urls), len(cross_search.DEFAULT_ENGINES))
    
    def test_get_search_urls_invalid_engine(self):
        """Test behavior with invalid engine names."""
        query = "test"
        engines = ['google', 'invalid_engine', 'bing']
        urls = cross_search.get_search_urls(query, engines)
        
        # Should only generate URLs for valid engines
        self.assertEqual(len(urls), 2)
        self.assertIn("google.com", urls[0])
        self.assertIn("bing.com", urls[1])
    
    def test_all_configured_engines(self):
        """Test that all configured engines produce valid URLs."""
        query = "test all engines"
        
        for engine_name, url_template in cross_search.SEARCH_ENGINES.items():
            urls = cross_search.get_search_urls(query, [engine_name])
            self.assertEqual(len(urls), 1)
            self.assertIn("test%20all%20engines", urls[0])
            self.assertTrue(urls[0].startswith("http"))
    
    @patch('sys.argv', ['cross_search.py', 'test', 'search', 'query'])
    def test_main_with_query(self):
        """Test main function with a search query."""
        with patch('builtins.print') as mock_print:
            cross_search.main()
            
            # Check that URLs were printed
            self.assertEqual(mock_print.call_count, len(cross_search.DEFAULT_ENGINES))
            
            # Check that printed values are URLs
            for call in mock_print.call_args_list:
                url = call[0][0]
                self.assertTrue(url.startswith("http"))
                self.assertIn("test%20search%20query", url)
    
    @patch('sys.argv', ['cross_search.py'])
    def test_main_without_query(self):
        """Test main function without a search query."""
        with self.assertRaises(SystemExit) as cm:
            cross_search.main()
        
        self.assertEqual(cm.exception.code, 1)
    
    @patch('sys.argv', ['cross_search.py', '--engines', 'google,bing', 'test', 'query'])
    def test_main_with_custom_engines(self):
        """Test main function with custom engines specified."""
        with patch('builtins.print') as mock_print:
            cross_search.main()
            
            # Check that only specified engines were used
            self.assertEqual(mock_print.call_count, 2)
            
            urls = [call[0][0] for call in mock_print.call_args_list]
            self.assertIn("google.com", urls[0])
            self.assertIn("bing.com", urls[1])


class TestCrossSearchIntegration(unittest.TestCase):
    """Integration tests for cross-search script."""
    
    def setUp(self):
        """Set up test environment."""
        self.script_path = os.path.expanduser(
            '~/Library/Application Support/qutebrowser/scripts/cross_search.py'
        )
    
    def test_script_exists(self):
        """Test that the script file exists."""
        self.assertTrue(os.path.exists(self.script_path))
    
    def test_script_is_executable(self):
        """Test that the script has executable permissions."""
        self.assertTrue(os.access(self.script_path, os.X_OK))
    
    def test_script_runs_successfully(self):
        """Test that the script can be executed."""
        result = subprocess.run(
            [sys.executable, self.script_path, 'test'],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("http", result.stdout)
    
    def test_script_error_handling(self):
        """Test script error handling with no arguments."""
        result = subprocess.run(
            [sys.executable, self.script_path],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error", result.stderr)


if __name__ == '__main__':
    unittest.main()
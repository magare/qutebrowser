# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the SOCMINT component."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtCore import QUrl

from qutebrowser.components import socmint


class TestHelperFunctions:
    """Test helper functions in the SOCMINT module."""
    
    def test_sanitize_identifier(self):
        """Test identifier sanitization."""
        assert socmint._sanitize_identifier('@username') == 'username'
        assert socmint._sanitize_identifier('user.name-123') == 'user.name-123'
        assert socmint._sanitize_identifier('(555) 123-4567') == '555 123-4567'
        assert socmint._sanitize_identifier('user@email.com') == 'user@email.com'
        assert socmint._sanitize_identifier('  spaces  ') == 'spaces'
        
    def test_format_phone_number_us(self):
        """Test US phone number formatting."""
        formats = socmint._format_phone_number('5551234567')
        assert formats['digits'] == '5551234567'
        assert formats['dashed'] == '555-123-4567'
        assert formats['dotted'] == '555.123.4567'
        assert formats['spaced'] == '555 123 4567'
        assert formats['parentheses'] == '(555) 123-4567'
        assert formats['international'] == '+15551234567'
        
    def test_format_phone_number_us_with_country(self):
        """Test US phone number with country code."""
        formats = socmint._format_phone_number('15551234567')
        assert formats['digits'] == '15551234567'
        assert formats['dashed'] == '555-123-4567'
        assert formats['international'] == '+15551234567'
        
    def test_format_phone_number_international(self):
        """Test international phone number formatting."""
        formats = socmint._format_phone_number('+44207946000')
        assert formats['international'] == '+44207946000'
        

class TestPivotCommand:
    """Test the pivot command."""
    
    @pytest.fixture
    def mock_tabbed_browser(self):
        """Create a mock tabbed browser."""
        browser = Mock()
        browser.tabopen = Mock()
        return browser
    
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    def test_pivot_username(self, mock_message, mock_objreg, mock_tabbed_browser):
        """Test pivot with username."""
        mock_objreg.get.return_value = mock_tabbed_browser
        
        socmint.pivot('johndoe', 0)
        
        assert mock_tabbed_browser.tabopen.called
        assert mock_tabbed_browser.tabopen.call_count >= 5
        mock_message.info.assert_called()
        
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    def test_pivot_email(self, mock_message, mock_objreg, mock_tabbed_browser):
        """Test pivot with email address."""
        mock_objreg.get.return_value = mock_tabbed_browser
        
        socmint.pivot('john@example.com', 0)
        
        assert mock_tabbed_browser.tabopen.called
        # Email searches use different platforms
        calls = mock_tabbed_browser.tabopen.call_args_list
        urls = [str(call[0][0].toString()) for call in calls]
        assert any('linkedin' in url for url in urls)
        
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    def test_pivot_phone(self, mock_message, mock_objreg, mock_tabbed_browser):
        """Test pivot with phone number."""
        mock_objreg.get.return_value = mock_tabbed_browser
        
        socmint.pivot('5551234567', 0)
        
        assert mock_tabbed_browser.tabopen.called
        # Phone searches use specific platforms
        calls = mock_tabbed_browser.tabopen.call_args_list
        urls = [str(call[0][0].toString()) for call in calls]
        assert any('truecaller' in url or 'whitepages' in url for url in urls)
        

class TestPlatformSearchCommand:
    """Test the platform_search command."""
    
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    def test_platform_search_valid(self, mock_message, mock_objreg):
        """Test platform search with valid platform."""
        mock_browser = Mock()
        mock_objreg.get.return_value = mock_browser
        
        socmint.platform_search('twitter', 'test query', 0)
        
        mock_browser.tabopen.assert_called_once()
        call_args = mock_browser.tabopen.call_args[0]
        assert isinstance(call_args[0], QUrl)
        assert 'twitter.com' in call_args[0].toString()
        assert 'test+query' in call_args[0].toString()
        
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    def test_platform_search_invalid(self, mock_message, mock_objreg):
        """Test platform search with invalid platform."""
        socmint.platform_search('invalidplatform', 'test', 0)
        
        mock_message.error.assert_called_with('Unknown platform: invalidplatform')
        mock_objreg.get.assert_not_called()
        

class TestCSearchCommand:
    """Test the csearch command."""
    
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    def test_csearch(self, mock_message, mock_objreg):
        """Test contextual search."""
        mock_browser = Mock()
        mock_objreg.get.return_value = mock_browser
        
        socmint.csearch('John Doe', 0, 'Microsoft', 'Seattle')
        
        # Should open multiple tabs (search engines + social searches)
        assert mock_browser.tabopen.call_count >= 8
        
        # Check that search query contains all terms
        calls = mock_browser.tabopen.call_args_list
        urls = [call[0][0].toString() for call in calls]
        assert any('John+Doe' in url for url in urls)
        

class TestSyncPrepCommand:
    """Test the syncprep command."""
    
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    def test_syncprep(self, mock_message, mock_objreg):
        """Test sync preparation."""
        mock_browser = Mock()
        mock_objreg.get.return_value = mock_browser
        
        socmint.syncprep(0)
        
        # Should open all sync URLs
        assert mock_browser.tabopen.call_count == len(socmint.SYNC_PREP_URLS)
        
        # Check that correct URLs are opened
        opened_urls = [call[0][0].toString() for call in mock_browser.tabopen.call_args_list]
        for url in socmint.SYNC_PREP_URLS.values():
            assert url in opened_urls
            

class TestRevPhoneCommand:
    """Test the revphone command."""
    
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    def test_revphone(self, mock_message, mock_objreg):
        """Test reverse phone lookup."""
        mock_browser = Mock()
        mock_objreg.get.return_value = mock_browser
        
        socmint.revphone('555-123-4567', 0)
        
        # Should open multiple tabs
        assert mock_browser.tabopen.call_count > 5
        
        # Check phone number is in URLs
        calls = mock_browser.tabopen.call_args_list
        urls = [call[0][0].toString() for call in calls]
        assert any('5551234567' in url or '555-123-4567' in url for url in urls)
        

class TestRevEmailCommand:
    """Test the revemail command."""
    
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    @patch('qutebrowser.components.socmint.pivot')
    def test_revemail_valid(self, mock_pivot, mock_message, mock_objreg):
        """Test reverse email lookup with valid email."""
        mock_browser = Mock()
        mock_objreg.get.return_value = mock_browser
        
        socmint.revemail('john.doe@example.com', 0)
        
        # Should open multiple tabs
        assert mock_browser.tabopen.call_count > 5
        
        # Should also call pivot with username
        mock_pivot.assert_called_once_with('john.doe', 0)
        
        # Check email is in URLs
        calls = mock_browser.tabopen.call_args_list
        urls = [call[0][0].toString() for call in calls]
        assert any('john.doe%40example.com' in url or 'john.doe@example.com' in url for url in urls)
        
    @patch('qutebrowser.components.socmint.objreg')
    @patch('qutebrowser.components.socmint.message')
    def test_revemail_invalid(self, mock_message, mock_objreg):
        """Test reverse email lookup with invalid email."""
        socmint.revemail('notanemail', 0)
        
        mock_message.error.assert_called_with('Invalid email format: notanemail')
        mock_objreg.get.assert_not_called()
        

class TestSOCMINTHelp:
    """Test the socmint-help command."""
    
    @patch('qutebrowser.components.socmint.message')
    def test_socmint_help(self, mock_message):
        """Test help command."""
        socmint.socmint_help()
        
        mock_message.info.assert_called_once()
        help_text = mock_message.info.call_args[0][0]
        
        # Verify help contains all commands
        assert ':pivot' in help_text
        assert ':platform-search' in help_text
        assert ':csearch' in help_text
        assert ':syncprep' in help_text
        assert ':revphone' in help_text
        assert ':revemail' in help_text


class TestPlatformURLs:
    """Test platform URL configurations."""
    
    def test_platform_urls_exist(self):
        """Test that platform URLs are defined."""
        assert len(socmint.PLATFORM_SEARCH_URLS) > 40
        assert 'twitter' in socmint.PLATFORM_SEARCH_URLS
        assert 'github' in socmint.PLATFORM_SEARCH_URLS
        assert 'linkedin' in socmint.PLATFORM_SEARCH_URLS
        
    def test_reverse_lookup_urls_exist(self):
        """Test that reverse lookup URLs are defined."""
        assert len(socmint.REVERSE_LOOKUP_URLS) > 15
        assert 'truecaller' in socmint.REVERSE_LOOKUP_URLS
        assert 'whitepages' in socmint.REVERSE_LOOKUP_URLS
        assert 'spokeo' in socmint.REVERSE_LOOKUP_URLS
        
    def test_sync_prep_urls_exist(self):
        """Test that sync prep URLs are defined."""
        assert len(socmint.SYNC_PREP_URLS) > 8
        assert 'google_contacts' in socmint.SYNC_PREP_URLS
        assert 'facebook_find' in socmint.SYNC_PREP_URLS
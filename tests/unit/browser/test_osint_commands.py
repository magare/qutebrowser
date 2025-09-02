# SPDX-FileCopyrightText: 2025 qutebrowser contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for OSINT commands."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from qutebrowser.qt.core import QUrl

from qutebrowser.browser import osint_commands
from qutebrowser.utils import objreg
from qutebrowser.api import cmdutils


class TestOSINTCommands:
    """Test OSINT command functionality."""

    @pytest.fixture
    def osint_cmd(self, qtbot, config_stub):
        """Create an OSINTCommands instance for testing."""
        tabbed_browser = Mock()
        tabbed_browser.tabopen = Mock()
        tabbed_browser.current_url = Mock(return_value=QUrl("https://example.com/page"))
        
        config_stub.val.osint.open_tabs_background = True
        config_stub.val.osint.max_tabs_per_search = 10
        config_stub.val.osint.trade_data_sources = ['importyeti', 'panjiva']
        config_stub.val.osint.vulnerability_databases = ['nvd', 'mitre']
        config_stub.val.osint.graph_api_endpoint = ""
        
        cmd = osint_commands.OSINTCommands(0, tabbed_browser)
        return cmd

    def test_cryptocurrency_forensics(self, osint_cmd):
        """Test cryptocurrency address lookup."""
        # Test Bitcoin address
        osint_cmd.cryptocurrency_forensics("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        assert osint_cmd._tabbed_browser.tabopen.called
        
        # Test Ethereum address
        osint_cmd.cryptocurrency_forensics("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1")
        assert osint_cmd._tabbed_browser.tabopen.call_count > 1

    def test_paste_site_search(self, osint_cmd):
        """Test paste site searching."""
        osint_cmd.paste_site_search("test keyword")
        
        # Should open multiple tabs with paste site searches
        assert osint_cmd._tabbed_browser.tabopen.called
        calls = osint_cmd._tabbed_browser.tabopen.call_args_list
        
        # Check that at least one call contains a Google dork
        google_dork_found = False
        for call in calls:
            url = call[0][0].toString()
            if "google.com/search" in url and "site:" in url:
                google_dork_found = True
                break
        assert google_dork_found

    def test_forum_community_search(self, osint_cmd):
        """Test forum and community searching."""
        # Test general search
        osint_cmd.forum_community_search("test query")
        assert osint_cmd._tabbed_browser.tabopen.called
        
        # Test platform-specific search
        osint_cmd._tabbed_browser.tabopen.reset_mock()
        osint_cmd.forum_community_search("test query", platform="telegram")
        
        calls = osint_cmd._tabbed_browser.tabopen.call_args_list
        telegram_found = False
        for call in calls:
            url = call[0][0].toString()
            if "t.me" in url or "telemetr" in url or "tgstat" in url:
                telegram_found = True
                break
        assert telegram_found

    def test_user_activity_analysis(self, osint_cmd):
        """Test user activity analysis across platforms."""
        osint_cmd.user_activity_analysis("testuser123")
        
        calls = osint_cmd._tabbed_browser.tabopen.call_args_list
        urls = [call[0][0].toString() for call in calls]
        
        # Check that various platforms are included
        assert any("twitter.com" in url for url in urls)
        assert any("github.com" in url for url in urls)
        assert any("linkedin.com" in url for url in urls)

    def test_identity_pivoting(self, osint_cmd):
        """Test identity pivoting across platforms."""
        osint_cmd.identity_pivoting("johndoe")
        
        calls = osint_cmd._tabbed_browser.tabopen.call_args_list
        urls = [call[0][0].toString() for call in calls]
        
        # Check that username enumeration services are included
        assert any("whatsmyname" in url.lower() for url in urls)
        assert any("namechk" in url.lower() for url in urls)

    @patch('urllib.request.urlopen')
    def test_export_to_graph_with_endpoint(self, mock_urlopen, osint_cmd, config_stub):
        """Test exporting entity to graph database."""
        config_stub.val.osint.graph_api_endpoint = "http://localhost:8080/api"
        
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response
        
        osint_cmd.export_to_graph("company", "ACME Corp")
        
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert request.full_url == "http://localhost:8080/api"
        
        # Check the data sent
        import json
        data = json.loads(request.data.decode('utf-8'))
        assert data['entity_type'] == "company"
        assert data['entity_value'] == "ACME Corp"

    def test_export_to_graph_no_endpoint(self, osint_cmd, config_stub):
        """Test export fails without configured endpoint."""
        config_stub.val.osint.graph_api_endpoint = ""
        
        with pytest.raises(cmdutils.CommandError) as exc_info:
            osint_cmd.export_to_graph("company", "ACME Corp")
        
        assert "No graph API endpoint configured" in str(exc_info.value)

    @patch('urllib.request.urlopen')
    def test_query_graph_database(self, mock_urlopen, osint_cmd, config_stub):
        """Test querying graph database."""
        config_stub.val.osint.graph_api_endpoint = "http://localhost:8080/api"
        
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"results": ["test1", "test2"]}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response
        
        osint_cmd.query_graph_database("MATCH (n) RETURN n")
        
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert "/query" in request.full_url
        
        import json
        data = json.loads(request.data.decode('utf-8'))
        assert data['query'] == "MATCH (n) RETURN n"
        
        # Check that a data URL was opened with results
        assert osint_cmd._tabbed_browser.tabopen.called

    def test_show_anomaly_alerts_empty(self, osint_cmd, monkeypatch):
        """Test showing alerts when none exist."""
        monkeypatch.setattr(objreg, 'get', lambda *args, **kwargs: [])
        
        osint_cmd.show_anomaly_alerts()
        # Should not crash and should not open tabs when no alerts
        assert not osint_cmd._tabbed_browser.tabopen.called

    def test_show_anomaly_alerts_with_data(self, osint_cmd, monkeypatch):
        """Test showing alerts with data."""
        test_alerts = [
            {
                'title': 'Test Alert',
                'description': 'Test description',
                'severity': 'high',
                'timestamp': '2025-01-01T12:00:00',
                'link': 'https://example.com'
            }
        ]
        monkeypatch.setattr(objreg, 'get', lambda *args, **kwargs: test_alerts)
        
        osint_cmd.show_anomaly_alerts()
        
        # Should open a data URL with the alerts
        assert osint_cmd._tabbed_browser.tabopen.called
        call_args = osint_cmd._tabbed_browser.tabopen.call_args
        url = call_args[0][0].toString()
        assert url.startswith("data:text/html")

    def test_clear_anomaly_alerts(self, osint_cmd, monkeypatch):
        """Test clearing alerts."""
        delete_called = False
        
        def mock_delete(*args, **kwargs):
            nonlocal delete_called
            delete_called = True
        
        monkeypatch.setattr(objreg, 'delete', mock_delete)
        
        osint_cmd.clear_anomaly_alerts()
        assert delete_called

    def test_trade_lookup(self, osint_cmd):
        """Test trade data lookup."""
        osint_cmd.trade_lookup("Apple Inc")
        
        calls = osint_cmd._tabbed_browser.tabopen.call_args_list
        urls = [call[0][0].toString() for call in calls]
        
        # Check that configured sources are included
        assert any("importyeti" in url for url in urls)
        assert any("panjiva" in url for url in urls)

    def test_sec_filings(self, osint_cmd):
        """Test SEC filings lookup."""
        osint_cmd.financial_regulatory_monitoring("AAPL")
        
        calls = osint_cmd._tabbed_browser.tabopen.call_args_list
        urls = [call[0][0].toString() for call in calls]
        
        # Check that SEC EDGAR is included
        assert any("sec.gov" in url for url in urls)
        assert any("AAPL" in url for url in urls)

    def test_sec_filings_with_form_type(self, osint_cmd):
        """Test SEC filings lookup with specific form type."""
        osint_cmd.financial_regulatory_monitoring("GOOGL", form_type="10-K")
        
        calls = osint_cmd._tabbed_browser.tabopen.call_args_list
        urls = [call[0][0].toString() for call in calls]
        
        # Check that form type is included in at least one URL
        assert any("10-K" in url for url in urls)

    def test_max_tabs_limit(self, osint_cmd, config_stub):
        """Test that max tabs limit is respected."""
        config_stub.val.osint.max_tabs_per_search = 3
        
        # Create a list of more URLs than the limit
        urls = [f"https://example{i}.com" for i in range(10)]
        osint_cmd._open_multiple_urls(urls)
        
        # Should only open 3 tabs
        assert osint_cmd._tabbed_browser.tabopen.call_count == 3

    def test_background_tabs_config(self, osint_cmd, config_stub):
        """Test background tab configuration."""
        config_stub.val.osint.open_tabs_background = False
        
        osint_cmd._open_url("https://example.com")
        
        call_args = osint_cmd._tabbed_browser.tabopen.call_args
        assert call_args[1]['background'] == False
        
        config_stub.val.osint.open_tabs_background = True
        osint_cmd._open_url("https://example.com")
        
        call_args = osint_cmd._tabbed_browser.tabopen.call_args
        assert call_args[1]['background'] == True
# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for infrastructure intelligence commands."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from qutebrowser.qt.core import QUrl
from qutebrowser.qt.network import QNetworkReply

from qutebrowser.components import infra_intelligence
from qutebrowser.api import cmdutils, apitypes


class TestInfraIntelligence:
    """Test infrastructure intelligence functions."""

    @pytest.fixture
    def mock_tab(self):
        """Create a mock tab for testing."""
        mock_tab = Mock(spec=apitypes.Tab)
        mock_tab.url = Mock(return_value=QUrl("https://example.com"))
        
        # Mock widget hierarchy
        mock_widget = Mock()
        mock_browser = Mock()
        mock_browser.load_url = Mock()
        mock_widget.parent = Mock(return_value=mock_browser)
        mock_tab._widget = mock_widget
        
        return mock_tab, mock_browser

    def test_get_current_url_valid(self, mock_tab):
        """Test getting current URL when valid."""
        tab, _ = mock_tab
        url = infra_intelligence._get_current_url(tab)
        assert url.host() == "example.com"

    def test_get_current_url_empty(self, mock_tab):
        """Test getting current URL when empty."""
        tab, _ = mock_tab
        tab.url = Mock(return_value=QUrl())
        # Should fall back to requested URL
        tab.url = Mock(side_effect=[QUrl(), QUrl("https://fallback.com")])
        url = infra_intelligence._get_current_url(tab)
        assert url.host() == "fallback.com"

    @patch('socket.gethostbyname')
    def test_resolve_domain_to_ip_success(self, mock_gethostbyname):
        """Test successful domain to IP resolution."""
        mock_gethostbyname.return_value = "93.184.216.34"
        
        ip = infra_intelligence._resolve_domain_to_ip("example.com")
        assert ip == "93.184.216.34"
        mock_gethostbyname.assert_called_once_with("example.com")

    @patch('socket.gethostbyname')
    def test_resolve_domain_to_ip_failure(self, mock_gethostbyname):
        """Test failed domain to IP resolution."""
        import socket
        mock_gethostbyname.side_effect = socket.gaierror("Name resolution failed")
        
        ip = infra_intelligence._resolve_domain_to_ip("invalid.domain")
        assert ip is None

    def test_display_in_buffer(self, mock_tab):
        """Test displaying content in a buffer."""
        tab, mock_browser = mock_tab
        
        infra_intelligence._display_in_buffer(tab, "Test Title", "<p>Test Content</p>")
        
        # Check that load_url was called with a data URL
        mock_browser.load_url.assert_called_once()
        call_args = mock_browser.load_url.call_args
        url = call_args[0][0]
        assert url.scheme() == "data"
        assert "Test Title" in url.toString()
        assert call_args[1]['newtab'] is True

    @patch.object(infra_intelligence, '_resolve_domain_to_ip')
    @patch.object(infra_intelligence, '_make_api_request')
    def test_asn_info_command(self, mock_api_request, mock_resolve, mock_tab):
        """Test ASN info command."""
        tab, _ = mock_tab
        mock_resolve.return_value = "93.184.216.34"
        
        infra_intelligence.asn_info(tab)
        
        mock_resolve.assert_called_once_with("example.com")
        mock_api_request.assert_called_once()
        
        # Check API URL contains the IP
        api_url = mock_api_request.call_args[0][0]
        assert "93.184.216.34" in api_url
        assert "stat.ripe.net" in api_url

    @patch.object(infra_intelligence, '_resolve_domain_to_ip')
    def test_asn_info_resolution_failure(self, mock_resolve, mock_tab):
        """Test ASN info when domain resolution fails."""
        tab, _ = mock_tab
        mock_resolve.return_value = None
        
        with patch.object(infra_intelligence, '_display_asn_error') as mock_error:
            infra_intelligence.asn_info(tab)
            mock_error.assert_called_once_with(tab, "example.com", "Failed to resolve domain to IP address")

    def test_asn_info_no_domain(self, mock_tab):
        """Test ASN info with no valid domain."""
        tab, _ = mock_tab
        tab.url = Mock(return_value=QUrl("about:blank"))
        
        with pytest.raises(cmdutils.CommandError, match="No valid domain"):
            infra_intelligence.asn_info(tab)

    @patch.object(infra_intelligence, '_resolve_domain_to_ip')
    @patch.object(infra_intelligence, '_make_api_request')
    def test_cable_route_command(self, mock_api_request, mock_resolve, mock_tab):
        """Test cable route command."""
        tab, _ = mock_tab
        mock_resolve.return_value = "93.184.216.34"
        
        infra_intelligence.cable_route(tab)
        
        mock_resolve.assert_called_once_with("example.com")
        mock_api_request.assert_called_once()
        
        # Check API URL for geolocation
        api_url = mock_api_request.call_args[0][0]
        assert "93.184.216.34" in api_url
        assert "ip-api.com" in api_url

    @patch.object(infra_intelligence, '_resolve_domain_to_ip')
    def test_shodan_lookup(self, mock_resolve, mock_tab):
        """Test Shodan lookup command."""
        tab, mock_browser = mock_tab
        mock_resolve.return_value = "93.184.216.34"
        
        infra_intelligence.shodan_lookup(tab)
        
        mock_resolve.assert_called_once_with("example.com")
        mock_browser.load_url.assert_called_once()
        
        # Check Shodan URL
        call_args = mock_browser.load_url.call_args
        url = call_args[0][0]
        assert url.toString() == "https://www.shodan.io/host/93.184.216.34"
        assert call_args[1]['newtab'] is True

    @patch.object(infra_intelligence, '_resolve_domain_to_ip')
    def test_censys_lookup(self, mock_resolve, mock_tab):
        """Test Censys lookup command."""
        tab, mock_browser = mock_tab
        mock_resolve.return_value = "93.184.216.34"
        
        infra_intelligence.censys_lookup(tab)
        
        mock_resolve.assert_called_once_with("example.com")
        mock_browser.load_url.assert_called_once()
        
        # Check Censys URL
        call_args = mock_browser.load_url.call_args
        url = call_args[0][0]
        assert url.toString() == "https://search.censys.io/hosts/93.184.216.34"
        assert call_args[1]['newtab'] is True

    def test_cert_pivot_non_https(self, mock_tab):
        """Test certificate pivot on non-HTTPS URL."""
        tab, _ = mock_tab
        tab.url = Mock(return_value=QUrl("http://example.com"))
        
        with pytest.raises(cmdutils.CommandError, match="Certificate pivoting requires HTTPS"):
            infra_intelligence.cert_pivot(tab)

    @patch.object(infra_intelligence, '_get_certificate_info')
    def test_cert_pivot_success(self, mock_cert_info, mock_tab):
        """Test successful certificate pivot."""
        tab, mock_browser = mock_tab
        mock_cert_info.return_value = {
            'common_name': '*.example.com',
            'san': ['example.com', 'www.example.com'],
            'issuer': 'Example CA',
            'not_before': '2023-01-01',
            'not_after': '2024-01-01'
        }
        
        infra_intelligence.cert_pivot(tab)
        
        mock_cert_info.assert_called_once_with("example.com")
        
        # Check that crt.sh was opened
        mock_browser.load_url.assert_called()
        call_args = mock_browser.load_url.call_args
        url = call_args[0][0]
        assert "crt.sh" in url.toString()

    def test_display_asn_info(self, mock_tab):
        """Test displaying ASN information."""
        tab, _ = mock_tab
        
        test_data = {
            'data': {
                'asns': [{
                    'asn': '15169',
                    'holder': 'GOOGLE'
                }],
                'resource': '142.250.0.0/15',
                'countries': [{'country': 'US'}]
            }
        }
        
        with patch.object(infra_intelligence, '_display_in_buffer') as mock_display:
            infra_intelligence._display_asn_info(tab, "example.com", "93.184.216.34", test_data)
            
            mock_display.assert_called_once()
            call_args = mock_display.call_args[0]
            assert call_args[0] == tab
            assert call_args[1] == "ASN Info: example.com"
            content = call_args[2]
            assert "AS15169" in content
            assert "GOOGLE" in content
            assert "142.250.0.0/15" in content
            assert "US" in content

    def test_display_cable_info(self, mock_tab):
        """Test displaying cable route information."""
        tab, _ = mock_tab
        
        geo_data = {
            'city': 'Mountain View',
            'country': 'United States',
            'lat': 37.4192,
            'lon': -122.0574
        }
        
        with patch.object(infra_intelligence, '_display_in_buffer') as mock_display:
            infra_intelligence._display_cable_info(tab, "example.com", "93.184.216.34", geo_data)
            
            mock_display.assert_called_once()
            call_args = mock_display.call_args[0]
            assert call_args[0] == tab
            assert call_args[1] == "Cable Route: example.com"
            content = call_args[2]
            assert "Mountain View" in content
            assert "United States" in content
            assert "37.4192" in content
            assert "-122.0574" in content

    def test_get_regional_cables(self):
        """Test getting regional submarine cables."""
        # Test known country
        cables = infra_intelligence._get_regional_cables("United States")
        assert "MAREA" in cables
        assert "Grace Hopper" in cables
        
        # Test unknown country
        cables = infra_intelligence._get_regional_cables("Unknown Country")
        assert "No specific cable data available" in cables

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_get_certificate_info_success(self, mock_ssl_context, mock_socket):
        """Test successful certificate information retrieval."""
        # Mock certificate data
        mock_cert = {
            'subject': ((('commonName', 'example.com'),),),
            'issuer': ((('organizationName', 'Example CA'),),),
            'subjectAltName': (('DNS', 'example.com'), ('DNS', 'www.example.com')),
            'notBefore': 'Jan  1 00:00:00 2023 GMT',
            'notAfter': 'Jan  1 00:00:00 2024 GMT'
        }
        
        # Setup mocks
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        mock_ssl_sock = MagicMock()
        mock_ssl_sock.getpeercert.return_value = mock_cert
        
        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssl_sock
        mock_ssl_context.return_value = mock_context
        
        cert_info = infra_intelligence._get_certificate_info("example.com")
        
        assert cert_info is not None
        assert cert_info['common_name'] == 'example.com'
        assert cert_info['issuer'] == 'Example CA'
        assert 'example.com' in cert_info['san']
        assert 'www.example.com' in cert_info['san']

    @patch('socket.create_connection')
    def test_get_certificate_info_failure(self, mock_socket):
        """Test failed certificate information retrieval."""
        import socket
        
        mock_socket.side_effect = socket.error("Connection failed")
        
        cert_info = infra_intelligence._get_certificate_info("example.com")
        assert cert_info is None

    def test_network_reply_success(self):
        """Test successful network reply handling."""
        mock_reply = Mock(spec=QNetworkReply)
        mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
        mock_reply.readAll.return_value = b'{"test": "data"}'
        mock_reply.deleteLater = Mock()
        
        mock_callback = Mock()
        infra_intelligence._pending_requests[mock_reply] = {'callback': mock_callback}
        
        infra_intelligence._on_network_reply(mock_reply)
        
        mock_callback.assert_called_once_with({"test": "data"})
        mock_reply.deleteLater.assert_called_once()

    def test_network_reply_error(self):
        """Test network reply error handling."""
        mock_reply = Mock(spec=QNetworkReply)
        mock_reply.error.return_value = QNetworkReply.NetworkError.HostNotFoundError
        mock_reply.errorString.return_value = "Host not found"
        mock_reply.deleteLater = Mock()
        
        mock_error_callback = Mock()
        infra_intelligence._pending_requests[mock_reply] = {
            'callback': Mock(),
            'error_callback': mock_error_callback
        }
        
        infra_intelligence._on_network_reply(mock_reply)
        
        mock_error_callback.assert_called_once_with("Host not found")
        mock_reply.deleteLater.assert_called_once()

    def test_get_tabbed_browser(self, mock_tab):
        """Test getting tabbed browser from tab."""
        tab, mock_browser = mock_tab
        result = infra_intelligence._get_tabbed_browser(tab)
        assert result == mock_browser

    def test_make_api_request(self):
        """Test making API request."""
        mock_callback = Mock()
        mock_error_callback = Mock()
        
        with patch.object(infra_intelligence, '_get_network_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_reply = Mock()
            mock_manager.get = Mock(return_value=mock_reply)
            mock_get_manager.return_value = mock_manager
            
            infra_intelligence._make_api_request(
                "https://test.api/endpoint",
                mock_callback,
                mock_error_callback
            )
            
            # Check that request was made
            mock_manager.get.assert_called_once()
            
            # Check that callbacks were registered
            assert mock_reply in infra_intelligence._pending_requests
            callbacks = infra_intelligence._pending_requests[mock_reply]
            assert callbacks['callback'] == mock_callback
            assert callbacks['error_callback'] == mock_error_callback

    def test_network_manager_singleton(self):
        """Test that network manager is a singleton."""
        # Clear any existing manager
        infra_intelligence._network_manager = None
        
        manager1 = infra_intelligence._get_network_manager()
        manager2 = infra_intelligence._get_network_manager()
        
        assert manager1 is manager2
        assert infra_intelligence._network_manager is not None
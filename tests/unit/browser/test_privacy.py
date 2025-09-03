# SPDX-FileCopyrightText: Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the privacy protection module."""

import time
import pytest
from unittest.mock import Mock, patch, MagicMock

from qutebrowser.qt.core import QUrl
from qutebrowser.qt.network import QNetworkRequest
from qutebrowser.browser import privacy


class TestTimestampObfuscator:
    """Tests for TimestampObfuscator class."""
    
    def test_disabled_by_default(self):
        """Test that timestamp obfuscation is disabled by default."""
        obfuscator = privacy.TimestampObfuscator()
        assert obfuscator._enabled is False
        assert obfuscator.get_random_delay() == 0
        
    def test_enable(self):
        """Test enabling timestamp obfuscation."""
        obfuscator = privacy.TimestampObfuscator()
        obfuscator.enable(True)
        assert obfuscator._enabled is True
        
    def test_random_delay_when_enabled(self):
        """Test that random delay is generated when enabled."""
        obfuscator = privacy.TimestampObfuscator()
        obfuscator.enable(True)
        delay = obfuscator.get_random_delay()
        assert 50 <= delay <= 300
        
    def test_should_delay_request(self):
        """Test request delay logic."""
        obfuscator = privacy.TimestampObfuscator()
        obfuscator.enable(True)
        
        # Should not delay critical resources
        should_delay, delay = obfuscator.should_delay_request("http://example.com/style.css")
        assert should_delay is False
        assert delay == 0
        
        # Should delay regular requests
        should_delay, delay = obfuscator.should_delay_request("http://example.com/page.html")
        assert should_delay is True
        assert 50 <= delay <= 300


class TestUserAgentRotator:
    """Tests for UserAgentRotator class."""
    
    def test_disabled_by_default(self):
        """Test that user agent rotation is disabled by default."""
        rotator = privacy.UserAgentRotator()
        assert rotator._rotation_enabled is False
        assert rotator.get_user_agent() == ''
        
    def test_enable_rotation(self):
        """Test enabling user agent rotation."""
        rotator = privacy.UserAgentRotator()
        rotator.enable_rotation(True)
        assert rotator._rotation_enabled is True
        
    def test_set_profile(self):
        """Test setting user agent profile."""
        rotator = privacy.UserAgentRotator()
        rotator.set_profile('windows_firefox')
        assert rotator._current_profile == 'windows_firefox'
        
    def test_get_user_agent_with_rotation(self):
        """Test getting user agent with rotation enabled."""
        rotator = privacy.UserAgentRotator()
        rotator.enable_rotation(True)
        rotator.set_profile('windows_chrome')
        
        agent = rotator.get_user_agent()
        assert agent in privacy.UserAgentRotator.USER_AGENTS['windows_chrome']
        
    def test_per_domain_agents(self):
        """Test per-domain user agent persistence."""
        rotator = privacy.UserAgentRotator()
        rotator.enable_rotation(True)
        
        agent1 = rotator.get_user_agent('example.com')
        agent2 = rotator.get_user_agent('example.com')
        assert agent1 == agent2  # Same domain should get same agent
        
    def test_rotation_after_interval(self):
        """Test agent rotation after interval."""
        rotator = privacy.UserAgentRotator()
        rotator.enable_rotation(True)
        rotator._rotation_interval = 0  # Immediate rotation
        
        # Store initial agent
        rotator.get_user_agent('example.com')
        initial_count = len(rotator._per_domain_agents)
        assert initial_count > 0
        
        # Force time to pass
        rotator._last_rotation = time.time() - 1
        
        # Get agent again, should trigger rotation
        rotator.get_user_agent('test.com')
        
        # After rotation, per-domain agents should be cleared
        assert len(rotator._per_domain_agents) == 1  # Only the new domain


class TestHeaderSanitizer:
    """Tests for HeaderSanitizer class."""
    
    def test_disabled_by_default(self):
        """Test that header sanitization is disabled by default."""
        sanitizer = privacy.HeaderSanitizer()
        assert sanitizer._enabled is False
        
    def test_sanitize_request_when_disabled(self):
        """Test that request is unchanged when disabled."""
        sanitizer = privacy.HeaderSanitizer()
        request = Mock(spec=QNetworkRequest)
        
        result = sanitizer.sanitize_request(request)
        assert result == request
        request.setRawHeader.assert_not_called()
        
    def test_sanitize_request_removes_tracking_headers(self):
        """Test that tracking headers are removed."""
        sanitizer = privacy.HeaderSanitizer()
        sanitizer.enable(True)
        
        request = Mock(spec=QNetworkRequest)
        request.rawHeader.return_value = b''
        
        sanitizer.sanitize_request(request)
        
        # Check that tracking headers are removed
        for header in privacy.HeaderSanitizer.TRACKING_HEADERS:
            request.setRawHeader.assert_any_call(header.encode(), b'')
            
    def test_sanitize_referrer(self):
        """Test referrer sanitization."""
        sanitizer = privacy.HeaderSanitizer()
        sanitizer.enable(True)
        sanitizer._sanitize_referrer = True
        
        request = Mock(spec=QNetworkRequest)
        # Mock rawHeader to return a Mock with data() method
        mock_header = Mock()
        mock_header.data.return_value = b'http://example.com/path/to/page'
        request.rawHeader.return_value = mock_header
        
        with patch('qutebrowser.browser.privacy.QUrl') as mock_qurl:
            mock_url = Mock()
            mock_url.scheme.return_value = 'http'
            mock_url.host.return_value = 'example.com'
            mock_url.port.return_value = -1
            mock_qurl.return_value = mock_url
            
            sanitizer.sanitize_request(request)
            request.setRawHeader.assert_any_call(b'Referer', b'http://example.com')


class TestFingerprintProtection:
    """Tests for FingerprintProtection class."""
    
    def test_disabled_by_default(self):
        """Test that fingerprint protection is disabled by default."""
        fp = privacy.FingerprintProtection()
        assert fp._canvas_noise_enabled is False
        assert fp._webgl_protection_enabled is False
        assert fp._font_enumeration_blocked is False
        assert fp._screen_resolution_spoofed is False
        
    def test_enable_canvas_protection(self):
        """Test enabling canvas protection."""
        fp = privacy.FingerprintProtection()
        fp.enable_canvas_protection(True)
        assert fp._canvas_noise_enabled is True
        
    def test_enable_webgl_protection(self):
        """Test enabling WebGL protection."""
        fp = privacy.FingerprintProtection()
        fp.enable_webgl_protection(True)
        assert fp._webgl_protection_enabled is True
        
    def test_enable_font_blocking(self):
        """Test enabling font blocking."""
        fp = privacy.FingerprintProtection()
        fp.enable_font_blocking(True)
        assert fp._font_enumeration_blocked is True
        
    def test_enable_resolution_spoofing(self):
        """Test enabling resolution spoofing."""
        fp = privacy.FingerprintProtection()
        fp.enable_resolution_spoofing(True, (2560, 1440))
        assert fp._screen_resolution_spoofed is True
        assert fp._spoofed_resolution == (2560, 1440)
        
    def test_get_protection_script_empty_when_disabled(self):
        """Test that no script is generated when all protections are disabled."""
        fp = privacy.FingerprintProtection()
        script = fp.get_protection_script()
        assert script == ''
        
    def test_get_protection_script_with_canvas(self):
        """Test script generation with canvas protection."""
        fp = privacy.FingerprintProtection()
        fp.enable_canvas_protection(True)
        script = fp.get_protection_script()
        assert 'HTMLCanvasElement.prototype.toDataURL' in script
        assert 'addNoise' in script
        
    def test_get_protection_script_with_webgl(self):
        """Test script generation with WebGL protection."""
        fp = privacy.FingerprintProtection()
        fp.enable_webgl_protection(True)
        script = fp.get_protection_script()
        assert 'WebGLRenderingContext.prototype.getParameter' in script
        assert 'Intel Inc.' in script
        
    def test_get_protection_script_with_fonts(self):
        """Test script generation with font blocking."""
        fp = privacy.FingerprintProtection()
        fp.enable_font_blocking(True)
        script = fp.get_protection_script()
        assert 'offsetWidth' in script
        assert 'fontFamily' in script
        
    def test_get_protection_script_with_resolution(self):
        """Test script generation with resolution spoofing."""
        fp = privacy.FingerprintProtection()
        fp.enable_resolution_spoofing(True)
        script = fp.get_protection_script()
        assert 'window.screen' in script
        assert '1920' in script  # Default resolution


class TestCookieManager:
    """Tests for CookieManager class."""
    
    def test_disabled_by_default(self):
        """Test that cookie features are disabled by default."""
        manager = privacy.CookieManager()
        assert manager._compartmentalized is False
        assert manager._auto_delete_enabled is False
        assert manager._first_party_isolation is False
        
    def test_store_and_retrieve_cookie(self):
        """Test storing and retrieving cookies."""
        manager = privacy.CookieManager()
        manager.store_cookie('example.com', 'session', 'abc123')
        
        cookies = manager.get_cookies('example.com')
        assert cookies == {'session': 'abc123'}
        
    def test_first_party_isolation(self):
        """Test first-party isolation."""
        manager = privacy.CookieManager()
        manager.enable_first_party_isolation(True)
        
        manager.store_cookie('tracker.com', 'id', '123', first_party='site1.com')
        manager.store_cookie('tracker.com', 'id', '456', first_party='site2.com')
        
        cookies1 = manager.get_cookies('tracker.com', first_party='site1.com')
        cookies2 = manager.get_cookies('tracker.com', first_party='site2.com')
        
        assert cookies1 == {'id': '123'}
        assert cookies2 == {'id': '456'}
        
    def test_delete_cookies_for_domain(self):
        """Test deleting cookies for a specific domain."""
        manager = privacy.CookieManager()
        manager.store_cookie('example.com', 'session', 'abc123')
        manager.store_cookie('other.com', 'session', 'xyz789')
        
        manager.delete_cookies_for_domain('example.com')
        
        assert manager.get_cookies('example.com') == {}
        assert manager.get_cookies('other.com') == {'session': 'xyz789'}
        
    def test_clear_all_cookies(self):
        """Test clearing all cookies."""
        manager = privacy.CookieManager()
        manager.store_cookie('example.com', 'session', 'abc123')
        manager.store_cookie('other.com', 'session', 'xyz789')
        
        manager.clear_all_cookies()
        
        assert manager.get_cookies('example.com') == {}
        assert manager.get_cookies('other.com') == {}


class TestNetworkSecurity:
    """Tests for NetworkSecurity class."""
    
    def test_disabled_by_default(self):
        """Test that network security features are disabled by default."""
        ns = privacy.NetworkSecurity()
        assert ns._doh_enabled is False
        assert ns._https_upgrade_enabled is False
        assert ns._request_pattern_analysis is False
        
    def test_enable_doh(self):
        """Test enabling DNS-over-HTTPS."""
        ns = privacy.NetworkSecurity()
        ns.enable_doh(True, 'cloudflare')
        assert ns._doh_enabled is True
        assert ns._doh_provider == 'cloudflare'
        
    def test_should_upgrade_to_https(self):
        """Test HTTPS upgrade logic."""
        ns = privacy.NetworkSecurity()
        ns.enable_https_upgrade(True)
        
        url = Mock(spec=QUrl)
        url.scheme.return_value = 'http'
        assert ns.should_upgrade_to_https(url) is True
        
        url.scheme.return_value = 'https'
        assert ns.should_upgrade_to_https(url) is False
        
    def test_analyze_request_pattern(self):
        """Test request pattern analysis."""
        ns = privacy.NetworkSecurity()
        ns.enable_pattern_analysis(True)
        
        # Simulate many requests to same domain
        for i in range(51):
            with patch('qutebrowser.qt.core.QUrl') as mock_qurl:
                mock_qurl.return_value.host.return_value = 'suspicious.com'
                warning = ns.analyze_request_pattern(f'http://suspicious.com/{i}', time.time())
                
        assert warning is not None
        assert 'Suspicious activity detected' in warning
        assert '51 requests' in warning


class TestContentSecurity:
    """Tests for ContentSecurity class."""
    
    def test_disabled_by_default(self):
        """Test that content security features are disabled by default."""
        cs = privacy.ContentSecurity()
        assert cs._js_sandbox_enhanced is False
        assert cs._webrtc_leak_prevention is False
        assert cs._referrer_policy == 'strict-origin-when-cross-origin'
        
    def test_set_referrer_policy(self):
        """Test setting referrer policy."""
        cs = privacy.ContentSecurity()
        cs.set_referrer_policy('no-referrer')
        assert cs._referrer_policy == 'no-referrer'
        
        # Invalid policy should not change
        cs.set_referrer_policy('invalid-policy')
        assert cs._referrer_policy == 'no-referrer'
        
    def test_get_csp_header(self):
        """Test CSP header generation."""
        cs = privacy.ContentSecurity()
        assert cs.get_csp_header() == ''
        
        cs.enable_js_sandbox(True)
        csp = cs.get_csp_header()
        assert "script-src 'self'" in csp
        assert "object-src 'none'" in csp
        
    def test_get_webrtc_protection_script(self):
        """Test WebRTC protection script generation."""
        cs = privacy.ContentSecurity()
        assert cs.get_webrtc_protection_script() == ''
        
        cs.enable_webrtc_protection(True)
        script = cs.get_webrtc_protection_script()
        assert 'RTCPeerConnection' in script
        assert 'WebRTC blocked for privacy' in script


class TestPrivacyManager:
    """Tests for PrivacyManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create a PrivacyManager instance."""
        with patch('qutebrowser.browser.privacy.config'):
            return privacy.PrivacyManager()
            
    def test_disabled_by_default(self, manager):
        """Test that privacy manager is disabled by default."""
        assert manager._enabled is False
        
    def test_enable(self, manager):
        """Test enabling privacy manager."""
        with patch('qutebrowser.browser.privacy.config.val.privacy') as mock_config:
            # Set all config values to True
            mock_config.timestamp_obfuscation = True
            mock_config.user_agent_rotation = True
            mock_config.header_sanitization = True
            mock_config.canvas_protection = True
            mock_config.webgl_protection = True
            mock_config.font_blocking = True
            mock_config.resolution_spoofing = True
            mock_config.cookie_compartmentalization = True
            mock_config.cookie_auto_delete = True
            mock_config.first_party_isolation = True
            mock_config.dns_over_https = True
            mock_config.https_upgrade = True
            mock_config.request_pattern_analysis = True
            mock_config.js_sandbox_enhanced = True
            mock_config.webrtc_protection = True
            
            manager.enable(True)
            assert manager._enabled is True
            assert manager.timestamp_obfuscator._enabled is True
            assert manager.user_agent_rotator._rotation_enabled is True
            
    def test_process_request(self, manager):
        """Test processing a network request."""
        manager.enable(True)
        manager.header_sanitizer.enable(True)
        manager.user_agent_rotator.enable_rotation(True)
        
        request = Mock(spec=QNetworkRequest)
        url = Mock(spec=QUrl)
        url.host.return_value = 'example.com'
        url.toString.return_value = 'http://example.com'
        request.url.return_value = url
        request.rawHeader.return_value = b''
        
        processed = manager.process_request(request)
        assert processed == request
        
    def test_get_injection_script(self, manager):
        """Test getting injection script."""
        script = manager.get_injection_script()
        assert script == ''  # Disabled by default
        
        manager.enable(True)
        manager.fingerprint_protection.enable_canvas_protection(True)
        
        script = manager.get_injection_script()
        assert 'HTMLCanvasElement' in script
        
    def test_get_status(self, manager):
        """Test getting privacy status."""
        status = manager.get_status()
        assert status['enabled'] is False
        assert all(not v for k, v in status.items() if k != 'enabled')
        
        manager.enable(True)
        manager.timestamp_obfuscator.enable(True)
        
        status = manager.get_status()
        assert status['enabled'] is True
        assert status['timestamp_obfuscation'] is True


def test_init():
    """Test privacy manager initialization."""
    with patch('qutebrowser.browser.privacy.objreg.register') as mock_register:
        manager = privacy.init()
        assert isinstance(manager, privacy.PrivacyManager)
        mock_register.assert_called_once_with('privacy-manager', manager)
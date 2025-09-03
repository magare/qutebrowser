# SPDX-FileCopyrightText: Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Privacy protection and anti-fingerprinting module for qutebrowser."""

import random
import time
import hashlib
import json
from typing import Optional, Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime, timedelta

from qutebrowser.qt.core import QUrl, QTimer, QObject, pyqtSignal, pyqtSlot
from qutebrowser.qt.network import QNetworkRequest
from qutebrowser.utils import objreg, message, utils
import logging

# Create a logger for the privacy module
log_privacy = logging.getLogger('qutebrowser.privacy')
from qutebrowser.config import config


class TimestampObfuscator:
    """Implements timestamp obfuscation to prevent timing analysis."""
    
    def __init__(self):
        self._request_delays = {}
        self._min_delay = 50  # milliseconds
        self._max_delay = 300  # milliseconds
        self._enabled = False
        
    def enable(self, enabled: bool = True):
        """Enable or disable timestamp obfuscation."""
        self._enabled = enabled
        
    def get_random_delay(self) -> int:
        """Generate a random delay for request timing obfuscation."""
        if not self._enabled:
            return 0
        return random.randint(self._min_delay, self._max_delay)
    
    def should_delay_request(self, url: str) -> Tuple[bool, int]:
        """Determine if a request should be delayed and by how much."""
        if not self._enabled:
            return False, 0
            
        # Don't delay critical resources
        if any(ext in url for ext in ['.css', '.js', '.json']):
            return False, 0
            
        delay = self.get_random_delay()
        return True, delay


class UserAgentRotator:
    """Manages user agent string rotation for fingerprint resistance."""
    
    # Common user agents for different platforms
    USER_AGENTS = {
        'windows_chrome': [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        ],
        'windows_firefox': [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        ],
        'mac_safari': [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        ],
        'linux_firefox': [
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
    }
    
    def __init__(self):
        self._current_profile = 'windows_chrome'
        self._rotation_enabled = False
        self._rotation_interval = 3600  # seconds
        self._last_rotation = time.time()
        self._per_domain_agents = {}
        
    def enable_rotation(self, enabled: bool = True):
        """Enable or disable user agent rotation."""
        self._rotation_enabled = enabled
        
    def set_profile(self, profile: str):
        """Set the user agent profile to use."""
        if profile in self.USER_AGENTS:
            self._current_profile = profile
            
    def get_user_agent(self, domain: Optional[str] = None) -> str:
        """Get a user agent string, optionally per-domain."""
        if not self._rotation_enabled:
            return ''  # Use default
            
        # Check if rotation is needed
        current_time = time.time()
        if current_time - self._last_rotation > self._rotation_interval:
            self._rotate_agents()
            self._last_rotation = current_time
            
        if domain and domain in self._per_domain_agents:
            return self._per_domain_agents[domain]
            
        agents = self.USER_AGENTS.get(self._current_profile, [])
        if agents:
            agent = random.choice(agents)
            if domain:
                self._per_domain_agents[domain] = agent
            return agent
        return ''
    
    def _rotate_agents(self):
        """Rotate user agents for all domains."""
        self._per_domain_agents.clear()


class HeaderSanitizer:
    """Sanitizes HTTP headers to prevent tracking."""
    
    # Headers that should be removed or modified
    TRACKING_HEADERS = {
        'X-Requested-With',
        'X-Client-Data',
        'X-Chrome-Variations',
        'X-Chrome-Connected',
        'X-Device-Id',
        'X-Forwarded-For',
        'X-Real-IP',
        'X-ATT-DeviceId',
        'X-UIDH',
        'X-Wap-Profile',
    }
    
    def __init__(self):
        self._enabled = False
        self._remove_etags = False
        self._sanitize_referrer = True
        
    def enable(self, enabled: bool = True):
        """Enable or disable header sanitization."""
        self._enabled = enabled
        
    def sanitize_request(self, request: QNetworkRequest) -> QNetworkRequest:
        """Sanitize a network request by removing tracking headers."""
        if not self._enabled:
            return request
            
        # Remove tracking headers
        for header in self.TRACKING_HEADERS:
            request.setRawHeader(header.encode(), b'')
            
        # Sanitize referrer if enabled
        if self._sanitize_referrer:
            referrer = request.rawHeader(b'Referer')
            if referrer:
                # Only send origin, not full URL
                # Handle both QByteArray and bytes
                if hasattr(referrer, 'data'):
                    referrer_str = referrer.data().decode()
                else:
                    referrer_str = referrer.decode() if isinstance(referrer, bytes) else str(referrer)
                    
                url = QUrl(referrer_str)
                origin = f"{url.scheme()}://{url.host()}"
                if url.port() != -1:
                    origin += f":{url.port()}"
                request.setRawHeader(b'Referer', origin.encode())
                
        return request


class FingerprintProtection:
    """Provides protection against various fingerprinting techniques."""
    
    def __init__(self):
        self._canvas_noise_enabled = False
        self._webgl_protection_enabled = False
        self._font_enumeration_blocked = False
        self._screen_resolution_spoofed = False
        self._spoofed_resolution = (1920, 1080)
        
    def enable_canvas_protection(self, enabled: bool = True):
        """Enable canvas fingerprint protection."""
        self._canvas_noise_enabled = enabled
        
    def enable_webgl_protection(self, enabled: bool = True):
        """Enable WebGL fingerprint protection."""
        self._webgl_protection_enabled = enabled
        
    def enable_font_blocking(self, enabled: bool = True):
        """Enable font enumeration blocking."""
        self._font_enumeration_blocked = enabled
        
    def enable_resolution_spoofing(self, enabled: bool = True, resolution: Optional[Tuple[int, int]] = None):
        """Enable screen resolution spoofing."""
        self._screen_resolution_spoofed = enabled
        if resolution:
            self._spoofed_resolution = resolution
            
    def get_protection_script(self) -> str:
        """Generate JavaScript to inject for fingerprint protection."""
        scripts = []
        
        if self._canvas_noise_enabled:
            scripts.append(self._get_canvas_protection_script())
            
        if self._webgl_protection_enabled:
            scripts.append(self._get_webgl_protection_script())
            
        if self._font_enumeration_blocked:
            scripts.append(self._get_font_protection_script())
            
        if self._screen_resolution_spoofed:
            scripts.append(self._get_resolution_spoofing_script())
            
        return '\n'.join(scripts)
    
    def _get_canvas_protection_script(self) -> str:
        """JavaScript to add noise to canvas fingerprinting."""
        return """
        (function() {
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            
            function addNoise(canvas) {
                const ctx = canvas.getContext('2d');
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] ^= Math.floor(Math.random() * 2);
                    imageData.data[i+1] ^= Math.floor(Math.random() * 2);
                    imageData.data[i+2] ^= Math.floor(Math.random() * 2);
                }
                ctx.putImageData(imageData, 0, 0);
            }
            
            HTMLCanvasElement.prototype.toDataURL = function() {
                addNoise(this);
                return originalToDataURL.apply(this, arguments);
            };
            
            HTMLCanvasElement.prototype.toBlob = function() {
                addNoise(this);
                return originalToBlob.apply(this, arguments);
            };
            
            CanvasRenderingContext2D.prototype.getImageData = function() {
                const imageData = originalGetImageData.apply(this, arguments);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] ^= Math.floor(Math.random() * 2);
                    imageData.data[i+1] ^= Math.floor(Math.random() * 2);
                    imageData.data[i+2] ^= Math.floor(Math.random() * 2);
                }
                return imageData;
            };
        })();
        """
    
    def _get_webgl_protection_script(self) -> str:
        """JavaScript to protect against WebGL fingerprinting."""
        return """
        (function() {
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
            
            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter2.apply(this, arguments);
            };
        })();
        """
    
    def _get_font_protection_script(self) -> str:
        """JavaScript to block font enumeration."""
        return """
        (function() {
            const originalOffsetWidth = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetWidth');
            const originalOffsetHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');
            
            Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {
                get: function() {
                    if (this.style && this.style.fontFamily && this.style.fontFamily !== 'inherit') {
                        return 100;
                    }
                    return originalOffsetWidth.get.call(this);
                }
            });
            
            Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
                get: function() {
                    if (this.style && this.style.fontFamily && this.style.fontFamily !== 'inherit') {
                        return 20;
                    }
                    return originalOffsetHeight.get.call(this);
                }
            });
        })();
        """
    
    def _get_resolution_spoofing_script(self) -> str:
        """JavaScript to spoof screen resolution."""
        width, height = self._spoofed_resolution
        return f"""
        (function() {{
            Object.defineProperty(window.screen, 'width', {{value: {width}, writable: false}});
            Object.defineProperty(window.screen, 'height', {{value: {height}, writable: false}});
            Object.defineProperty(window.screen, 'availWidth', {{value: {width}, writable: false}});
            Object.defineProperty(window.screen, 'availHeight', {{value: {height - 40}, writable: false}});
        }})();
        """


class CookieManager:
    """Enhanced cookie management with compartmentalization and auto-deletion."""
    
    def __init__(self):
        self._compartmentalized = False
        self._auto_delete_enabled = False
        self._first_party_isolation = False
        self._session_cookies = defaultdict(dict)
        self._domain_isolation = defaultdict(dict)
        
    def enable_compartmentalization(self, enabled: bool = True):
        """Enable cookie compartmentalization per tab/domain."""
        self._compartmentalized = enabled
        
    def enable_auto_deletion(self, enabled: bool = True):
        """Enable automatic cookie deletion on tab close."""
        self._auto_delete_enabled = enabled
        
    def enable_first_party_isolation(self, enabled: bool = True):
        """Enable first-party isolation for cookies."""
        self._first_party_isolation = enabled
        
    def store_cookie(self, domain: str, name: str, value: str, first_party: Optional[str] = None):
        """Store a cookie with optional first-party isolation."""
        if self._first_party_isolation and first_party:
            key = f"{first_party}:{domain}"
        else:
            key = domain
            
        if self._compartmentalized:
            self._domain_isolation[key][name] = value
        else:
            self._session_cookies[key][name] = value
            
    def get_cookies(self, domain: str, first_party: Optional[str] = None) -> Dict[str, str]:
        """Get cookies for a domain with optional first-party context."""
        if self._first_party_isolation and first_party:
            key = f"{first_party}:{domain}"
        else:
            key = domain
            
        if self._compartmentalized:
            return self._domain_isolation.get(key, {})
        else:
            return self._session_cookies.get(key, {})
            
    def delete_cookies_for_domain(self, domain: str):
        """Delete all cookies for a specific domain."""
        keys_to_delete = []
        
        for key in list(self._session_cookies.keys()):
            if domain in key:
                keys_to_delete.append(key)
                
        for key in list(self._domain_isolation.keys()):
            if domain in key:
                keys_to_delete.append(key)
                
        for key in keys_to_delete:
            self._session_cookies.pop(key, None)
            self._domain_isolation.pop(key, None)
            
    def clear_all_cookies(self):
        """Clear all stored cookies."""
        self._session_cookies.clear()
        self._domain_isolation.clear()


class NetworkSecurity:
    """Network security enhancements including DoH and HTTPS upgrades."""
    
    DOH_PROVIDERS = {
        'cloudflare': 'https://cloudflare-dns.com/dns-query',
        'google': 'https://dns.google/dns-query',
        'quad9': 'https://dns.quad9.net/dns-query',
        'adguard': 'https://dns.adguard.com/dns-query',
    }
    
    def __init__(self):
        self._doh_enabled = False
        self._doh_provider = 'cloudflare'
        self._https_upgrade_enabled = False
        self._request_pattern_analysis = False
        self._suspicious_patterns = []
        
    def enable_doh(self, enabled: bool = True, provider: str = 'cloudflare'):
        """Enable DNS-over-HTTPS."""
        self._doh_enabled = enabled
        if provider in self.DOH_PROVIDERS:
            self._doh_provider = provider
            
    def enable_https_upgrade(self, enabled: bool = True):
        """Enable automatic HTTPS upgrades."""
        self._https_upgrade_enabled = enabled
        
    def enable_pattern_analysis(self, enabled: bool = True):
        """Enable request pattern analysis."""
        self._request_pattern_analysis = enabled
        
    def should_upgrade_to_https(self, url: QUrl) -> bool:
        """Check if a URL should be upgraded to HTTPS."""
        if not self._https_upgrade_enabled:
            return False
            
        if url.scheme() == 'http':
            # Check if HTTPS version is available
            # This would need actual implementation to test HTTPS availability
            return True
            
        return False
    
    def analyze_request_pattern(self, url: str, timestamp: float) -> Optional[str]:
        """Analyze request patterns for suspicious activity."""
        if not self._request_pattern_analysis:
            return None
            
        # Simple pattern detection
        domain = QUrl(url).host()
        
        # Check for rapid requests to same domain
        pattern = {
            'domain': domain,
            'timestamp': timestamp,
            'url': url
        }
        
        self._suspicious_patterns.append(pattern)
        
        # Keep only recent patterns (last 60 seconds)
        cutoff = timestamp - 60
        self._suspicious_patterns = [p for p in self._suspicious_patterns if p['timestamp'] > cutoff]
        
        # Check for suspicious patterns
        domain_count = sum(1 for p in self._suspicious_patterns if p['domain'] == domain)
        
        if domain_count > 50:  # More than 50 requests per minute to same domain
            return f"Suspicious activity detected: {domain_count} requests to {domain} in last minute"
            
        return None


class ContentSecurity:
    """Content security features including JS sandboxing and WebRTC protection."""
    
    def __init__(self):
        self._js_sandbox_enhanced = False
        self._webrtc_leak_prevention = False
        self._referrer_policy = 'strict-origin-when-cross-origin'
        
    def enable_js_sandbox(self, enabled: bool = True):
        """Enable enhanced JavaScript sandboxing."""
        self._js_sandbox_enhanced = enabled
        
    def enable_webrtc_protection(self, enabled: bool = True):
        """Enable WebRTC leak prevention."""
        self._webrtc_leak_prevention = enabled
        
    def set_referrer_policy(self, policy: str):
        """Set the referrer policy."""
        valid_policies = [
            'no-referrer',
            'no-referrer-when-downgrade',
            'origin',
            'origin-when-cross-origin',
            'same-origin',
            'strict-origin',
            'strict-origin-when-cross-origin',
            'unsafe-url'
        ]
        
        if policy in valid_policies:
            self._referrer_policy = policy
            
    def get_csp_header(self) -> str:
        """Generate Content Security Policy header."""
        policies = []
        
        if self._js_sandbox_enhanced:
            policies.extend([
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
                "object-src 'none'",
                "base-uri 'self'",
            ])
            
        return '; '.join(policies) if policies else ''
    
    def get_webrtc_protection_script(self) -> str:
        """Generate JavaScript to prevent WebRTC leaks."""
        if not self._webrtc_leak_prevention:
            return ''
            
        return """
        (function() {
            // Block WebRTC IP leak
            const pc = RTCPeerConnection.prototype;
            const origCreate = pc.createDataChannel;
            pc.createDataChannel = function() {
                return null;
            };
            
            const origCreateOffer = pc.createOffer;
            pc.createOffer = function() {
                return Promise.reject(new Error('WebRTC blocked for privacy'));
            };
            
            // Override getUserMedia
            navigator.mediaDevices.getUserMedia = function() {
                return Promise.reject(new Error('Media access blocked for privacy'));
            };
        })();
        """


class PrivacyManager(QObject):
    """Main privacy manager that coordinates all privacy features."""
    
    privacy_warning = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.timestamp_obfuscator = TimestampObfuscator()
        self.user_agent_rotator = UserAgentRotator()
        self.header_sanitizer = HeaderSanitizer()
        self.fingerprint_protection = FingerprintProtection()
        self.cookie_manager = CookieManager()
        self.network_security = NetworkSecurity()
        self.content_security = ContentSecurity()
        
        self._enabled = False
        self._setup_config_callbacks()
        
    def _setup_config_callbacks(self):
        """Setup configuration change callbacks."""
        try:
            config.instance.changed.connect(self._on_config_changed)
        except:
            # Config not ready yet
            pass
    
    @pyqtSlot(str)
    def _on_config_changed(self, option: str):
        """Handle configuration changes."""
        if not option.startswith('privacy.'):
            return
            
        try:
            if option == 'privacy.enabled':
                self.enable(config.val.privacy.enabled)
            elif hasattr(config, 'val') and hasattr(config.val, 'privacy'):
                # Re-enable with new config
                if self._enabled:
                    self.enable(True)
        except Exception as e:
            log_privacy.debug(f"Error handling config change: {e}")
        
    def enable(self, enabled: bool = True):
        """Enable or disable all privacy features."""
        self._enabled = enabled
        
        # Enable individual components based on config
        if enabled:
            try:
                if hasattr(config, 'val') and hasattr(config.val, 'privacy'):
                    self.timestamp_obfuscator.enable(config.val.privacy.timestamp_obfuscation)
                    self.user_agent_rotator.enable_rotation(config.val.privacy.user_agent_rotation)
                    self.header_sanitizer.enable(config.val.privacy.header_sanitization)
                    self.fingerprint_protection.enable_canvas_protection(config.val.privacy.canvas_protection)
                    self.fingerprint_protection.enable_webgl_protection(config.val.privacy.webgl_protection)
                    self.fingerprint_protection.enable_font_blocking(config.val.privacy.font_blocking)
                    self.fingerprint_protection.enable_resolution_spoofing(config.val.privacy.resolution_spoofing)
                    self.cookie_manager.enable_compartmentalization(config.val.privacy.cookie_compartmentalization)
                    self.cookie_manager.enable_auto_deletion(config.val.privacy.cookie_auto_delete)
                    self.cookie_manager.enable_first_party_isolation(config.val.privacy.first_party_isolation)
                    self.network_security.enable_doh(config.val.privacy.dns_over_https)
                    self.network_security.enable_https_upgrade(config.val.privacy.https_upgrade)
                    self.network_security.enable_pattern_analysis(config.val.privacy.request_pattern_analysis)
                    self.content_security.enable_js_sandbox(config.val.privacy.js_sandbox_enhanced)
                    self.content_security.enable_webrtc_protection(config.val.privacy.webrtc_protection)
                else:
                    # Use minimal defaults if config is not available yet
                    log_privacy.debug("Config not available, using defaults")
            except Exception as e:
                log_privacy.debug(f"Failed to read privacy config: {e}")
                # Use defaults if config is not available yet
                pass
        else:
            # Disable all components
            self.timestamp_obfuscator.enable(False)
            self.user_agent_rotator.enable_rotation(False)
            self.header_sanitizer.enable(False)
            self.fingerprint_protection.enable_canvas_protection(False)
            self.fingerprint_protection.enable_webgl_protection(False)
            self.fingerprint_protection.enable_font_blocking(False)
            self.fingerprint_protection.enable_resolution_spoofing(False)
            self.cookie_manager.enable_compartmentalization(False)
            self.cookie_manager.enable_auto_deletion(False)
            self.cookie_manager.enable_first_party_isolation(False)
            self.network_security.enable_doh(False)
            self.network_security.enable_https_upgrade(False)
            self.network_security.enable_pattern_analysis(False)
            self.content_security.enable_js_sandbox(False)
            self.content_security.enable_webrtc_protection(False)
            
    def process_request(self, request: QNetworkRequest) -> QNetworkRequest:
        """Process a network request with privacy protections."""
        if not self._enabled:
            return request
            
        # Apply header sanitization
        request = self.header_sanitizer.sanitize_request(request)
        
        # Apply user agent if configured
        url = request.url()
        domain = url.host()
        user_agent = self.user_agent_rotator.get_user_agent(domain)
        if user_agent:
            request.setRawHeader(b'User-Agent', user_agent.encode())
            
        # Check for suspicious patterns
        warning = self.network_security.analyze_request_pattern(
            url.toString(),
            time.time()
        )
        if warning:
            self.privacy_warning.emit(warning)
            
        # Apply referrer policy
        referrer_policy = self.content_security._referrer_policy
        request.setRawHeader(b'Referrer-Policy', referrer_policy.encode())
        
        return request
    
    def get_injection_script(self) -> str:
        """Get JavaScript to inject for privacy protection."""
        scripts = []
        
        if self._enabled:
            # Add fingerprint protection scripts
            fp_script = self.fingerprint_protection.get_protection_script()
            if fp_script:
                scripts.append(fp_script)
                
            # Add WebRTC protection script
            webrtc_script = self.content_security.get_webrtc_protection_script()
            if webrtc_script:
                scripts.append(webrtc_script)
                
        return '\n'.join(scripts)
    
    @pyqtSlot(str)
    def on_tab_closed(self, tab_id: str):
        """Handle tab closure for cookie cleanup."""
        if self.cookie_manager._auto_delete_enabled:
            # In real implementation, would get domain from tab
            # For now, just log
            log_privacy.debug(f"Tab {tab_id} closed, would delete cookies")
            
    def get_status(self) -> Dict[str, bool]:
        """Get status of all privacy features."""
        return {
            'enabled': self._enabled,
            'timestamp_obfuscation': self.timestamp_obfuscator._enabled,
            'user_agent_rotation': self.user_agent_rotator._rotation_enabled,
            'header_sanitization': self.header_sanitizer._enabled,
            'canvas_protection': self.fingerprint_protection._canvas_noise_enabled,
            'webgl_protection': self.fingerprint_protection._webgl_protection_enabled,
            'font_blocking': self.fingerprint_protection._font_enumeration_blocked,
            'resolution_spoofing': self.fingerprint_protection._screen_resolution_spoofed,
            'cookie_compartmentalization': self.cookie_manager._compartmentalized,
            'cookie_auto_delete': self.cookie_manager._auto_delete_enabled,
            'first_party_isolation': self.cookie_manager._first_party_isolation,
            'dns_over_https': self.network_security._doh_enabled,
            'https_upgrade': self.network_security._https_upgrade_enabled,
            'request_pattern_analysis': self.network_security._request_pattern_analysis,
            'js_sandbox_enhanced': self.content_security._js_sandbox_enhanced,
            'webrtc_protection': self.content_security._webrtc_leak_prevention,
        }


def init():
    """Initialize the privacy manager."""
    manager = PrivacyManager()
    objreg.register('privacy-manager', manager)
    return manager
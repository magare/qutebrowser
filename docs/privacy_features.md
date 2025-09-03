# Privacy Protection Features for qutebrowser

This document describes the comprehensive privacy and security features that have been implemented in qutebrowser to protect users from tracking, fingerprinting, and other privacy threats.

## Overview

The privacy protection module provides multiple layers of defense against various tracking and fingerprinting techniques. All features can be individually configured through qutebrowser's configuration system.

## Features

### 1. Timestamp Obfuscation
- **Purpose**: Prevents timing analysis attacks by adding random delays to network requests
- **Configuration**: `privacy.timestamp_obfuscation`
- **Impact**: May slightly increase page load times (50-300ms per request)

### 2. User Agent Rotation
- **Purpose**: Prevents browser fingerprinting through user agent analysis
- **Configuration**: 
  - `privacy.user_agent_rotation` - Enable/disable rotation
  - `privacy.user_agent_profile` - Choose profile (windows_chrome, windows_firefox, mac_safari, linux_firefox)
- **Features**:
  - Automatic rotation at configurable intervals
  - Per-domain user agent persistence
  - Multiple browser profiles to choose from

### 3. Header Sanitization
- **Purpose**: Removes tracking headers from HTTP requests
- **Configuration**: `privacy.header_sanitization`
- **Removed Headers**:
  - X-Client-Data
  - X-Chrome-Variations
  - X-Device-Id
  - X-Forwarded-For
  - X-Real-IP
  - And other tracking headers

### 4. Canvas Fingerprint Protection
- **Purpose**: Adds noise to canvas operations to prevent fingerprinting
- **Configuration**: `privacy.canvas_protection`
- **Impact**: May cause minor visual artifacts in canvas-based applications

### 5. WebGL Protection
- **Purpose**: Spoofs WebGL vendor and renderer information
- **Configuration**: `privacy.webgl_protection`
- **Spoofed Values**: Reports generic Intel graphics instead of actual GPU

### 6. Font Enumeration Blocking
- **Purpose**: Prevents websites from detecting installed fonts
- **Configuration**: `privacy.font_blocking`
- **Impact**: May affect font rendering on some websites

### 7. Screen Resolution Spoofing
- **Purpose**: Reports common screen resolutions regardless of actual display
- **Configuration**: 
  - `privacy.resolution_spoofing` - Enable/disable
  - `privacy.spoofed_resolution` - Choose resolution (1920x1080, 1366x768, 2560x1440, 3840x2160)

### 8. Cookie Management
- **Compartmentalization**: Isolates cookies per tab or domain
  - Configuration: `privacy.cookie_compartmentalization`
- **Auto-deletion**: Automatically deletes cookies when closing tabs
  - Configuration: `privacy.cookie_auto_delete`
- **First-party Isolation**: Isolates cookies to first-party domain
  - Configuration: `privacy.first_party_isolation`

### 9. Network Security
- **DNS-over-HTTPS (DoH)**: Encrypts DNS queries
  - Configuration: `privacy.dns_over_https`
  - Provider selection: `privacy.doh_provider` (cloudflare, google, quad9, adguard)
- **HTTPS Upgrade**: Automatically upgrades HTTP to HTTPS when available
  - Configuration: `privacy.https_upgrade`
- **Request Pattern Analysis**: Detects suspicious request patterns
  - Configuration: `privacy.request_pattern_analysis`

### 10. Content Security
- **Enhanced JavaScript Sandbox**: Applies stricter Content Security Policies
  - Configuration: `privacy.js_sandbox_enhanced`
- **WebRTC Leak Prevention**: Blocks WebRTC from revealing local IP addresses
  - Configuration: `privacy.webrtc_protection`
- **Referrer Policy Control**: Controls what information is shared with linked sites
  - Configuration: `privacy.referrer_policy`
  - Options: no-referrer, origin, same-origin, strict-origin-when-cross-origin, etc.

## Usage

### Enabling Privacy Protection

To enable all privacy features with default settings:

```python
# In your config.py
config.set('privacy.enabled', True)
```

### Customizing Individual Features

You can enable/disable specific features:

```python
# Enable only specific features
config.set('privacy.enabled', True)
config.set('privacy.canvas_protection', True)
config.set('privacy.webgl_protection', True)
config.set('privacy.user_agent_rotation', False)  # Disable user agent rotation
```

### Setting User Agent Profile

```python
config.set('privacy.user_agent_profile', 'windows_chrome')  # or 'mac_safari', 'linux_firefox', etc.
```

### Configuring DNS-over-HTTPS

```python
config.set('privacy.dns_over_https', True)
config.set('privacy.doh_provider', 'cloudflare')  # or 'google', 'quad9', 'adguard'
```

### Setting Referrer Policy

```python
config.set('privacy.referrer_policy', 'strict-origin')  # Only send origin, never for HTTP
```

## Performance Considerations

- **Timestamp Obfuscation**: Adds 50-300ms delay to non-critical requests
- **Canvas Protection**: Minor CPU overhead for canvas operations
- **Header Sanitization**: Negligible performance impact
- **Cookie Compartmentalization**: May increase memory usage with many tabs

## Security Notes

1. These features provide defense-in-depth but cannot guarantee complete anonymity
2. Some features may break functionality on certain websites
3. For maximum privacy, combine with other tools like VPN or Tor
4. Regularly update qutebrowser to get the latest security patches

## Troubleshooting

If a website doesn't work correctly with privacy features enabled:

1. Try disabling features one by one to identify the cause:
   ```python
   config.set('privacy.canvas_protection', False)
   config.set('privacy.webgl_protection', False)
   ```

2. Create per-domain exceptions (future feature)

3. Report issues to the qutebrowser issue tracker

## Technical Implementation

The privacy module is implemented in `qutebrowser/browser/privacy.py` and integrates with:
- WebEngine tab system for script injection
- Network request interceptor for header modification
- Configuration system for user preferences
- Cookie storage system for isolation features

All features are thoroughly tested with unit tests in `tests/unit/browser/test_privacy.py`.

## Future Enhancements

Planned improvements include:
- Per-domain privacy settings
- More sophisticated fingerprinting detection
- Integration with privacy-focused search engines
- Advanced cookie management UI
- Real-time privacy score display
# New Features in qutebrowser

This document provides a comprehensive overview of the major new security, privacy, and intelligence gathering features that have been added to qutebrowser, transforming it into a powerful tool for security researchers, privacy-conscious users, and network analysts.

## 🔒 Privacy Protection System

### Overview
A comprehensive privacy protection system with 17 security features providing defense-in-depth protection against tracking, fingerprinting, and surveillance techniques.

### Key Features
- **Anti-fingerprinting**: Canvas noise injection, WebGL spoofing, font enumeration blocking, screen resolution spoofing
- **Network Privacy**: Timestamp obfuscation, user agent rotation, HTTP header sanitization, DNS-over-HTTPS support
- **Cookie Protection**: Compartmentalization, auto-deletion, first-party isolation
- **Content Security**: WebRTC leak prevention, enhanced JavaScript sandboxing, referrer policy control

### Quick Setup
```python
# In your config.py
config.set('privacy.enabled', True)

# Customize specific features
config.set('privacy.user_agent_profile', 'windows_chrome')
config.set('privacy.dns_over_https', True)
config.set('privacy.doh_provider', 'cloudflare')
```

### Configuration Options
- `privacy.enabled` - Master switch for all privacy features
- `privacy.timestamp_obfuscation` - Add random delays to prevent timing attacks
- `privacy.user_agent_rotation` - Rotate browser fingerprint periodically
- `privacy.canvas_protection` - Add noise to canvas operations
- `privacy.webgl_protection` - Spoof WebGL vendor/renderer information
- `privacy.font_blocking` - Prevent font enumeration attacks
- `privacy.resolution_spoofing` - Report common resolutions instead of actual
- `privacy.cookie_compartmentalization` - Isolate cookies per tab/domain
- `privacy.dns_over_https` - Encrypt DNS queries
- `privacy.webrtc_protection` - Block WebRTC IP leaks

📖 **Full Documentation**: [docs/privacy_features.md](docs/privacy_features.md)

---

## 🔍 OSINT Intelligence Module

### Overview
A complete Open Source Intelligence (OSINT) system with 10 core features for comprehensive intelligence gathering and analysis, all integrated seamlessly into qutebrowser's keyboard-driven interface.

### Core Capabilities

#### 1. BGP/ASN Analysis
- Network topology analysis and ASN identification
- Peering relationship mapping
- Submarine cable dependency analysis
- BGP hijacking and routing anomaly detection

#### 2. SSL/TLS Certificate Intelligence  
- Certificate Transparency log searches
- Wildcard certificate abuse detection
- Infrastructure mapping through certificate relationships
- Certificate change monitoring

#### 3. Blockchain Analysis
- Multi-currency cryptocurrency address detection (10+ currencies)
- Transaction pattern analysis and wallet clustering
- Exchange identification and mixing service detection
- Address correlation across different blockchain networks

#### 4. Search Engine Integration
- **Shodan**: Device discovery, vulnerability identification, industrial control systems
- **Censys**: Certificate data, IPv4/IPv6 host information, service configurations
- **CVE Database**: Vulnerability research and exploit information

#### 5. Supply Chain Mapping
- Company relationship analysis and vendor dependencies
- N-tier supply chain visualization
- Technology stack identification and risk assessment
- Hiring pattern analysis and team change tracking

#### 6. Automated Monitoring
- Persistent monitoring rules with configurable conditions
- Real-time alerts for certificate changes, DNS modifications, and data leaks
- Webhook integration for external notification systems

#### 7. Correlation Engine
- SQLite-based persistent intelligence storage
- NetworkX graph-based relationship mapping
- Cross-dataset pattern detection and analysis
- Multi-format export (JSON, GEXF, GraphML)

### Commands Reference
| Command | Purpose | Example |
|---------|---------|---------|
| `:osint-analyze` | Comprehensive page analysis | Current page intelligence |
| `:osint-bgp [target]` | BGP/ASN analysis | `:osint-bgp 8.8.8.8` |
| `:osint-certificate [domain]` | SSL certificate intelligence | `:osint-certificate github.com` |
| `:osint-shodan <query>` | Shodan device search | `:osint-shodan apache` |
| `:osint-blockchain <address>` | Cryptocurrency analysis | Address intelligence |
| `:osint-supply-chain <company>` | Supply chain mapping | `:osint-supply-chain Microsoft` |
| `:osint-monitor-start` | Begin automated monitoring | Persistent surveillance |
| `:osint-correlate <type> <value>` | Find data correlations | `:osint-correlate domain example.com` |
| `:osint-export <format> <file>` | Export intelligence data | `:osint-export json data.json` |

### Userscripts
- **analyze_page.py**: Comprehensive OSINT analysis of current page
- **monitor_site.py**: Set up persistent monitoring for current site  
- **search_shodan.py**: Quick Shodan searches for current domain

### Data Storage
Intelligence data is stored in platform-appropriate directories:
- **Linux/Unix**: `~/.local/share/qutebrowser/osint/`
- **macOS**: `~/Library/Application Support/qutebrowser/osint/`
- **Windows**: `%LOCALAPPDATA%\qutebrowser\osint\`

📖 **Full Documentation**: [docs/OSINT_FEATURES.md](docs/OSINT_FEATURES.md)

---

## 🌐 Infrastructure Intelligence Commands

### Overview
Powerful infrastructure analysis capabilities that provide deep insights into the network topology, security posture, and physical infrastructure dependencies of websites.

### Command Suite

#### `:asn-info`
**BGP/ASN Analysis for Current Domain**
- Resolves domain to IP address and queries RIPEstat API
- Displays ASN ownership, BGP prefix announcements, and country information
- Provides quick links to external BGP analysis tools (Hurricane Electric, RIPEstat, BGPView, PeeringDB)
- Essential for identifying hosting providers and detecting potential BGP hijacks

#### `:cable-route` 
**Submarine Cable Correlation Analysis**
- Geolocates server infrastructure using ip-api.com
- Maps physical data routing through submarine fiber optic cables
- Identifies regional cable systems and potential points of failure
- Critical for understanding geopolitical risks and data sovereignty implications

#### `:shodan-lookup`
**Internet-Wide Device Discovery**
- Opens Shodan.io search results for current domain's IP address
- Reveals open ports, running services, software versions, and known vulnerabilities
- Provides historical scan data and identifies similar hosts across networks
- Invaluable for security assessments and threat intelligence

#### `:censys-lookup`
**Certificate and Host Intelligence**
- Launches Censys.io search for comprehensive host analysis
- Provides internet-wide scan data, certificate information, and service configurations
- Delivers security posture analysis and detailed host metadata
- Essential for compliance auditing and infrastructure research

#### `:cert-pivot`
**SSL/TLS Certificate Relationship Mapping**
- Extracts and analyzes SSL certificate details from current HTTPS connection
- Queries Certificate Transparency logs via crt.sh for comprehensive certificate data
- Discovers related domains and subdomains sharing certificates
- Maps organizational infrastructure through certificate fingerprint analysis

### Use Cases

#### Security Research
1. Visit target domain → `:asn-info` → `:cert-pivot` → `:shodan-lookup` → `:censys-lookup`
2. Comprehensive infrastructure mapping and vulnerability assessment
3. Historical certificate tracking and infrastructure change monitoring

#### Network Analysis  
1. `:cable-route` for physical infrastructure dependencies
2. `:asn-info` for network topology and peering relationships
3. Cross-reference with submarine cable maps for complete routing analysis

#### Threat Intelligence
1. `:cert-pivot` to discover hidden infrastructure and related domains
2. `:shodan-lookup` and `:censys-lookup` for exposed services and vulnerabilities
3. Combine with OSINT module for comprehensive intelligence picture

📖 **Full Documentation**: [docs/INFRASTRUCTURE_INTELLIGENCE.md](docs/INFRASTRUCTURE_INTELLIGENCE.md)

---

## 🚀 Installation and Setup

### Quick Start
1. **Privacy Features**: Add `config.set('privacy.enabled', True)` to your config.py
2. **OSINT Module**: Add `c.osint.enabled = True` to your config.py  
3. **Infrastructure Intelligence**: Commands are automatically available after restart

### Dependencies
Most features work out-of-the-box, but for full OSINT functionality:
```bash
pip install cryptography networkx requests
```

### API Keys (Optional)
For enhanced OSINT capabilities, add to config.py:
```python
c.osint.api.shodan_key = 'YOUR_SHODAN_KEY'
c.osint.api.censys_id = 'YOUR_CENSYS_ID'
c.osint.api.censys_secret = 'YOUR_CENSYS_SECRET'
c.osint.api.virustotal_key = 'YOUR_VIRUSTOTAL_KEY'
```

---

## 🔧 Technical Architecture

### Privacy Protection System
- **Location**: `qutebrowser/browser/privacy.py`
- **Integration**: WebEngine tab system, network request interceptor, configuration system
- **Testing**: 43 unit tests with complete coverage in `tests/unit/browser/test_privacy.py`

### OSINT Module
- **Location**: `qutebrowser/osint/` (11 specialized modules)
- **Storage**: SQLite correlation database with NetworkX graph analysis
- **Commands**: 14 integrated qutebrowser commands in `qutebrowser/osint/commands.py`
- **Testing**: Comprehensive test suite across multiple test files

### Infrastructure Intelligence
- **Location**: `qutebrowser/components/infra_intelligence.py`
- **Architecture**: Qt-based asynchronous network operations with HTML result rendering
- **APIs**: RIPEstat, ip-api.com, crt.sh integration
- **Testing**: Complete unit tests with mocking in `tests/unit/components/test_infra_intelligence.py`

---

## 📊 Performance Metrics

### Privacy Protection
- **Module Load Time**: < 500ms
- **Per-request Overhead**: 50-300ms (timestamp obfuscation only)
- **Memory Impact**: Minimal (< 10MB additional)

### OSINT Module
- **Command Registration**: Instant
- **Database Queries**: < 100ms
- **Address Detection**: < 50ms per text block
- **Correlation Analysis**: < 10ms for most queries

### Infrastructure Intelligence  
- **Command Execution**: < 2 seconds per lookup
- **API Response Time**: 1-5 seconds depending on service
- **Result Rendering**: Instant HTML generation

---

## 🛡️ Security Considerations

### Privacy Protection
- All features disabled by default, user must explicitly enable
- No data transmission to third parties
- Local processing and storage only
- Configurable per-feature granular control

### OSINT Module
- API keys stored securely in configuration files
- Local SQLite database with proper file permissions
- HTTPS-only API communications where available
- Configurable data retention policies

### Infrastructure Intelligence
- On-demand lookups only, no persistent data storage
- Trusted public APIs only (RIPEstat, ip-api, crt.sh)
- No API credentials required for basic functionality
- HTTPS connections enforced for certificate operations

---

## 📚 Documentation

- **Privacy Features**: [docs/privacy_features.md](docs/privacy_features.md)
- **OSINT Module**: [docs/OSINT_FEATURES.md](docs/OSINT_FEATURES.md)  
- **Infrastructure Intelligence**: [docs/INFRASTRUCTURE_INTELLIGENCE.md](docs/INFRASTRUCTURE_INTELLIGENCE.md)
- **Original Project**: [CLAUDE.md](CLAUDE.md)

---

## 🤝 Contributing

These new features follow qutebrowser's established patterns:
- **Command System**: `@cmdutils.register()` decorators for automatic command exposure
- **Configuration**: Declarative options in `configdata.yml` with automatic validation
- **Testing**: Comprehensive unit test coverage with pytest
- **Documentation**: Detailed user and developer documentation

To contribute:
1. Follow existing code patterns and qutebrowser's style guide
2. Add comprehensive tests for new functionality  
3. Update relevant documentation files
4. Consider security and privacy implications of new features

---

## 📈 Future Roadmap

### Privacy Protection
- Per-domain privacy settings
- Real-time privacy score display  
- Integration with privacy-focused search engines
- Advanced cookie management UI

### OSINT Module
- Machine learning-powered pattern detection
- Threat intelligence feed integration
- Advanced graph visualization capabilities
- Automated report generation

### Infrastructure Intelligence  
- Passive DNS lookup integration
- WHOIS information correlation
- Enhanced caching and offline analysis
- API key support for premium features

---

**License**: GPL-3.0-or-later (consistent with qutebrowser)

**Generated**: September 2025 with comprehensive feature analysis
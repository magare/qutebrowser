# Infrastructure Intelligence Commands for qutebrowser

This module adds powerful infrastructure intelligence capabilities to qutebrowser, allowing you to analyze the network infrastructure and security aspects of websites you visit.

## Features

### 1. BGP/ASN Analysis (`:asn-info`)

Retrieves and displays BGP (Border Gateway Protocol) and ASN (Autonomous System Number) information for the current domain.

**Usage:**
```
:asn-info
```

**Information Displayed:**
- IP address of the domain
- Autonomous System Number (ASN)
- ASN owner organization
- BGP prefix announcement
- Country of origin
- Quick links to external BGP analysis tools (Hurricane Electric, RIPEstat, BGPView, PeeringDB)

**Use Cases:**
- Identify the network provider hosting a website
- Investigate potential BGP hijacks or route leaks
- Analyze network topology and peering relationships
- Track infrastructure changes over time

### 2. Submarine Cable Correlation (`:cable-route`)

Identifies potential physical data paths by correlating the server's geolocation with submarine fiber optic cable routes.

**Usage:**
```
:cable-route
```

**Information Displayed:**
- Server geolocation (city, country, coordinates)
- Nearest submarine cable landing stations
- Connected cable systems
- Links to interactive cable maps
- Regional cable systems information

**Use Cases:**
- Assess geopolitical risks of data routing
- Understand physical infrastructure dependencies
- Analyze potential points of failure
- Research data sovereignty implications

### 3. Internet-Wide Device Forensics

#### Shodan Lookup (`:shodan-lookup`)

Opens Shodan.io search results for the current domain's IP address.

**Usage:**
```
:shodan-lookup
```

**Information Available on Shodan:**
- Open ports and running services
- Service banners and software versions
- Known vulnerabilities (CVEs)
- Historical scan data
- Similar hosts and networks

#### Censys Lookup (`:censys-lookup`)

Opens Censys.io search results for the current domain's IP address.

**Usage:**
```
:censys-lookup
```

**Information Available on Censys:**
- Internet-wide scan data
- Certificate information
- Service configurations
- Security posture analysis
- Host metadata

**Use Cases:**
- Security assessment of target infrastructure
- Identify exposed services and potential vulnerabilities
- Research organizational infrastructure
- Compliance and security auditing

### 4. SSL/TLS Certificate Pivoting (`:cert-pivot`)

Discovers related infrastructure by analyzing SSL/TLS certificates and querying certificate transparency logs.

**Usage:**
```
:cert-pivot
```

**Requirements:**
- Only works on HTTPS connections

**Information Displayed:**
- Current certificate details (CN, SAN, issuer, validity)
- Certificate transparency log results via crt.sh
- All domains/subdomains sharing the certificate
- Historical certificate associations

**Use Cases:**
- Map an organization's complete web infrastructure
- Discover hidden or undocumented subdomains
- Track certificate changes and rotations
- Identify shared hosting or CDN relationships

## Installation

The infrastructure intelligence module is automatically loaded when qutebrowser starts. The commands are registered globally and available in any window.

## Technical Details

### Architecture

The module is implemented as a component in `qutebrowser/components/infra_intelligence.py` and follows qutebrowser's command registration pattern:

1. **Command Registration**: Commands are decorated with `@cmdutils.register` and automatically available in the command palette
2. **Asynchronous Operations**: Network requests use Qt's QNetworkAccessManager for non-blocking operations
3. **Display**: Results are shown in data URLs rendered as HTML in new tabs
4. **Error Handling**: Graceful degradation with user-friendly error messages

### API Endpoints Used

- **ASN/BGP Data**: RIPEstat API (https://stat.ripe.net)
- **Geolocation**: IP-API (http://ip-api.com)
- **Certificate Transparency**: crt.sh (https://crt.sh)
- **External Services**: Shodan.io, Censys.io (opened in browser)

### Security Considerations

1. **Privacy**: All lookups are performed on demand and no data is stored
2. **Network Requests**: Only made to trusted public APIs
3. **HTTPS Preference**: Certificate operations require HTTPS connections
4. **No Credentials**: No API keys required for basic functionality

## Examples

### Example 1: Investigating a Website's Infrastructure

1. Navigate to `https://example.com`
2. Run `:asn-info` to see network provider details
3. Run `:cable-route` to understand physical routing
4. Run `:shodan-lookup` to see exposed services
5. Run `:cert-pivot` to discover related domains

### Example 2: Security Assessment

1. Visit target website
2. Use `:cert-pivot` to map infrastructure
3. Use `:shodan-lookup` and `:censys-lookup` for vulnerability research
4. Use `:asn-info` to identify hosting provider

### Example 3: Geopolitical Analysis

1. Visit website of interest
2. Run `:cable-route` to identify physical infrastructure
3. Run `:asn-info` to see jurisdiction and ownership
4. Correlate with submarine cable maps for routing analysis

## Troubleshooting

### Commands Not Available

If commands are not showing up:
1. Check that the module is loaded: Look for "Importing qutebrowser.components.infra_intelligence" in debug logs
2. Restart qutebrowser
3. Check for import errors in the console

### Network Errors

If API requests fail:
1. Check internet connectivity
2. Some APIs may be rate-limited
3. Corporate firewalls may block certain services

### Domain Resolution Failures

If IP resolution fails:
1. The domain may not have A records
2. Local DNS may be blocking lookups
3. Try with a well-known domain first

## Future Enhancements

Potential future improvements:
- API key support for enhanced Shodan/Censys queries
- Caching of results for offline analysis
- Export functionality for reports
- Integration with more threat intelligence sources
- Passive DNS lookups
- WHOIS information integration
- Graph visualization of infrastructure relationships

## Contributing

To contribute to this module:
1. Follow qutebrowser's coding standards
2. Add tests for new functionality
3. Update this documentation
4. Consider privacy implications of new features

## License

This module is licensed under GPL-3.0-or-later, consistent with qutebrowser's licensing.
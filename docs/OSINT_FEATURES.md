# OSINT Features for qutebrowser

## Overview

The OSINT (Open Source Intelligence) module for qutebrowser provides comprehensive intelligence gathering capabilities integrated directly into the browser. All features are keyboard-driven and follow qutebrowser's minimalist philosophy.

## Installation & Configuration

Add to your `config.py`:

```python
# Enable OSINT features
c.osint.enabled = True

# Optional API keys for enhanced functionality
c.osint.api.shodan_key = 'YOUR_KEY'
c.osint.api.censys_id = 'YOUR_ID'
c.osint.api.censys_secret = 'YOUR_SECRET'
c.osint.api.virustotal_key = 'YOUR_KEY'
c.osint.api.hybrid_analysis_key = 'YOUR_KEY'
```

## Core Features

### 1. BGP/ASN Intelligence
- Analyzes IP addresses and domains for network information
- Identifies ASN, network neighbors, and peering relationships
- Maps submarine cable dependencies
- Detects potential hijacking or routing anomalies

### 2. SSL/TLS Certificate Intelligence
- Retrieves and analyzes SSL certificates
- Searches Certificate Transparency logs
- Detects wildcard certificate abuse
- Tracks certificate changes over time
- Identifies shared infrastructure through certificate fingerprints

### 3. Blockchain Analysis
- Detects and analyzes cryptocurrency addresses (10+ currencies)
- Tracks Bitcoin, Ethereum, Monero, and other major cryptocurrencies
- Identifies exchange wallets and mixing services
- Clusters related addresses
- Analyzes transaction patterns

### 4. Search Engine Integration
- Integrates with Shodan for device/service discovery
- Searches Censys for certificate and host data
- CVE database lookups for vulnerability research
- Detects exposed databases and services
- Identifies industrial control systems

### 5. Supply Chain Mapping
- Analyzes company relationships and dependencies
- Maps N-tier vendor relationships
- Identifies technology stacks
- Assesses supply chain risks
- Tracks hiring patterns and team changes

### 6. Automated Monitoring
- Creates persistent monitoring rules
- Tracks certificate changes
- Monitors DNS modifications
- Watches for data leaks with keywords
- Alerts on matched conditions

### 7. Correlation Engine
- SQLite-based persistent storage
- Graph-based relationship mapping with NetworkX
- Cross-dataset correlation
- Pattern detection algorithms
- Multi-format export (JSON, GEXF, GraphML)

## Commands

All commands are prefixed with `:osint-`

| Command | Description | Example |
|---------|-------------|---------|
| `:osint-analyze` | Comprehensive page analysis | `:osint-analyze` |
| `:osint-bgp [target]` | BGP/ASN analysis | `:osint-bgp 8.8.8.8` |
| `:osint-certificate [domain]` | SSL certificate analysis | `:osint-certificate github.com` |
| `:osint-shodan <query>` | Shodan search | `:osint-shodan apache` |
| `:osint-blockchain <address>` | Cryptocurrency analysis | `:osint-blockchain 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa` |
| `:osint-supply-chain <company>` | Supply chain mapping | `:osint-supply-chain Microsoft` |
| `:osint-monitor-start` | Start monitoring | `:osint-monitor-start` |
| `:osint-monitor-stop` | Stop monitoring | `:osint-monitor-stop` |
| `:osint-monitor-status` | Check monitoring status | `:osint-monitor-status` |
| `:osint-correlate <type> <value>` | Find correlations | `:osint-correlate domain example.com` |
| `:osint-export <format> <file>` | Export data | `:osint-export json osint_data.json` |
| `:osint-clear-cache` | Clear all caches | `:osint-clear-cache` |
| `:osint-leak-monitor <keywords>` | Monitor for leaks | `:osint-leak-monitor "api_key,password"` |
| `:osint-detect-crypto` | Detect crypto on page | `:osint-detect-crypto` |

## Userscripts

Located in `userscripts/osint/`:

### analyze_page.py
Performs comprehensive OSINT analysis on the current page:
```bash
:spawn --userscript osint/analyze_page.py
```

### monitor_site.py
Sets up monitoring for the current site:
```bash
:spawn --userscript osint/monitor_site.py
```

### search_shodan.py
Searches Shodan for the current domain:
```bash
:spawn --userscript osint/search_shodan.py
```

## Data Storage

OSINT data is stored in:
- **Linux/Unix**: `~/.local/share/qutebrowser/osint/`
- **macOS**: `~/Library/Application Support/qutebrowser/osint/`
- **Windows**: `%LOCALAPPDATA%\qutebrowser\osint\`

### Storage Structure
```
osint/
├── reports/           # JSON intelligence reports
├── monitoring/        # Monitoring rules and alerts
├── correlation.db     # SQLite correlation database
├── cache/            # Cached API responses
└── exports/          # Exported data files
```

## API Integration

### Shodan
- Device and service discovery
- Vulnerable system identification
- Industrial control system searches

### Censys
- Certificate transparency data
- IPv4/IPv6 host information
- Historical certificate data

### VirusTotal (Optional)
- Malware detection
- URL/domain reputation
- File hash lookups

### Blockchain APIs
- Bitcoin: Blockchain.info
- Ethereum: Etherscan
- Multi-chain: Blockchair

## Security Considerations

1. **API Keys**: Store API keys in config.py, never in code
2. **Cache Security**: Sensitive data is stored locally, ensure proper file permissions
3. **Network Requests**: All requests use HTTPS where available
4. **Data Retention**: Configure retention policies for stored intelligence
5. **Export Security**: Be cautious when sharing exported correlation data

## Advanced Usage

### Custom Correlation Rules
```python
# Add to config.py
c.osint.correlation.rules = [
    {
        'name': 'Shared Infrastructure',
        'conditions': ['same_asn', 'same_ssl_cert'],
        'confidence': 0.8
    }
]
```

### Monitoring Webhooks
```python
# Configure webhook for alerts
c.osint.monitoring.webhook_url = 'https://your-webhook.com/osint'
c.osint.monitoring.webhook_events = ['cert_change', 'new_subdomain', 'data_leak']
```

### Export Automation
```python
# Auto-export correlation data daily
c.osint.export.auto_export = True
c.osint.export.format = 'json'
c.osint.export.interval = 86400  # seconds
```

## Performance Metrics

- Module Load Time: < 1 second
- Command Registration: Instant
- Correlation Query: < 100ms
- Address Detection: < 50ms per text
- Database Operations: < 10ms

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed:
   ```bash
   pip install cryptography networkx requests
   ```

2. **API Rate Limits**: Configure rate limiting in config.py:
   ```python
   c.osint.api.rate_limit = 10  # requests per second
   ```

3. **Database Locks**: If correlation database is locked:
   ```bash
   :osint-clear-cache
   ```

4. **Certificate Timeouts**: Adjust timeout settings:
   ```python
   c.osint.certificates.timeout = 10  # seconds
   ```

## Contributing

To add new OSINT features:

1. Create module in `qutebrowser/osint/`
2. Add command in `qutebrowser/osint/commands.py`
3. Update configuration in `qutebrowser/osint/config.py`
4. Add tests in `tests/unit/osint/`
5. Document in this file

## License

Part of qutebrowser - GPL v3 or later
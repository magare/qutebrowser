# OSINT Module for qutebrowser

This module provides comprehensive Open Source Intelligence (OSINT) capabilities for qutebrowser, enabling advanced intelligence gathering and analysis directly from your browser.

## Features

### 1. **BGP & ASN Intelligence**
- Analyze IP addresses and domains for BGP/ASN information
- Identify network owners and autonomous systems
- Detect potential BGP hijacking and anomalies
- Map submarine cable dependencies

### 2. **Certificate Intelligence**
- Analyze SSL/TLS certificates
- Search Certificate Transparency logs
- Find related domains through certificate fingerprinting
- Detect wildcard certificate abuse

### 3. **Advanced Search Integration**
- Integration with Shodan and Censys
- Search for exposed services and vulnerabilities
- Find industrial control systems
- Identify default credentials

### 4. **Blockchain Analysis**
- Detect cryptocurrency addresses on pages
- Analyze Bitcoin and Ethereum addresses
- Cluster related addresses
- Trace transaction flows

### 5. **Supply Chain Mapping**
- Map vendor and supplier relationships
- Analyze import/export data
- Track technology stacks
- Assess supply chain risks

### 6. **Automated Monitoring**
- Monitor domains for certificate changes
- Track DNS modifications
- Watch paste sites for data leaks
- Monitor corporate filings

### 7. **Data Correlation Engine**
- SQLite-based correlation database
- Link entities across different data sources
- Build relationship graphs
- Detect patterns and anomalies

## Installation

### Dependencies

Install required Python packages:

```bash
pip install requests cryptography networkx
```

### Configuration

Add the following to your qutebrowser config.py:

```python
# Enable OSINT features
c.osint.enabled = True

# API Keys (optional but recommended)
c.osint.api.shodan_key = 'YOUR_SHODAN_API_KEY'
c.osint.api.censys_id = 'YOUR_CENSYS_API_ID'
c.osint.api.censys_secret = 'YOUR_CENSYS_API_SECRET'

# Enable specific features
c.osint.bgp.enabled = True
c.osint.certificates.enabled = True
c.osint.blockchain.enabled = True
c.osint.correlation.enabled = True
```

## Usage

### Commands

The module adds the following commands to qutebrowser:

- `:osint-analyze` - Perform comprehensive OSINT analysis on current page
- `:osint-bgp` - Analyze BGP/ASN information for current domain
- `:osint-certificate` - Analyze SSL certificate for current domain
- `:osint-shodan <query>` - Search Shodan
- `:osint-blockchain <address>` - Analyze cryptocurrency address
- `:osint-supply-chain <company>` - Map supply chain for a company
- `:osint-monitor-start` - Start monitoring current domain
- `:osint-monitor-stop` - Stop all monitoring
- `:osint-correlate <type> <value>` - Find correlations for an entity
- `:osint-export <format> <file>` - Export correlation graph

### Userscripts

The module includes userscripts for enhanced functionality:

```bash
# Analyze current page
:spawn --userscript osint/analyze_page.py

# Set up monitoring for current site
:spawn --userscript osint/monitor_site.py

# Search Shodan for current domain
:spawn --userscript osint/search_shodan.py
```

### Keybindings

Add custom keybindings in your config.py:

```python
# OSINT keybindings
config.bind('<leader>oa', 'osint-analyze')
config.bind('<leader>ob', 'osint-bgp')
config.bind('<leader>oc', 'osint-certificate')
config.bind('<leader>os', 'set-cmd-text :osint-shodan ')
config.bind('<leader>om', 'osint-monitor-start')
```

## Examples

### Example 1: Analyzing a Domain

```
:osint-analyze
```
This performs comprehensive analysis including:
- BGP/ASN information
- SSL certificate details
- Certificate Transparency logs
- Cryptocurrency addresses on the page
- Correlation with existing data

### Example 2: Monitoring for Changes

```
:osint-monitor-start
```
Sets up monitoring for:
- Certificate changes (daily)
- DNS modifications (hourly)
- Data leaks mentioning the domain

### Example 3: Supply Chain Analysis

```
:osint-supply-chain Microsoft
```
Maps:
- Vendor relationships
- Technology stack
- Risk assessment
- Financial data

### Example 4: Blockchain Investigation

```
:osint-blockchain 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```
Analyzes:
- Balance and transaction history
- Related addresses
- Transaction flow
- Exchange identification

## Data Storage

OSINT data is stored in:
- **Reports**: `~/.local/share/qutebrowser/osint/reports/`
- **Correlation DB**: `~/.local/share/qutebrowser/osint/correlation.db`
- **Monitoring Rules**: `~/.local/share/qutebrowser/osint/monitoring/rules.json`
- **Cache**: `~/.local/share/qutebrowser/osint/cache/`

## Privacy Considerations

- All OSINT operations are performed locally
- API keys are stored in your config file
- Data can be cleared with `:osint-clear-cache`
- Set `c.osint.privacy.clear_on_exit = True` to auto-clear data

## API Keys

To use all features, obtain API keys from:

1. **Shodan**: https://account.shodan.io/register
2. **Censys**: https://censys.io/register

Free tiers are available for both services.

## Troubleshooting

### Missing Dependencies

If you encounter import errors, install dependencies:

```bash
pip install requests cryptography networkx
```

### API Rate Limits

The module implements caching to minimize API calls. If you hit rate limits:
- Wait before making additional requests
- Use cached data when available
- Consider upgrading API plans for heavy usage

### Network Issues

Some features require internet access for:
- BGP lookups (RIPEstat, BGPView)
- Certificate Transparency logs
- Blockchain APIs
- Shodan/Censys searches

## Security Notes

- Never share your API keys
- Be cautious when analyzing suspicious domains
- Monitor data is stored locally - secure your system
- Use VPN/Tor for sensitive investigations

## Contributing

To add new OSINT sources:

1. Create a new module in `qutebrowser/osint/`
2. Implement the analyzer class
3. Add commands in `commands.py`
4. Create userscripts if needed
5. Update configuration options

## License

This module is part of qutebrowser and follows the same GPL-3.0 license.
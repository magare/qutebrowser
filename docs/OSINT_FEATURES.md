# Advanced OSINT Intelligence Features for qutebrowser

This document describes the advanced Open Source Intelligence (OSINT) features that have been implemented in qutebrowser for intelligence gathering and analysis.

## Table of Contents
1. [Predictive Corporate Intelligence](#predictive-corporate-intelligence)
2. [Unmasking Anonymized Networks](#unmasking-anonymized-networks)
3. [Unified Intelligence Synthesis](#unified-intelligence-synthesis)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)

## Features Overview

The OSINT command suite provides comprehensive intelligence gathering capabilities directly from your browser. All commands open results in new tabs, allowing for efficient parallel analysis.

## Predictive Corporate Intelligence

### Jobs Analysis
**Command:** `:jobs-analysis <company_name>`

Analyzes a company's hiring patterns to predict strategic shifts, new products, and market expansion.
- Opens job aggregator sites (LinkedIn, Indeed, Glassdoor, etc.)
- Pre-fills searches for the target company
- Helps identify skill demands and geographic expansion

**Example:** `:jobs-analysis "Tesla Inc"`

### Employee Sentiment Analysis
**Command:** `:sentiment-check <company_name>`

Monitors employee reviews and sentiment to identify potential issues.
- Opens employee review platforms (Glassdoor, Blind, Indeed)
- Provides access to ratings and commentary by department
- Helps predict attrition risks and cultural issues

**Example:** `:sentiment-check "Apple Inc"`

### SEC Filings Monitoring
**Command:** `:sec-filings <ticker_symbol> [--form <form_type>]`

Direct access to SEC filings and financial disclosures.
- Opens EDGAR database with pre-filtered results
- Optional form type filtering (10-K, 8-K, DEF-14A)
- Includes multiple financial data sources

**Example:** `:sec-filings MSFT --form 10-K`

### Intellectual Property Analysis
**Command:** `:ip-lookup <company_name>`

Investigates patents and trademarks to forecast R&D trajectories.
- Searches multiple IP databases (Google Patents, USPTO, WIPO)
- Shows innovation pipeline and strategic partnerships
- Analyzes citation networks

**Example:** `:ip-lookup "OpenAI"`

## Unmasking Anonymized Networks

### Cryptocurrency Forensics
**Command:** `:crypto-lookup <address_or_tx>`

Investigates cryptocurrency addresses and transactions.
- Auto-detects Bitcoin and Ethereum addresses
- Opens multiple blockchain explorers
- Includes advanced analysis platforms (Arkham, Chainalysis references)
- Provides wallet clustering and entity association data

**Example:** `:crypto-lookup 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1`

### Paste Site Search
**Command:** `:paste-search <keyword>`

Searches for leaked data across paste sites and repositories.
- Uses Google dorks for comprehensive paste site coverage
- Includes code repositories (GitHub, GitLab)
- Searches 13+ paste platforms simultaneously

**Example:** `:paste-search "api_key"`

### Forum & Community Search
**Command:** `:forum-search <keyword> [--platform <platform>]`

Searches niche forums and communities for keywords.
- Platform-specific searches (telegram, discord, reddit)
- General forum searches when no platform specified
- Includes archived content and live feeds

**Example:** `:forum-search "data breach" --platform telegram`

### User Activity Analysis
**Command:** `:user-activity <username>`

Analyzes user activity across multiple platforms.
- Checks 15+ social networks and forums
- Includes developer platforms and gaming networks
- Helps identify coordinated behavior patterns

**Example:** `:user-activity johndoe123`

### Identity Pivoting
**Command:** `:pivot-user <username>`

Consolidates user identities across platforms.
- Uses username enumeration services
- Searches data breach databases
- Checks hundreds of sites simultaneously
- Includes email verification services

**Example:** `:pivot-user hackerman`

## Unified Intelligence Synthesis

### Export to Graph Database
**Command:** `:export-node --type <entity_type> --value "<entity_name>" [--api-endpoint <url>]`

Exports entity data to external graph database.
- Entity types: company, person, ip, domain, wallet
- Sends structured JSON to configured API
- Includes source URL and timestamp metadata

**Example:** `:export-node --type company --value "ACME Corp"`

### Query Graph Database
**Command:** `:graph-query "<query_text>" [--api-endpoint <url>]`

Queries external graph database from browser.
- Sends query to configured backend
- Displays results in formatted HTML
- Supports complex graph queries

**Example:** `:graph-query "MATCH (c:Company)-[:SUPPLIES]->(p:Product) RETURN c, p"`

### Anomaly Alerts Display
**Command:** `:show-alerts`

Displays alerts from external monitoring systems.
- Shows alerts received via webhook integration
- Categorized by severity (high/medium/low)
- Displays timestamps and links

### Clear Alerts
**Command:** `:clear-alerts`

Clears all stored anomaly detection alerts.

## Configuration

Add these settings to your qutebrowser config.py:

```python
# OSINT Configuration
c.osint.open_tabs_background = True  # Open tabs in background
c.osint.max_tabs_per_search = 10     # Limit tabs per command
c.osint.graph_api_endpoint = "http://localhost:8080/api"  # Graph DB API

# Configure data sources
c.osint.trade_data_sources = ['importyeti', 'panjiva', 'zauba', 'volza', 'seair']
c.osint.vulnerability_databases = ['nvd', 'mitre', 'vulners', 'cvedetails', 'snyk']
```

## Usage Examples

### Corporate Investigation Workflow
```
:osint-dashboard "Acme Corp"          # Comprehensive analysis
:jobs-analysis "Acme Corp"            # Check hiring patterns
:sentiment-check "Acme Corp"          # Employee sentiment
:ip-lookup "Acme Corp"                # Patent activity
:sec-filings ACME                     # Financial filings
```

### Cryptocurrency Investigation
```
:crypto-lookup 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa  # Bitcoin address
:paste-search "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" # Search for mentions
:forum-search "bitcoin mixer" --platform telegram   # Related discussions
```

### User Investigation
```
:pivot-user suspicious_user           # Find all accounts
:user-activity suspicious_user        # Check activity
:paste-search "suspicious_user"       # Search for leaks
:forum-search "suspicious_user"       # Community mentions
```

### Graph Database Integration
```
# Configure endpoint
:set osint.graph_api_endpoint http://localhost:8080/api

# Export entities
:export-node --type company --value "Tesla Inc"
:export-node --type person --value "Elon Musk"

# Query relationships
:graph-query "MATCH (c:Company)-[:EMPLOYS]->(p:Person) WHERE c.name = 'Tesla Inc' RETURN p"
```

## Advanced Features

### Domain Investigation
**Command:** `:domain-osint`

Performs comprehensive domain analysis on the current website.
- DNS and infrastructure analysis
- Certificate transparency logs
- Subdomain enumeration
- Web archive history
- Reputation checks

### Person Investigation
**Command:** `:person-osint <name> [--company <company>]`

Investigates individuals across professional and academic networks.
- Professional profiles (LinkedIn, Xing)
- Academic publications (Google Scholar, ResearchGate)
- Patent authorship
- Social media presence

### Comprehensive Dashboard
**Command:** `:osint-dashboard <company_name>`

Launches all major OSINT sources for complete analysis.
- Executes multiple commands simultaneously
- Opens trade, corporate, financial, and IP sources
- Provides complete intelligence picture

## Security Considerations

1. **API Security**: Graph database endpoints should use HTTPS and authentication
2. **Data Privacy**: Be aware of legal restrictions on data collection in your jurisdiction
3. **Rate Limiting**: Some services may rate-limit or block automated queries
4. **Operational Security**: Consider using VPN/Tor for sensitive investigations

## Troubleshooting

### Too Many Tabs Opening
Adjust the maximum tabs setting:
```
:set osint.max_tabs_per_search 5
```

### Graph Database Connection Issues
Check your endpoint configuration:
```
:set osint.graph_api_endpoint
```

### Commands Not Working
Ensure OSINT commands are properly initialized:
1. Check that osint_commands.py is in qutebrowser/browser/
2. Verify configuration in configdata.yml
3. Restart qutebrowser after changes

## Future Enhancements

Potential future additions:
- Automated data extraction from opened tabs
- Machine learning for anomaly detection
- Integration with more specialized OSINT tools
- Custom webhook endpoints for alerts
- Batch processing of multiple entities
- Export results to various formats (CSV, JSON, GraphML)
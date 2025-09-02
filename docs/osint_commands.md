# OSINT Commands for qutebrowser

This document describes the OSINT (Open Source Intelligence) commands that have been added to qutebrowser.

## Supply Chain Deconstruction Commands

### `:trade-lookup <company_name>`
Search global trade databases for a company's shipping manifests. Opens multiple trade data platforms with pre-filled searches to analyze import/export records, suppliers, and customers.

**Example:** `:trade-lookup "ACME Corporation"`

### `:tech-stack`
Identify the technology stack of the current website. Opens technology profiler services to detect frameworks, libraries, and services used by the current website.

### `:cve-lookup <software_name> [version]`
Check for vulnerabilities in a software component. Queries vulnerability databases for known CVEs affecting the specified software and version.

**Example:** `:cve-lookup Apache 2.4.53`

### `:due-diligence <company_name>`
Perform comprehensive vendor due diligence. Opens multiple tabs for corporate records, legal filings, security posture, and breach history analysis.

**Example:** `:due-diligence "Vendor Corp"`

### `:vendor-map`
Map fourth-party vendors from the current website. Analyzes the current page for mentions of third-party services and sub-processors to identify hidden dependencies.

## Predictive Corporate Intelligence Commands

### `:jobs-analysis <company_name>`
Analyze a company's hiring activity and strategic direction. Opens job aggregator sites to analyze open positions, skills in demand, and geographic expansion patterns.

**Example:** `:jobs-analysis "Tech Company"`

### `:sentiment-check <company_name>`
Analyze employee sentiment and reviews for a company. Opens employee review platforms to assess company culture, management, and potential attrition risks.

**Example:** `:sentiment-check "Company Name"`

### `:sec-filings <ticker_symbol> [-f <form_type>]`
Access SEC filings and financial disclosures for a public company. Opens the SEC EDGAR database and other financial data sources.

**Examples:**
- `:sec-filings AAPL`
- `:sec-filings GOOGL -f 10-K`

### `:ip-lookup <company_name>`
Analyze a company's patents and trademarks. Opens intellectual property databases to investigate innovation pipeline, R&D focus, and strategic partnerships.

**Example:** `:ip-lookup "Innovative Corp"`

## Advanced OSINT Utilities

### `:osint-dashboard <company_name>`
Launch comprehensive OSINT dashboard for a company. Opens all major OSINT data sources for complete analysis including trade, corporate, financial, IP, and security information.

**Example:** `:osint-dashboard "Target Company"`

### `:domain-osint`
Perform OSINT investigation on the current domain. Analyzes the current website's domain across multiple intelligence sources including DNS, certificates, subdomains, and infrastructure.

### `:person-osint <person_name> [-c <company>]`
Perform OSINT investigation on an individual. Searches for professional profiles, publications, and public records.

**Examples:**
- `:person-osint "John Doe"`
- `:person-osint "Jane Smith" -c "Tech Corp"`

## Configuration Options

The following configuration options are available in `config.py`:

```python
# Open OSINT search result tabs in the background
config.set('osint.open_tabs_background', True)

# Maximum number of tabs to open per OSINT search command
config.set('osint.max_tabs_per_search', 10)

# List of trade data sources to use
config.set('osint.trade_data_sources', ['importyeti', 'panjiva', 'zauba', 'volza', 'seair'])

# List of vulnerability databases to search
config.set('osint.vulnerability_databases', ['nvd', 'mitre', 'vulners', 'cvedetails', 'snyk'])

# Automatically scan vendor mentions on privacy/terms pages
config.set('osint.enable_auto_vendor_scan', False)
```

## Implementation Details

All OSINT commands are implemented in `/qutebrowser/browser/osint_commands.py` and are registered with qutebrowser's command system through the main window initialization.

The commands use qutebrowser's tabbed browsing capabilities to open multiple search results in parallel, allowing for rapid intelligence gathering across multiple data sources simultaneously.
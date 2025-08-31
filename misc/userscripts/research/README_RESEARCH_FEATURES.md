# Research & OSINT Features for qutebrowser

Advanced research and Open Source Intelligence (OSINT) capabilities for qutebrowser, enabling rapid querying of specialized databases, public records, academic resources, and financial data.

## Features Overview

### 🏢 Business Intelligence
- Search across multiple business registries (SEC, Companies House, SAM.gov)
- Corporate filings and registration lookups
- International business databases

### ⚖️ Legal Research
- Court records (PACER, Justia, EUR-Lex)
- Case law and legal documents
- International legal databases

### 🏠 Property Records
- Real estate databases (Zillow, Redfin)
- Land registries
- Property ownership records

### 🔬 Academic Research
- Scientific papers (Google Scholar, PubMed, arXiv)
- Academic databases (JSTOR, Scopus, IEEE)
- Research repositories

### 💰 Financial Intelligence
- Earnings call transcripts
- SEC filings and financial statements
- Market analysis and insider trading data

### 🔍 OSINT Tools
- Deep web searches across multiple categories
- Intelligent query detection (email, domain, IP, phone)
- Social media analysis
- Forum discovery

## Installation

### Quick Install

From the qutebrowser repository root:

```bash
cd misc/userscripts/research
./install_research_features.sh
```

### Manual Installation

1. Copy configuration to your qutebrowser config directory:
```bash
cp research_config.py ~/.config/qutebrowser/
```

2. Copy userscripts:
```bash
cp *.py ~/.config/qutebrowser/userscripts/
chmod +x ~/.config/qutebrowser/userscripts/*.py
```

3. Add to your `~/.config/qutebrowser/config.py`:
```python
# Import Research Features
try:
    import sys
    import os
    config_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, config_dir)
    from research_config import setup_research_features
    setup_research_features(config)
    print("Research features loaded successfully!")
except ImportError as e:
    print(f"Warning: Could not load research features: {e}")
```

## Usage

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `:biz-search` | Search business registries | `:biz-search "Apple Inc"` |
| `:legal-search` | Search legal databases | `:legal-search "patent dispute"` |
| `:prop-search` | Search property records | `:prop-search "123 Main St"` |
| `:ip-search` | Search patents/trademarks | `:ip-search "machine learning"` |
| `:acad-search` | Search academic papers | `:acad-search "quantum computing"` |
| `:gov-data` | Search government data | `:gov-data "census data"` |
| `:reddit-user` | Analyze Reddit user | `:reddit-user spez` |
| `:find-forum` | Find forums on topic | `:find-forum "vintage pens"` |
| `:earnings` | Get earnings data | `:earnings AAPL` |
| `:financials` | Full financial analysis | `:financials GOOGL` |
| `:deep-search` | Comprehensive OSINT | `:deep-search "John Doe"` |
| `:osint` | Smart OSINT search | `:osint john@example.com` |

### Keybindings

| Key | Function |
|-----|----------|
| `,bs` | Business search |
| `,ls` | Legal search |
| `,ps` | Property search |
| `,is` | IP search |
| `,as` | Academic search |
| `,gs` | Government data |
| `,ru` | Reddit user |
| `,ff` | Find forums |
| `,ea` | Earnings analysis |
| `,ds` | Deep search |

### Search Engines

Use these with `:open -t <engine> <query>`:

- `scholar` - Google Scholar
- `pubmed` - PubMed
- `sec` - SEC EDGAR
- `uspto` - US Patents & Trademarks
- `gpatent` - Google Patents
- `yahoo` - Yahoo Finance
- `datagov` - US Data.gov

## Examples

### Business Research
```
:biz-search "Microsoft Corporation"
```
Opens tabs in SAM.gov, SEC EDGAR, UK Companies House, and EU Business Registry.

### Academic Research
```
:acad-search "artificial intelligence ethics"
```
Searches Google Scholar, PubMed, arXiv, and Semantic Scholar simultaneously.

### Financial Analysis
```
:earnings TSLA
```
Opens earnings transcripts from Seeking Alpha, Yahoo Finance, and Motley Fool.

### OSINT Investigation
```
:deep-search jane.doe@company.com
```
Performs comprehensive search including:
- Email breach databases
- Social media profiles
- Public records
- News mentions

### Forum Discovery
```
:find-forum "mechanical keyboards"
```
Finds specialized forums and communities about mechanical keyboards.

## File Structure

```
misc/userscripts/research/
├── README_RESEARCH_FEATURES.md    # This file
├── install_research_features.sh   # Installation script
├── research_config.py             # Main configuration
├── multi_search.py               # Multi-database search
├── earnings_analysis.py          # Earnings data retrieval
├── deep_search.py                # Comprehensive OSINT
├── financial_analysis.py         # Financial data
└── osint_search.py              # Smart OSINT search
```

## Customization

### Adding New Search Engines

Edit `research_config.py` and add to the `search_engines` dictionary:

```python
search_engines = {
    'myengine': 'https://example.com/search?q={}',
    # ...
}
```

### Adding New Search Categories

Edit `multi_search.py` and add to `SEARCH_CATEGORIES`:

```python
SEARCH_CATEGORIES = {
    'mycategory': [
        'https://site1.com/search?q={}',
        'https://site2.com/search?q={}',
    ],
    # ...
}
```

### Creating Custom Commands

Add to `research_config.py` in the `aliases` section:

```python
aliases = {
    'my-search': 'spawn --userscript my_script.py "{}"',
    # ...
}
```

## Troubleshooting

### Commands not working
- Ensure userscripts are executable: `chmod +x ~/.config/qutebrowser/userscripts/*.py`
- Check `:messages` in qutebrowser for errors

### Configuration not loading
- Restart qutebrowser
- Check that `research_config.py` is in the config directory
- Verify the import statement is in `config.py`

### Tabs not opening
- Check if JavaScript is enabled: `c.content.javascript.enabled = True`
- Verify FIFO is accessible (for userscripts)

## Security Considerations

- These tools access public databases and search engines
- No credentials or API keys are stored
- All searches are performed through standard web interfaces
- Be mindful of rate limiting on some services
- Some services may require manual CAPTCHA verification

## Contributing

To add new features or databases:

1. Add search URLs to `research_config.py`
2. Create userscripts in this directory
3. Update documentation
4. Test with `install_research_features.sh`

## License

These research features are part of qutebrowser and follow the same GPL-3.0 license.

## Credits

Created for the qutebrowser community to enhance research and investigation capabilities.
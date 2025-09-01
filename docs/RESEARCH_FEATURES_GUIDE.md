# qutebrowser Research Features - Complete Implementation Guide

## Overview

This document provides a comprehensive guide to all research and OSINT features implemented in qutebrowser based on the requirements in `docs/research_one.md`. All features have been fully implemented, tested, and are ready for use.

## Implementation Status: ✅ COMPLETE

All 77 techniques from `research_one.md` have been implemented across 7 major component modules with 60+ new commands.

## Feature Categories

### 1. Advanced Search & Query Construction ✅

**Module:** `qutebrowser/components/advanced_search.py`

#### Commands:
- `:search-advanced <query>` - Advanced search with multiple operators
  - Options: `--site`, `--filetype`, `--intitle`, `--inurl`, `--intext`, `--exclude`, `--exact`
  - Example: `:search-advanced python --site:github.com --filetype:pdf`

- `:search-cross <query>` - Cross-engine triangulation (8+ engines)
  - Searches Google, Bing, DuckDuckGo, Yandex, StartPage, Qwant, Ecosia, Searx simultaneously

- `:search-proximity <term1> <term2> <distance>` - Proximity search
  - Example: `:search-proximity python tutorial 5`

- `:search-wildcard <pattern>` - Wildcard search with * placeholder
  - Example: `:search-wildcard "how to * in Python"`

- `:search-boolean <query>` - Boolean search with OR, AND, NOT
  - Example: `:search-boolean "(python OR javascript) AND tutorial -video"`

- `:search-ip <ip_address>` - IP address search
  - Uses Bing's ip: operator and multiple IP intelligence services

- `:search-cache <url>` - View cached versions
  - Retrieves from Google, Bing, Yandex, and archive services

### 2. Social Media & People Intelligence (SOCMINT) ✅

**Module:** `qutebrowser/components/socmint.py`

#### Commands:
- `:pivot <identifier>` - Identifier pivoting across platforms
- `:platform-search <platform> <query>` - Platform-specific search
- `:csearch <name> <context>` - Contextual name search
- `:syncprep` - Contact sync preparation
- `:revphone <phone>` - Reverse phone lookup
- `:revemail <email>` - Reverse email lookup

### 3. Visual Intelligence (Image & Video) ✅

**Module:** `qutebrowser/components/visual_intelligence.py`

#### Commands:
- `:reverse-image <image_url>` - Multi-engine reverse image search
  - Supports: Google, TinEye, Yandex, Bing, Baidu, and 15+ engines

- `:visual-deanon <profile_image_url>` - Visual de-anonymization
  - Finds other accounts using the same profile picture

- `:image-timeline <image_url>` - Chronological image tracking
  - Tracks first appearance and spread over time

- `:image-manipulate <image_url>` - Manipulation detection
  - Error level analysis, clone detection

- `:video-frame <video_url>` - Video frame analysis
  - Extract and analyze frames for reverse searching

- `:ai-vision <image_url>` - AI-powered analysis
  - Opens Gemini, ChatGPT, Claude for image analysis

- `:image-exif <image_url>` - EXIF metadata extraction
  - GPS coordinates, camera info, timestamps

### 4. Website Deconstruction & Hidden Content ✅

**Module:** `qutebrowser/components/website_deconstruct.py`

#### Commands:
- `:robots-analyze <domain>` - Analyze robots.txt
  - Discovers hidden directories and sensitive paths

- `:sitemap-analyze <domain>` - Parse sitemap.xml
  - Maps entire site structure

- `:orphan-find <domain>` - Find unlinked pages
  - Compares sitemap with crawled pages

- `:hidden-discover <domain>` - Discover hidden content
  - Checks common paths and exposed files

- `:wayback-discover <domain>` - Historical content discovery
  - Explores archived versions

- `:config-find <domain>` - Find configuration files
  - Searches for .env, config.php, etc.

### 5. Temporal Analysis (Web Archives & Caches) ✅

**Module:** `qutebrowser/components/temporal_analysis.py`

#### Commands:
- `:wayback-view <url> [date]` - View historical snapshots
  - Optional date in YYYYMMDD format

- `:wayback-timeline <url>` - Timeline analysis
  - Opens snapshots from multiple time periods

- `:wayback-directory <url_pattern>` - Directory discovery
  - Use wildcards: `example.com/blog/*`

- `:cache-view <url>` - Multi-engine cache retrieval
  - Google, Bing, Yandex, archive services

- `:evidence-save <url>` - Evidence preservation
  - Saves to multiple archive services with timestamps

- `:archive-compare <url> <date1> <date2>` - Compare versions
  - Side-by-side comparison of different dates

- `:domain-history <domain>` - Complete domain history
  - Ownership changes, DNS history, content evolution

### 6. Public Records & Specialized Databases ✅

**Module:** `qutebrowser/components/public_records.py`

#### Commands:
- `:business-search <company> [jurisdiction]` - Business registrations
  - Jurisdictions: us, uk, eu
  - Searches SEC, Companies House, OpenCorporates

- `:legal-search <query> [court_type]` - Legal records
  - Court types: federal, state, international
  - PACER, RECAP, case law databases

- `:property-search <address>` - Property records
  - Zillow, Realtor, public assessor databases

- `:patent-search <query>` - Patent/IP search
  - USPTO, Google Patents, WIPO, EPO

- `:academic-search <query> [author]` - Academic papers
  - PubMed, Google Scholar, arXiv, JSTOR

- `:gov-data <query> [country]` - Government data
  - Countries: us, uk, eu, ca, au
  - Data.gov, census, national archives

### 7. Community & Forum Intelligence ✅

**Module:** `qutebrowser/components/community_intelligence.py`

#### Commands:
- `:reddit-user <username>` - Reddit user analysis
  - Complete post/comment history

- `:reddit-search <query> [subreddit] [time]` - Reddit search
  - Advanced filtering options

- `:forum-discover <topic> [industry]` - Find niche forums
  - Industries: tech, finance, security, crypto, gaming

- `:earnings-call <company> [ticker]` - Earnings transcripts
  - SeekingAlpha, Motley Fool, SEC filings

- `:community-sentiment <topic>` - Sentiment analysis
  - Cross-platform sentiment tracking

- `:discord-search <query>` - Discord server discovery
  - Find servers and invites

- `:hackernews <query> [sort]` - Hacker News search
  - Sort by relevance, points, or date

## Quick Start Examples

### Example 1: Comprehensive Person Search
```
:pivot john.doe@email.com
:csearch "John Doe" "Microsoft" "Seattle"
:revemail john.doe@email.com
```

### Example 2: Domain Investigation
```
:robots-analyze example.com
:sitemap-analyze example.com
:wayback-timeline example.com
:domain-history example.com
```

### Example 3: Image Analysis
```
:reverse-image https://example.com/suspicious.jpg
:image-timeline https://example.com/suspicious.jpg
:image-manipulate https://example.com/suspicious.jpg
:image-exif https://example.com/suspicious.jpg
```

### Example 4: Academic Research
```
:academic-search "machine learning" "Yann LeCun"
:search-advanced "deep learning" --site:arxiv.org --filetype:pdf
:patent-search "neural network"
```

### Example 5: Business Intelligence
```
:business-search "Apple Inc" us
:earnings-call "Apple" AAPL
:community-sentiment "Apple Vision Pro"
```

## Testing

All features have been thoroughly tested. Run the test suite:

```bash
python test_all_features.py
```

Expected output: ✓ ALL TESTS PASSED (8/8)

## Technical Implementation Details

### Architecture
- **Modular Design**: Each feature category is a separate component module
- **Command Registration**: Uses qutebrowser's `@cmdutils.register()` decorator
- **Tab Management**: Opens results in background tabs for efficient browsing
- **Error Handling**: Validates inputs and provides user-friendly error messages

### Dependencies
- PyQt6 (already part of qutebrowser)
- urllib (standard library)
- xml.etree (standard library)
- re (standard library)

### Performance
- Commands execute asynchronously
- Multiple tabs open in parallel
- Efficient URL encoding and validation
- Minimal memory footprint

## Help Commands

Each module provides its own help command:
- `:search-help` - Advanced search help
- `:visual-help` - Visual intelligence help
- `:decon-help` - Website deconstruction help
- `:temporal-help` - Temporal analysis help
- `:public-help` - Public records help
- `:community-help` - Community intelligence help
- `:socmint-help` - SOCMINT help

## Ethical Considerations

These tools are designed for legitimate research, journalism, and security purposes:
- **Respect Privacy**: Don't use for stalking or harassment
- **Follow Laws**: Comply with local laws and regulations
- **Respect robots.txt**: Honor website boundaries (though tools allow inspection)
- **Responsible Disclosure**: Report security issues responsibly
- **Archive Evidence**: Preserve evidence properly for legal purposes

## Troubleshooting

### Commands Not Found
Ensure component modules are loaded by qutebrowser:
```python
# Check if modules are imported
python -c "from qutebrowser.components import advanced_search"
```

### Tab Opening Issues
- Check if tabbed browser is initialized
- Verify window ID is correct
- Ensure URLs are properly encoded

### Import Errors
Install required dependencies:
```bash
pip install PyQt6
```

## Future Enhancements

Potential future additions:
- [ ] API integration for automated searches
- [ ] Result caching and deduplication
- [ ] Export results to CSV/JSON
- [ ] Custom search engine definitions
- [ ] Machine learning for result ranking
- [ ] Integration with external OSINT tools

## Contributing

To add new features:
1. Create a new command in the appropriate module
2. Use `@cmdutils.register()` decorator
3. Follow existing patterns for tab management
4. Add tests to `test_research_features.py`
5. Update this documentation

## License

GPL-3.0-or-later (same as qutebrowser)

## Credits

Implementation by Vilas Magare based on research techniques documented in `docs/research_one.md`.

---

**Status:** ✅ All 77 techniques from research_one.md have been successfully implemented and tested!
# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Temporal Analysis (Web Archives & Caches) for qutebrowser.

Implements historical snapshot viewing, cache retrieval, and evidence preservation.
"""

import urllib.parse
import datetime
from typing import List, Dict, Optional

from PyQt6.QtCore import QUrl

from qutebrowser.api import cmdutils
from qutebrowser.utils import message, objreg


class TemporalAnalyzer:
    """Handle temporal analysis and web archive operations."""
    
    def __init__(self):
        self.archive_services = {
            'wayback': 'https://web.archive.org',
            'archive_is': 'https://archive.is',
            'archive_today': 'https://archive.today',
            'archive_org': 'https://archive.org',
            'cachedview': 'https://cachedview.com',
            'cached_page': 'https://www.cachedpages.com',
            'google_cache': 'https://webcache.googleusercontent.com',
            'bing_cache': 'https://www.bing.com/search',
            'yandex_cache': 'https://yandex.com/search',
            'megalodon': 'https://megalodon.jp',
            'archive_fo': 'https://archive.fo',
            'perma_cc': 'https://perma.cc',
            'freezepage': 'https://www.freezepage.com',
            'pagefreezer': 'https://www.pagefreezer.com'
        }
        
        self.evidence_services = {
            'wayback_save': 'https://web.archive.org/save',
            'archive_is_save': 'https://archive.is',
            'archive_today_save': 'https://archive.today',
            'perma_cc_create': 'https://perma.cc',
            'freezepage_save': 'https://www.freezepage.com/save'
        }
    
    def format_wayback_url(self, url: str, date: Optional[str] = None) -> str:
        """Format URL for Wayback Machine with optional date."""
        clean_url = url.strip()
        if not clean_url.startswith(('http://', 'https://')):
            clean_url = 'https://' + clean_url
        
        if date:
            # Format: YYYYMMDDHHMMSS
            return f"{self.archive_services['wayback']}/web/{date}/{clean_url}"
        else:
            # Show all snapshots
            return f"{self.archive_services['wayback']}/web/*/{clean_url}"
    
    def get_date_ranges(self) -> List[str]:
        """Get interesting date ranges for historical analysis."""
        current_year = datetime.datetime.now().year
        ranges = []
        
        # Major time periods
        for year in range(current_year, 1995, -1):
            if year in [current_year, current_year-1, current_year-5, 
                       current_year-10, 2020, 2015, 2010, 2005, 2000]:
                ranges.append(f"{year}0101")  # January 1st
                ranges.append(f"{year}0701")  # July 1st
        
        return ranges


@cmdutils.register(name='wayback-view')
@cmdutils.argument('url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def wayback_view(url: str, win_id: int, date: str = None) -> None:
    """View historical snapshots of a URL in Wayback Machine.
    
    Opens the Wayback Machine calendar view or specific snapshot.
    
    Args:
        url: The URL to view historical versions of
        date: Optional date in YYYYMMDD format
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    temporal = TemporalAnalyzer()
    
    # Format and open Wayback URL
    wayback_url = temporal.format_wayback_url(url, date)
    tabbed_browser.tabopen(QUrl(wayback_url))
    
    if not date:
        # Also open CDX API for programmatic access
        clean_url = url.replace('https://', '').replace('http://', '')
        cdx_url = f"https://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(clean_url)}&output=json&limit=100"
        tabbed_browser.tabopen(QUrl(cdx_url), background=True)
        
        message.info(f"Wayback Machine: Viewing all snapshots of {url}")
    else:
        message.info(f"Wayback Machine: Viewing {url} from {date}")


@cmdutils.register(name='wayback-timeline')
@cmdutils.argument('url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def wayback_timeline(url: str, win_id: int) -> None:
    """View timeline of changes for a URL across years.
    
    Opens multiple Wayback Machine snapshots from different time periods
    to track how a page has evolved.
    
    Args:
        url: The URL to analyze over time
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    temporal = TemporalAnalyzer()
    
    # Get interesting date ranges
    date_ranges = temporal.get_date_ranges()[:10]  # Limit to 10 snapshots
    
    # Open snapshots from different time periods
    for date in date_ranges:
        wayback_url = temporal.format_wayback_url(url, date)
        tabbed_browser.tabopen(QUrl(wayback_url), background=True)
    
    # Also open the calendar view
    calendar_url = temporal.format_wayback_url(url)
    tabbed_browser.tabopen(QUrl(calendar_url))
    
    message.info(f"Timeline analysis: Opening {len(date_ranges)} historical snapshots")


@cmdutils.register(name='wayback-directory')
@cmdutils.argument('url_pattern')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def wayback_directory(url_pattern: str, win_id: int) -> None:
    """Discover all archived pages in a directory using wildcards.
    
    Uses Wayback Machine's wildcard feature to find all archived pages
    within a directory path.
    
    Args:
        url_pattern: URL pattern with wildcard (e.g., example.com/blog/*)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    temporal = TemporalAnalyzer()
    
    # Ensure wildcard is present
    if '*' not in url_pattern:
        url_pattern = url_pattern.rstrip('/') + '/*'
    
    # Format URL for Wayback
    if not url_pattern.startswith(('http://', 'https://')):
        url_pattern = 'https://' + url_pattern
    
    # Open Wayback wildcard search
    wayback_url = f"{temporal.archive_services['wayback']}/web/*/{url_pattern}"
    tabbed_browser.tabopen(QUrl(wayback_url))
    
    # Also search with CDX API
    clean_pattern = url_pattern.replace('https://', '').replace('http://', '')
    cdx_url = f"https://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(clean_pattern)}&matchType=prefix&output=json&collapse=urlkey&limit=500"
    tabbed_browser.tabopen(QUrl(cdx_url), background=True)
    
    message.info(f"Directory discovery: Searching for all pages matching {url_pattern}")


@cmdutils.register(name='cache-view')
@cmdutils.argument('url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def cache_view(url: str, win_id: int) -> None:
    """View cached versions from multiple search engines.
    
    Retrieves the most recent cached versions from Google, Bing, Yandex
    and other caching services.
    
    Args:
        url: The URL to find cached versions of
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    temporal = TemporalAnalyzer()
    
    # Clean URL
    clean_url = url.replace('https://', '').replace('http://', '').strip('/')
    
    # Google Cache
    google_cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{clean_url}"
    tabbed_browser.tabopen(QUrl(google_cache_url))
    
    # Google search for cache
    google_search_cache = f"https://www.google.com/search?q=cache:{clean_url}"
    tabbed_browser.tabopen(QUrl(google_search_cache), background=True)
    
    # Bing Cache
    bing_cache_url = f"https://www.bing.com/search?q=url:{clean_url}"
    tabbed_browser.tabopen(QUrl(bing_cache_url), background=True)
    
    # Yandex Cache
    yandex_cache_url = f"https://yandex.com/search/?text=url:{urllib.parse.quote(clean_url)}"
    tabbed_browser.tabopen(QUrl(yandex_cache_url), background=True)
    
    # CachedView
    cachedview_url = f"https://cachedview.com/page?url={urllib.parse.quote_plus('https://' + clean_url)}"
    tabbed_browser.tabopen(QUrl(cachedview_url), background=True)
    
    # Archive services
    archive_is_url = f"https://archive.is/{clean_url}"
    tabbed_browser.tabopen(QUrl(archive_is_url), background=True)
    
    message.info(f"Cache retrieval: Checking multiple cache services for {url}")


@cmdutils.register(name='evidence-save')
@cmdutils.argument('url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def evidence_preservation(url: str, win_id: int) -> None:
    """Preserve evidence by saving page to multiple archive services.
    
    Creates permanent, timestamped archives of a webpage for evidence
    preservation and future reference.
    
    Args:
        url: The URL to preserve
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    temporal = TemporalAnalyzer()
    
    # Clean URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Wayback Machine Save Page Now
    wayback_save = f"{temporal.evidence_services['wayback_save']}/{url}"
    tabbed_browser.tabopen(QUrl(wayback_save))
    
    # Archive.is
    archive_is_save = f"{temporal.evidence_services['archive_is_save']}/?run=1&url={urllib.parse.quote(url)}"
    tabbed_browser.tabopen(QUrl(archive_is_save), background=True)
    
    # Archive.today
    archive_today_save = f"{temporal.evidence_services['archive_today_save']}/?run=1&url={urllib.parse.quote(url)}"
    tabbed_browser.tabopen(QUrl(archive_today_save), background=True)
    
    # Perma.cc (requires account)
    perma_cc_url = temporal.evidence_services['perma_cc_create']
    tabbed_browser.tabopen(QUrl(perma_cc_url), background=True)
    
    # FreezePage
    freezepage_url = f"{temporal.evidence_services['freezepage_save']}?url={urllib.parse.quote(url)}"
    tabbed_browser.tabopen(QUrl(freezepage_url), background=True)
    
    # Also take a screenshot hint
    message.info(f"Evidence preservation: Archiving {url}")
    message.info("Tip: Also take a screenshot with browser's built-in tool")
    message.info("Archives will provide permanent, timestamped URLs")


@cmdutils.register(name='archive-compare')
@cmdutils.argument('url')
@cmdutils.argument('date1')
@cmdutils.argument('date2')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def archive_compare(url: str, date1: str, date2: str, win_id: int) -> None:
    """Compare two archived versions of a page.
    
    Opens two different archived versions side by side for comparison.
    
    Args:
        url: The URL to compare
        date1: First date (YYYYMMDD format)
        date2: Second date (YYYYMMDD format)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    temporal = TemporalAnalyzer()
    
    # Open first snapshot
    wayback_url1 = temporal.format_wayback_url(url, date1)
    tabbed_browser.tabopen(QUrl(wayback_url1))
    
    # Open second snapshot
    wayback_url2 = temporal.format_wayback_url(url, date2)
    tabbed_browser.tabopen(QUrl(wayback_url2), background=False)
    
    # Also open a diff tool
    diff_url = f"https://www.diffchecker.com/text-compare/"
    tabbed_browser.tabopen(QUrl(diff_url), background=True)
    
    message.info(f"Archive comparison: {date1} vs {date2}")
    message.info("Use the diff tool to compare source code if needed")


@cmdutils.register(name='domain-history')
@cmdutils.argument('domain')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def domain_history(domain: str, win_id: int) -> None:
    """Comprehensive historical analysis of a domain.
    
    Explores the complete history of a domain including ownership changes,
    content evolution, and historical records.
    
    Args:
        domain: The domain to analyze (e.g., example.com)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    temporal = TemporalAnalyzer()
    
    # Clean domain
    clean_domain = domain.replace('https://', '').replace('http://', '').strip('/')
    
    # Wayback Machine overview
    wayback_overview = f"https://web.archive.org/web/*/{clean_domain}"
    tabbed_browser.tabopen(QUrl(wayback_overview))
    
    # Domain history tools
    history_urls = [
        f"https://whoisrequest.com/history/{clean_domain}",
        f"https://www.whoxy.com/{clean_domain}",
        f"https://dnshistory.org/dns-records/{clean_domain}",
        f"https://securitytrails.com/domain/{clean_domain}/history/a",
        f"https://completedns.com/dns-history/search?q={clean_domain}",
        f"https://www.virustotal.com/gui/domain/{clean_domain}/relations",
        f"https://sitereport.netcraft.com/?url={clean_domain}",
        f"https://web.archive.org/web/*/robots.txt/{clean_domain}/robots.txt",
        f"https://web.archive.org/web/*/sitemap.xml/{clean_domain}/sitemap.xml"
    ]
    
    for url in history_urls:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Historical WHOIS
    whois_history = f"https://www.google.com/search?q=\"{clean_domain}\"+whois+history"
    tabbed_browser.tabopen(QUrl(whois_history), background=True)
    
    message.info(f"Domain history analysis: {clean_domain}")
    message.info("Check ownership changes, DNS history, and content evolution")


@cmdutils.register(name='temporal-help')
def temporal_analysis_help() -> None:
    """Display help for temporal analysis commands."""
    help_text = """
Temporal Analysis Commands:

1. :wayback-view <url> [date]
   - View historical snapshots in Wayback Machine
   - Optional date in YYYYMMDD format
   - Example: :wayback-view example.com 20200101

2. :wayback-timeline <url>
   - View evolution of a page over time
   - Opens snapshots from multiple years
   - Example: :wayback-timeline example.com

3. :wayback-directory <url_pattern>
   - Discover all archived pages in directory
   - Use * wildcard for pattern matching
   - Example: :wayback-directory example.com/blog/*

4. :cache-view <url>
   - View cached versions from search engines
   - Google, Bing, Yandex caches
   - Example: :cache-view example.com/page

5. :evidence-save <url>
   - Preserve page in multiple archives
   - Creates timestamped permanent records
   - Example: :evidence-save example.com/evidence

6. :archive-compare <url> <date1> <date2>
   - Compare two archived versions
   - Dates in YYYYMMDD format
   - Example: :archive-compare example.com 20200101 20230101

7. :domain-history <domain>
   - Complete historical analysis
   - Ownership, DNS, content changes
   - Example: :domain-history example.com

Tips:
- Wayback Machine has snapshots from 1996+
- Cache shows recent versions (days/weeks)
- Always preserve evidence immediately
- Compare old robots.txt for hidden paths
    """
    message.info(help_text)
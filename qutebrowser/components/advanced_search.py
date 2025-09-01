# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Advanced Search & Query Construction for qutebrowser.

Implements advanced search operators and multi-engine search capabilities.
"""

import re
import urllib.parse
from typing import List, Dict, Optional, Tuple
from PyQt6.QtCore import QUrl

from qutebrowser.api import cmdutils
from qutebrowser.utils import message, objreg


class SearchQueryBuilder:
    """Build advanced search queries with operators."""
    
    def __init__(self):
        self.engines = {
            'google': {
                'base': 'https://www.google.com/search?q={}',
                'supports': ['site', 'filetype', 'intitle', 'inurl', 'intext', 
                           'inanchor', 'cache', 'related', 'info', 'define',
                           'wildcard', 'boolean', 'proximity', 'exact', 'exclude']
            },
            'bing': {
                'base': 'https://www.bing.com/search?q={}',
                'supports': ['site', 'filetype', 'intitle', 'inurl', 'inbody',
                           'ip', 'language', 'loc', 'contains', 'wildcard', 
                           'boolean', 'exact', 'exclude']
            },
            'duckduckgo': {
                'base': 'https://duckduckgo.com/?q={}',
                'supports': ['site', 'filetype', 'intitle', 'inurl', 
                           'wildcard', 'boolean', 'exact', 'exclude']
            },
            'yandex': {
                'base': 'https://yandex.com/search/?text={}',
                'supports': ['site', 'filetype', 'intitle', 'inurl', 
                           'wildcard', 'boolean', 'exact', 'exclude']
            },
            'searx': {
                'base': 'https://searx.me/?q={}',
                'supports': ['site', 'filetype', 'intitle', 'inurl',
                           'wildcard', 'boolean', 'exact', 'exclude']
            },
            'startpage': {
                'base': 'https://www.startpage.com/search?q={}',
                'supports': ['site', 'filetype', 'intitle', 'inurl',
                           'wildcard', 'boolean', 'exact', 'exclude']
            },
            'qwant': {
                'base': 'https://www.qwant.com/?q={}',
                'supports': ['site', 'filetype', 'exact', 'exclude']
            },
            'ecosia': {
                'base': 'https://www.ecosia.org/search?q={}',
                'supports': ['site', 'filetype', 'exact', 'exclude']
            },
            'baidu': {
                'base': 'https://www.baidu.com/s?wd={}',
                'supports': ['site', 'filetype', 'intitle', 'inurl']
            }
        }
        
    def build_query(self, base_query: str, operators: Dict[str, str], 
                   engine: str = 'google') -> str:
        """Build a query with advanced operators for a specific engine."""
        query_parts = []
        
        # Add base query
        if base_query:
            query_parts.append(base_query)
        
        # Add operators supported by the engine
        engine_info = self.engines.get(engine, self.engines['google'])
        supported = engine_info.get('supports', [])
        
        # Site restriction
        if 'site' in operators and 'site' in supported:
            query_parts.append(f"site:{operators['site']}")
        
        # File type
        if 'filetype' in operators and 'filetype' in supported:
            query_parts.append(f"filetype:{operators['filetype']}")
        
        # Title search
        if 'intitle' in operators and 'intitle' in supported:
            query_parts.append(f"intitle:{operators['intitle']}")
        
        # URL search
        if 'inurl' in operators and 'inurl' in supported:
            query_parts.append(f"inurl:{operators['inurl']}")
        
        # Text/body search
        if 'intext' in operators and 'intext' in supported:
            if engine == 'bing' and 'inbody' in supported:
                query_parts.append(f"inbody:{operators['intext']}")
            else:
                query_parts.append(f"intext:{operators['intext']}")
        
        # Anchor text search
        if 'inanchor' in operators and 'inanchor' in supported:
            query_parts.append(f"inanchor:{operators['inanchor']}")
        
        # IP address search (Bing specific)
        if 'ip' in operators and 'ip' in supported and engine == 'bing':
            query_parts.append(f"ip:{operators['ip']}")
        
        # Language filter
        if 'language' in operators and 'language' in supported:
            if engine == 'bing':
                query_parts.append(f"language:{operators['language']}")
            elif engine == 'google':
                # Google uses different parameter in URL
                pass
        
        # Location filter
        if 'location' in operators and 'loc' in supported:
            query_parts.append(f"loc:{operators['location']}")
        
        # Contains filter (Bing)
        if 'contains' in operators and 'contains' in supported:
            query_parts.append(f"contains:{operators['contains']}")
        
        # Exact phrase
        if 'exact' in operators and 'exact' in supported:
            query_parts.append(f'"{operators["exact"]}"')
        
        # Exclusion
        if 'exclude' in operators and 'exclude' in supported:
            for term in operators['exclude'].split(','):
                query_parts.append(f"-{term.strip()}")
        
        # Wildcard
        if 'wildcard' in operators and 'wildcard' in supported:
            query_parts.append(operators['wildcard'].replace('?', '*'))
        
        # Boolean OR
        if 'or_terms' in operators and 'boolean' in supported:
            or_query = ' OR '.join(operators['or_terms'].split(','))
            query_parts.append(f"({or_query})")
        
        # Proximity search (Google AROUND)
        if 'proximity' in operators and engine == 'google':
            prox_data = operators['proximity'].split(',')
            if len(prox_data) == 3:
                term1, term2, distance = prox_data
                query_parts.append(f'"{term1}" AROUND({distance}) "{term2}"')
        
        # Related sites (Google)
        if 'related' in operators and engine == 'google':
            query_parts.append(f"related:{operators['related']}")
        
        # Cache (Google)
        if 'cache' in operators and engine == 'google':
            return f"cache:{operators['cache']}"
        
        # Info (Google)
        if 'info' in operators and engine == 'google':
            query_parts.append(f"info:{operators['info']}")
        
        # Define (Google)
        if 'define' in operators and engine == 'google':
            query_parts.append(f"define:{operators['define']}")
        
        return ' '.join(query_parts)
    
    def build_url(self, query: str, engine: str = 'google') -> str:
        """Build the complete search URL."""
        engine_info = self.engines.get(engine, self.engines['google'])
        encoded_query = urllib.parse.quote_plus(query)
        return engine_info['base'].format(encoded_query)


@cmdutils.register(name='search-advanced')
@cmdutils.argument('query', completion='searchengine')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def search_advanced(query: str, win_id: int, 
                    site: str = None,
                    filetype: str = None,
                    intitle: str = None,
                    inurl: str = None,
                    intext: str = None,
                    exclude: str = None,
                    exact: str = None) -> None:
    """Perform advanced search with operators.
    
    Args:
        query: Base search query
        site: Limit to specific site (e.g., github.com)
        filetype: Search for specific file types (pdf, doc, xls, etc.)
        intitle: Search in page titles
        inurl: Search in URLs
        intext: Search in page text
        exclude: Terms to exclude (comma-separated)
        exact: Exact phrase to search
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    builder = SearchQueryBuilder()
    
    # Build operators dictionary
    operators = {}
    if site:
        operators['site'] = site
    if filetype:
        operators['filetype'] = filetype
    if intitle:
        operators['intitle'] = intitle
    if inurl:
        operators['inurl'] = inurl
    if intext:
        operators['intext'] = intext
    if exclude:
        operators['exclude'] = exclude
    if exact:
        operators['exact'] = exact
    
    # Build and open search for multiple engines
    engines_to_use = ['google', 'bing', 'duckduckgo']
    for engine in engines_to_use:
        built_query = builder.build_query(query, operators, engine)
        url = builder.build_url(built_query, engine)
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Advanced search: {query} with {len(operators)} operators")


@cmdutils.register(name='search-cross')
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def search_cross_engine(query: str, win_id: int) -> None:
    """Cross-engine triangulation search.
    
    Searches the same query across multiple search engines simultaneously
    to leverage different indexing and ranking algorithms.
    
    Args:
        query: The search query
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    builder = SearchQueryBuilder()
    
    # Use all available search engines
    all_engines = ['google', 'bing', 'duckduckgo', 'yandex', 'startpage', 
                   'qwant', 'ecosia', 'searx']
    
    for engine in all_engines:
        url = builder.build_url(query, engine)
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Cross-engine search across {len(all_engines)} engines: {query}")


@cmdutils.register(name='search-proximity')
@cmdutils.argument('term1')
@cmdutils.argument('term2')
@cmdutils.argument('distance', choices=['1', '2', '3', '4', '5', '10', '15', '20'])
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def search_proximity(term1: str, term2: str, distance: str, win_id: int) -> None:
    """Proximity search using AROUND operator.
    
    Finds pages where two terms appear within a specified number of words
    of each other.
    
    Args:
        term1: First search term
        term2: Second search term
        distance: Maximum word distance between terms
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Google supports AROUND operator
    google_query = f'"{term1}" AROUND({distance}) "{term2}"'
    google_url = f'https://www.google.com/search?q={urllib.parse.quote_plus(google_query)}'
    
    # Bing uses NEAR operator
    bing_query = f'"{term1}" NEAR:{distance} "{term2}"'
    bing_url = f'https://www.bing.com/search?q={urllib.parse.quote_plus(bing_query)}'
    
    tabbed_browser.tabopen(QUrl(google_url))
    tabbed_browser.tabopen(QUrl(bing_url), background=True)
    
    message.info(f"Proximity search: '{term1}' within {distance} words of '{term2}'")


@cmdutils.register(name='search-wildcard')
@cmdutils.argument('pattern')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def search_wildcard(pattern: str, win_id: int) -> None:
    """Wildcard search with * placeholder.
    
    Use * to represent unknown words in a phrase.
    Example: "how to * in Python" finds variations like "how to code in Python"
    
    Args:
        pattern: Search pattern with * wildcards
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Ensure pattern is quoted if it contains wildcards
    if '*' in pattern and not pattern.startswith('"'):
        pattern = f'"{pattern}"'
    
    engines = ['google', 'bing', 'duckduckgo']
    for engine in engines:
        if engine == 'google':
            url = f'https://www.google.com/search?q={urllib.parse.quote_plus(pattern)}'
        elif engine == 'bing':
            url = f'https://www.bing.com/search?q={urllib.parse.quote_plus(pattern)}'
        else:
            url = f'https://duckduckgo.com/?q={urllib.parse.quote_plus(pattern)}'
        
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Wildcard search: {pattern}")


@cmdutils.register(name='search-boolean')
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def search_boolean(query: str, win_id: int) -> None:
    """Boolean search with OR, AND, NOT operators.
    
    Use OR for alternatives, AND for required terms, NOT or - for exclusions.
    Use parentheses to group terms.
    Example: (python OR javascript) AND tutorial -video
    
    Args:
        query: Boolean search query
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Ensure OR is capitalized
    query = re.sub(r'\bor\b', 'OR', query, flags=re.IGNORECASE)
    query = re.sub(r'\band\b', 'AND', query, flags=re.IGNORECASE)
    query = re.sub(r'\bnot\b', 'NOT', query, flags=re.IGNORECASE)
    
    engines = ['google', 'bing', 'duckduckgo']
    for engine in engines:
        if engine == 'google':
            url = f'https://www.google.com/search?q={urllib.parse.quote_plus(query)}'
        elif engine == 'bing':
            url = f'https://www.bing.com/search?q={urllib.parse.quote_plus(query)}'
        else:
            url = f'https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}'
        
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Boolean search: {query}")


@cmdutils.register(name='search-ip')
@cmdutils.argument('ip_address')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def search_ip(ip_address: str, win_id: int) -> None:
    """Search for websites hosted at a specific IP address.
    
    Uses Bing's ip: operator and other IP intelligence services.
    
    Args:
        ip_address: The IP address to search
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Validate IP format
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if not ip_pattern.match(ip_address):
        message.error(f"Invalid IP address format: {ip_address}")
        return
    
    # Bing IP search
    bing_url = f'https://www.bing.com/search?q=ip:{ip_address}'
    
    # Other IP intelligence services
    services = [
        f'https://www.shodan.io/host/{ip_address}',
        f'https://www.virustotal.com/gui/ip-address/{ip_address}',
        f'https://www.abuseipdb.com/check/{ip_address}',
        f'https://ipinfo.io/{ip_address}',
        f'https://search.censys.io/hosts/{ip_address}',
        f'https://www.robtex.com/ip-lookup/{ip_address}',
        f'https://www.threatcrowd.org/ip.php?ip={ip_address}',
        f'https://www.hybrid-analysis.com/search?query={ip_address}'
    ]
    
    tabbed_browser.tabopen(QUrl(bing_url))
    for service_url in services:
        tabbed_browser.tabopen(QUrl(service_url), background=True)
    
    message.info(f"IP address search: {ip_address}")


@cmdutils.register(name='search-cache')
@cmdutils.argument('url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def search_cache(url: str, win_id: int) -> None:
    """View cached versions of a webpage.
    
    Retrieves cached versions from Google, Bing, and archive services.
    
    Args:
        url: The URL to find cached versions of
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Clean URL (remove protocol if present)
    clean_url = url.replace('https://', '').replace('http://', '').strip('/')
    
    # Cache services
    cache_urls = [
        f'https://webcache.googleusercontent.com/search?q=cache:{clean_url}',
        f'https://www.bing.com/search?q=cache:{clean_url}',
        f'https://web.archive.org/web/*/{clean_url}',
        f'https://archive.is/{clean_url}',
        f'https://archive.today/{clean_url}',
        f'https://cachedview.com/page?url={urllib.parse.quote_plus(url)}'
    ]
    
    for cache_url in cache_urls:
        tabbed_browser.tabopen(QUrl(cache_url), background=True)
    
    message.info(f"Cache search for: {clean_url}")


@cmdutils.register(name='search-help')
def search_help() -> None:
    """Display help for advanced search commands."""
    help_text = """
Advanced Search Commands:

1. :search-advanced <query> [options]
   - Perform search with multiple operators
   - Options: --site, --filetype, --intitle, --inurl, --intext, --exclude, --exact
   - Example: :search-advanced python --site:github.com --filetype:pdf

2. :search-cross <query>
   - Cross-engine triangulation across 8+ search engines
   - Example: :search-cross "advanced qutebrowser features"

3. :search-proximity <term1> <term2> <distance>
   - Find terms within N words of each other
   - Example: :search-proximity python tutorial 5

4. :search-wildcard <pattern>
   - Use * as placeholder for unknown words
   - Example: :search-wildcard "how to * in Python"

5. :search-boolean <query>
   - Boolean search with OR, AND, NOT, parentheses
   - Example: :search-boolean "(python OR javascript) AND tutorial -video"

6. :search-ip <ip_address>
   - Find websites hosted at an IP address
   - Example: :search-ip 192.168.1.1

7. :search-cache <url>
   - View cached versions of a webpage
   - Example: :search-cache example.com

Tips:
- Use quotes for exact phrases
- Combine operators for powerful searches
- Tab completion works for all commands
    """
    message.info(help_text)
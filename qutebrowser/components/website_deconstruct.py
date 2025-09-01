# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Website Deconstruction & Hidden Content Discovery for qutebrowser.

Implements robots.txt analysis, sitemap parsing, and hidden content discovery.
"""

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urlparse, urljoin

from PyQt6.QtCore import QUrl

from qutebrowser.api import cmdutils
from qutebrowser.utils import message, objreg


class WebsiteDeconstructor:
    """Handle website structure analysis and hidden content discovery."""
    
    def __init__(self):
        self.common_hidden_paths = [
            '/admin', '/administrator', '/wp-admin', '/wp-login.php',
            '/login', '/signin', '/auth', '/authenticate',
            '/api', '/api/v1', '/api/v2', '/graphql', '/rest',
            '/backup', '/backups', '/db', '/database', '/sql',
            '/temp', '/tmp', '/cache', '/logs', '/log',
            '/test', '/tests', '/testing', '/dev', '/development',
            '/stage', '/staging', '/demo', '/sandbox',
            '/config', '/configuration', '/settings', '/setup',
            '/private', '/secure', '/secret', '/hidden',
            '/upload', '/uploads', '/files', '/documents', '/media',
            '/download', '/downloads', '/export', '/exports',
            '/.git', '/.svn', '/.hg', '/.bzr',
            '/.env', '/.env.local', '/.env.production',
            '/.htaccess', '/.htpasswd', '/.DS_Store',
            '/robots.txt', '/sitemap.xml', '/sitemap_index.xml',
            '/crossdomain.xml', '/clientaccesspolicy.xml',
            '/swagger', '/swagger-ui', '/api-docs',
            '/phpmyadmin', '/pma', '/mysql', '/myadmin',
            '/console', '/shell', '/terminal', '/cmd',
            '/backup.sql', '/dump.sql', '/database.sql',
            '/config.php', '/configuration.php', '/settings.php',
            '/web.config', '/app.config', '/package.json',
            '/composer.json', '/requirements.txt', '/Gemfile'
        ]
        
        self.interesting_file_extensions = [
            '.bak', '.backup', '.old', '.orig', '.original',
            '.save', '.saved', '.copy', '.temp', '.tmp',
            '.swp', '.swo', '.swn',  # Vim swap files
            '.log', '.logs', '.out', '.err', '.error',
            '.sql', '.dump', '.db', '.sqlite', '.sqlite3',
            '.tar', '.tar.gz', '.tar.bz2', '.zip', '.rar', '.7z',
            '.conf', '.config', '.cfg', '.ini', '.yaml', '.yml',
            '.json', '.xml', '.csv', '.xls', '.xlsx',
            '.key', '.pem', '.crt', '.cert', '.p12', '.pfx',
            '.txt', '.md', '.rst', '.doc', '.docx', '.pdf'
        ]
    
    def parse_robots_txt(self, content: str) -> Dict[str, List[str]]:
        """Parse robots.txt content and extract interesting paths."""
        result = {
            'disallowed': [],
            'allowed': [],
            'sitemaps': [],
            'crawl_delay': None,
            'interesting_paths': []
        }
        
        lines = content.split('\n')
        current_user_agent = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if ':' not in line:
                continue
            
            directive, value = line.split(':', 1)
            directive = directive.strip().lower()
            value = value.strip()
            
            if directive == 'user-agent':
                current_user_agent = value.lower()
            elif directive == 'disallow' and value:
                result['disallowed'].append(value)
                # Disallowed paths are often interesting
                if any(keyword in value.lower() for keyword in 
                      ['admin', 'private', 'secure', 'api', 'config', 'backup']):
                    result['interesting_paths'].append(value)
            elif directive == 'allow' and value:
                result['allowed'].append(value)
            elif directive == 'sitemap':
                result['sitemaps'].append(value)
            elif directive == 'crawl-delay':
                try:
                    result['crawl_delay'] = float(value)
                except ValueError:
                    pass
        
        return result
    
    def parse_sitemap_xml(self, content: str) -> Dict[str, List[str]]:
        """Parse sitemap.xml and extract URLs."""
        result = {
            'urls': [],
            'sitemaps': [],  # For sitemap index files
            'images': [],
            'videos': []
        }
        
        try:
            root = ET.fromstring(content)
            
            # Handle different sitemap namespaces
            namespaces = {
                '': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'image': 'http://www.google.com/schemas/sitemap-image/1.1',
                'video': 'http://www.google.com/schemas/sitemap-video/1.1'
            }
            
            # Extract URLs from regular sitemap
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None and loc.text:
                    result['urls'].append(loc.text)
                
                # Extract image URLs
                for img in url_elem.findall('.//{http://www.google.com/schemas/sitemap-image/1.1}loc'):
                    if img.text:
                        result['images'].append(img.text)
                
                # Extract video URLs
                for vid in url_elem.findall('.//{http://www.google.com/schemas/sitemap-video/1.1}content_loc'):
                    if vid.text:
                        result['videos'].append(vid.text)
            
            # Handle sitemap index files
            for sitemap_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc = sitemap_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None and loc.text:
                    result['sitemaps'].append(loc.text)
        
        except ET.ParseError as e:
            message.warning(f"Failed to parse sitemap XML: {e}")
        
        return result
    
    def extract_base_domain(self, url: str) -> str:
        """Extract base domain from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"


@cmdutils.register(name='robots-analyze')
@cmdutils.argument('domain')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def analyze_robots_txt(domain: str, win_id: int) -> None:
    """Analyze robots.txt for hidden directories and interesting paths.
    
    Fetches and analyzes a website's robots.txt file to discover potentially
    sensitive or hidden directories that are disallowed from crawling.
    
    Args:
        domain: The domain to analyze (e.g., example.com)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    decon = WebsiteDeconstructor()
    
    # Ensure proper URL format
    if not domain.startswith(('http://', 'https://')):
        domain = 'https://' + domain
    
    base_url = decon.extract_base_domain(domain)
    robots_url = urljoin(base_url, '/robots.txt')
    
    # Open robots.txt
    tabbed_browser.tabopen(QUrl(robots_url))
    
    # Also check historical robots.txt
    wayback_robots = f'https://web.archive.org/web/*/robots.txt/{base_url}/robots.txt'
    tabbed_browser.tabopen(QUrl(wayback_robots), background=True)
    
    # Try to fetch and parse robots.txt
    try:
        with urllib.request.urlopen(robots_url, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            parsed = decon.parse_robots_txt(content)
            
            # Open interesting disallowed paths
            for path in parsed['interesting_paths'][:10]:  # Limit to 10 paths
                full_url = urljoin(base_url, path)
                tabbed_browser.tabopen(QUrl(full_url), background=True)
            
            # Open sitemaps
            for sitemap in parsed['sitemaps'][:5]:
                if not sitemap.startswith(('http://', 'https://')):
                    sitemap = urljoin(base_url, sitemap)
                tabbed_browser.tabopen(QUrl(sitemap), background=True)
            
            message.info(f"Robots.txt analysis: Found {len(parsed['disallowed'])} disallowed paths")
            if parsed['interesting_paths']:
                message.info(f"Opening {min(10, len(parsed['interesting_paths']))} interesting paths")
    
    except Exception as e:
        message.warning(f"Could not fetch robots.txt: {e}")
        message.info("Opening robots.txt and Wayback Machine for manual analysis")


@cmdutils.register(name='sitemap-analyze')
@cmdutils.argument('domain')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def analyze_sitemap(domain: str, win_id: int) -> None:
    """Analyze sitemap.xml to discover all indexed pages.
    
    Fetches and analyzes a website's sitemap to discover all pages intended
    for indexing, including potential orphan pages.
    
    Args:
        domain: The domain to analyze (e.g., example.com)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    decon = WebsiteDeconstructor()
    
    # Ensure proper URL format
    if not domain.startswith(('http://', 'https://')):
        domain = 'https://' + domain
    
    base_url = decon.extract_base_domain(domain)
    
    # Common sitemap locations
    sitemap_urls = [
        urljoin(base_url, '/sitemap.xml'),
        urljoin(base_url, '/sitemap_index.xml'),
        urljoin(base_url, '/sitemap1.xml'),
        urljoin(base_url, '/sitemaps/sitemap.xml'),
        urljoin(base_url, '/sitemap/sitemap.xml'),
        urljoin(base_url, '/sitemap.xml.gz'),
        urljoin(base_url, '/sitemap-main.xml'),
        urljoin(base_url, '/wp-sitemap.xml'),  # WordPress
        urljoin(base_url, '/post-sitemap.xml'),  # WordPress
        urljoin(base_url, '/page-sitemap.xml'),  # WordPress
    ]
    
    # Open sitemap URLs
    for sitemap_url in sitemap_urls[:5]:
        tabbed_browser.tabopen(QUrl(sitemap_url), background=True)
    
    # Try to fetch and parse main sitemap
    main_sitemap = urljoin(base_url, '/sitemap.xml')
    try:
        with urllib.request.urlopen(main_sitemap, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            parsed = decon.parse_sitemap_xml(content)
            
            # If it's a sitemap index, open the individual sitemaps
            if parsed['sitemaps']:
                for sitemap in parsed['sitemaps'][:5]:
                    tabbed_browser.tabopen(QUrl(sitemap), background=True)
                message.info(f"Sitemap index found: {len(parsed['sitemaps'])} sitemaps")
            
            # Open a sample of discovered URLs
            if parsed['urls']:
                sample_urls = parsed['urls'][:10]
                for url in sample_urls:
                    tabbed_browser.tabopen(QUrl(url), background=True)
                message.info(f"Sitemap analysis: Found {len(parsed['urls'])} URLs")
    
    except Exception as e:
        message.warning(f"Could not fetch sitemap: {e}")
        message.info("Opening common sitemap locations for manual analysis")


@cmdutils.register(name='orphan-find')
@cmdutils.argument('domain')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def find_orphan_pages(domain: str, win_id: int) -> None:
    """Find orphan pages using sitemap and search engines.
    
    Discovers unlinked "orphan" pages by comparing sitemap entries with
    crawled/indexed pages.
    
    Args:
        domain: The domain to analyze (e.g., example.com)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Ensure proper URL format
    if not domain.startswith(('http://', 'https://')):
        domain = 'https://' + domain
    
    # Clean domain for search
    clean_domain = domain.replace('https://', '').replace('http://', '').strip('/')
    
    # Search for pages indexed by search engines
    search_queries = [
        f'site:{clean_domain}',
        f'site:{clean_domain} -inurl:www',
        f'site:{clean_domain} inurl:test',
        f'site:{clean_domain} inurl:dev',
        f'site:{clean_domain} inurl:staging',
        f'site:{clean_domain} inurl:old',
        f'site:{clean_domain} inurl:backup',
        f'site:{clean_domain} inurl:archive',
        f'site:{clean_domain} inurl:beta',
        f'site:{clean_domain} inurl:alpha',
        f'site:{clean_domain} inurl:demo',
        f'site:{clean_domain} inurl:temp',
        f'site:{clean_domain} filetype:pdf',
        f'site:{clean_domain} filetype:doc',
        f'site:{clean_domain} filetype:xls'
    ]
    
    # Open searches in different search engines
    for query in search_queries[:8]:
        google_url = f'https://www.google.com/search?q={urllib.parse.quote_plus(query)}'
        tabbed_browser.tabopen(QUrl(google_url), background=True)
    
    # Also open sitemap for comparison
    sitemap_url = urljoin(domain, '/sitemap.xml')
    tabbed_browser.tabopen(QUrl(sitemap_url), background=True)
    
    # Open tools for finding orphan pages
    tools = [
        f'https://www.xml-sitemaps.com/validate-xml-sitemap.html?sitemap={urllib.parse.quote_plus(sitemap_url)}',
        f'https://www.google.com/search?q=site:{clean_domain}+-inurl:index',
        f'https://www.bing.com/search?q=site:{clean_domain}'
    ]
    
    for tool_url in tools:
        tabbed_browser.tabopen(QUrl(tool_url), background=True)
    
    message.info("Orphan page discovery initiated")
    message.info("Compare sitemap URLs with search engine results")


@cmdutils.register(name='hidden-discover')
@cmdutils.argument('domain')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def discover_hidden_content(domain: str, win_id: int) -> None:
    """Discover hidden directories and files.
    
    Attempts to find hidden content using common paths and search techniques.
    
    Args:
        domain: The domain to analyze (e.g., example.com)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    decon = WebsiteDeconstructor()
    
    # Ensure proper URL format
    if not domain.startswith(('http://', 'https://')):
        domain = 'https://' + domain
    
    base_url = decon.extract_base_domain(domain)
    clean_domain = domain.replace('https://', '').replace('http://', '').strip('/')
    
    # Check common hidden paths
    paths_to_check = decon.common_hidden_paths[:15]
    for path in paths_to_check:
        full_url = urljoin(base_url, path)
        tabbed_browser.tabopen(QUrl(full_url), background=True)
    
    # Search for exposed files
    file_searches = [
        f'site:{clean_domain} ext:sql',
        f'site:{clean_domain} ext:bak',
        f'site:{clean_domain} ext:log',
        f'site:{clean_domain} ext:config',
        f'site:{clean_domain} ext:env',
        f'site:{clean_domain} ext:git',
        f'site:{clean_domain} "index of /"',
        f'site:{clean_domain} "parent directory"',
        f'site:{clean_domain} "directory listing"'
    ]
    
    for query in file_searches:
        google_url = f'https://www.google.com/search?q={urllib.parse.quote_plus(query)}'
        tabbed_browser.tabopen(QUrl(google_url), background=True)
    
    message.info(f"Hidden content discovery: Checking {len(paths_to_check)} common paths")
    message.info("Also searching for exposed files and directory listings")


@cmdutils.register(name='wayback-discover')
@cmdutils.argument('domain')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def wayback_discovery(domain: str, win_id: int) -> None:
    """Discover historical content using Wayback Machine.
    
    Explores archived versions of the website to find old/removed content.
    
    Args:
        domain: The domain to analyze (e.g., example.com)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Ensure proper URL format
    if not domain.startswith(('http://', 'https://')):
        domain = 'https://' + domain
    
    clean_domain = domain.replace('https://', '').replace('http://', '')
    
    # Wayback Machine searches
    wayback_urls = [
        f'https://web.archive.org/web/*/{domain}',
        f'https://web.archive.org/web/*/{domain}/*',
        f'https://web.archive.org/web/*/{domain}/robots.txt',
        f'https://web.archive.org/web/*/{domain}/sitemap.xml',
        f'https://web.archive.org/web/*/{domain}/admin',
        f'https://web.archive.org/web/*/{domain}/login',
        f'https://web.archive.org/web/*/{domain}/api',
        f'https://web.archive.org/web/*/{domain}/backup',
        f'https://web.archive.org/web/*/{domain}/.git',
        f'https://web.archive.org/web/*/{domain}/wp-admin',
        f'https://web.archive.org/web/2010*/{domain}',  # Old versions
        f'https://web.archive.org/web/2015*/{domain}',
        f'https://web.archive.org/web/2020*/{domain}'
    ]
    
    for url in wayback_urls[:10]:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Also check other archive services
    other_archives = [
        f'https://archive.is/{domain}',
        f'https://archive.today/{domain}',
        f'https://cachedview.com/page?url={urllib.parse.quote_plus(domain)}',
        f'https://www.google.com/search?q=cache:{clean_domain}'
    ]
    
    for archive_url in other_archives:
        tabbed_browser.tabopen(QUrl(archive_url), background=True)
    
    message.info("Historical content discovery initiated")
    message.info("Check different time periods for removed content")


@cmdutils.register(name='config-find')
@cmdutils.argument('domain')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def find_config_files(domain: str, win_id: int) -> None:
    """Find exposed configuration and sensitive files.
    
    Searches for accidentally exposed configuration files, backups, and
    sensitive data.
    
    Args:
        domain: The domain to analyze (e.g., example.com)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    decon = WebsiteDeconstructor()
    
    # Ensure proper URL format
    if not domain.startswith(('http://', 'https://')):
        domain = 'https://' + domain
    
    base_url = decon.extract_base_domain(domain)
    clean_domain = domain.replace('https://', '').replace('http://', '').strip('/')
    
    # Common configuration files
    config_files = [
        '/.env', '/.env.local', '/.env.production', '/.env.development',
        '/config.php', '/configuration.php', '/settings.php', '/wp-config.php',
        '/config.json', '/settings.json', '/package.json', '/composer.json',
        '/web.config', '/app.config', '/.htaccess', '/.htpasswd',
        '/database.yml', '/database.yaml', '/config.yml', '/config.yaml',
        '/Dockerfile', '/docker-compose.yml', '/.dockerignore',
        '/.git/config', '/.git/HEAD', '/.gitignore',
        '/backup.sql', '/dump.sql', '/database.sql', '/db.sql',
        '/phpinfo.php', '/info.php', '/test.php', '/debug.php',
        '/readme.txt', '/README.md', '/CHANGELOG.md', '/TODO.md',
        '/crossdomain.xml', '/clientaccesspolicy.xml'
    ]
    
    # Check config files
    for file_path in config_files[:20]:
        full_url = urljoin(base_url, file_path)
        tabbed_browser.tabopen(QUrl(full_url), background=True)
    
    # Search for exposed configs
    config_searches = [
        f'site:{clean_domain} "db_password"',
        f'site:{clean_domain} "api_key"',
        f'site:{clean_domain} "secret_key"',
        f'site:{clean_domain} "aws_access_key"',
        f'site:{clean_domain} "private_key"',
        f'site:{clean_domain} "connectionstring"',
        f'site:{clean_domain} "SMTP_PASSWORD"',
        f'site:{clean_domain} ext:env',
        f'site:{clean_domain} ext:config',
        f'site:{clean_domain} ext:ini'
    ]
    
    for query in config_searches[:5]:
        google_url = f'https://www.google.com/search?q={urllib.parse.quote_plus(query)}'
        tabbed_browser.tabopen(QUrl(google_url), background=True)
    
    message.info("Configuration file discovery initiated")
    message.warning("Be responsible - do not access unauthorized content")


@cmdutils.register(name='decon-help')
def website_deconstruction_help() -> None:
    """Display help for website deconstruction commands."""
    help_text = """
Website Deconstruction Commands:

1. :robots-analyze <domain>
   - Analyze robots.txt for hidden directories
   - Check historical robots.txt via Wayback Machine
   - Example: :robots-analyze example.com

2. :sitemap-analyze <domain>
   - Parse sitemap.xml to discover all pages
   - Find sitemap index files
   - Example: :sitemap-analyze example.com

3. :orphan-find <domain>
   - Find unlinked orphan pages
   - Compare sitemap with search results
   - Example: :orphan-find example.com

4. :hidden-discover <domain>
   - Check common hidden paths
   - Search for exposed files
   - Example: :hidden-discover example.com

5. :wayback-discover <domain>
   - Explore archived versions
   - Find removed/old content
   - Example: :wayback-discover example.com

6. :config-find <domain>
   - Search for exposed config files
   - Find backup and sensitive files
   - Example: :config-find example.com

Tips:
- Many commands open multiple tabs
- Check robots.txt first for clues
- Compare current and historical versions
- Be ethical - respect boundaries
    """
    message.info(help_text)
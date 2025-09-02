# SPDX-FileCopyrightText: 2025 qutebrowser contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""OSINT (Open Source Intelligence) commands for qutebrowser."""

import urllib.parse
from typing import Optional

from qutebrowser.api import cmdutils
from qutebrowser.config import config
from qutebrowser.utils import message, objreg, qtutils
from qutebrowser.qt.core import QUrl


class OSINTCommands:
    """OSINT command dispatcher for browser intelligence gathering.
    
    Contains commands for supply chain analysis, corporate intelligence,
    and various OSINT data collection techniques.
    """

    def __init__(self, win_id, tabbed_browser):
        self._win_id = win_id
        self._tabbed_browser = tabbed_browser

    def _open_url(self, url: str, background: Optional[bool] = None):
        """Helper to open a URL in a new tab."""
        if background is None:
            background = config.val.osint.open_tabs_background
        self._tabbed_browser.tabopen(QUrl(url), background=background)

    def _open_multiple_urls(self, urls: list[str]):
        """Helper to open multiple URLs in new tabs."""
        max_tabs = config.val.osint.max_tabs_per_search
        urls_to_open = urls[:max_tabs]
        
        if len(urls) > max_tabs:
            message.warning(f"Opening only first {max_tabs} tabs (configured limit)")
        
        for i, url in enumerate(urls_to_open):
            # Open first tab in foreground if configured, rest follow config
            background = config.val.osint.open_tabs_background if i > 0 else False
            self._open_url(url, background=background)

    def _get_current_url(self):
        """Get the current page URL."""
        try:
            return self._tabbed_browser.current_url()
        except qtutils.QtValueError:
            raise cmdutils.CommandError("No valid URL in current tab")

    def _get_current_domain(self):
        """Get the current page domain."""
        url = self._get_current_url()
        return url.host()

    # ============================================================================
    # Supply Chain Deconstruction Commands
    # ============================================================================

    @cmdutils.register(instance='osint-commands', scope='window')
    @cmdutils.argument('company_name', completion=None)
    def trade_lookup(self, company_name: str):
        """Search global trade databases for a company's shipping manifests.
        
        Opens multiple trade data platforms with pre-filled searches for the
        specified company to analyze import/export records, suppliers, and customers.
        
        Args:
            company_name: Name of the company to search for.
        """
        encoded_name = urllib.parse.quote(company_name)
        
        # Build URLs based on configured sources
        source_urls = {
            'importyeti': f"https://www.importyeti.com/search?q={encoded_name}",
            'panjiva': f"https://panjiva.com/search?q={encoded_name}",
            'zauba': f"https://www.zauba.com/import-search.php?search={encoded_name}",
            'volza': f"https://www.volza.com/search/?q={encoded_name}",
            'seair': f"https://www.seair.co.in/us-import-export-data-search.aspx?q={encoded_name}"
        }
        
        # Only use configured sources
        configured_sources = config.val.osint.trade_data_sources
        urls = [source_urls[source] for source in configured_sources 
                if source in source_urls]
        
        if not urls:
            message.warning("No trade data sources configured")
            return
        
        self._open_multiple_urls(urls)
        message.info(f"Opened trade data searches for: {company_name}")

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='tech-stack')
    def tech_stack_analysis(self):
        """Identify the technology stack of the current website.
        
        Opens technology profiler services to detect frameworks, libraries,
        and services used by the current website.
        """
        current_url = self._get_current_url()
        domain = self._get_current_domain()
        
        if not domain:
            raise cmdutils.CommandError("Cannot determine domain from current URL")
        
        urls = [
            f"https://builtwith.com/{domain}",
            f"https://www.wappalyzer.com/lookup/{domain}",
            f"https://w3techs.com/sites/info/{domain}",
            f"https://whatcms.org/?s={domain}"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Analyzing technology stack for: {domain}")

    @cmdutils.register(instance='osint-commands', scope='window')
    @cmdutils.argument('software_name', completion=None)
    @cmdutils.argument('version', completion=None)
    def cve_lookup(self, software_name: str, version: Optional[str] = None):
        """Check for vulnerabilities in a software component.
        
        Queries vulnerability databases for known CVEs affecting the specified
        software and version.
        
        Args:
            software_name: Name of the software to check.
            version: Optional version number.
        """
        query = software_name
        if version:
            query += f" {version}"
        
        encoded_query = urllib.parse.quote(query)
        
        # Build URLs based on configured sources
        source_urls = {
            'nvd': f"https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&query={encoded_query}",
            'mitre': f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={encoded_query}",
            'vulners': f"https://vulners.com/search?query={encoded_query}",
            'cvedetails': f"https://www.cvedetails.com/google-search-results.php?q={encoded_query}",
            'snyk': f"https://snyk.io/vuln/search?q={encoded_query}&type=any"
        }
        
        # Only use configured sources
        configured_sources = config.val.osint.vulnerability_databases
        urls = [source_urls[source] for source in configured_sources 
                if source in source_urls]
        
        if not urls:
            message.warning("No vulnerability databases configured")
            return
        
        self._open_multiple_urls(urls)
        message.info(f"Searching vulnerabilities for: {query}")

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='due-diligence')
    @cmdutils.argument('company_name', completion=None)
    def vendor_due_diligence(self, company_name: str):
        """Perform comprehensive vendor due diligence.
        
        Opens multiple tabs for corporate records, legal filings, security posture,
        and breach history analysis of the specified company.
        
        Args:
            company_name: Name of the company to investigate.
        """
        encoded_name = urllib.parse.quote(company_name)
        domain_guess = company_name.lower().replace(' ', '') + '.com'
        
        urls = [
            # Corporate Records
            f"https://opencorporates.com/companies?q={encoded_name}",
            f"https://www.dnb.com/business-directory/company-search.html?term={encoded_name}",
            
            # Legal Filings
            f"https://www.courtlistener.com/?q={encoded_name}&type=o",
            f"https://www.justia.com/search?q={encoded_name}",
            f"https://www.plainsite.org/search/?q={encoded_name}",
            
            # Security Posture
            f"https://www.shodan.io/search?query={encoded_name}",
            f"https://search.censys.io/search?resource=hosts&q={encoded_name}",
            f"https://securityscorecard.com/research/search/{domain_guess}",
            
            # Breach History
            f"https://haveibeenpwned.com/DomainSearch/{domain_guess}",
            f"https://breachdirectory.org/search?domain={domain_guess}",
            f"https://www.dehashed.com/search?query={encoded_name}"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Performing due diligence on: {company_name}")

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='vendor-map')
    def vendor_mapping(self):
        """Map fourth-party vendors from the current website.
        
        Analyzes the current page for mentions of third-party services and
        sub-processors to identify hidden dependencies.
        """
        current_url = self._get_current_url()
        domain = self._get_current_domain()
        
        if not domain:
            raise cmdutils.CommandError("Cannot determine domain from current URL")
        
        # First, open privacy and terms pages to find vendor mentions
        base_url = f"{current_url.scheme()}://{domain}"
        
        urls = [
            f"{base_url}/privacy",
            f"{base_url}/privacy-policy",
            f"{base_url}/terms",
            f"{base_url}/terms-of-service",
            f"{base_url}/security",
            f"{base_url}/sub-processors",
            f"{base_url}/third-party",
            f"{base_url}/vendors",
            f"{base_url}/partners"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Mapping vendors for: {domain}")

    # ============================================================================
    # Predictive Corporate Intelligence Commands
    # ============================================================================

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='jobs-analysis')
    @cmdutils.argument('company_name', completion=None)
    def talent_acquisition_analysis(self, company_name: str):
        """Analyze a company's hiring activity and strategic direction.
        
        Opens job aggregator sites to analyze open positions, skills in demand,
        and geographic expansion patterns.
        
        Args:
            company_name: Name of the company to analyze.
        """
        encoded_name = urllib.parse.quote(company_name)
        
        urls = [
            f"https://www.linkedin.com/jobs/search/?keywords={encoded_name}",
            f"https://www.indeed.com/jobs?q=company%3A%22{encoded_name}%22",
            f"https://www.glassdoor.com/Jobs/jobs.htm?sc.keyword={encoded_name}",
            f"https://www.monster.com/jobs/search?q={encoded_name}&where=",
            f"https://www.ziprecruiter.com/jobs-search?search={encoded_name}",
            f"https://angel.co/company/{encoded_name.lower().replace(' ', '-')}/jobs",
            f"https://www.dice.com/jobs?q={encoded_name}",
            f"https://remote.co/company/{encoded_name.lower().replace(' ', '-')}"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Analyzing talent acquisition for: {company_name}")

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='sentiment-check')
    @cmdutils.argument('company_name', completion=None)
    def employee_sentiment_analysis(self, company_name: str):
        """Analyze employee sentiment and reviews for a company.
        
        Opens employee review platforms to assess company culture, management,
        and potential attrition risks.
        
        Args:
            company_name: Name of the company to analyze.
        """
        encoded_name = urllib.parse.quote(company_name)
        formatted_name = company_name.lower().replace(' ', '-')
        
        urls = [
            f"https://www.glassdoor.com/Reviews/company-reviews.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword={encoded_name}",
            f"https://www.indeed.com/cmp?q={encoded_name}",
            f"https://www.comparably.com/companies/{formatted_name}",
            f"https://www.teamblind.com/company/{formatted_name}",
            f"https://www.kununu.com/us/search?q={encoded_name}",
            f"https://www.ambitionbox.com/reviews/{formatted_name}-reviews",
            f"https://www.vault.com/company-profiles/{formatted_name}"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Analyzing employee sentiment for: {company_name}")

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='sec-filings')
    @cmdutils.argument('ticker_symbol', completion=None)
    @cmdutils.argument('form_type', flag='f', completion=None)
    def financial_regulatory_monitoring(self, ticker_symbol: str, 
                                       form_type: Optional[str] = None):
        """Access SEC filings and financial disclosures for a public company.
        
        Opens the SEC EDGAR database and other financial data sources for the
        specified ticker symbol.
        
        Args:
            ticker_symbol: Stock ticker symbol (e.g., AAPL, GOOGL).
            form_type: Optional SEC form type filter (e.g., 10-K, 8-K, DEF-14A).
        """
        ticker = ticker_symbol.upper()
        
        # Base EDGAR search
        edgar_url = f"https://www.sec.gov/edgar/browse/?CIK={ticker}"
        if form_type:
            edgar_url += f"&type={form_type}"
        
        urls = [
            edgar_url,
            f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=&dateb=&owner=include&count=100",
            f"https://finance.yahoo.com/quote/{ticker}/sec-filings",
            f"https://finviz.com/quote.ashx?t={ticker}",
            f"https://www.marketwatch.com/investing/stock/{ticker}/financials",
            f"https://seekingalpha.com/symbol/{ticker}/sec-filings",
            f"https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}/sec-filings"
        ]
        
        self._open_multiple_urls(urls)
        
        form_msg = f" (Form: {form_type})" if form_type else ""
        message.info(f"Opening SEC filings for: {ticker}{form_msg}")

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='ip-lookup')
    @cmdutils.argument('company_name', completion=None)
    def intellectual_property_analysis(self, company_name: str):
        """Analyze a company's patents and trademarks.
        
        Opens intellectual property databases to investigate innovation pipeline,
        R&D focus, and strategic partnerships.
        
        Args:
            company_name: Name of the company (assignee/applicant).
        """
        encoded_name = urllib.parse.quote(company_name)
        
        urls = [
            f"https://patents.google.com/?assignee={encoded_name}",
            f"https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&p=1&u=%2Fnetahtml%2FPTO%2Fsearch-bool.html&r=0&f=S&l=50&TERM1={encoded_name}&FIELD1=ASNM&co1=AND&TERM2=&FIELD2=&d=PTXT",
            f"https://www.uspto.gov/trademarks/search?searchText={encoded_name}",
            f"https://www.wipo.int/branddb/en/search.jsp?q={encoded_name}",
            f"https://worldwide.espacenet.com/patent/search?q={encoded_name}",
            f"https://www.lens.org/lens/search/patent/list?q={encoded_name}",
            f"https://patentscope.wipo.int/search/en/search.jsf?query={encoded_name}"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Analyzing intellectual property for: {company_name}")

    # ============================================================================
    # Unmasking Anonymized Networks Commands
    # ============================================================================

    @cmdutils.register(instance='osint-commands', scope='window',
                       name='crypto-lookup')
    @cmdutils.argument('address_or_tx', completion=None)
    def cryptocurrency_forensics(self, address_or_tx: str):
        """Investigate cryptocurrency address or transaction.
        
        Opens blockchain explorers and analysis platforms to trace transactions,
        identify wallet clusters, and potential entity associations.
        
        Args:
            address_or_tx: Cryptocurrency address or transaction hash.
        """
        # Auto-detect if it's likely Bitcoin (starts with 1, 3, or bc1) or Ethereum (0x)
        is_ethereum = address_or_tx.startswith('0x')
        is_bitcoin = (address_or_tx[:1] in '13' or 
                     address_or_tx.startswith('bc1'))
        
        urls = []
        
        # Multi-chain explorers
        urls.extend([
            f"https://www.blockchain.com/explorer/search?search={address_or_tx}",
            f"https://blockchair.com/search?q={address_or_tx}",
            f"https://www.walletexplorer.com/address/{address_or_tx}",
            f"https://www.bitcoinabuse.com/reports/{address_or_tx}"
        ])
        
        if is_ethereum or len(address_or_tx) in [40, 42]:  # Ethereum address length
            urls.extend([
                f"https://etherscan.io/search?q={address_or_tx}",
                f"https://ethplorer.io/address/{address_or_tx}",
                f"https://bloxy.info/address/{address_or_tx}",
                f"https://etherchain.org/account/{address_or_tx}"
            ])
        
        if is_bitcoin or len(address_or_tx) in [26, 34, 42, 62]:  # Bitcoin address lengths
            urls.extend([
                f"https://www.blockchain.com/btc/address/{address_or_tx}",
                f"https://btc.com/{address_or_tx}",
                f"https://live.blockcypher.com/btc/address/{address_or_tx}",
                f"https://www.bitcoinwhoswho.com/address/{address_or_tx}"
            ])
        
        # Advanced analysis platforms
        urls.extend([
            f"https://intel.arkham.com/search?q={address_or_tx}",
            f"https://www.chainalysis.com/free-cryptocurrency-sanctions-screening-tools/",
            f"https://crystalblockchain.com/",
            f"https://www.elliptic.co/"
        ])
        
        self._open_multiple_urls(urls)
        message.info(f"Investigating crypto address/tx: {address_or_tx[:16]}...")

    @cmdutils.register(instance='osint-commands', scope='window',
                       name='paste-search')
    @cmdutils.argument('keyword', completion=None)
    def paste_site_search(self, keyword: str):
        """Search for keywords across paste sites and code repositories.
        
        Searches multiple paste sites for leaked data, credentials, or
        sensitive information mentions.
        
        Args:
            keyword: Keyword or phrase to search for.
        """
        encoded_keyword = urllib.parse.quote(keyword)
        
        # Google dorks for paste sites
        paste_sites = [
            "pastebin.com",
            "paste.ee",
            "ghostbin.co",
            "dpaste.com",
            "paste2.org",
            "pastebin.pl",
            "paste.mozilla.org",
            "paste.ubuntu.com",
            "paste.debian.net",
            "rentry.co",
            "justpaste.it",
            "controlc.com",
            "privatebin.net"
        ]
        
        # Build Google dork query
        site_query = " OR ".join([f"site:{site}" for site in paste_sites])
        google_dork = f'"{keyword}" ({site_query})'
        encoded_dork = urllib.parse.quote(google_dork)
        
        urls = [
            # Direct Google search with dork
            f"https://www.google.com/search?q={encoded_dork}",
            
            # Individual paste site searches where supported
            f"https://pastebin.com/search?q={encoded_keyword}",
            f"https://paste.ee/search?query={encoded_keyword}",
            
            # Code repository searches
            f"https://github.com/search?q={encoded_keyword}&type=code",
            f"https://gitlab.com/search?search={encoded_keyword}",
            f"https://gist.github.com/search?q={encoded_keyword}",
            
            # Alternative search engines
            f"https://www.bing.com/search?q={encoded_dork}",
            f"https://duckduckgo.com/?q={encoded_dork}",
            
            # Specialized paste search
            f"https://psbdmp.ws/search/{encoded_keyword}",
            f"https://www.google.com/search?q=site:psbdmp.ws+{encoded_keyword}"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Searching paste sites for: {keyword}")

    @cmdutils.register(instance='osint-commands', scope='window',
                       name='forum-search')
    @cmdutils.argument('keyword', completion=None)
    @cmdutils.argument('platform', flag='p', completion=None)
    def forum_community_search(self, keyword: str, platform: Optional[str] = None):
        """Search niche forums and communities for keywords.
        
        Searches specific online communities, forums, and discussion platforms
        for mentions of keywords, usernames, or topics.
        
        Args:
            keyword: Keyword or phrase to search for.
            platform: Optional specific platform to focus on (telegram, discord, reddit).
        """
        encoded_keyword = urllib.parse.quote(keyword)
        
        urls = []
        
        if not platform or platform == 'telegram':
            urls.extend([
                f"https://www.google.com/search?q=site:t.me+{encoded_keyword}",
                f"https://lyzem.com/?q={encoded_keyword}",
                f"https://telemetr.io/en/search?q={encoded_keyword}",
                f"https://tgstat.com/search?q={encoded_keyword}"
            ])
        
        if not platform or platform == 'discord':
            urls.extend([
                f"https://www.google.com/search?q=site:discord.com+{encoded_keyword}",
                f"https://discord.me/servers/search/{encoded_keyword}",
                f"https://disboard.org/search?keyword={encoded_keyword}"
            ])
        
        if not platform or platform == 'reddit':
            urls.extend([
                f"https://www.reddit.com/search/?q={encoded_keyword}",
                f"https://redditsearch.io/?term={encoded_keyword}&dataviz=false&aggs=false&subreddits=&searchtype=posts,comments&search=true&start=0&end=0&size=100"
            ])
        
        # General forum searches
        if not platform:
            urls.extend([
                f"https://boardreader.com/s/{encoded_keyword}.html",
                f"https://www.google.com/search?q=intext:{encoded_keyword}+forum",
                f"https://4chan.org/search?q={encoded_keyword}",
                f"https://archived.moe/_/search/text/{encoded_keyword}/",
                f"https://twitter.com/search?q={encoded_keyword}&f=live",
                f"https://www.facebook.com/search/posts/?q={encoded_keyword}"
            ])
        
        self._open_multiple_urls(urls)
        
        platform_msg = f" on {platform}" if platform else " across forums"
        message.info(f"Searching{platform_msg} for: {keyword}")

    @cmdutils.register(instance='osint-commands', scope='window',
                       name='user-activity')
    @cmdutils.argument('username', completion=None)
    def user_activity_analysis(self, username: str):
        """Analyze user activity across multiple platforms.
        
        Searches for a username across social networks and forums to identify
        coordinated behavior patterns or sock puppet accounts.
        
        Args:
            username: Username to search for across platforms.
        """
        encoded_username = urllib.parse.quote(username)
        
        urls = [
            # Social Media
            f"https://twitter.com/{username}",
            f"https://www.instagram.com/{username}",
            f"https://www.facebook.com/{username}",
            f"https://www.linkedin.com/in/{username}",
            f"https://www.reddit.com/user/{username}",
            f"https://www.youtube.com/@{username}",
            f"https://www.tiktok.com/@{username}",
            f"https://medium.com/@{username}",
            
            # Developer Platforms
            f"https://github.com/{username}",
            f"https://gitlab.com/{username}",
            f"https://stackoverflow.com/users/{username}",
            f"https://dev.to/{username}",
            
            # Forums
            f"https://news.ycombinator.com/user?id={username}",
            f"https://lobste.rs/u/{username}",
            
            # Gaming
            f"https://steamcommunity.com/id/{username}",
            f"https://www.twitch.tv/{username}",
            
            # Search aggregators
            f"https://www.google.com/search?q=%22{encoded_username}%22",
            f"https://namechk.com/search/{username}"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Analyzing activity for user: {username}")

    @cmdutils.register(instance='osint-commands', scope='window',
                       name='pivot-user')
    @cmdutils.argument('username', completion=None)
    def identity_pivoting(self, username: str):
        """Pivot across platforms to consolidate user identities.
        
        Uses username enumeration services to find all accounts associated
        with a username across hundreds of platforms.
        
        Args:
            username: Username to enumerate across platforms.
        """
        encoded_username = urllib.parse.quote(username)
        
        urls = [
            # Username enumeration services
            f"https://whatsmyname.app/search/{username}",
            f"https://namechk.com/{username}",
            f"https://checkusernames.com/search/{username}",
            f"https://knowem.com/checkusernames.php?u={username}",
            f"https://usersearch.org/search/{username}",
            f"https://instantusername.com/#{username}",
            
            # Alternative tools
            f"https://sherlock-project.github.io/search?username={username}",
            f"https://www.social-searcher.com/search-users/?q={encoded_username}",
            
            # Data breach search
            f"https://haveibeenpwned.com/unifiedsearch/{username}",
            f"https://dehashed.com/search?query={username}",
            f"https://intelx.io/?s={username}",
            
            # Email permutation if it looks like it could be one
            f"https://hunter.io/email-verifier/{username}",
            f"https://www.voilanorbert.com/verify/{username}"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Pivoting identity for username: {username}")

    # ============================================================================
    # Unified Intelligence Synthesis Commands
    # ============================================================================

    @cmdutils.register(instance='osint-commands', scope='window',
                       name='export-node')
    @cmdutils.argument('entity_type', flag='t', completion=None)
    @cmdutils.argument('entity_value', flag='v', completion=None)
    @cmdutils.argument('api_endpoint', flag='e', completion=None)
    def export_to_graph(self, entity_type: str, entity_value: str, 
                       api_endpoint: Optional[str] = None):
        """Export entity data to external graph database.
        
        Sends structured entity data to a configured API endpoint for
        integration with external graph databases or analysis tools.
        
        Args:
            entity_type: Type of entity (company, person, ip, domain, wallet).
            entity_value: Value/name of the entity.
            api_endpoint: Optional API endpoint override.
        """
        import json
        import urllib.request
        import urllib.error
        from datetime import datetime
        
        # Use configured endpoint or override
        endpoint = api_endpoint or config.val.osint.graph_api_endpoint
        
        if not endpoint:
            raise cmdutils.CommandError(
                "No graph API endpoint configured. Set osint.graph_api_endpoint "
                "or provide --api-endpoint flag"
            )
        
        # Build entity payload
        current_url = str(self._get_current_url())
        payload = {
            "entity_type": entity_type,
            "entity_value": entity_value,
            "source_url": current_url,
            "timestamp": datetime.now().isoformat(),
            "user_agent": "qutebrowser-osint/1.0"
        }
        
        try:
            # Send to API
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                endpoint,
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    message.info(f"[SUCCESS] Exported {entity_type}: {entity_value}")
                else:
                    message.error(f"[ERROR] Export failed: {response.getcode()}")
                    
        except urllib.error.URLError as e:
            message.error(f"[ERROR] Export failed: {str(e)}")

    @cmdutils.register(instance='osint-commands', scope='window',
                       name='graph-query')
    @cmdutils.argument('query_text', completion=None)
    @cmdutils.argument('api_endpoint', flag='e', completion=None)
    def query_graph_database(self, query_text: str, api_endpoint: Optional[str] = None):
        """Query external graph database from browser.
        
        Sends queries to your external graph database and displays results.
        
        Args:
            query_text: Query string for the graph database.
            api_endpoint: Optional API endpoint override.
        """
        import json
        import urllib.request
        import urllib.error
        
        # Use configured endpoint or override
        endpoint = api_endpoint or config.val.osint.graph_api_endpoint
        
        if not endpoint:
            raise cmdutils.CommandError(
                "No graph API endpoint configured. Set osint.graph_api_endpoint "
                "or provide --api-endpoint flag"
            )
        
        # Prepare query endpoint
        query_endpoint = f"{endpoint}/query"
        
        payload = {
            "query": query_text,
            "format": "json"
        }
        
        try:
            # Send to API
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                query_endpoint,
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    result_data = response.read().decode('utf-8')
                    results = json.loads(result_data)
                    
                    # Format results for display
                    formatted = json.dumps(results, indent=2)
                    
                    # Open results in new tab as data URL
                    html_content = f"""
                    <html>
                    <head>
                        <title>Graph Query Results</title>
                        <style>
                            body {{ font-family: monospace; padding: 20px; }}
                            pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                            h2 {{ color: #333; }}
                        </style>
                    </head>
                    <body>
                        <h2>Query: {query_text}</h2>
                        <pre>{formatted}</pre>
                    </body>
                    </html>
                    """
                    
                    # Create data URL and open in new tab
                    import base64
                    encoded = base64.b64encode(html_content.encode()).decode()
                    data_url = f"data:text/html;base64,{encoded}"
                    self._open_url(data_url)
                    
                    message.info(f"Query executed: {len(results)} results")
                else:
                    message.error(f"Query failed: {response.getcode()}")
                    
        except urllib.error.URLError as e:
            message.error(f"Query failed: {str(e)}")

    @cmdutils.register(instance='osint-commands', scope='window',
                       name='show-alerts')
    def show_anomaly_alerts(self):
        """Display anomaly detection alerts from external monitoring.
        
        Shows alerts that have been received from external monitoring systems
        via webhook or local service integration.
        """
        # Get alerts from internal storage
        alerts = objreg.get('osint-alerts', scope='global', default=[])
        
        if not alerts:
            message.info("No active alerts")
            return
        
        # Format alerts as HTML
        html_content = """
        <html>
        <head>
            <title>OSINT Anomaly Alerts</title>
            <style>
                body { font-family: sans-serif; padding: 20px; }
                .alert { 
                    border: 1px solid #ddd; 
                    padding: 10px; 
                    margin: 10px 0;
                    border-radius: 5px;
                }
                .alert-high { background: #ffe0e0; border-color: #ff0000; }
                .alert-medium { background: #fff0e0; border-color: #ffa500; }
                .alert-low { background: #e0f0ff; border-color: #0080ff; }
                .timestamp { color: #666; font-size: 0.9em; }
                h2 { color: #333; }
            </style>
        </head>
        <body>
            <h2>Anomaly Detection Alerts</h2>
        """
        
        for alert in alerts[-50:]:  # Show last 50 alerts
            severity = alert.get('severity', 'low')
            html_content += f"""
            <div class="alert alert-{severity}">
                <strong>{alert.get('title', 'Alert')}</strong><br>
                {alert.get('description', '')}<br>
                <span class="timestamp">{alert.get('timestamp', '')}</span>
                {f'<br><a href="{alert["link"]}">View Details</a>' if alert.get('link') else ''}
            </div>
            """
        
        html_content += "</body></html>"
        
        # Open as data URL
        import base64
        encoded = base64.b64encode(html_content.encode()).decode()
        data_url = f"data:text/html;base64,{encoded}"
        self._open_url(data_url)
        
        message.info(f"Showing {len(alerts)} alerts")

    @cmdutils.register(instance='osint-commands', scope='window',
                       name='clear-alerts')
    def clear_anomaly_alerts(self):
        """Clear all anomaly detection alerts."""
        objreg.delete('osint-alerts', scope='global')
        message.info("All alerts cleared")

    # ============================================================================
    # Advanced OSINT Utilities
    # ============================================================================

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='osint-dashboard')
    @cmdutils.argument('company_name', completion=None)
    def osint_dashboard(self, company_name: str):
        """Launch comprehensive OSINT dashboard for a company.
        
        Opens all major OSINT data sources for complete analysis including trade,
        corporate, financial, IP, and security information.
        
        Args:
            company_name: Name of the company to investigate.
        """
        message.info(f"Launching full OSINT dashboard for: {company_name}")
        
        # Run all major OSINT commands
        self.trade_lookup(company_name)
        self.vendor_due_diligence(company_name)
        self.talent_acquisition_analysis(company_name)
        self.employee_sentiment_analysis(company_name)
        self.intellectual_property_analysis(company_name)
        
        message.info(f"OSINT dashboard launched for: {company_name}")

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='domain-osint')
    def domain_investigation(self):
        """Perform OSINT investigation on the current domain.
        
        Analyzes the current website's domain across multiple intelligence sources
        including DNS, certificates, subdomains, and infrastructure.
        """
        domain = self._get_current_domain()
        
        if not domain:
            raise cmdutils.CommandError("Cannot determine domain from current URL")
        
        urls = [
            # DNS and Infrastructure
            f"https://dnsdumpster.com/dns/{domain}",
            f"https://dnslytics.com/domain/{domain}",
            f"https://securitytrails.com/domain/{domain}",
            
            # Certificates
            f"https://crt.sh/?q={domain}",
            f"https://censys.io/certificates?q={domain}",
            
            # Subdomains
            f"https://subdomains.whoisxmlapi.com/lookup/{domain}",
            f"https://www.virustotal.com/gui/domain/{domain}/relations",
            
            # Web Archive
            f"https://web.archive.org/web/*/{domain}",
            
            # Reputation
            f"https://urlvoid.com/scan/{domain}",
            f"https://www.abuseipdb.com/check/{domain}",
            
            # WHOIS
            f"https://whois.domaintools.com/{domain}",
            f"https://who.is/whois/{domain}"
        ]
        
        self._open_multiple_urls(urls)
        message.info(f"Investigating domain: {domain}")

    @cmdutils.register(instance='osint-commands', scope='window', 
                       name='person-osint')
    @cmdutils.argument('person_name', completion=None)
    @cmdutils.argument('company', flag='c', completion=None)
    def person_investigation(self, person_name: str, company: Optional[str] = None):
        """Perform OSINT investigation on an individual.
        
        Searches for professional profiles, publications, and public records.
        
        Args:
            person_name: Full name of the person to investigate.
            company: Optional company affiliation to narrow search.
        """
        encoded_name = urllib.parse.quote(person_name)
        search_query = person_name
        
        if company:
            search_query += f" {company}"
            encoded_query = urllib.parse.quote(search_query)
        else:
            encoded_query = encoded_name
        
        urls = [
            # Professional Networks
            f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}",
            f"https://www.xing.com/search/members?keywords={encoded_query}",
            
            # Academic/Research
            f"https://scholar.google.com/scholar?q={encoded_name}",
            f"https://www.researchgate.net/search/researcher?q={encoded_name}",
            f"https://orcid.org/orcid-search/search?searchQuery={encoded_name}",
            
            # Patents
            f"https://patents.google.com/?inventor={encoded_name}",
            
            # General Search
            f"https://www.google.com/search?q={encoded_query}",
            f"https://pipl.com/search/?q={encoded_name}",
            
            # Social Media
            f"https://twitter.com/search?q={encoded_query}&f=user",
            f"https://www.facebook.com/search/people/?q={encoded_query}"
        ]
        
        self._open_multiple_urls(urls)
        
        target = f"{person_name} ({company})" if company else person_name
        message.info(f"Investigating individual: {target}")


def init(win_id, parent):
    """Initialize the OSINT commands for a window.
    
    Args:
        win_id: The window ID.
        parent: The parent TabbedBrowser object.
    """
    dispatcher = OSINTCommands(win_id, parent)
    objreg.register('osint-commands', dispatcher, scope='window', window=win_id)
    return dispatcher
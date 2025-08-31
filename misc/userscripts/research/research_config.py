#!/usr/bin/env python3
"""
Advanced Research Features for qutebrowser
Implements specialized database searches, forum intelligence, and earnings analysis
"""

import os
from qutebrowser.config.configfiles import ConfigAPI
from qutebrowser.config import configdata

def setup_research_features(config):
    """Configure all research-related features"""
    
    # ========================================
    # SEARCH ENGINE CONFIGURATIONS
    # ========================================
    
    search_engines = {
        # Default search
        'DEFAULT': 'https://www.google.com/search?q={}',
        
        # === Business Registrations ===
        'sam': 'https://sam.gov/search/?keywords={}',  # US Federal contractors
        'ukc': 'https://find-and-update.company-information.service.gov.uk/search?q={}',  # UK Companies House
        'bris': 'https://e-justice.europa.eu/content_find_a_company-489-en.do?init=true&companyName={}',  # EU Business Registry
        'sec': 'https://www.sec.gov/edgar/search/#/entityName={}',  # SEC EDGAR
        'nysos': 'https://apps.dos.ny.gov/publicInquiry/EntityDisplay?q={}',  # NY Secretary of State
        'cados': 'https://businesssearch.sos.ca.gov/CBS/SearchResults?SearchType=LPLLC&SearchCriteria={}',  # California SOS
        
        # === Legal Records ===
        'pacer': 'https://pcl.uscourts.gov/pcl/pages/search/findCase.jsf?searchTerm={}',  # US Federal Courts
        'austlii': 'http://www.austlii.edu.au/cgi-bin/sinosrch.cgi?query={}',  # Australian Legal
        'eurlex': 'https://eur-lex.europa.eu/search.html?text={}',  # EU Law
        'justia': 'https://dockets.justia.com/search?query={}',  # US Court Dockets
        'canlii': 'https://www.canlii.org/en/#search/text={}',  # Canadian Legal
        
        # === Property Records ===
        'acris': 'https://a836-acris.nyc.gov/CP/LookUp/Index?borough=1&block=&lot=&easement=&parties={}',  # NYC Property
        'uklr': 'https://propertyservices.landregistry.gov.uk/#/property-search?search={}',  # UK Land Registry
        'zillow': 'https://www.zillow.com/homes/{}_rb/',  # Zillow Property Search
        'redfin': 'https://www.redfin.com/stingray/do/query-location?query={}&v=2',  # Redfin Property
        
        # === Intellectual Property ===
        'uspto': 'https://www.uspto.gov/trademarks/search?searchText={}',  # US Patents & Trademarks
        'gpatent': 'https://patents.google.com/?q={}',  # Google Patents
        'wipo': 'https://www.wipo.int/reference/en/branddb/?q={}',  # WIPO Global Brand
        'epo': 'https://worldwide.espacenet.com/patent/search?q={}',  # European Patent Office
        'tmview': 'https://www.tmdn.org/tmview/results?query={}',  # EU Trademark Search
        
        # === Academic & Scientific ===
        'scholar': 'https://scholar.google.com/scholar?q={}',  # Google Scholar
        'pubmed': 'https://pubmed.ncbi.nlm.nih.gov/?term={}',  # PubMed
        'jstor': 'https://www.jstor.org/action/doBasicSearch?Query={}',  # JSTOR
        'scopus': 'https://www.scopus.com/results/results.uri?src=s&sot=b&sdt=b&origin=searchbasic&rr=&sl=0&searchterm1={}',  # Scopus
        'ieee': 'https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={}',  # IEEE Xplore
        'arxiv': 'https://arxiv.org/search/?query={}&searchtype=all',  # arXiv
        'ssrn': 'https://papers.ssrn.com/sol3/results.cfm?npage=1&search_mode=search&txtKey_Words={}',  # SSRN
        
        # === Government Data ===
        'datagov': 'https://catalog.data.gov/dataset?q={}',  # US Data.gov
        'ukdata': 'https://data.gov.uk/search?q={}',  # UK Open Data
        'eugov': 'https://data.europa.eu/data/datasets?query={}',  # EU Open Data
        'census': 'https://data.census.gov/all?q={}',  # US Census
        'foia': 'https://www.foia.gov/search.html?query={}',  # FOIA Search
        
        # === Financial & Earnings ===
        'yahoo': 'https://finance.yahoo.com/quote/{}/analysis',  # Yahoo Finance
        'seeking': 'https://seekingalpha.com/symbol/{}/earnings/transcripts',  # Seeking Alpha Transcripts
        'fool': 'https://www.fool.com/quote/{}',  # Motley Fool
        'finviz': 'https://finviz.com/quote.ashx?t={}',  # FinViz
        
        # === Social Media & Forums ===
        'reddit': 'https://www.reddit.com/search/?q={}',  # Reddit Search
        'reddituser': 'https://www.reddit.com/search/?q=author%3A{}',  # Reddit User Search
        'hackernews': 'https://hn.algolia.com/?query={}',  # Hacker News
        'twitter': 'https://twitter.com/search?q={}',  # Twitter/X Search
        'linkedin': 'https://www.linkedin.com/search/results/all/?keywords={}',  # LinkedIn
    }
    
    config.set('url.searchengines', search_engines)
    
    # ========================================
    # COMMAND ALIASES FOR MASTER SEARCHES
    # ========================================
    
    aliases = {
        # Business Registration Master Search
        'biz-search': 'spawn --userscript multi_search.py business "{}"',
        'biz-us': 'spawn --userscript multi_search.py business-us "{}"',
        'biz-intl': 'spawn --userscript multi_search.py business-intl "{}"',
        
        # Legal Records Master Search
        'legal-search': 'spawn --userscript multi_search.py legal "{}"',
        'court-search': 'spawn --userscript multi_search.py court "{}"',
        
        # Property Records Master Search
        'prop-search': 'spawn --userscript multi_search.py property "{}"',
        'prop-nyc': 'open -t https://a836-acris.nyc.gov/CP/LookUp/Index?borough=1&block=&lot=&easement=&parties={}',
        
        # Intellectual Property Master Search
        'ip-search': 'spawn --userscript multi_search.py ip "{}"',
        'patent-search': 'spawn --userscript multi_search.py patent "{}"',
        'trademark-search': 'spawn --userscript multi_search.py trademark "{}"',
        
        # Academic Research Master Search
        'acad-search': 'spawn --userscript multi_search.py academic "{}"',
        'research': 'spawn --userscript multi_search.py research "{}"',
        
        # Government Data Master Search
        'gov-data': 'spawn --userscript multi_search.py govdata "{}"',
        'gov-search': 'spawn --userscript multi_search.py government "{}"',
        
        # Reddit User Analysis
        'reddit-user': 'open -t https://www.reddit.com/search/?q=author%3A{}',
        'reddit-sub': 'open -t https://www.reddit.com/search/?q=author%3A{0}%20subreddit%3A{1}',
        
        # Forum Discovery
        'find-forum': 'open -t https://www.google.com/search?q="{}"+"forum"+OR+"community"+OR+"discussion"',
        'find-discord': 'open -t https://www.google.com/search?q="{}"+"discord.gg"+OR+"discord+server"',
        'find-slack': 'open -t https://www.google.com/search?q="{}"+"slack"+OR+"join.slack.com"',
        
        # Earnings Analysis
        'earnings': 'spawn --userscript earnings_analysis.py "{}"',
        'transcript': 'spawn --userscript earnings_analysis.py transcript "{}"',
        'financials': 'spawn --userscript financial_analysis.py "{}"',
        
        # Combined Deep Search
        'deep-search': 'spawn --userscript deep_search.py "{}"',
        'osint': 'spawn --userscript osint_search.py "{}"',
        
        # Quick shortcuts
        'gs': 'open -t https://scholar.google.com/scholar?q={}',
        'pm': 'open -t https://pubmed.ncbi.nlm.nih.gov/?term={}',
        'sec': 'open -t https://www.sec.gov/edgar/search/#/entityName={}',
        'patent': 'open -t https://patents.google.com/?q={}',
    }
    
    config.set('aliases', aliases)
    
    # ========================================
    # KEYBINDINGS FOR QUICK ACCESS
    # ========================================
    
    # Research-specific keybindings
    config.bind(',bs', 'set-cmd-text :biz-search ')
    config.bind(',ls', 'set-cmd-text :legal-search ')
    config.bind(',ps', 'set-cmd-text :prop-search ')
    config.bind(',is', 'set-cmd-text :ip-search ')
    config.bind(',as', 'set-cmd-text :acad-search ')
    config.bind(',gs', 'set-cmd-text :gov-data ')
    config.bind(',ru', 'set-cmd-text :reddit-user ')
    config.bind(',ff', 'set-cmd-text :find-forum ')
    config.bind(',ea', 'set-cmd-text :earnings ')
    config.bind(',ds', 'set-cmd-text :deep-search ')
    
    # Quick search engine access
    config.bind(',sc', 'set-cmd-text :open -t scholar ')
    config.bind(',pm', 'set-cmd-text :open -t pubmed ')
    config.bind(',se', 'set-cmd-text :open -t sec ')
    config.bind(',pt', 'set-cmd-text :open -t gpatent ')
    
    print("Research features configured successfully!")

# Apply configuration if this is being sourced from config.py
if __name__ == '__config__':
    setup_research_features(config)
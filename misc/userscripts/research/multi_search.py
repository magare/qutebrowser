#!/usr/bin/env python3
"""
Multi-Search Userscript for qutebrowser
Opens multiple search tabs for different databases based on category
"""

import os
import sys
import urllib.parse

# Database categories with their search URLs
SEARCH_CATEGORIES = {
    'business': [
        'https://sam.gov/search/?keywords={}',
        'https://find-and-update.company-information.service.gov.uk/search?q={}',
        'https://www.sec.gov/edgar/search/#/entityName={}',
        'https://opencorporates.com/companies?q={}',
    ],
    
    'business-us': [
        'https://sam.gov/search/?keywords={}',
        'https://www.sec.gov/edgar/search/#/entityName={}',
        'https://businesssearch.sos.ca.gov/CBS/SearchResults?SearchType=LPLLC&SearchCriteria={}',
        'https://apps.dos.ny.gov/publicInquiry/EntityDisplay?q={}',
    ],
    
    'business-intl': [
        'https://find-and-update.company-information.service.gov.uk/search?q={}',
        'https://e-justice.europa.eu/content_find_a_company-489-en.do?init=true&companyName={}',
        'https://opencorporates.com/companies?q={}',
        'https://www.northdata.com/search?q={}',
    ],
    
    'legal': [
        'https://dockets.justia.com/search?query={}',
        'https://www.courtlistener.com/?q={}',
        'https://eur-lex.europa.eu/search.html?text={}',
        'https://www.canlii.org/en/#search/text={}',
    ],
    
    'court': [
        'https://pcl.uscourts.gov/pcl/pages/search/findCase.jsf?searchTerm={}',
        'https://dockets.justia.com/search?query={}',
        'https://www.courtlistener.com/?q={}',
    ],
    
    'property': [
        'https://www.zillow.com/homes/{}_rb/',
        'https://www.redfin.com/stingray/do/query-location?query={}&v=2',
        'https://www.realtor.com/realestateandhomes-search/{}',
        'https://propertyservices.landregistry.gov.uk/#/property-search?search={}',
    ],
    
    'ip': [
        'https://patents.google.com/?q={}',
        'https://www.uspto.gov/trademarks/search?searchText={}',
        'https://worldwide.espacenet.com/patent/search?q={}',
        'https://www.wipo.int/reference/en/branddb/?q={}',
    ],
    
    'patent': [
        'https://patents.google.com/?q={}',
        'https://worldwide.espacenet.com/patent/search?q={}',
        'https://patentscope.wipo.int/search/en/result.jsf?query={}',
    ],
    
    'trademark': [
        'https://www.uspto.gov/trademarks/search?searchText={}',
        'https://www.tmdn.org/tmview/results?query={}',
        'https://www.wipo.int/reference/en/branddb/?q={}',
    ],
    
    'academic': [
        'https://scholar.google.com/scholar?q={}',
        'https://pubmed.ncbi.nlm.nih.gov/?term={}',
        'https://arxiv.org/search/?query={}&searchtype=all',
        'https://www.semanticscholar.org/search?q={}',
    ],
    
    'research': [
        'https://scholar.google.com/scholar?q={}',
        'https://pubmed.ncbi.nlm.nih.gov/?term={}',
        'https://www.jstor.org/action/doBasicSearch?Query={}',
        'https://papers.ssrn.com/sol3/results.cfm?npage=1&search_mode=search&txtKey_Words={}',
    ],
    
    'govdata': [
        'https://catalog.data.gov/dataset?q={}',
        'https://data.gov.uk/search?q={}',
        'https://data.europa.eu/data/datasets?query={}',
        'https://data.census.gov/all?q={}',
    ],
    
    'government': [
        'https://www.usa.gov/search?query={}',
        'https://www.gov.uk/search/all?keywords={}',
        'https://europa.eu/search/?q={}',
        'https://www.foia.gov/search.html?query={}',
    ],
    
    'osint': [
        'https://www.google.com/search?q={}',
        'https://duckduckgo.com/?q={}',
        'https://www.bing.com/search?q={}',
        'https://search.yahoo.com/search?p={}',
        'https://pipl.com/search/?q={}',
        'https://www.spokeo.com/search?q={}',
    ],
}

def main():
    if len(sys.argv) < 3:
        print("Usage: multi_search.py <category> <search_term>", file=sys.stderr)
        sys.exit(1)
    
    category = sys.argv[1].lower()
    search_term = ' '.join(sys.argv[2:])
    
    # Get FIFO for sending commands to qutebrowser
    fifo = os.environ.get('QUTE_FIFO')
    if not fifo:
        print("QUTE_FIFO not set", file=sys.stderr)
        sys.exit(1)
    
    # Get search URLs for the category
    if category not in SEARCH_CATEGORIES:
        # If category not found, try a general search
        search_urls = [
            'https://www.google.com/search?q={}',
            'https://duckduckgo.com/?q={}',
        ]
    else:
        search_urls = SEARCH_CATEGORIES[category]
    
    # URL encode the search term
    encoded_term = urllib.parse.quote_plus(search_term)
    
    # Open each search in a new tab
    with open(fifo, 'w') as f:
        for url_template in search_urls:
            url = url_template.format(encoded_term)
            f.write(f'open -t {url}\n')
        
        # Show message
        f.write(f'message-info "Opened {len(search_urls)} search tabs for: {search_term}"\n')

if __name__ == '__main__':
    main()
# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Public Records & Specialized Databases for qutebrowser.

Access to government records, legal documents, academic research, and more.
"""

import urllib.parse
from typing import List, Dict, Optional

from PyQt6.QtCore import QUrl

from qutebrowser.api import cmdutils
from qutebrowser.utils import message, objreg


class PublicRecordsAccess:
    """Handle public records and database searches."""
    
    def __init__(self):
        # Business Registration Databases
        self.business_databases = {
            # US Federal
            'sam_gov': 'https://sam.gov/search/',
            'sec_edgar': 'https://www.sec.gov/edgar/search/',
            'irs_exempt': 'https://www.irs.gov/charities-non-profits/search-for-tax-exempt-organizations',
            'fcc_universal': 'https://apps.fcc.gov/cgb/form499/499a.cfm',
            
            # US States
            'delaware_sos': 'https://icis.corp.delaware.gov/ecorp/entitysearch/namesearch.aspx',
            'california_sos': 'https://bizfileonline.sos.ca.gov/search/business',
            'nevada_sos': 'https://esos.nv.gov/EntitySearch/OnlineEntitySearch',
            'wyoming_sos': 'https://wyobiz.wyo.gov/Business/FilingSearch.aspx',
            'new_york_sos': 'https://apps.dos.ny.gov/publicInquiry/',
            'texas_sos': 'https://mycpa.cpa.state.tx.us/coa/',
            'florida_sunbiz': 'https://search.sunbiz.org/Inquiry/CorporationSearch/ByName',
            
            # UK
            'companies_house': 'https://find-and-update.company-information.service.gov.uk/',
            'uk_charities': 'https://register-of-charities.charitycommission.gov.uk/charity-search',
            
            # EU
            'eu_bris': 'https://e-justice.europa.eu/content_find_a_company-489-en.do',
            'eu_transparency': 'https://ec.europa.eu/transparencyregister/public/homePage.do',
            
            # International
            'opencorporates': 'https://opencorporates.com/companies',
            'icij_offshore': 'https://offshoreleaks.icij.org/',
            'gleif_lei': 'https://search.gleif.org/',
            
            # Other Countries
            'canada_corps': 'https://www.ic.gc.ca/app/scr/cc/CorporationsCanada/fdrlCrpSrch.html',
            'australia_abr': 'https://abr.business.gov.au/',
            'singapore_acra': 'https://www.bizfile.gov.sg/ngbbizfileinternet/faces/oracle/webcenter/portalapp/pages/BizfileHomepage.jspx',
            'hong_kong_cr': 'https://www.icris.cr.gov.hk/csci/',
            'india_mca': 'https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html'
        }
        
        # Legal Records Databases
        self.legal_databases = {
            # US Federal Courts
            'pacer': 'https://pacer.uscourts.gov/',
            'recap': 'https://www.courtlistener.com/recap/',
            'justia_federal': 'https://dockets.justia.com/browse/noscat-1',
            'us_tax_court': 'https://www.ustaxcourt.gov/case_search.html',
            
            # US State Courts
            'court_reference': 'https://www.ncsc.org/information-and-resources/state-court-websites',
            'judyrecords': 'https://www.judyrecords.com/',
            'unicourt': 'https://unicourt.com/',
            
            # International Courts
            'icj': 'https://www.icj-cij.org/en/cases',
            'icc': 'https://www.icc-cpi.int/cases',
            'echr': 'https://hudoc.echr.coe.int/eng',
            'eu_curia': 'https://curia.europa.eu/juris/recherche.jsf',
            
            # Legal Research
            'google_scholar_case': 'https://scholar.google.com/scholar?hl=en&as_sdt=2006',
            'justia': 'https://law.justia.com/',
            'findlaw': 'https://caselaw.findlaw.com/',
            'leagle': 'https://www.leagle.com/',
            'bailii': 'https://www.bailii.org/',
            'austlii': 'https://www.austlii.edu.au/',
            'canlii': 'https://www.canlii.org/en/'
        }
        
        # Property Records
        self.property_databases = {
            # US Property
            'zillow': 'https://www.zillow.com/',
            'realtor': 'https://www.realtor.com/',
            'redfin': 'https://www.redfin.com/',
            'property_shark': 'https://www.propertyshark.com/',
            'nyc_acris': 'https://a836-acris.nyc.gov/DS/DocumentSearch/Index',
            'chicago_recorder': 'https://www.cookcountyil.gov/service/recorder-deeds-online-records-search',
            'la_assessor': 'https://portal.assessor.lacounty.gov/',
            
            # UK Property
            'uk_land_registry': 'https://www.gov.uk/search-property-information-land-registry',
            'rightmove': 'https://www.rightmove.co.uk/',
            'zoopla': 'https://www.zoopla.co.uk/',
            
            # Canada Property
            'canada_realtor': 'https://www.realtor.ca/',
            'ontario_land': 'https://www.onland.ca/ui/',
            'bc_assessment': 'https://www.bcassessment.ca/'
        }
        
        # Intellectual Property
        self.ip_databases = {
            # Patents
            'uspto_patents': 'https://patft.uspto.gov/',
            'google_patents': 'https://patents.google.com/',
            'epo_espacenet': 'https://worldwide.espacenet.com/',
            'wipo_global': 'https://patentscope.wipo.int/',
            'japan_jpo': 'https://www.j-platpat.inpit.go.jp/',
            
            # Trademarks
            'uspto_tess': 'https://tmsearch.uspto.gov/',
            'euipo': 'https://euipo.europa.eu/eSearch/',
            'wipo_madrid': 'https://www.wipo.int/madrid/monitor/en/',
            'canada_cipo': 'https://www.ic.gc.ca/app/opic-cipo/trdmrks/srch/home',
            
            # Copyright
            'us_copyright': 'https://cocatalog.loc.gov/',
            'uk_ipo': 'https://www.gov.uk/search-for-trademark'
        }
        
        # Academic & Scientific
        self.academic_databases = {
            'pubmed': 'https://pubmed.ncbi.nlm.nih.gov/',
            'google_scholar': 'https://scholar.google.com/',
            'jstor': 'https://www.jstor.org/',
            'scopus': 'https://www.scopus.com/',
            'web_of_science': 'https://www.webofscience.com/',
            'ieee_xplore': 'https://ieeexplore.ieee.org/',
            'arxiv': 'https://arxiv.org/',
            'ssrn': 'https://www.ssrn.com/',
            'researchgate': 'https://www.researchgate.net/',
            'academia_edu': 'https://www.academia.edu/',
            'semantic_scholar': 'https://www.semanticscholar.org/',
            'core': 'https://core.ac.uk/',
            'doaj': 'https://doaj.org/',
            'plos': 'https://plos.org/',
            'biorxiv': 'https://www.biorxiv.org/',
            'chemrxiv': 'https://chemrxiv.org/',
            'psyarxiv': 'https://psyarxiv.com/'
        }
        
        # Government Data
        self.government_data = {
            # US Government
            'data_gov': 'https://www.data.gov/',
            'census': 'https://data.census.gov/',
            'bls': 'https://www.bls.gov/data/',
            'fred': 'https://fred.stlouisfed.org/',
            'usaspending': 'https://www.usaspending.gov/',
            'foia': 'https://www.foia.gov/',
            'national_archives': 'https://www.archives.gov/',
            'loc': 'https://www.loc.gov/',
            
            # International
            'uk_data': 'https://data.gov.uk/',
            'eu_data': 'https://data.europa.eu/',
            'canada_data': 'https://open.canada.ca/',
            'australia_data': 'https://data.gov.au/',
            'world_bank': 'https://data.worldbank.org/',
            'un_data': 'https://data.un.org/',
            'oecd': 'https://data.oecd.org/'
        }


@cmdutils.register(name='business-search')
@cmdutils.argument('company_name')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def business_search(company_name: str, win_id: int, jurisdiction: str = None) -> None:
    """Search business registration databases.
    
    Search for company registrations, SEC filings, and corporate records.
    
    Args:
        company_name: Name of the company to search
        jurisdiction: Optional jurisdiction (us, uk, eu, etc.)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    records = PublicRecordsAccess()
    
    encoded_name = urllib.parse.quote_plus(company_name)
    
    # Default searches
    default_searches = [
        f"{records.business_databases['opencorporates']}?q={encoded_name}",
        f"{records.business_databases['sec_edgar']}#/entitySearch/{encoded_name}",
        f"https://www.google.com/search?q=\"{encoded_name}\"+site:sec.gov",
        f"https://www.google.com/search?q=\"{encoded_name}\"+corporation+filing"
    ]
    
    for url in default_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Jurisdiction-specific searches
    if jurisdiction:
        jurisdiction = jurisdiction.lower()
        if jurisdiction == 'us':
            us_searches = ['sam_gov', 'delaware_sos', 'california_sos', 'nevada_sos']
            for db in us_searches:
                if db in records.business_databases:
                    base_url = records.business_databases[db]
                    tabbed_browser.tabopen(QUrl(base_url), background=True)
        elif jurisdiction == 'uk':
            uk_url = f"{records.business_databases['companies_house']}?q={encoded_name}"
            tabbed_browser.tabopen(QUrl(uk_url), background=True)
        elif jurisdiction == 'eu':
            eu_url = records.business_databases['eu_bris']
            tabbed_browser.tabopen(QUrl(eu_url), background=True)
    
    message.info(f"Business search: {company_name}")


@cmdutils.register(name='legal-search')
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def legal_search(query: str, win_id: int, court_type: str = None) -> None:
    """Search legal records and court documents.
    
    Search for court cases, legal opinions, and judicial records.
    
    Args:
        query: Search query (case name, party name, docket number)
        court_type: Optional court type (federal, state, international)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    records = PublicRecordsAccess()
    
    encoded_query = urllib.parse.quote_plus(query)
    
    # General legal searches
    general_searches = [
        f"{records.legal_databases['google_scholar_case']}&q={encoded_query}",
        f"{records.legal_databases['justia']}/search?q={encoded_query}",
        f"{records.legal_databases['recap']}/?q={encoded_query}",
        f"{records.legal_databases['judyrecords']}/search?q={encoded_query}",
        f"https://www.google.com/search?q=\"{encoded_query}\"+court+case"
    ]
    
    for url in general_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Court-type specific
    if court_type:
        court_type = court_type.lower()
        if court_type == 'federal':
            tabbed_browser.tabopen(QUrl(records.legal_databases['pacer']), background=True)
        elif court_type == 'international':
            int_courts = ['icj', 'icc', 'echr', 'eu_curia']
            for court in int_courts:
                if court in records.legal_databases:
                    tabbed_browser.tabopen(QUrl(records.legal_databases[court]), background=True)
    
    message.info(f"Legal search: {query}")


@cmdutils.register(name='property-search')
@cmdutils.argument('address')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def property_search(address: str, win_id: int) -> None:
    """Search property records and real estate databases.
    
    Search for property ownership, assessments, and transaction history.
    
    Args:
        address: Property address to search
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    records = PublicRecordsAccess()
    
    encoded_address = urllib.parse.quote_plus(address)
    
    # US Property searches
    property_searches = [
        f"{records.property_databases['zillow']}/homes/{encoded_address}_rb/",
        f"{records.property_databases['realtor']}/realestateandhomes-search/{encoded_address}",
        f"{records.property_databases['redfin']}/search?query={encoded_address}",
        f"https://www.google.com/search?q=\"{encoded_address}\"+property+records",
        f"https://www.google.com/search?q=\"{encoded_address}\"+site:zillow.com"
    ]
    
    for url in property_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Public records searches
    public_searches = [
        f"https://www.google.com/search?q=\"{encoded_address}\"+assessor",
        f"https://www.google.com/search?q=\"{encoded_address}\"+\"property tax\"",
        f"https://www.google.com/search?q=\"{encoded_address}\"+deed"
    ]
    
    for url in public_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Property search: {address}")


@cmdutils.register(name='patent-search')
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def patent_search(query: str, win_id: int) -> None:
    """Search patent and intellectual property databases.
    
    Search for patents, trademarks, and other IP records.
    
    Args:
        query: Search query (invention name, inventor, company, patent number)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    records = PublicRecordsAccess()
    
    encoded_query = urllib.parse.quote_plus(query)
    
    # Patent searches
    patent_searches = [
        f"{records.ip_databases['google_patents']}/search?q={encoded_query}",
        f"{records.ip_databases['uspto_patents']}/netahtml/PTO/search-bool.html",
        f"{records.ip_databases['epo_espacenet']}/search?q={encoded_query}",
        f"{records.ip_databases['wipo_global']}/search/en/search.jsf"
    ]
    
    for url in patent_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Trademark search
    trademark_url = f"https://tmsearch.uspto.gov/search/search-information?searchText={encoded_query}"
    tabbed_browser.tabopen(QUrl(trademark_url), background=True)
    
    message.info(f"Patent/IP search: {query}")


@cmdutils.register(name='academic-search')
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def academic_search(query: str, win_id: int, author: str = None) -> None:
    """Search academic and scientific databases.
    
    Search for research papers, studies, and scholarly articles.
    
    Args:
        query: Search query (topic, title, keywords)
        author: Optional author name to search
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    records = PublicRecordsAccess()
    
    encoded_query = urllib.parse.quote_plus(query)
    
    # Build search query with author if provided
    if author:
        author_encoded = urllib.parse.quote_plus(author)
        scholar_query = f"author:\"{author}\" {query}"
        pubmed_query = f"{query} {author}[Author]"
    else:
        scholar_query = query
        pubmed_query = query
    
    # Academic searches
    academic_searches = [
        f"{records.academic_databases['google_scholar']}/scholar?q={urllib.parse.quote_plus(scholar_query)}",
        f"{records.academic_databases['pubmed']}/?term={urllib.parse.quote_plus(pubmed_query)}",
        f"{records.academic_databases['semantic_scholar']}/search?q={encoded_query}",
        f"{records.academic_databases['arxiv']}/search/?query={encoded_query}&searchtype=all",
        f"{records.academic_databases['core']}/search?q={encoded_query}",
        f"{records.academic_databases['researchgate']}/search?q={encoded_query}"
    ]
    
    for url in academic_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Field-specific repositories
    field_repos = ['ssrn', 'biorxiv', 'chemrxiv', 'psyarxiv']
    for repo in field_repos[:2]:  # Limit to 2 field-specific
        if repo in records.academic_databases:
            base_url = records.academic_databases[repo]
            tabbed_browser.tabopen(QUrl(base_url), background=True)
    
    message.info(f"Academic search: {query}")
    if author:
        message.info(f"Author filter: {author}")


@cmdutils.register(name='gov-data')
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def government_data_search(query: str, win_id: int, country: str = 'us') -> None:
    """Search government data portals and archives.
    
    Access government datasets, statistics, and public records.
    
    Args:
        query: Search query
        country: Country code (us, uk, eu, ca, au, etc.)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    records = PublicRecordsAccess()
    
    encoded_query = urllib.parse.quote_plus(query)
    country = country.lower()
    
    # Country-specific searches
    if country == 'us':
        gov_searches = [
            f"{records.government_data['data_gov']}/search?q={encoded_query}",
            f"{records.government_data['census']}/searchresults.html?q={encoded_query}",
            f"{records.government_data['usaspending']}/search?query={encoded_query}",
            f"{records.government_data['national_archives']}/research/search?query={encoded_query}"
        ]
    elif country == 'uk':
        gov_searches = [
            f"{records.government_data['uk_data']}/search?q={encoded_query}",
            f"https://www.gov.uk/search/all?keywords={encoded_query}"
        ]
    elif country == 'eu':
        gov_searches = [
            f"{records.government_data['eu_data']}/data/search?q={encoded_query}",
            f"https://europa.eu/search/?query={encoded_query}"
        ]
    elif country == 'ca':
        gov_searches = [
            f"{records.government_data['canada_data']}/en/search/inventory?keywords={encoded_query}"
        ]
    else:
        # Default to international sources
        gov_searches = [
            f"{records.government_data['world_bank']}/search?q={encoded_query}",
            f"{records.government_data['un_data']}/Search.aspx?q={encoded_query}",
            f"{records.government_data['oecd']}/search?q={encoded_query}"
        ]
    
    for url in gov_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Also search Google for government data
    google_gov = f"https://www.google.com/search?q=\"{encoded_query}\"+site:gov+OR+site:gov.uk+OR+site:europa.eu"
    tabbed_browser.tabopen(QUrl(google_gov), background=True)
    
    message.info(f"Government data search ({country}): {query}")


@cmdutils.register(name='public-help')
def public_records_help() -> None:
    """Display help for public records commands."""
    help_text = """
Public Records Commands:

1. :business-search <company_name> [jurisdiction]
   - Search business registrations
   - Jurisdictions: us, uk, eu
   - Example: :business-search "Apple Inc" us

2. :legal-search <query> [court_type]
   - Search court cases and legal documents
   - Court types: federal, state, international
   - Example: :legal-search "Smith v. Jones"

3. :property-search <address>
   - Search property records
   - Real estate transactions, assessments
   - Example: :property-search "123 Main St, City, State"

4. :patent-search <query>
   - Search patents and trademarks
   - Multiple patent offices
   - Example: :patent-search "artificial intelligence"

5. :academic-search <query> [author]
   - Search research papers
   - Optional author filter
   - Example: :academic-search "quantum computing" "John Doe"

6. :gov-data <query> [country]
   - Search government data
   - Countries: us, uk, eu, ca, au
   - Example: :gov-data "unemployment statistics" us

Tips:
- Many databases require registration
- Some records may have access fees
- Check multiple jurisdictions
- Use specific terms for better results
    """
    message.info(help_text)
#!/usr/bin/env python3
"""
OSINT Search Userscript for qutebrowser
Advanced Open Source Intelligence gathering
"""

import os
import sys
import urllib.parse
import re

def detect_query_type(query):
    """Detect the type of query for targeted OSINT"""
    # Email pattern
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
        return 'email'
    
    # Domain pattern
    if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
        return 'domain'
    
    # IP address pattern
    if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', query):
        return 'ip'
    
    # Phone number (various formats)
    if re.match(r'^[\+\d][\d\s\-\(\)]+\d$', query):
        return 'phone'
    
    # Social media handle
    if query.startswith('@') or query.startswith('#'):
        return 'social'
    
    # Bitcoin address
    if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', query):
        return 'bitcoin'
    
    # Default to name/company
    return 'entity'

def get_osint_urls(query, query_type):
    """Generate OSINT URLs based on query type"""
    encoded_query = urllib.parse.quote_plus(query)
    urls = []
    
    if query_type == 'email':
        urls = [
            f'https://haveibeenpwned.com/account/{query}',
            f'https://www.google.com/search?q="{encoded_query}"',
            f'https://hunter.io/email-verifier/{query}',
            f'https://emailrep.io/{query}',
            f'https://tools.epieos.com/email.php?email={query}',
            f'https://www.skymem.info/srch?q={encoded_query}',
        ]
    
    elif query_type == 'domain':
        urls = [
            f'https://www.whois.com/whois/{query}',
            f'https://www.shodan.io/search?query={query}',
            f'https://crt.sh/?q={query}',
            f'https://dnsdumpster.com/?q={query}',
            f'https://web.archive.org/web/*/{query}',
            f'https://builtwith.com/{query}',
            f'https://www.virustotal.com/gui/domain/{query}',
            f'https://securitytrails.com/domain/{query}',
        ]
    
    elif query_type == 'ip':
        urls = [
            f'https://www.shodan.io/host/{query}',
            f'https://www.abuseipdb.com/check/{query}',
            f'https://www.virustotal.com/gui/ip-address/{query}',
            f'https://ipinfo.io/{query}',
            f'https://www.maxmind.com/en/locate-my-ip-address?ip={query}',
            f'https://search.censys.io/hosts/{query}',
        ]
    
    elif query_type == 'phone':
        clean_phone = re.sub(r'[^\d+]', '', query)
        urls = [
            f'https://www.truecaller.com/search/{clean_phone}',
            f'https://www.google.com/search?q="{encoded_query}"',
            f'https://www.whitepages.com/phone/{clean_phone}',
            f'https://sync.me/search/?number={clean_phone}',
            f'https://www.whocalld.com/+{clean_phone}',
        ]
    
    elif query_type == 'social':
        handle = query.lstrip('@#')
        urls = [
            f'https://www.google.com/search?q="{encoded_query}"',
            f'https://twitter.com/{handle}',
            f'https://instagram.com/{handle}',
            f'https://www.tiktok.com/@{handle}',
            f'https://github.com/{handle}',
            f'https://keybase.io/{handle}',
            f'https://namechk.com/?n={handle}',
        ]
    
    elif query_type == 'bitcoin':
        urls = [
            f'https://www.blockchain.com/btc/address/{query}',
            f'https://blockchair.com/bitcoin/address/{query}',
            f'https://www.walletexplorer.com/address/{query}',
            f'https://bitref.com/{query}',
        ]
    
    else:  # entity (person/company)
        urls = [
            # People search
            f'https://www.google.com/search?q="{encoded_query}"',
            f'https://pipl.com/search/?q={encoded_query}',
            f'https://www.spokeo.com/search?q={encoded_query}',
            f'https://www.whitepages.com/name/{encoded_query}',
            f'https://www.beenverified.com/people/{encoded_query}/',
            
            # Professional/Business
            f'https://www.linkedin.com/search/results/all/?keywords={encoded_query}',
            f'https://opencorporates.com/companies?q={encoded_query}',
            f'https://www.crunchbase.com/textsearch?q={encoded_query}',
            
            # Social Media
            f'https://www.google.com/search?q=site:facebook.com+"{encoded_query}"',
            f'https://www.google.com/search?q=site:twitter.com+"{encoded_query}"',
            f'https://www.google.com/search?q=site:instagram.com+"{encoded_query}"',
            
            # Public Records
            f'https://www.judyrecords.com/search?q={encoded_query}',
            f'https://www.google.com/search?q="{encoded_query}"+filetype:pdf',
        ]
    
    return urls

def main():
    if len(sys.argv) < 2:
        print("Usage: osint_search.py <query>", file=sys.stderr)
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    
    # Get FIFO for sending commands to qutebrowser
    fifo = os.environ.get('QUTE_FIFO')
    if not fifo:
        print("QUTE_FIFO not set", file=sys.stderr)
        sys.exit(1)
    
    # Detect query type
    query_type = detect_query_type(query)
    
    # Get OSINT URLs
    urls = get_osint_urls(query, query_type)
    
    # Open each URL in a new tab
    with open(fifo, 'w') as f:
        for url in urls:
            f.write(f'open -t {url}\n')
        
        f.write(f'message-info "OSINT search ({query_type}): {len(urls)} tabs opened for {query}"\n')

if __name__ == '__main__':
    main()
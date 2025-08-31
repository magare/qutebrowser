#!/usr/bin/env python3
"""
Deep Search OSINT Userscript for qutebrowser
Performs comprehensive searches across multiple categories
"""

import os
import sys
import urllib.parse

def generate_deep_search_urls(query):
    """Generate comprehensive search URLs for deep investigation"""
    encoded_query = urllib.parse.quote_plus(query)
    
    # Check if query looks like an email
    is_email = '@' in query
    
    # Check if query looks like a domain
    is_domain = '.' in query and not ' ' in query and not is_email
    
    # Check if query looks like a phone number
    is_phone = query.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('+', '').isdigit()
    
    urls = []
    
    # General search engines
    urls.extend([
        f'https://www.google.com/search?q="{encoded_query}"',
        f'https://duckduckgo.com/?q="{encoded_query}"',
        f'https://www.bing.com/search?q="{encoded_query}"',
    ])
    
    # Social media
    urls.extend([
        f'https://www.google.com/search?q=site:linkedin.com+"{encoded_query}"',
        f'https://www.google.com/search?q=site:twitter.com+"{encoded_query}"',
        f'https://www.google.com/search?q=site:facebook.com+"{encoded_query}"',
        f'https://www.google.com/search?q=site:instagram.com+"{encoded_query}"',
        f'https://www.reddit.com/search/?q={encoded_query}',
    ])
    
    if is_email:
        # Email-specific searches
        urls.extend([
            f'https://haveibeenpwned.com/account/{query}',
            f'https://www.google.com/search?q="{encoded_query}"',
            f'https://hunter.io/email-verifier/{query}',
        ])
    
    if is_domain:
        # Domain-specific searches
        urls.extend([
            f'https://www.whois.com/whois/{query}',
            f'https://www.shodan.io/search?query={query}',
            f'https://dnsdumpster.com/?q={query}',
            f'https://web.archive.org/web/*/{query}',
            f'https://builtwith.com/{query}',
        ])
    
    if is_phone:
        # Phone number searches
        urls.extend([
            f'https://www.truecaller.com/search/{query}',
            f'https://www.google.com/search?q="{encoded_query}"',
            f'https://www.whitepages.com/phone/{query}',
        ])
    
    if not (is_email or is_domain or is_phone):
        # Person/Company name searches
        urls.extend([
            f'https://opencorporates.com/companies?q={encoded_query}',
            f'https://www.sec.gov/edgar/search/#/entityName={encoded_query}',
            f'https://scholar.google.com/scholar?q=author:"{encoded_query}"',
            f'https://patents.google.com/?inventor={encoded_query}',
        ])
    
    # News and media
    urls.extend([
        f'https://news.google.com/search?q="{encoded_query}"',
        f'https://www.google.com/search?q="{encoded_query}"&tbm=nws',
    ])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls

def main():
    if len(sys.argv) < 2:
        print("Usage: deep_search.py <query>", file=sys.stderr)
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    
    # Get FIFO for sending commands to qutebrowser
    fifo = os.environ.get('QUTE_FIFO')
    if not fifo:
        print("QUTE_FIFO not set", file=sys.stderr)
        sys.exit(1)
    
    # Generate search URLs
    urls = generate_deep_search_urls(query)
    
    # Limit to first 15 URLs to avoid overwhelming the browser
    urls = urls[:15]
    
    # Open each URL in a new tab
    with open(fifo, 'w') as f:
        for url in urls:
            f.write(f'open -t {url}\n')
        
        f.write(f'message-info "Deep search initiated: {len(urls)} tabs opened for {query}"\n')

if __name__ == '__main__':
    main()
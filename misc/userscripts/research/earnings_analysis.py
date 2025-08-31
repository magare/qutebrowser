#!/usr/bin/env python3
"""
Earnings Analysis Userscript for qutebrowser
Fetches earnings call transcripts and financial data
"""

import os
import sys
import urllib.parse
import json

def get_earnings_urls(ticker, mode='all'):
    """Generate URLs for earnings information"""
    ticker = ticker.upper()
    
    urls = {
        'transcript': [
            f'https://seekingalpha.com/symbol/{ticker}/earnings/transcripts',
            f'https://www.fool.com/earnings-call-transcripts/{ticker}/',
            f'https://finance.yahoo.com/quote/{ticker}/analysis',
        ],
        'analysis': [
            f'https://finance.yahoo.com/quote/{ticker}/analysis',
            f'https://www.marketwatch.com/investing/stock/{ticker}/analystestimates',
            f'https://finviz.com/quote.ashx?t={ticker}',
        ],
        'calendar': [
            f'https://finance.yahoo.com/quote/{ticker}/calendar',
            f'https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}/earnings',
            f'https://www.zacks.com/stock/quote/{ticker}/earnings-calendar',
        ],
        'all': [
            f'https://seekingalpha.com/symbol/{ticker}/earnings/transcripts',
            f'https://finance.yahoo.com/quote/{ticker}/analysis',
            f'https://finviz.com/quote.ashx?t={ticker}',
            f'https://www.marketwatch.com/investing/stock/{ticker}',
            f'https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}/earnings',
        ]
    }
    
    return urls.get(mode, urls['all'])

def search_company_by_name(company_name):
    """Generate search URLs to find ticker symbol"""
    encoded_name = urllib.parse.quote_plus(company_name)
    
    return [
        f'https://finance.yahoo.com/lookup?s={encoded_name}',
        f'https://www.marketwatch.com/tools/quotes/lookup.asp?lookup={encoded_name}',
        f'https://www.google.com/search?q={encoded_name}+stock+ticker+symbol',
    ]

def main():
    if len(sys.argv) < 2:
        print("Usage: earnings_analysis.py <ticker_or_company> [mode]", file=sys.stderr)
        print("Modes: transcript, analysis, calendar, all (default)", file=sys.stderr)
        sys.exit(1)
    
    query = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'all'
    
    # Get FIFO for sending commands to qutebrowser
    fifo = os.environ.get('QUTE_FIFO')
    if not fifo:
        print("QUTE_FIFO not set", file=sys.stderr)
        sys.exit(1)
    
    # Determine if query is a ticker (short, all caps) or company name
    is_ticker = len(query) <= 5 and query.replace('.', '').replace('-', '').isalpha()
    
    if is_ticker:
        urls = get_earnings_urls(query, mode)
        message = f"Opening earnings data for {query.upper()}"
    else:
        # Search for company ticker
        urls = search_company_by_name(query)
        message = f"Searching for ticker symbol: {query}"
    
    # Open each URL in a new tab
    with open(fifo, 'w') as f:
        for url in urls:
            f.write(f'open -t {url}\n')
        
        f.write(f'message-info "{message} ({len(urls)} tabs)"\n')

if __name__ == '__main__':
    main()
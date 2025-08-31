#!/usr/bin/env python3
"""
Financial Analysis Userscript for qutebrowser
Comprehensive financial data retrieval
"""

import os
import sys
import urllib.parse

def get_financial_urls(ticker):
    """Generate URLs for comprehensive financial analysis"""
    ticker = ticker.upper()
    
    return [
        # Fundamental Data
        f'https://finance.yahoo.com/quote/{ticker}',
        f'https://finviz.com/quote.ashx?t={ticker}',
        f'https://www.marketwatch.com/investing/stock/{ticker}',
        
        # Financial Statements
        f'https://finance.yahoo.com/quote/{ticker}/financials',
        f'https://finance.yahoo.com/quote/{ticker}/balance-sheet',
        f'https://finance.yahoo.com/quote/{ticker}/cash-flow',
        
        # SEC Filings
        f'https://www.sec.gov/edgar/search/#/entityName={ticker}',
        f'https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&owner=exclude&action=getcompany',
        
        # Analysis & Ratings
        f'https://www.tipranks.com/stocks/{ticker}/forecast',
        f'https://stockcharts.com/h-sc/ui?s={ticker}',
        f'https://www.zacks.com/stock/quote/{ticker}',
        
        # Options & Insider Trading
        f'https://finance.yahoo.com/quote/{ticker}/options',
        f'https://finance.yahoo.com/quote/{ticker}/insider-transactions',
        f'https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}/insider-activity',
        
        # News & Sentiment
        f'https://finviz.com/quote.ashx?t={ticker}&ta=0&p=d&b=1',
        f'https://seekingalpha.com/symbol/{ticker}/news',
    ]

def main():
    if len(sys.argv) < 2:
        print("Usage: financial_analysis.py <ticker>", file=sys.stderr)
        sys.exit(1)
    
    ticker = sys.argv[1]
    
    # Get FIFO for sending commands to qutebrowser
    fifo = os.environ.get('QUTE_FIFO')
    if not fifo:
        print("QUTE_FIFO not set", file=sys.stderr)
        sys.exit(1)
    
    # Get financial URLs
    urls = get_financial_urls(ticker)
    
    # Open each URL in a new tab
    with open(fifo, 'w') as f:
        for url in urls:
            f.write(f'open -t {url}\n')
        
        f.write(f'message-info "Opening comprehensive financial analysis for {ticker.upper()} ({len(urls)} tabs)"\n')

if __name__ == '__main__':
    main()
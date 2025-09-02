#!/usr/bin/env python3
"""
Userscript to perform comprehensive OSINT analysis on the current page.

Usage: :spawn --userscript osint/analyze_page.py
"""

import os
import sys
import json
from urllib.parse import urlparse

# Add qutebrowser modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from qutebrowser.osint.core import OSINTEngine
from qutebrowser.osint.bgp import BGPAnalyzer
from qutebrowser.osint.certificates import CertificateIntelligence
from qutebrowser.osint.blockchain import BlockchainAnalyzer
from qutebrowser.osint.correlation import CorrelationDatabase


def main():
    """Main function for page analysis."""
    # Get current URL from qutebrowser
    url = os.environ.get('QUTE_URL', '')
    if not url:
        print("Error: No URL provided", file=sys.stderr)
        return
        
    # Get page content
    content = os.environ.get('QUTE_SELECTED_TEXT', '')
    if not content:
        # Try to get full page HTML
        content = os.environ.get('QUTE_HTML', '')
        
    # Parse URL
    parsed = urlparse(url)
    domain = parsed.hostname
    
    # Initialize OSINT components
    engine = OSINTEngine()
    bgp = BGPAnalyzer()
    cert_intel = CertificateIntelligence()
    blockchain = BlockchainAnalyzer()
    correlation = CorrelationDatabase()
    
    results = {
        'url': url,
        'domain': domain,
        'analyses': {}
    }
    
    # Perform BGP/ASN analysis
    if domain:
        print(f"Analyzing BGP/ASN for {domain}...")
        bgp_data = bgp.analyze_domain(domain)
        results['analyses']['bgp'] = bgp_data
        
        # Add to correlation database
        domain_entity = correlation.add_entity('domain', domain)
        if bgp_data.get('asn'):
            asn_entity = correlation.add_entity('asn', str(bgp_data['asn']))
            correlation.add_relationship(domain_entity, asn_entity, 'hosted_in_asn')
            
    # Perform certificate analysis
    if domain:
        print(f"Analyzing SSL certificate for {domain}...")
        cert_data = cert_intel.get_certificate(domain)
        if cert_data:
            results['analyses']['certificate'] = cert_data
            
            # Search Certificate Transparency logs
            ct_results = cert_intel.search_certificate_transparency(domain)
            results['analyses']['ct_logs'] = ct_results
            
            # Add to correlation database
            if cert_data.get('fingerprint_sha256'):
                cert_entity = correlation.add_entity(
                    'ssl_cert', 
                    cert_data['fingerprint_sha256']
                )
                correlation.add_relationship(
                    domain_entity, cert_entity, 'has_certificate'
                )
                
    # Detect and analyze cryptocurrency addresses in content
    if content:
        print("Scanning for cryptocurrency addresses...")
        crypto_addresses = blockchain.detect_addresses(content)
        
        if crypto_addresses:
            results['analyses']['blockchain'] = {}
            
            for crypto_type, addresses in crypto_addresses.items():
                results['analyses']['blockchain'][crypto_type] = []
                
                for address in addresses[:5]:  # Limit to 5 addresses per type
                    print(f"Analyzing {crypto_type} address: {address}")
                    
                    if crypto_type == 'bitcoin':
                        analysis = blockchain.analyze_bitcoin_address(address)
                    elif crypto_type == 'ethereum':
                        analysis = blockchain.analyze_ethereum_address(address)
                    else:
                        analysis = {'address': address, 'type': crypto_type}
                        
                    results['analyses']['blockchain'][crypto_type].append(analysis)
                    
                    # Add to correlation database
                    addr_entity = correlation.add_entity('crypto_address', address)
                    correlation.add_relationship(
                        domain_entity, addr_entity, 'contains_address'
                    )
                    
    # Find correlations
    print("Finding correlations...")
    correlations = correlation.correlate_data('domain', domain)
    results['correlations'] = correlations
    
    # Output results
    output_file = os.environ.get('QUTE_FIFO')
    if output_file:
        with open(output_file, 'w') as f:
            # Send command to open results in new tab
            results_json = json.dumps(results, indent=2)
            
            # Create HTML output
            html = f"""
            <html>
            <head>
                <title>OSINT Analysis - {domain}</title>
                <style>
                    body {{ font-family: monospace; padding: 20px; }}
                    h1 {{ color: #333; }}
                    h2 {{ color: #666; margin-top: 30px; }}
                    pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
                    .warning {{ color: #ff6600; font-weight: bold; }}
                    .success {{ color: #00aa00; font-weight: bold; }}
                </style>
            </head>
            <body>
                <h1>OSINT Analysis Results</h1>
                <p><strong>URL:</strong> {url}</p>
                <p><strong>Domain:</strong> {domain}</p>
                
                <h2>BGP/ASN Information</h2>
                <pre>{json.dumps(results.get('analyses', {}).get('bgp', {}), indent=2)}</pre>
                
                <h2>SSL Certificate</h2>
                <pre>{json.dumps(results.get('analyses', {}).get('certificate', {}), indent=2)}</pre>
                
                <h2>Cryptocurrency Addresses</h2>
                <pre>{json.dumps(results.get('analyses', {}).get('blockchain', {}), indent=2)}</pre>
                
                <h2>Correlations</h2>
                <pre>{json.dumps(results.get('correlations', []), indent=2)}</pre>
                
                <hr>
                <p><small>Analysis completed at {os.popen('date').read().strip()}</small></p>
            </body>
            </html>
            """
            
            # Write command to open results
            f.write(f"open -t data:text/html;base64,{__import__('base64').b64encode(html.encode()).decode()}\n")
            
    print("Analysis complete!")


if __name__ == '__main__':
    main()
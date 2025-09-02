#!/usr/bin/env python3
"""
Userscript to search Shodan for the current domain/IP.

Usage: :spawn --userscript osint/search_shodan.py
"""

import os
import sys
import json
import socket
from urllib.parse import urlparse

# Add qutebrowser modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from qutebrowser.osint.search_engines import AdvancedSearchEngine


def main():
    """Search Shodan for current site."""
    # Get current URL
    url = os.environ.get('QUTE_URL', '')
    if not url:
        print("Error: No URL provided", file=sys.stderr)
        return
        
    parsed = urlparse(url)
    domain = parsed.hostname
    
    if not domain:
        print("Error: Could not extract domain from URL", file=sys.stderr)
        return
        
    # Initialize search engine
    search = AdvancedSearchEngine()
    
    # Resolve domain to IP
    try:
        ip = socket.gethostbyname(domain)
    except socket.gaierror:
        ip = None
        
    results = {
        'domain': domain,
        'ip': ip,
        'shodan_results': {}
    }
    
    # Search for domain
    print(f"Searching Shodan for domain: {domain}")
    domain_results = search.search_shodan(f'hostname:{domain}')
    results['shodan_results']['domain'] = domain_results
    
    # Search for IP if available
    if ip:
        print(f"Searching Shodan for IP: {ip}")
        ip_results = search.search_shodan(f'ip:{ip}')
        results['shodan_results']['ip'] = ip_results
        
    # Search for exposed services
    print("Searching for exposed services...")
    service_queries = [
        ('Web Server', f'hostname:{domain} port:80,443,8080,8443'),
        ('SSH', f'hostname:{domain} port:22'),
        ('Database', f'hostname:{domain} port:3306,5432,27017,6379'),
        ('FTP', f'hostname:{domain} port:21'),
        ('RDP', f'hostname:{domain} port:3389'),
    ]
    
    for service_name, query in service_queries:
        service_results = search.search_shodan(query)
        if service_results.get('total', 0) > 0:
            results['shodan_results'][service_name.lower().replace(' ', '_')] = service_results
            
    # Check for vulnerabilities
    print("Checking for vulnerabilities...")
    vuln_results = search.search_shodan(f'hostname:{domain} has_vuln:true')
    if vuln_results.get('total', 0) > 0:
        results['vulnerabilities'] = vuln_results
        
    # Output results
    output_file = os.environ.get('QUTE_FIFO')
    if output_file:
        with open(output_file, 'w') as f:
            # Create HTML output
            html = f"""
            <html>
            <head>
                <title>Shodan Search - {domain}</title>
                <style>
                    body {{ font-family: monospace; padding: 20px; }}
                    h1 {{ color: #333; }}
                    h2 {{ color: #666; margin-top: 30px; }}
                    pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
                    .warning {{ color: #ff6600; font-weight: bold; }}
                    .critical {{ color: #ff0000; font-weight: bold; }}
                    .info {{ color: #0066cc; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background: #f0f0f0; }}
                </style>
            </head>
            <body>
                <h1>Shodan Search Results</h1>
                <p><strong>Domain:</strong> {domain}</p>
                <p><strong>IP:</strong> {ip or 'N/A'}</p>
                
                <h2>Summary</h2>
                <table>
                    <tr>
                        <th>Search Type</th>
                        <th>Results Found</th>
                        <th>Status</th>
                    </tr>
            """
            
            for search_type, search_data in results['shodan_results'].items():
                if isinstance(search_data, dict):
                    total = search_data.get('total', 0)
                    status = 'Found' if total > 0 else 'None'
                    status_class = 'warning' if total > 0 else 'info'
                    html += f"""
                    <tr>
                        <td>{search_type.replace('_', ' ').title()}</td>
                        <td>{total}</td>
                        <td class="{status_class}">{status}</td>
                    </tr>
                    """
                    
            html += "</table>"
            
            # Add vulnerability section if found
            if 'vulnerabilities' in results and results['vulnerabilities'].get('total', 0) > 0:
                html += f"""
                <h2 class="critical">⚠️ Vulnerabilities Found</h2>
                <p class="critical">{results['vulnerabilities']['total']} vulnerable services detected!</p>
                """
                
                if 'statistics' in results['vulnerabilities']:
                    vulns = results['vulnerabilities']['statistics'].get('vulnerabilities', [])
                    if vulns:
                        html += "<h3>CVE List:</h3><ul>"
                        for vuln in vulns[:10]:  # Limit to top 10
                            html += f"<li>{vuln}</li>"
                        html += "</ul>"
                        
            # Add detailed results
            html += """
                <h2>Detailed Results</h2>
                <pre>""" + json.dumps(results, indent=2) + """</pre>
                
                <hr>
                <p><small>Search completed at """ + os.popen('date').read().strip() + """</small></p>
            </body>
            </html>
            """
            
            # Write command to open results
            import base64
            encoded_html = base64.b64encode(html.encode()).decode()
            f.write(f"open -t data:text/html;base64,{encoded_html}\n")
            
    print("Shodan search complete!")


if __name__ == '__main__':
    main()
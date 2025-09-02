#!/usr/bin/env python3
"""
Userscript to set up monitoring for the current site.

Usage: :spawn --userscript osint/monitor_site.py
"""

import os
import sys

# Add qutebrowser modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from urllib.parse import urlparse
from qutebrowser.osint.monitoring import MonitoringEngine


def main():
    """Set up monitoring for current site."""
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
        
    # Initialize monitoring engine
    monitor = MonitoringEngine()
    
    # Create monitoring rules for the domain
    rules_created = []
    
    # Monitor certificate changes
    cert_rule = monitor.add_rule(
        name=f"Certificate Monitor - {domain}",
        rule_type='cert',
        target=domain,
        conditions={},
        actions=['notify', 'log'],
        interval=86400  # Daily check
    )
    rules_created.append(('Certificate', cert_rule))
    
    # Monitor DNS changes
    dns_rule = monitor.add_rule(
        name=f"DNS Monitor - {domain}",
        rule_type='domain',
        target=domain,
        conditions={},
        actions=['notify', 'log'],
        interval=3600  # Hourly check
    )
    rules_created.append(('DNS', dns_rule))
    
    # Monitor for data leaks mentioning the domain
    leak_rule = monitor.add_rule(
        name=f"Data Leak Monitor - {domain}",
        rule_type='paste',
        target='all',
        conditions={
            'keywords': [domain, domain.replace('.', '[.]')],
            'patterns': {
                'email': f'[a-zA-Z0-9._%+-]+@{domain}',
                'subdomain': f'[a-zA-Z0-9.-]+\\.{domain}'
            }
        },
        actions=['notify', 'log'],
        interval=300  # Check every 5 minutes
    )
    rules_created.append(('Data Leak', leak_rule))
    
    # Start monitoring if not already running
    monitor.start_monitoring()
    
    # Send notification
    output_file = os.environ.get('QUTE_FIFO')
    if output_file:
        with open(output_file, 'w') as f:
            message = f"Monitoring enabled for {domain}\\n"
            message += "Rules created:\\n"
            for rule_type, rule_id in rules_created:
                message += f"  - {rule_type}: {rule_id}\\n"
            
            f.write(f"message-info '{message}'\n")
            
    print(f"Monitoring enabled for {domain}")
    for rule_type, rule_id in rules_created:
        print(f"  {rule_type}: {rule_id}")


if __name__ == '__main__':
    main()
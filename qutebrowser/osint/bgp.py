"""BGP and ASN intelligence gathering module."""

import json
import socket
import ipaddress
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import requests
from PyQt6.QtCore import QObject, pyqtSignal, QUrl

from qutebrowser.utils import message, log
from qutebrowser.osint.core import IntelligenceReport

logger = log.osint_bgp = logging.getLogger('osint.bgp')


class BGPAnalyzer(QObject):
    """Analyzer for BGP and ASN intelligence."""
    
    bgp_data_received = pyqtSignal(dict)
    asn_info_received = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cache = {}
        
    def analyze_ip(self, ip: str) -> Dict[str, Any]:
        """Analyze an IP address for BGP/ASN information."""
        if ip in self.cache:
            logger.debug(f"Using cached BGP data for {ip}")
            return self.cache[ip]
            
        result = {
            'ip': ip,
            'asn': None,
            'asn_name': None,
            'country': None,
            'prefix': None,
            'description': None,
            'bgp_routes': [],
            'peers': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Query RIPEstat API for BGP information
            asn_data = self._query_ripestat_asn(ip)
            if asn_data:
                result.update(asn_data)
                
            # Query BGPView API for additional routing information
            bgp_data = self._query_bgpview(ip)
            if bgp_data:
                result['bgp_routes'] = bgp_data.get('routes', [])
                result['peers'] = bgp_data.get('peers', [])
                
            # Query Team Cymru whois for ASN info
            cymru_data = self._query_team_cymru(ip)
            if cymru_data and not result['asn']:
                result.update(cymru_data)
                
            self.cache[ip] = result
            self.bgp_data_received.emit(result)
            
        except Exception as e:
            logger.error(f"Error analyzing IP {ip}: {e}")
            
        return result
    
    def _query_ripestat_asn(self, ip: str) -> Optional[Dict[str, Any]]:
        """Query RIPEstat API for ASN information."""
        try:
            url = f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok' and data.get('data'):
                    asn_info = data['data'].get('asns', [])
                    if asn_info:
                        asn = asn_info[0]
                        return {
                            'asn': asn.get('asn'),
                            'asn_name': asn.get('holder', ''),
                            'prefix': data['data'].get('resource', '')
                        }
        except Exception as e:
            logger.debug(f"RIPEstat query failed for {ip}: {e}")
        return None
    
    def _query_bgpview(self, ip: str) -> Optional[Dict[str, Any]]:
        """Query BGPView API for BGP routing information."""
        try:
            url = f"https://api.bgpview.io/ip/{ip}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok' and data.get('data'):
                    bgp_data = data['data']
                    return {
                        'routes': bgp_data.get('prefixes', []),
                        'peers': bgp_data.get('rir_allocation', {})
                    }
        except Exception as e:
            logger.debug(f"BGPView query failed for {ip}: {e}")
        return None
    
    def _query_team_cymru(self, ip: str) -> Optional[Dict[str, Any]]:
        """Query Team Cymru whois for ASN information."""
        try:
            # Perform DNS lookup for ASN info
            reversed_ip = '.'.join(reversed(ip.split('.')))
            query = f"{reversed_ip}.origin.asn.cymru.com"
            
            result = socket.gethostbyname(query)
            if result:
                parts = result.split('|')
                if len(parts) >= 3:
                    return {
                        'asn': parts[0].strip(),
                        'prefix': parts[1].strip(),
                        'country': parts[2].strip()
                    }
        except Exception as e:
            logger.debug(f"Team Cymru query failed for {ip}: {e}")
        return None
    
    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze a domain for BGP/ASN information."""
        try:
            # Resolve domain to IP
            ip = socket.gethostbyname(domain)
            result = self.analyze_ip(ip)
            result['domain'] = domain
            return result
        except socket.gaierror as e:
            logger.error(f"Failed to resolve domain {domain}: {e}")
            return {'domain': domain, 'error': str(e)}
    
    def find_network_neighbors(self, asn: str) -> List[Dict[str, Any]]:
        """Find neighboring ASNs and peer networks."""
        neighbors = []
        try:
            url = f"https://api.bgpview.io/asn/{asn}/peers"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok' and data.get('data'):
                    for peer in data['data'].get('ipv4_peers', []):
                        neighbors.append({
                            'asn': peer.get('asn'),
                            'name': peer.get('name', ''),
                            'country': peer.get('country_code', ''),
                            'relationship': 'ipv4_peer'
                        })
                    for peer in data['data'].get('ipv6_peers', []):
                        neighbors.append({
                            'asn': peer.get('asn'),
                            'name': peer.get('name', ''),
                            'country': peer.get('country_code', ''),
                            'relationship': 'ipv6_peer'
                        })
        except Exception as e:
            logger.error(f"Failed to find neighbors for ASN {asn}: {e}")
            
        self.asn_info_received.emit({'asn': asn, 'neighbors': neighbors})
        return neighbors
    
    def check_bgp_hijacking(self, prefix: str) -> Dict[str, Any]:
        """Check for potential BGP hijacking or anomalies."""
        result = {
            'prefix': prefix,
            'anomalies': [],
            'legitimate_origin': None,
            'current_origins': []
        }
        
        try:
            # Query for current BGP announcements
            url = f"https://api.bgpview.io/prefix/{prefix}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok' and data.get('data'):
                    prefix_data = data['data']
                    
                    # Check for multiple origin ASNs (potential hijacking indicator)
                    origins = []
                    for asn in prefix_data.get('asns', []):
                        origins.append({
                            'asn': asn.get('asn'),
                            'name': asn.get('name', ''),
                            'country': asn.get('country_code', '')
                        })
                    
                    result['current_origins'] = origins
                    
                    if len(origins) > 1:
                        result['anomalies'].append({
                            'type': 'multiple_origins',
                            'severity': 'high',
                            'description': f"Prefix announced by {len(origins)} different ASNs"
                        })
                        
        except Exception as e:
            logger.error(f"Failed to check BGP hijacking for {prefix}: {e}")
            
        return result
    
    def get_submarine_cable_dependencies(self, ip: str) -> List[Dict[str, str]]:
        """Identify potential submarine cable dependencies based on geolocation."""
        cables = []
        
        try:
            # Get geolocation for IP
            url = f"https://ipapi.co/{ip}/json/"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                geo_data = response.json()
                
                # Map known submarine cable landing points
                cable_map = {
                    'US': ['TAT-14', 'AC-1', 'MAREA', 'Dunant'],
                    'UK': ['TAT-14', 'AC-1', 'Celtic', 'Grace Hopper'],
                    'JP': ['JUPITER', 'PC-1', 'Unity', 'FASTER'],
                    'SG': ['SEA-ME-WE 3', 'APG', 'Unity'],
                    'AU': ['Southern Cross', 'Hawaiki', 'Indigo'],
                }
                
                country = geo_data.get('country_code', '')
                if country in cable_map:
                    for cable in cable_map[country]:
                        cables.append({
                            'name': cable,
                            'country': country,
                            'type': 'submarine_cable'
                        })
                        
        except Exception as e:
            logger.debug(f"Failed to identify cable dependencies for {ip}: {e}")
            
        return cables
    
    def create_report(self, target: str, data: Dict[str, Any]) -> IntelligenceReport:
        """Create an intelligence report from BGP analysis."""
        return IntelligenceReport(
            source='bgp_analyzer',
            target=target,
            data_type='bgp_asn',
            data=data,
            confidence=0.8 if data.get('asn') else 0.3,
            tags=['network', 'bgp', 'asn', 'infrastructure']
        )
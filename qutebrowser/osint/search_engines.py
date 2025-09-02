"""Integration with advanced search engines like Shodan, Censys, and others."""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import quote

import requests
from PyQt6.QtCore import QObject, pyqtSignal

try:
    from qutebrowser.config import config
except ImportError:
    # For testing without full qutebrowser environment
    config = None
from qutebrowser.utils import message, log
from qutebrowser.osint.core import IntelligenceReport

logger = log.osint_search = logging.getLogger('osint.search')


class AdvancedSearchEngine(QObject):
    """Integration with IoT and infrastructure search engines."""
    
    search_complete = pyqtSignal(dict)
    vulnerability_found = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_cache = {}
        
    def search_shodan(self, query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Search Shodan for internet-connected devices."""
        if not api_key:
            if config:
                api_key = getattr(getattr(config.val, 'content', None), 'osint_shodan_api_key', None)
            else:
                api_key = None
            
        if not api_key:
            logger.warning("Shodan API key not configured")
            return {'error': 'Shodan API key required'}
            
        cache_key = f"shodan:{query}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
            
        results = {
            'query': query,
            'engine': 'shodan',
            'timestamp': datetime.now().isoformat(),
            'total': 0,
            'results': []
        }
        
        try:
            url = "https://api.shodan.io/shodan/host/search"
            params = {
                'key': api_key,
                'query': query,
                'facets': 'country,org,port,vuln'
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                results['total'] = data.get('total', 0)
                
                for match in data.get('matches', []):
                    result_item = {
                        'ip': match.get('ip_str'),
                        'port': match.get('port'),
                        'hostname': match.get('hostnames', []),
                        'org': match.get('org'),
                        'os': match.get('os'),
                        'location': {
                            'country': match.get('location', {}).get('country_name'),
                            'city': match.get('location', {}).get('city'),
                            'latitude': match.get('location', {}).get('latitude'),
                            'longitude': match.get('location', {}).get('longitude')
                        },
                        'vulns': match.get('vulns', []),
                        'data': match.get('data', ''),
                        'timestamp': match.get('timestamp')
                    }
                    
                    results['results'].append(result_item)
                    
                    # Check for vulnerabilities
                    if result_item['vulns']:
                        self.vulnerability_found.emit({
                            'ip': result_item['ip'],
                            'vulns': result_item['vulns'],
                            'severity': 'high'
                        })
                        
                # Process facets for statistics
                results['statistics'] = {
                    'countries': data.get('facets', {}).get('country', []),
                    'organizations': data.get('facets', {}).get('org', []),
                    'ports': data.get('facets', {}).get('port', []),
                    'vulnerabilities': data.get('facets', {}).get('vuln', [])
                }
                
                self.search_cache[cache_key] = results
                self.search_complete.emit(results)
                
        except Exception as e:
            logger.error(f"Shodan search failed for '{query}': {e}")
            results['error'] = str(e)
            
        return results
    
    def search_censys(self, query: str, api_id: Optional[str] = None, 
                     api_secret: Optional[str] = None) -> Dict[str, Any]:
        """Search Censys for internet assets."""
        if not api_id or not api_secret:
            if config:
                api_id = getattr(getattr(config.val, 'content', None), 'osint_censys_api_id', None)
                api_secret = getattr(getattr(config.val, 'content', None), 'osint_censys_api_secret', None)
            
            if not api_id or not api_secret:
                logger.warning("Censys API credentials not configured")
                return {'error': 'Censys API credentials required'}
                
        cache_key = f"censys:{query}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
            
        results = {
            'query': query,
            'engine': 'censys',
            'timestamp': datetime.now().isoformat(),
            'total': 0,
            'results': []
        }
        
        try:
            url = "https://search.censys.io/api/v2/hosts/search"
            headers = {
                'Accept': 'application/json',
            }
            
            params = {
                'q': query,
                'per_page': 100,
                'virtual_hosts': 'INCLUDE'
            }
            
            response = requests.get(url, params=params, headers=headers, 
                                  auth=(api_id, api_secret), timeout=30)
                                  
            if response.status_code == 200:
                data = response.json()
                results['total'] = data.get('result', {}).get('total', 0)
                
                for hit in data.get('result', {}).get('hits', []):
                    result_item = {
                        'ip': hit.get('ip'),
                        'name': hit.get('name'),
                        'services': [],
                        'location': hit.get('location', {}),
                        'autonomous_system': hit.get('autonomous_system', {}),
                        'last_updated': hit.get('last_updated_at')
                    }
                    
                    # Process services
                    for service in hit.get('services', []):
                        result_item['services'].append({
                            'port': service.get('port'),
                            'service_name': service.get('service_name'),
                            'transport_protocol': service.get('transport_protocol'),
                            'extended_service_name': service.get('extended_service_name')
                        })
                        
                    results['results'].append(result_item)
                    
                self.search_cache[cache_key] = results
                self.search_complete.emit(results)
                
        except Exception as e:
            logger.error(f"Censys search failed for '{query}': {e}")
            results['error'] = str(e)
            
        return results
    
    def search_by_cve(self, cve_id: str) -> Dict[str, Any]:
        """Search for systems vulnerable to a specific CVE."""
        results = {
            'cve': cve_id,
            'timestamp': datetime.now().isoformat(),
            'vulnerable_systems': []
        }
        
        # Search Shodan for CVE
        shodan_query = f"vuln:{cve_id}"
        shodan_results = self.search_shodan(shodan_query)
        
        if 'results' in shodan_results:
            for system in shodan_results['results']:
                results['vulnerable_systems'].append({
                    'source': 'shodan',
                    'ip': system.get('ip'),
                    'hostname': system.get('hostname'),
                    'org': system.get('org'),
                    'port': system.get('port')
                })
                
        # Get CVE details from NVD
        cve_details = self._get_cve_details(cve_id)
        if cve_details:
            results['cve_details'] = cve_details
            
        return results
    
    def _get_cve_details(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """Get CVE details from NVD (National Vulnerability Database)."""
        try:
            url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])
                
                if vulnerabilities:
                    cve_item = vulnerabilities[0].get('cve', {})
                    
                    return {
                        'id': cve_item.get('id'),
                        'description': cve_item.get('descriptions', [{}])[0].get('value', ''),
                        'severity': cve_item.get('metrics', {}).get('cvssMetricV31', [{}])[0].get('cvssData', {}).get('baseSeverity', 'UNKNOWN'),
                        'score': cve_item.get('metrics', {}).get('cvssMetricV31', [{}])[0].get('cvssData', {}).get('baseScore', 0),
                        'published': cve_item.get('published'),
                        'last_modified': cve_item.get('lastModified')
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get CVE details for {cve_id}: {e}")
            
        return None
    
    def search_exposed_databases(self) -> List[Dict[str, Any]]:
        """Search for exposed databases and data stores."""
        exposed_dbs = []
        
        # Common exposed database signatures
        db_queries = [
            ('mongodb', 'port:27017 -authentication'),
            ('elasticsearch', 'port:9200 json'),
            ('redis', 'port:6379 -requirepass'),
            ('cassandra', 'port:9042 "Invalid or unsupported protocol version"'),
            ('mysql', 'port:3306 "mysql_native_password"'),
            ('postgresql', 'port:5432 "PostgreSQL"'),
            ('couchdb', 'port:5984 "couchdb"'),
            ('memcached', 'port:11211 "STAT items"')
        ]
        
        for db_type, query in db_queries:
            results = self.search_shodan(query)
            
            if 'results' in results:
                for system in results['results']:
                    exposed_dbs.append({
                        'type': db_type,
                        'ip': system.get('ip'),
                        'port': system.get('port'),
                        'hostname': system.get('hostname'),
                        'org': system.get('org'),
                        'location': system.get('location'),
                        'risk': 'critical' if 'authentication' not in system.get('data', '') else 'high'
                    })
                    
        return exposed_dbs
    
    def search_industrial_control_systems(self) -> List[Dict[str, Any]]:
        """Search for exposed industrial control systems."""
        ics_results = []
        
        # Common ICS/SCADA search queries
        ics_queries = [
            ('modbus', 'port:502'),
            ('dnp3', 'port:20000 source address'),
            ('s7', 'port:102'),
            ('bacnet', 'port:47808'),
            ('niagara', 'port:1911,4911 product:Niagara'),
            ('scada', '"SCADA"'),
            ('plc', '"Programmable Logic Controller"')
        ]
        
        for system_type, query in ics_queries:
            results = self.search_shodan(query)
            
            if 'results' in results:
                for system in results['results']:
                    ics_results.append({
                        'type': system_type,
                        'ip': system.get('ip'),
                        'port': system.get('port'),
                        'hostname': system.get('hostname'),
                        'org': system.get('org'),
                        'location': system.get('location'),
                        'data': system.get('data', '')[:500],  # Truncate data
                        'risk': 'critical'  # ICS exposure is always critical
                    })
                    
        return ics_results
    
    def find_default_credentials(self, ip: str) -> List[Dict[str, Any]]:
        """Search for services potentially using default credentials."""
        default_cred_indicators = []
        
        # Search for common services with default credentials
        services_to_check = [
            {'service': 'webcam', 'query': f'ip:{ip} "default password"'},
            {'service': 'router', 'query': f'ip:{ip} "admin/admin"'},
            {'service': 'printer', 'query': f'ip:{ip} port:9100'},
            {'service': 'iot', 'query': f'ip:{ip} "default login"'}
        ]
        
        for service_info in services_to_check:
            results = self.search_shodan(service_info['query'])
            
            if results.get('total', 0) > 0:
                default_cred_indicators.append({
                    'service': service_info['service'],
                    'ip': ip,
                    'likelihood': 'high',
                    'recommendation': 'Change default credentials immediately'
                })
                
        return default_cred_indicators
    
    def create_report(self, query: str, results: Dict[str, Any]) -> IntelligenceReport:
        """Create an intelligence report from search results."""
        confidence = 0.7  # Moderate confidence for search results
        
        if results.get('total', 0) > 0:
            confidence = 0.8
            
        return IntelligenceReport(
            source='advanced_search',
            target=query,
            data_type='infrastructure_search',
            data=results,
            confidence=confidence,
            tags=['search', 'infrastructure', 'iot', 'exposure']
        )
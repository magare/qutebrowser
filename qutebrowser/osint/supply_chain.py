"""Supply chain mapping and analysis module."""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

import requests
from PyQt6.QtCore import QObject, pyqtSignal

from qutebrowser.utils import message, log
from qutebrowser.osint.core import IntelligenceReport

logger = log.osint_supply = logging.getLogger('osint.supply_chain')


class SupplyChainMapper(QObject):
    """Mapper for supply chain intelligence and vendor relationships."""
    
    vendor_found = pyqtSignal(dict)
    supply_chain_mapped = pyqtSignal(dict)
    risk_identified = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.company_cache = {}
        self.vendor_relationships = defaultdict(set)
        
    def analyze_company(self, company_name: str) -> Dict[str, Any]:
        """Analyze a company's supply chain and vendor relationships."""
        if company_name in self.company_cache:
            return self.company_cache[company_name]
            
        result = {
            'company': company_name,
            'timestamp': datetime.now().isoformat(),
            'vendors': [],
            'customers': [],
            'partners': [],
            'subsidiaries': [],
            'parent_company': None,
            'financial_data': {},
            'risk_assessment': {},
            'technologies': [],
            'certifications': [],
            'locations': []
        }
        
        # Search for import/export data
        trade_data = self._search_trade_databases(company_name)
        if trade_data:
            result['vendors'] = trade_data.get('suppliers', [])
            result['customers'] = trade_data.get('buyers', [])
            
        # Search for corporate filings
        corporate_data = self._search_corporate_filings(company_name)
        if corporate_data:
            result['financial_data'] = corporate_data.get('financials', {})
            result['subsidiaries'] = corporate_data.get('subsidiaries', [])
            result['parent_company'] = corporate_data.get('parent', None)
            
        # Search for technology stack
        tech_stack = self._identify_technology_stack(company_name)
        if tech_stack:
            result['technologies'] = tech_stack
            
        # Perform risk assessment
        result['risk_assessment'] = self._assess_supply_chain_risk(result)
        
        self.company_cache[company_name] = result
        self.supply_chain_mapped.emit(result)
        
        return result
    
    def _search_trade_databases(self, company: str) -> Dict[str, Any]:
        """Search import/export databases for trade relationships."""
        trade_data = {
            'suppliers': [],
            'buyers': [],
            'trade_volume': 0,
            'primary_products': []
        }
        
        try:
            # In production, this would query actual trade databases like:
            # - ImportYeti
            # - Panjiva
            # - Import Genius
            # - Bill of Lading databases
            
            # Simulated search for demonstration
            # Search for company as consignee (importer)
            suppliers = self._query_import_records(company, 'consignee')
            for supplier in suppliers:
                trade_data['suppliers'].append({
                    'name': supplier.get('shipper'),
                    'country': supplier.get('origin_country'),
                    'products': supplier.get('products', []),
                    'last_shipment': supplier.get('date'),
                    'frequency': supplier.get('shipment_count', 1)
                })
                
            # Search for company as shipper (exporter)
            buyers = self._query_import_records(company, 'shipper')
            for buyer in buyers:
                trade_data['buyers'].append({
                    'name': buyer.get('consignee'),
                    'country': buyer.get('destination_country'),
                    'products': buyer.get('products', []),
                    'last_shipment': buyer.get('date'),
                    'frequency': buyer.get('shipment_count', 1)
                })
                
        except Exception as e:
            logger.error(f"Failed to search trade databases for {company}: {e}")
            
        return trade_data
    
    def _query_import_records(self, company: str, role: str) -> List[Dict[str, Any]]:
        """Query import/export records (placeholder for actual implementation)."""
        # This would connect to real trade databases
        # For demonstration, returning simulated data
        records = []
        
        # Simulated API call
        # url = f"https://api.tradedatabase.com/search?{role}={company}"
        # response = requests.get(url, timeout=30)
        
        return records
    
    def _search_corporate_filings(self, company: str) -> Dict[str, Any]:
        """Search SEC filings and corporate databases."""
        corporate_data = {
            'financials': {},
            'subsidiaries': [],
            'parent': None,
            'executives': [],
            'risk_factors': []
        }
        
        try:
            # Search SEC EDGAR database
            edgar_data = self._query_sec_edgar(company)
            if edgar_data:
                corporate_data.update(edgar_data)
                
            # Search international corporate registries
            # This would query databases like:
            # - Companies House (UK)
            # - Orbis
            # - D&B Hoovers
            
        except Exception as e:
            logger.error(f"Failed to search corporate filings for {company}: {e}")
            
        return corporate_data
    
    def _query_sec_edgar(self, company: str) -> Optional[Dict[str, Any]]:
        """Query SEC EDGAR database for company filings."""
        try:
            # SEC EDGAR API endpoint
            cik = self._get_company_cik(company)
            if not cik:
                return None
                
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
            headers = {
                'User-Agent': 'Qutebrowser OSINT Module (contact@example.com)'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant financial data
                facts = data.get('facts', {})
                
                return {
                    'financials': self._extract_financial_metrics(facts),
                    'fiscal_year_end': data.get('fiscal_year_end'),
                    'entity_name': data.get('entityName')
                }
                
        except Exception as e:
            logger.debug(f"SEC EDGAR query failed for {company}: {e}")
            
        return None
    
    def _get_company_cik(self, company: str) -> Optional[int]:
        """Get CIK (Central Index Key) for a company."""
        # This would query SEC's company tickers JSON
        # For demo purposes, returning None
        return None
    
    def _extract_financial_metrics(self, facts: Dict) -> Dict[str, Any]:
        """Extract key financial metrics from XBRL facts."""
        metrics = {}
        
        # Extract common financial metrics
        us_gaap = facts.get('us-gaap', {})
        
        metric_mapping = {
            'revenue': 'Revenues',
            'net_income': 'NetIncomeLoss',
            'assets': 'Assets',
            'liabilities': 'Liabilities',
            'cash': 'CashAndCashEquivalentsAtCarryingValue'
        }
        
        for key, xbrl_name in metric_mapping.items():
            if xbrl_name in us_gaap:
                units = us_gaap[xbrl_name].get('units', {})
                if 'USD' in units:
                    values = units['USD']
                    if values:
                        # Get most recent value
                        latest = sorted(values, key=lambda x: x.get('end', ''))[-1]
                        metrics[key] = {
                            'value': latest.get('val'),
                            'date': latest.get('end'),
                            'period': latest.get('frame')
                        }
                        
        return metrics
    
    def _identify_technology_stack(self, company: str) -> List[Dict[str, str]]:
        """Identify technology stack and software dependencies."""
        tech_stack = []
        
        try:
            # Check for public repositories (GitHub, GitLab)
            github_repos = self._search_github_org(company)
            for repo in github_repos:
                # Analyze repository for technology indicators
                languages = repo.get('languages', [])
                dependencies = repo.get('dependencies', [])
                
                for lang in languages:
                    tech_stack.append({
                        'type': 'programming_language',
                        'name': lang,
                        'source': 'github'
                    })
                    
            # Check job postings for technology requirements
            job_tech = self._analyze_job_postings(company)
            tech_stack.extend(job_tech)
            
            # Check for SBOM (Software Bill of Materials) if available
            sbom = self._search_sbom(company)
            if sbom:
                for component in sbom:
                    tech_stack.append({
                        'type': 'dependency',
                        'name': component.get('name'),
                        'version': component.get('version'),
                        'source': 'sbom'
                    })
                    
        except Exception as e:
            logger.error(f"Failed to identify tech stack for {company}: {e}")
            
        return tech_stack
    
    def _search_github_org(self, company: str) -> List[Dict[str, Any]]:
        """Search for company's GitHub organization and repositories."""
        repos = []
        
        try:
            # GitHub API search
            url = f"https://api.github.com/search/users?q={company}+type:org"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for org in data.get('items', [])[:3]:  # Check top 3 results
                    # Get organization repos
                    repos_url = org.get('repos_url')
                    if repos_url:
                        repos_response = requests.get(repos_url, timeout=10)
                        if repos_response.status_code == 200:
                            org_repos = repos_response.json()
                            
                            for repo in org_repos:
                                repos.append({
                                    'name': repo.get('name'),
                                    'languages': [repo.get('language')],
                                    'description': repo.get('description'),
                                    'url': repo.get('html_url')
                                })
                                
        except Exception as e:
            logger.debug(f"GitHub search failed for {company}: {e}")
            
        return repos
    
    def _analyze_job_postings(self, company: str) -> List[Dict[str, str]]:
        """Analyze job postings to identify technology requirements."""
        tech_requirements = []
        
        # Common technology keywords to search for
        tech_keywords = [
            'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Vue',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'TensorFlow', 'PyTorch', 'Spark', 'Hadoop', 'Kafka'
        ]
        
        # This would query job posting APIs or scrape job sites
        # For demonstration, returning empty list
        
        return tech_requirements
    
    def _search_sbom(self, company: str) -> List[Dict[str, Any]]:
        """Search for Software Bill of Materials."""
        # This would search for published SBOMs
        # Many companies now publish these for transparency
        return []
    
    def _assess_supply_chain_risk(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess supply chain risks based on collected data."""
        risk_assessment = {
            'overall_risk': 'medium',
            'risk_factors': [],
            'vulnerabilities': [],
            'recommendations': []
        }
        
        # Check geographic concentration risk
        supplier_countries = set()
        for vendor in company_data.get('vendors', []):
            if vendor.get('country'):
                supplier_countries.add(vendor['country'])
                
        if len(supplier_countries) <= 2:
            risk_assessment['risk_factors'].append({
                'type': 'geographic_concentration',
                'severity': 'high',
                'description': f'Supply chain concentrated in {len(supplier_countries)} countries'
            })
            risk_assessment['overall_risk'] = 'high'
            
        # Check for single points of failure
        critical_vendors = [v for v in company_data.get('vendors', []) 
                          if v.get('frequency', 0) > 10]
        if critical_vendors:
            risk_assessment['risk_factors'].append({
                'type': 'vendor_dependency',
                'severity': 'medium',
                'description': f'{len(critical_vendors)} critical vendor dependencies identified'
            })
            
        # Check technology vulnerabilities
        for tech in company_data.get('technologies', []):
            vulns = self._check_technology_vulnerabilities(tech.get('name'), tech.get('version'))
            if vulns:
                risk_assessment['vulnerabilities'].extend(vulns)
                
        # Generate recommendations
        if risk_assessment['risk_factors']:
            risk_assessment['recommendations'].append('Diversify supplier base geographically')
            risk_assessment['recommendations'].append('Implement vendor redundancy for critical components')
            risk_assessment['recommendations'].append('Conduct regular third-party risk assessments')
            
        self.risk_identified.emit(risk_assessment)
        return risk_assessment
    
    def _check_technology_vulnerabilities(self, tech_name: str, version: Optional[str] = None) -> List[Dict[str, str]]:
        """Check for known vulnerabilities in technology stack."""
        vulnerabilities = []
        
        # This would query CVE databases for the technology
        # For demonstration, returning empty list
        
        return vulnerabilities
    
    def map_nth_party_vendors(self, company: str, depth: int = 3) -> Dict[str, Any]:
        """Map supply chain to N-th tier vendors."""
        supply_chain_map = {
            'root': company,
            'depth': depth,
            'tiers': {},
            'total_vendors': 0
        }
        
        current_tier = [company]
        
        for tier_level in range(1, depth + 1):
            next_tier = []
            supply_chain_map[f'tier_{tier_level}'] = []
            
            for company_name in current_tier:
                company_data = self.analyze_company(company_name)
                
                for vendor in company_data.get('vendors', []):
                    vendor_name = vendor.get('name')
                    if vendor_name:
                        supply_chain_map[f'tier_{tier_level}'].append({
                            'name': vendor_name,
                            'parent': company_name,
                            'country': vendor.get('country'),
                            'products': vendor.get('products', [])
                        })
                        next_tier.append(vendor_name)
                        supply_chain_map['total_vendors'] += 1
                        
            current_tier = list(set(next_tier))  # Remove duplicates
            
            if not current_tier:
                break  # No more vendors to explore
                
        return supply_chain_map
    
    def identify_shared_suppliers(self, companies: List[str]) -> Dict[str, List[str]]:
        """Identify suppliers shared between multiple companies."""
        shared_suppliers = defaultdict(list)
        
        for company in companies:
            company_data = self.analyze_company(company)
            
            for vendor in company_data.get('vendors', []):
                vendor_name = vendor.get('name')
                if vendor_name:
                    shared_suppliers[vendor_name].append(company)
                    
        # Filter to only shared suppliers
        shared_suppliers = {k: v for k, v in shared_suppliers.items() if len(v) > 1}
        
        return dict(shared_suppliers)
    
    def analyze_patent_dependencies(self, company: str) -> List[Dict[str, Any]]:
        """Analyze patent filings to identify technology dependencies."""
        patents = []
        
        try:
            # Query patent databases (USPTO, EPO, WIPO)
            # This would use APIs like:
            # - USPTO PatentsView API
            # - EPO Open Patent Services
            # - Google Patents Public Datasets
            
            # For demonstration, returning empty list
            pass
            
        except Exception as e:
            logger.error(f"Failed to analyze patents for {company}: {e}")
            
        return patents
    
    def track_hiring_patterns(self, company: str) -> Dict[str, Any]:
        """Track hiring patterns to predict strategic changes."""
        hiring_analysis = {
            'company': company,
            'timestamp': datetime.now().isoformat(),
            'total_openings': 0,
            'departments': defaultdict(int),
            'skills_in_demand': defaultdict(int),
            'locations': defaultdict(int),
            'trend': 'stable',
            'strategic_indicators': []
        }
        
        # This would query job posting APIs and platforms
        # Analyzing:
        # - Volume of postings over time
        # - Types of roles being hired
        # - Required skills and technologies
        # - Geographic expansion patterns
        
        return dict(hiring_analysis)
    
    def create_report(self, company: str, supply_chain_data: Dict[str, Any]) -> IntelligenceReport:
        """Create an intelligence report from supply chain analysis."""
        confidence = 0.7  # Moderate confidence for supply chain data
        
        # Adjust confidence based on data completeness
        if supply_chain_data.get('vendors') and supply_chain_data.get('financial_data'):
            confidence = 0.8
            
        tags = ['supply_chain', 'vendor', 'third_party_risk']
        
        # Add risk tags
        risk_level = supply_chain_data.get('risk_assessment', {}).get('overall_risk')
        if risk_level == 'high':
            tags.append('high_risk')
        elif risk_level == 'critical':
            tags.append('critical_risk')
            
        return IntelligenceReport(
            source='supply_chain_mapper',
            target=company,
            data_type='supply_chain_analysis',
            data=supply_chain_data,
            confidence=confidence,
            tags=tags
        )
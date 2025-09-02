"""Automated monitoring and alerting system for OSINT data."""

import os
import json
import hashlib
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import threading
import time

import requests
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from qutebrowser.utils import message, log
from qutebrowser.osint.core import IntelligenceReport
try:
    from qutebrowser.utils import standarddir
except ImportError:
    # For testing without full qutebrowser environment
    import tempfile
    from pathlib import Path
    class MockStandardDir:
        @staticmethod
        def data():
            return Path(tempfile.gettempdir()) / 'qutebrowser_test'
    standarddir = MockStandardDir()

logger = log.osint_monitor = logging.getLogger('osint.monitoring')


class MonitoringRule:
    """Defines a monitoring rule for automated tracking."""
    
    def __init__(self, rule_id: str, name: str, rule_type: str, 
                 target: str, conditions: Dict[str, Any], 
                 actions: List[str], interval: int = 3600):
        self.rule_id = rule_id
        self.name = name
        self.rule_type = rule_type  # 'paste', 'cert', 'domain', 'filing', 'social'
        self.target = target
        self.conditions = conditions
        self.actions = actions
        self.interval = interval  # Check interval in seconds
        self.last_check = None
        self.enabled = True
        self.matches = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'rule_type': self.rule_type,
            'target': self.target,
            'conditions': self.conditions,
            'actions': self.actions,
            'interval': self.interval,
            'enabled': self.enabled,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'match_count': len(self.matches)
        }


class MonitoringEngine(QObject):
    """Engine for automated monitoring and alerting."""
    
    alert_triggered = pyqtSignal(dict)
    data_leak_detected = pyqtSignal(dict)
    change_detected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules: Dict[str, MonitoringRule] = {}
        self.monitoring_active = False
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._run_checks)
        self.paste_sites = self._get_paste_sites()
        self.monitored_data = defaultdict(dict)
        self._init_storage()
        # Don't auto-start monitoring
        self.check_timer.stop()
        
    def _init_storage(self):
        """Initialize storage for monitoring data."""
        self.storage_path = Path(standarddir.data()) / 'osint' / 'monitoring'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.rules_file = self.storage_path / 'rules.json'
        self.alerts_file = self.storage_path / 'alerts.json'
        
        # Only load rules if file exists and we're not in test mode
        if self.rules_file.exists() and not os.environ.get('OSINT_TEST_MODE'):
            self._load_rules()
        
    def _get_paste_sites(self) -> List[Dict[str, str]]:
        """Get list of paste sites to monitor."""
        return [
            {'name': 'pastebin', 'url': 'https://pastebin.com/api/scraping.php'},
            {'name': 'ghostbin', 'url': 'https://ghostbin.co/recent'},
            {'name': 'dpaste', 'url': 'https://dpaste.org/api/'},
            {'name': 'hastebin', 'url': 'https://hastebin.com/documents'},
            {'name': 'rentry', 'url': 'https://rentry.co/api/recent'},
            {'name': 'textbin', 'url': 'https://textbin.net/api/latest'}
        ]
        
    def add_rule(self, name: str, rule_type: str, target: str, 
                 conditions: Dict[str, Any], actions: List[str], 
                 interval: int = 3600) -> str:
        """Add a new monitoring rule."""
        rule_id = hashlib.md5(f"{name}{target}{datetime.now()}".encode()).hexdigest()[:8]
        
        rule = MonitoringRule(
            rule_id=rule_id,
            name=name,
            rule_type=rule_type,
            target=target,
            conditions=conditions,
            actions=actions,
            interval=interval
        )
        
        self.rules[rule_id] = rule
        self._save_rules()
        
        logger.info(f"Added monitoring rule: {name} (ID: {rule_id})")
        return rule_id
        
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a monitoring rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self._save_rules()
            logger.info(f"Removed monitoring rule: {rule_id}")
            return True
        return False
        
    def _save_rules(self):
        """Save monitoring rules to disk."""
        rules_data = {
            rule_id: rule.to_dict() 
            for rule_id, rule in self.rules.items()
        }
        
        with open(self.rules_file, 'w') as f:
            json.dump(rules_data, f, indent=2)
            
    def _load_rules(self):
        """Load monitoring rules from disk."""
        if self.rules_file.exists():
            try:
                with open(self.rules_file, 'r') as f:
                    rules_data = json.load(f)
                    
                for rule_id, rule_dict in rules_data.items():
                    rule = MonitoringRule(
                        rule_id=rule_dict['rule_id'],
                        name=rule_dict['name'],
                        rule_type=rule_dict['rule_type'],
                        target=rule_dict['target'],
                        conditions=rule_dict['conditions'],
                        actions=rule_dict['actions'],
                        interval=rule_dict.get('interval', 3600)
                    )
                    rule.enabled = rule_dict.get('enabled', True)
                    self.rules[rule_id] = rule
                    
            except Exception as e:
                logger.error(f"Failed to load monitoring rules: {e}")
                
    def start_monitoring(self):
        """Start the monitoring engine."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.check_timer.start(60000)  # Check every minute
            logger.info("Monitoring engine started")
            message.info("OSINT monitoring started")
            
    def stop_monitoring(self):
        """Stop the monitoring engine."""
        if self.monitoring_active:
            self.monitoring_active = False
            self.check_timer.stop()
            logger.info("Monitoring engine stopped")
            message.info("OSINT monitoring stopped")
            
    def _run_checks(self):
        """Run monitoring checks for all active rules."""
        if not self.monitoring_active:
            return
            
        current_time = datetime.now()
        
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
                
            # Check if it's time to run this rule
            if rule.last_check:
                time_since_check = (current_time - rule.last_check).total_seconds()
                if time_since_check < rule.interval:
                    continue
                    
            # Run the appropriate check based on rule type
            try:
                if rule.rule_type == 'paste':
                    self._check_paste_sites(rule)
                elif rule.rule_type == 'cert':
                    self._check_certificate_changes(rule)
                elif rule.rule_type == 'domain':
                    self._check_domain_changes(rule)
                elif rule.rule_type == 'filing':
                    self._check_corporate_filings(rule)
                elif rule.rule_type == 'social':
                    self._check_social_media(rule)
                elif rule.rule_type == 'blockchain':
                    self._check_blockchain_activity(rule)
                    
                rule.last_check = current_time
                
            except Exception as e:
                logger.error(f"Error checking rule {rule_id}: {e}")
                
    def _check_paste_sites(self, rule: MonitoringRule):
        """Monitor paste sites for sensitive data."""
        keywords = rule.conditions.get('keywords', [])
        regex_patterns = rule.conditions.get('patterns', [])
        
        for site in self.paste_sites:
            try:
                # Check recent pastes
                recent_pastes = self._get_recent_pastes(site)
                
                for paste in recent_pastes:
                    content = paste.get('content', '')
                    
                    # Check for keywords
                    for keyword in keywords:
                        if keyword.lower() in content.lower():
                            self._trigger_alert(rule, {
                                'type': 'keyword_match',
                                'site': site['name'],
                                'keyword': keyword,
                                'paste_id': paste.get('id'),
                                'url': paste.get('url'),
                                'content_preview': content[:500]
                            })
                            
                    # Check for patterns (e.g., email addresses, API keys)
                    for pattern_name, pattern in regex_patterns.items():
                        import re
                        if re.search(pattern, content):
                            self._trigger_alert(rule, {
                                'type': 'pattern_match',
                                'site': site['name'],
                                'pattern': pattern_name,
                                'paste_id': paste.get('id'),
                                'url': paste.get('url'),
                                'content_preview': content[:500]
                            })
                            
            except Exception as e:
                logger.debug(f"Failed to check paste site {site['name']}: {e}")
                
    def _get_recent_pastes(self, site: Dict[str, str]) -> List[Dict[str, Any]]:
        """Get recent pastes from a paste site."""
        pastes = []
        
        # This would implement actual scraping/API calls for each paste site
        # For demonstration, returning empty list
        
        return pastes
        
    def _check_certificate_changes(self, rule: MonitoringRule):
        """Monitor for SSL certificate changes."""
        domain = rule.target
        
        try:
            from qutebrowser.osint.certificates import CertificateIntelligence
            cert_intel = CertificateIntelligence()
            
            # Get current certificate
            current_cert = cert_intel.get_certificate(domain)
            
            if current_cert:
                cert_hash = current_cert.get('fingerprint_sha256')
                
                # Check if certificate has changed
                previous_hash = self.monitored_data['certificates'].get(domain)
                
                if previous_hash and previous_hash != cert_hash:
                    self._trigger_alert(rule, {
                        'type': 'certificate_change',
                        'domain': domain,
                        'old_fingerprint': previous_hash,
                        'new_fingerprint': cert_hash,
                        'issuer': current_cert.get('issuer'),
                        'not_after': current_cert.get('not_after')
                    })
                    
                self.monitored_data['certificates'][domain] = cert_hash
                
                # Only check CT logs if explicitly requested
                if rule.conditions.get('check_ct_logs', False):
                    try:
                        ct_results = cert_intel.search_certificate_transparency(domain)
                        
                        for cert in ct_results[:10]:  # Limit to 10 most recent
                            cert_id = cert.get('id')
                            if cert_id not in rule.matches:
                                rule.matches.append(cert_id)
                                
                                # New certificate issued
                                self._trigger_alert(rule, {
                                    'type': 'new_certificate',
                                    'domain': domain,
                                    'certificate': cert
                                })
                    except:
                        pass  # CT log check failed, continue
                        
        except Exception as e:
            logger.error(f"Failed to check certificate for {domain}: {e}")
            
    def _check_domain_changes(self, rule: MonitoringRule):
        """Monitor domain registration and DNS changes."""
        domain = rule.target
        
        try:
            # Check DNS records
            import socket
            
            current_ips = set()
            try:
                results = socket.getaddrinfo(domain, None)
                current_ips = {r[4][0] for r in results}
            except socket.gaierror:
                pass
                
            previous_ips = set(self.monitored_data['dns'].get(domain, []))
            
            if previous_ips and current_ips != previous_ips:
                added_ips = current_ips - previous_ips
                removed_ips = previous_ips - current_ips
                
                self._trigger_alert(rule, {
                    'type': 'dns_change',
                    'domain': domain,
                    'added_ips': list(added_ips),
                    'removed_ips': list(removed_ips),
                    'current_ips': list(current_ips)
                })
                
            self.monitored_data['dns'][domain] = list(current_ips)
            
            # Check for subdomain changes
            self._check_subdomains(rule, domain)
            
        except Exception as e:
            logger.error(f"Failed to check domain {domain}: {e}")
            
    def _check_subdomains(self, rule: MonitoringRule, domain: str):
        """Check for new subdomains."""
        # This would use Certificate Transparency logs or DNS enumeration
        # to find new subdomains
        pass
        
    def _check_corporate_filings(self, rule: MonitoringRule):
        """Monitor SEC filings and corporate announcements."""
        company = rule.target
        filing_types = rule.conditions.get('filing_types', ['10-K', '10-Q', '8-K'])
        
        try:
            # Check SEC EDGAR for new filings
            # This would implement actual SEC API calls
            
            # Check for specific events in 8-K filings
            if '8-K' in filing_types:
                # Material events to monitor
                material_events = [
                    'Item 1.01',  # Entry into Material Agreement
                    'Item 2.01',  # Completion of Acquisition
                    'Item 5.02',  # Departure of Directors or Officers
                    'Item 7.01',  # Regulation FD Disclosure
                ]
                
                # Would check for these specific items in recent filings
                
        except Exception as e:
            logger.error(f"Failed to check filings for {company}: {e}")
            
    def _check_social_media(self, rule: MonitoringRule):
        """Monitor social media for mentions and sentiment."""
        target = rule.target
        platforms = rule.conditions.get('platforms', ['twitter', 'reddit'])
        
        # This would implement social media monitoring
        # Using APIs or web scraping for each platform
        pass
        
    def _check_blockchain_activity(self, rule: MonitoringRule):
        """Monitor blockchain addresses for activity."""
        address = rule.target
        
        try:
            from qutebrowser.osint.blockchain import BlockchainAnalyzer
            blockchain = BlockchainAnalyzer()
            
            # Check for new transactions
            if 'bitcoin' in address or address.startswith(('1', '3', 'bc1')):
                current_data = blockchain.analyze_bitcoin_address(address)
            elif address.startswith('0x'):
                current_data = blockchain.analyze_ethereum_address(address)
            else:
                return
                
            previous_tx_count = self.monitored_data['blockchain'].get(
                f"{address}_tx_count", 0
            )
            
            current_tx_count = current_data.get('transaction_count', 0)
            
            if previous_tx_count and current_tx_count > previous_tx_count:
                self._trigger_alert(rule, {
                    'type': 'new_transaction',
                    'address': address,
                    'new_transactions': current_tx_count - previous_tx_count,
                    'current_balance': current_data.get('balance', 0),
                    'recent_activity': current_data.get('transactions', [])[:5]
                })
                
            self.monitored_data['blockchain'][f"{address}_tx_count"] = current_tx_count
            
        except Exception as e:
            logger.error(f"Failed to check blockchain address {address}: {e}")
            
    def _trigger_alert(self, rule: MonitoringRule, alert_data: Dict[str, Any]):
        """Trigger an alert based on rule actions."""
        alert = {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'timestamp': datetime.now().isoformat(),
            'data': alert_data
        }
        
        # Execute actions
        for action in rule.actions:
            if action == 'notify':
                message.warning(f"OSINT Alert: {rule.name} - {alert_data.get('type')}")
                self.alert_triggered.emit(alert)
                
            elif action == 'log':
                self._log_alert(alert)
                
            elif action == 'email':
                # Would send email notification
                pass
                
            elif action == 'webhook':
                # Would call webhook URL
                pass
                
        # Special handling for data leaks
        if alert_data.get('type') in ['keyword_match', 'pattern_match']:
            self.data_leak_detected.emit(alert)
            
        # Handle changes
        if 'change' in alert_data.get('type', ''):
            self.change_detected.emit(alert)
            
    def _log_alert(self, alert: Dict[str, Any]):
        """Log alert to file."""
        alerts = []
        
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r') as f:
                    alerts = json.load(f)
            except:
                pass
                
        alerts.append(alert)
        
        # Keep only last 1000 alerts
        alerts = alerts[-1000:]
        
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)
            
    def get_alerts(self, rule_id: Optional[str] = None, 
                   days: int = 7) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        alerts = []
        
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r') as f:
                    all_alerts = json.load(f)
                    
                cutoff_date = datetime.now() - timedelta(days=days)
                
                for alert in all_alerts:
                    alert_time = datetime.fromisoformat(alert['timestamp'])
                    
                    if alert_time >= cutoff_date:
                        if rule_id is None or alert['rule_id'] == rule_id:
                            alerts.append(alert)
                            
            except Exception as e:
                logger.error(f"Failed to load alerts: {e}")
                
        return alerts
        
    def create_leak_monitor(self, keywords: List[str], 
                           email_domains: List[str] = None) -> str:
        """Create a monitor for data leaks on paste sites."""
        patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'api_key': r'[a-zA-Z0-9]{32,}',
            'private_key': r'-----BEGIN (RSA )?PRIVATE KEY-----',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'github_token': r'ghp_[a-zA-Z0-9]{36}'
        }
        
        if email_domains:
            email_pattern = '|'.join(f'@{domain}' for domain in email_domains)
            patterns['company_email'] = email_pattern
            
        return self.add_rule(
            name='Data Leak Monitor',
            rule_type='paste',
            target='all',
            conditions={
                'keywords': keywords,
                'patterns': patterns
            },
            actions=['notify', 'log'],
            interval=300  # Check every 5 minutes
        )
        
    def create_infrastructure_monitor(self, domains: List[str]) -> str:
        """Create a monitor for infrastructure changes."""
        rule_ids = []
        
        for domain in domains:
            # Monitor certificate changes
            cert_rule = self.add_rule(
                name=f'Certificate Monitor - {domain}',
                rule_type='cert',
                target=domain,
                conditions={},
                actions=['notify', 'log'],
                interval=86400  # Daily
            )
            rule_ids.append(cert_rule)
            
            # Monitor DNS changes
            dns_rule = self.add_rule(
                name=f'DNS Monitor - {domain}',
                rule_type='domain',
                target=domain,
                conditions={},
                actions=['notify', 'log'],
                interval=3600  # Hourly
            )
            rule_ids.append(dns_rule)
            
        return rule_ids
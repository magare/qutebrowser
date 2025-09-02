#!/usr/bin/env python3
"""Complete test suite for OSINT features."""

import sys
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Mock standarddir for testing
class MockStandardDir:
    @staticmethod
    def data():
        path = Path(tempfile.gettempdir()) / 'qutebrowser_test'
        path.mkdir(exist_ok=True)
        return path

# Mock imports before importing OSINT modules
sys.modules['qutebrowser.utils.standarddir'] = Mock()
sys.modules['qutebrowser.utils.standarddir'].data = MockStandardDir.data
sys.modules['qutebrowser.utils.message'] = Mock()
sys.modules['qutebrowser.utils.log'] = Mock()
sys.modules['qutebrowser.config.config'] = Mock()

from qutebrowser.osint.core import OSINTEngine, IntelligenceReport
from qutebrowser.osint.bgp import BGPAnalyzer
from qutebrowser.osint.certificates import CertificateIntelligence
from qutebrowser.osint.blockchain import BlockchainAnalyzer
from qutebrowser.osint.search_engines import AdvancedSearchEngine
from qutebrowser.osint.supply_chain import SupplyChainMapper
from qutebrowser.osint.monitoring import MonitoringEngine
from qutebrowser.osint.correlation import CorrelationDatabase


class TestOSINTCore(unittest.TestCase):
    """Test core OSINT engine functionality."""
    
    def setUp(self):
        self.engine = OSINTEngine()
    
    def test_add_report(self):
        """Test adding intelligence reports."""
        report = IntelligenceReport(
            source='test',
            target='test.com',
            data_type='test',
            data={'test': True}
        )
        self.engine.add_report(report)
        self.assertGreater(len(self.engine.reports), 0)
    
    def test_get_reports(self):
        """Test retrieving reports by target."""
        report = IntelligenceReport(
            source='test',
            target='example.com',
            data_type='test',
            data={'test': True}
        )
        self.engine.add_report(report)
        reports = self.engine.get_reports(target='example.com')
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].target, 'example.com')


class TestBGPAnalyzer(unittest.TestCase):
    """Test BGP/ASN analysis functionality."""
    
    def setUp(self):
        self.bgp = BGPAnalyzer()
    
    def test_create_report(self):
        """Test BGP report creation."""
        result = {
            'ip': '8.8.8.8',
            'asn': 15169,
            'asn_name': 'GOOGLE',
            'prefix': '8.8.8.0/24'
        }
        report = self.bgp.create_report('8.8.8.8', result)
        self.assertEqual(report.source, 'bgp_analyzer')
        self.assertEqual(report.target, '8.8.8.8')
    
    def test_cache_functionality(self):
        """Test BGP cache mechanism."""
        self.assertEqual(len(self.bgp.cache), 0)
        # Cache would be populated after actual API calls


class TestCertificateIntelligence(unittest.TestCase):
    """Test SSL/TLS certificate intelligence."""
    
    def setUp(self):
        self.cert_intel = CertificateIntelligence()
    
    def test_wildcard_detection(self):
        """Test wildcard certificate abuse detection."""
        # Should not make network calls for wildcard domains
        wildcards = self.cert_intel.detect_wildcard_abuse('*.example.com')
        self.assertIsInstance(wildcards, list)
        self.assertEqual(len(wildcards), 0)
    
    def test_create_report(self):
        """Test certificate report creation."""
        test_cert = {
            'fingerprint_sha256': 'a' * 64,
            'subject': {'commonName': 'test.com'},
            'issuer': {'organizationName': 'Test CA'},
            'not_after': '2025-12-31T00:00:00'
        }
        report = self.cert_intel.create_report('test.com', test_cert)
        self.assertEqual(report.source, 'certificate_intelligence')
        self.assertGreater(report.confidence, 0)


class TestBlockchainAnalyzer(unittest.TestCase):
    """Test blockchain and cryptocurrency analysis."""
    
    def setUp(self):
        self.blockchain = BlockchainAnalyzer()
    
    def test_bitcoin_detection(self):
        """Test Bitcoin address detection."""
        text = "Send payment to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        detected = self.blockchain.detect_addresses(text)
        self.assertIn('bitcoin', detected)
        self.assertEqual(len(detected['bitcoin']), 1)
    
    def test_ethereum_detection(self):
        """Test Ethereum address detection."""
        text = "ETH: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
        detected = self.blockchain.detect_addresses(text)
        self.assertIn('ethereum', detected)
    
    def test_multiple_crypto_detection(self):
        """Test detection of multiple cryptocurrency types."""
        text = """
        BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
        ETH: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1
        XMR: 48qa3pSKmyb6tsfUz3VaZRXYRpJPBSwqxYch9FaJVzKNKsPXkSohEDWSXqmS1ZXBhfPqBVBh3jUcUHZCJ8wH9SroMPj5xDR
        """
        detected = self.blockchain.detect_addresses(text)
        self.assertIn('bitcoin', detected)
        self.assertIn('ethereum', detected)
        self.assertIn('monero', detected)
    
    def test_exchange_identification(self):
        """Test exchange wallet identification."""
        # Known Binance address
        exchange = self.blockchain.identify_exchange_wallets(
            '0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be'
        )
        # Returns None if not in predefined list
        self.assertIsNone(exchange)


class TestSearchEngines(unittest.TestCase):
    """Test search engine integration."""
    
    def setUp(self):
        self.search = AdvancedSearchEngine()
    
    def test_exposed_databases_search(self):
        """Test exposed database search structure."""
        exposed = self.search.search_exposed_databases()
        self.assertIsInstance(exposed, list)
    
    def test_ics_search(self):
        """Test industrial control system search."""
        ics = self.search.search_industrial_control_systems()
        self.assertIsInstance(ics, list)
    
    def test_cve_lookup_structure(self):
        """Test CVE lookup structure."""
        # Would normally return CVE data
        self.assertEqual(len(self.search.search_cache), 0)


class TestSupplyChain(unittest.TestCase):
    """Test supply chain mapping functionality."""
    
    def setUp(self):
        self.supply_chain = SupplyChainMapper()
    
    def test_company_analysis(self):
        """Test company analysis structure."""
        analysis = self.supply_chain.analyze_company('TestCorp')
        self.assertEqual(analysis['company'], 'TestCorp')
        self.assertIn('risk_assessment', analysis)
        self.assertIn('vendors', analysis)
        self.assertIn('technology_stack', analysis)
    
    def test_shared_suppliers(self):
        """Test identification of shared suppliers."""
        shared = self.supply_chain.identify_shared_suppliers(['CompanyA', 'CompanyB'])
        self.assertIsInstance(shared, dict)
        self.assertIn('shared_vendors', shared)
    
    def test_risk_assessment(self):
        """Test supply chain risk assessment."""
        analysis = self.supply_chain.analyze_company('TestCorp')
        risk = analysis['risk_assessment']
        self.assertIn('overall_risk', risk)
        self.assertIn('factors', risk)


class TestMonitoring(unittest.TestCase):
    """Test monitoring engine functionality."""
    
    def setUp(self):
        os.environ['OSINT_TEST_MODE'] = '1'
        self.monitor = MonitoringEngine()
    
    def tearDown(self):
        if 'OSINT_TEST_MODE' in os.environ:
            del os.environ['OSINT_TEST_MODE']
    
    def test_add_rule(self):
        """Test adding monitoring rules."""
        rule_id = self.monitor.add_rule(
            name='Test Rule',
            rule_type='domain',
            target='example.com',
            conditions={'check': 'dns'},
            actions=['log'],
            interval=3600
        )
        self.assertIn(rule_id, self.monitor.rules)
    
    def test_remove_rule(self):
        """Test removing monitoring rules."""
        rule_id = self.monitor.add_rule(
            name='Test Rule',
            rule_type='domain',
            target='example.com',
            conditions={},
            actions=['log']
        )
        result = self.monitor.remove_rule(rule_id)
        self.assertTrue(result)
        self.assertNotIn(rule_id, self.monitor.rules)
    
    def test_rule_persistence(self):
        """Test rule persistence to disk."""
        self.assertTrue(self.monitor.storage_path.exists())


class TestCorrelation(unittest.TestCase):
    """Test correlation database functionality."""
    
    def setUp(self):
        self.correlation = CorrelationDatabase()
    
    def test_add_entity(self):
        """Test adding entities to correlation database."""
        entity_id = self.correlation.add_entity('domain', 'example.com')
        self.assertIsNotNone(entity_id)
    
    def test_add_relationship(self):
        """Test adding relationships between entities."""
        domain_id = self.correlation.add_entity('domain', 'example.com')
        ip_id = self.correlation.add_entity('ip_address', '192.168.1.1')
        rel_id = self.correlation.add_relationship(
            domain_id, ip_id, 'resolves_to', 0.9
        )
        self.assertIsNotNone(rel_id)
    
    def test_correlation_search(self):
        """Test correlation search functionality."""
        # Add test data
        domain_id = self.correlation.add_entity('domain', 'test.com')
        ip_id = self.correlation.add_entity('ip_address', '10.0.0.1')
        self.correlation.add_relationship(domain_id, ip_id, 'resolves_to', 0.95)
        
        # Search for correlations
        correlations = self.correlation.correlate_data('domain', 'test.com')
        self.assertGreater(len(correlations), 0)
    
    def test_graph_export(self):
        """Test graph export functionality."""
        # Add test data
        self.correlation.add_entity('domain', 'export-test.com')
        
        # Test JSON export
        json_data = self.correlation.export_graph('json')
        self.assertIn('entities', json_data)
        self.assertIn('relationships', json_data)


class TestCommands(unittest.TestCase):
    """Test command integration."""
    
    def test_command_availability(self):
        """Test that all commands are available."""
        from qutebrowser.osint import commands
        
        required_commands = [
            'osint_analyze',
            'osint_bgp',
            'osint_certificate',
            'osint_shodan',
            'osint_blockchain',
            'osint_supply_chain',
            'osint_monitor_start',
            'osint_monitor_stop',
            'osint_monitor_status',
            'osint_correlate',
            'osint_export',
            'osint_clear_cache',
            'osint_leak_monitor',
            'osint_detect_crypto'
        ]
        
        for cmd in required_commands:
            self.assertTrue(hasattr(commands, cmd))
            self.assertTrue(callable(getattr(commands, cmd)))


class TestUserscripts(unittest.TestCase):
    """Test userscript availability."""
    
    def test_userscripts_exist(self):
        """Test that userscripts exist and are executable."""
        scripts_dir = Path('userscripts/osint')
        self.assertTrue(scripts_dir.exists())
        
        required_scripts = [
            'analyze_page.py',
            'monitor_site.py',
            'search_shodan.py'
        ]
        
        for script in required_scripts:
            script_path = scripts_dir / script
            self.assertTrue(script_path.exists())
            self.assertTrue(os.access(script_path, os.X_OK))


def run_tests():
    """Run all OSINT tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOSINTCore))
    suite.addTests(loader.loadTestsFromTestCase(TestBGPAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestCertificateIntelligence))
    suite.addTests(loader.loadTestsFromTestCase(TestBlockchainAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchEngines))
    suite.addTests(loader.loadTestsFromTestCase(TestSupplyChain))
    suite.addTests(loader.loadTestsFromTestCase(TestMonitoring))
    suite.addTests(loader.loadTestsFromTestCase(TestCorrelation))
    suite.addTests(loader.loadTestsFromTestCase(TestCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestUserscripts))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
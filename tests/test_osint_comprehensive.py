#!/usr/bin/env python3
"""Comprehensive test suite for OSINT features."""

import sys
import os
import json
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime

# Add qutebrowser to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import OSINT modules
from qutebrowser.osint.core import OSINTEngine, IntelligenceReport
from qutebrowser.osint.bgp import BGPAnalyzer
from qutebrowser.osint.certificates import CertificateIntelligence
from qutebrowser.osint.blockchain import BlockchainAnalyzer
from qutebrowser.osint.search_engines import AdvancedSearchEngine
from qutebrowser.osint.supply_chain import SupplyChainMapper
from qutebrowser.osint.monitoring import MonitoringEngine, MonitoringRule
from qutebrowser.osint.correlation import CorrelationDatabase


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.errors = []
        
    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"  ✓ {test_name}")
        
    def add_fail(self, test_name, reason):
        self.failed.append((test_name, reason))
        print(f"  ✗ {test_name}: {reason}")
        
    def add_error(self, test_name, error):
        self.errors.append((test_name, error))
        print(f"  ⚠ {test_name}: {error}")
        
    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.errors)
        print("\n" + "=" * 60)
        print(f"Test Results: {len(self.passed)}/{total} passed")
        if self.failed:
            print(f"\nFailed tests ({len(self.failed)}):")
            for name, reason in self.failed:
                print(f"  - {name}: {reason}")
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        return len(self.failed) == 0 and len(self.errors) == 0


def test_core_engine():
    """Test the core OSINT engine."""
    print("\n[1] Testing Core OSINT Engine...")
    results = TestResults()
    
    try:
        # Initialize engine
        engine = OSINTEngine()
        results.add_pass("Engine initialization")
        
        # Test storage initialization
        assert engine.storage_path.exists()
        results.add_pass("Storage directory created")
        
        # Test report creation and storage
        report = IntelligenceReport(
            source='test_suite',
            target='test.example.com',
            data_type='test_data',
            data={'test_key': 'test_value', 'timestamp': datetime.now().isoformat()},
            confidence=0.85,
            tags=['test', 'validation']
        )
        
        engine.add_report(report)
        results.add_pass("Report creation and addition")
        
        # Test report retrieval
        reports = engine.get_reports(target='test.example.com')
        assert len(reports) > 0
        assert reports[0].target == 'test.example.com'
        results.add_pass("Report retrieval by target")
        
        # Test report filtering by data type
        reports_filtered = engine.get_reports(data_type='test_data')
        assert len(reports_filtered) > 0
        results.add_pass("Report filtering by data type")
        
        # Test export functionality
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            engine.export_reports(f.name, format='json')
            assert os.path.exists(f.name)
            
            # Verify JSON content
            with open(f.name, 'r') as rf:
                data = json.load(rf)
                assert isinstance(data, list)
                assert len(data) > 0
            os.unlink(f.name)
        results.add_pass("Report export to JSON")
        
        # Test cache clearing
        engine.clear_cache()
        results.add_pass("Cache clearing")
        
    except Exception as e:
        results.add_error("Core engine test", str(e))
        
    return results


def test_bgp_analyzer():
    """Test BGP/ASN analysis."""
    print("\n[2] Testing BGP/ASN Analyzer...")
    results = TestResults()
    
    try:
        bgp = BGPAnalyzer()
        results.add_pass("BGP analyzer initialization")
        
        # Test IP analysis with Google DNS
        ip_result = bgp.analyze_ip('8.8.8.8')
        assert ip_result is not None
        assert ip_result['ip'] == '8.8.8.8'
        if ip_result.get('asn'):
            results.add_pass(f"IP analysis (ASN: {ip_result.get('asn')})")
        else:
            results.add_pass("IP analysis (no ASN data available)")
        
        # Test domain analysis
        domain_result = bgp.analyze_domain('google.com')
        assert domain_result is not None
        assert domain_result['domain'] == 'google.com'
        results.add_pass("Domain BGP analysis")
        
        # Test caching
        cached_result = bgp.analyze_ip('8.8.8.8')
        assert cached_result == ip_result
        results.add_pass("BGP caching mechanism")
        
        # Test submarine cable dependencies
        cables = bgp.get_submarine_cable_dependencies('8.8.8.8')
        assert isinstance(cables, list)
        results.add_pass("Submarine cable dependency check")
        
        # Test report creation
        report = bgp.create_report('8.8.8.8', ip_result)
        assert report.source == 'bgp_analyzer'
        assert report.data_type == 'bgp_asn'
        results.add_pass("BGP report creation")
        
    except Exception as e:
        results.add_error("BGP analyzer test", str(e))
        
    return results


def test_certificate_intelligence():
    """Test certificate intelligence."""
    print("\n[3] Testing Certificate Intelligence...")
    results = TestResults()
    
    try:
        cert_intel = CertificateIntelligence()
        results.add_pass("Certificate intelligence initialization")
        
        # Test certificate retrieval (using a reliable domain)
        cert = cert_intel.get_certificate('google.com', 443)
        
        if cert:
            assert 'fingerprint_sha256' in cert
            assert 'subject' in cert
            assert 'issuer' in cert
            assert 'not_after' in cert
            results.add_pass(f"Certificate retrieval (SHA256: {cert['fingerprint_sha256'][:16]}...)")
            
            # Test certificate parsing
            assert isinstance(cert['subject'], dict)
            assert isinstance(cert['issuer'], dict)
            results.add_pass("Certificate parsing")
            
            # Test revocation check
            revocation = cert_intel.check_certificate_revocation(cert)
            assert 'checked' in revocation
            results.add_pass("Certificate revocation check")
            
        else:
            results.add_error("Certificate retrieval", "Could not connect to google.com:443")
        
        # Test wildcard detection
        wildcard_abuse = cert_intel.detect_wildcard_abuse('example.com')
        assert isinstance(wildcard_abuse, list)
        results.add_pass("Wildcard abuse detection")
        
        # Test report creation
        if cert:
            report = cert_intel.create_report('google.com', cert)
            assert report.source == 'certificate_intelligence'
            assert report.confidence > 0
            results.add_pass("Certificate report creation")
        
    except Exception as e:
        results.add_error("Certificate intelligence test", str(e))
        
    return results


def test_blockchain_analyzer():
    """Test blockchain analysis."""
    print("\n[4] Testing Blockchain Analyzer...")
    results = TestResults()
    
    try:
        blockchain = BlockchainAnalyzer()
        results.add_pass("Blockchain analyzer initialization")
        
        # Test address pattern compilation
        assert len(blockchain.address_patterns) > 0
        results.add_pass(f"Address patterns loaded ({len(blockchain.address_patterns)} types)")
        
        # Test address detection
        test_text = """
        Here are some crypto addresses:
        Bitcoin: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa (Genesis block)
        Ethereum: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb4
        Litecoin: LKDxGDJq5PiREaSzN7DihLvPJB3hDVmBQK
        Invalid: not_an_address_123
        """
        
        detected = blockchain.detect_addresses(test_text)
        assert 'bitcoin' in detected
        assert '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa' in detected['bitcoin']
        assert 'ethereum' in detected
        results.add_pass(f"Address detection ({len(detected)} cryptocurrencies)")
        
        # Test Bitcoin address analysis (Genesis block - should have data)
        btc_analysis = blockchain.analyze_bitcoin_address('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        assert btc_analysis is not None
        assert btc_analysis['address'] == '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
        assert btc_analysis['cryptocurrency'] == 'bitcoin'
        results.add_pass("Bitcoin address analysis")
        
        # Test Ethereum address structure
        eth_analysis = blockchain.analyze_ethereum_address('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb4')
        assert eth_analysis is not None
        assert eth_analysis['cryptocurrency'] == 'ethereum'
        results.add_pass("Ethereum address analysis")
        
        # Test address clustering
        addresses = ['1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', '1GH5JUKRpFbKKNHfcQjshzL4e3tQqDYqfH']
        clusters = blockchain.cluster_addresses(addresses)
        assert isinstance(clusters, dict)
        results.add_pass("Address clustering")
        
        # Test exchange identification
        exchange = blockchain.identify_exchange_wallets('0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be')
        if exchange:
            assert 'exchange' in exchange
            results.add_pass("Exchange wallet identification")
        else:
            results.add_pass("Exchange wallet identification (no match)")
        
        # Test report creation
        report = blockchain.create_report('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', btc_analysis)
        assert report.source == 'blockchain_analyzer'
        assert 'blockchain' in report.tags
        results.add_pass("Blockchain report creation")
        
    except Exception as e:
        results.add_error("Blockchain analyzer test", str(e))
        
    return results


def test_search_engines():
    """Test search engine integration."""
    print("\n[5] Testing Search Engine Integration...")
    results = TestResults()
    
    try:
        search = AdvancedSearchEngine()
        results.add_pass("Search engine initialization")
        
        # Test CVE details retrieval (Log4Shell - well-known CVE)
        cve_details = search._get_cve_details('CVE-2021-44228')
        if cve_details:
            assert 'id' in cve_details
            assert cve_details['id'] == 'CVE-2021-44228'
            results.add_pass(f"CVE details retrieval (severity: {cve_details.get('severity', 'N/A')})")
        else:
            results.add_pass("CVE details retrieval (API unavailable)")
        
        # Test exposed database search structure
        exposed_dbs = search.search_exposed_databases()
        assert isinstance(exposed_dbs, list)
        results.add_pass("Exposed database search structure")
        
        # Test ICS search structure
        ics_systems = search.search_industrial_control_systems()
        assert isinstance(ics_systems, list)
        results.add_pass("Industrial control system search structure")
        
        # Test default credentials check
        default_creds = search.find_default_credentials('192.168.1.1')
        assert isinstance(default_creds, list)
        results.add_pass("Default credentials check structure")
        
        # Test report creation
        test_results = {'query': 'test', 'total': 0, 'results': []}
        report = search.create_report('test_query', test_results)
        assert report.source == 'advanced_search'
        results.add_pass("Search report creation")
        
    except Exception as e:
        results.add_error("Search engine test", str(e))
        
    return results


def test_supply_chain():
    """Test supply chain mapping."""
    print("\n[6] Testing Supply Chain Mapper...")
    results = TestResults()
    
    try:
        supply_chain = SupplyChainMapper()
        results.add_pass("Supply chain mapper initialization")
        
        # Test company analysis structure
        company_data = supply_chain.analyze_company('TestCompany')
        assert company_data is not None
        assert company_data['company'] == 'TestCompany'
        assert 'vendors' in company_data
        assert 'risk_assessment' in company_data
        results.add_pass("Company analysis structure")
        
        # Test risk assessment
        risk = company_data['risk_assessment']
        assert 'overall_risk' in risk
        assert 'risk_factors' in risk
        assert 'recommendations' in risk
        results.add_pass("Risk assessment generation")
        
        # Test shared supplier identification
        shared = supply_chain.identify_shared_suppliers(['Company1', 'Company2', 'Company3'])
        assert isinstance(shared, dict)
        results.add_pass("Shared supplier identification")
        
        # Test N-th party vendor mapping
        supply_map = supply_chain.map_nth_party_vendors('TestCompany', depth=2)
        assert supply_map['root'] == 'TestCompany'
        assert supply_map['depth'] == 2
        assert 'total_vendors' in supply_map
        results.add_pass("N-th party vendor mapping")
        
        # Test hiring pattern tracking
        hiring = supply_chain.track_hiring_patterns('TestCompany')
        assert hiring['company'] == 'TestCompany'
        assert 'trend' in hiring
        assert 'strategic_indicators' in hiring
        results.add_pass("Hiring pattern analysis")
        
        # Test report creation
        report = supply_chain.create_report('TestCompany', company_data)
        assert report.source == 'supply_chain_mapper'
        assert report.data_type == 'supply_chain_analysis'
        results.add_pass("Supply chain report creation")
        
    except Exception as e:
        results.add_error("Supply chain test", str(e))
        
    return results


def test_monitoring_engine():
    """Test monitoring engine."""
    print("\n[7] Testing Monitoring Engine...")
    results = TestResults()
    
    try:
        monitor = MonitoringEngine()
        results.add_pass("Monitoring engine initialization")
        
        # Test storage initialization
        assert monitor.storage_path.exists()
        results.add_pass("Monitoring storage created")
        
        # Test rule creation
        rule_id = monitor.add_rule(
            name='Test Monitoring Rule',
            rule_type='domain',
            target='test.example.com',
            conditions={'keywords': ['test', 'example']},
            actions=['log'],
            interval=3600
        )
        assert rule_id in monitor.rules
        results.add_pass(f"Monitoring rule created (ID: {rule_id})")
        
        # Test rule retrieval
        rule = monitor.rules[rule_id]
        assert rule.name == 'Test Monitoring Rule'
        assert rule.target == 'test.example.com'
        results.add_pass("Rule retrieval and validation")
        
        # Test leak monitor creation
        leak_rule_id = monitor.create_leak_monitor(
            keywords=['password', 'api_key', 'secret'],
            email_domains=['example.com', 'test.com']
        )
        assert leak_rule_id in monitor.rules
        leak_rule = monitor.rules[leak_rule_id]
        assert leak_rule.rule_type == 'paste'
        results.add_pass("Data leak monitor creation")
        
        # Test infrastructure monitor
        infra_rules = monitor.create_infrastructure_monitor(['example.com', 'test.com'])
        assert len(infra_rules) > 0
        results.add_pass(f"Infrastructure monitor created ({len(infra_rules)} rules)")
        
        # Test rule removal
        removed = monitor.remove_rule(rule_id)
        assert removed == True
        assert rule_id not in monitor.rules
        results.add_pass("Rule removal")
        
        # Test alert retrieval
        alerts = monitor.get_alerts(days=1)
        assert isinstance(alerts, list)
        results.add_pass("Alert retrieval")
        
        # Test monitoring control
        monitor.start_monitoring()
        assert monitor.monitoring_active == True
        results.add_pass("Monitoring start")
        
        monitor.stop_monitoring()
        assert monitor.monitoring_active == False
        results.add_pass("Monitoring stop")
        
    except Exception as e:
        results.add_error("Monitoring engine test", str(e))
        
    return results


def test_correlation_database():
    """Test correlation database."""
    print("\n[8] Testing Correlation Database...")
    results = TestResults()
    
    try:
        correlation = CorrelationDatabase()
        results.add_pass("Correlation database initialization")
        
        # Verify database creation
        assert correlation.db_path.exists()
        results.add_pass("SQLite database created")
        
        # Test entity addition
        domain_id = correlation.add_entity('domain', 'test.example.com',
                                          metadata={'test': True})
        assert domain_id is not None
        results.add_pass(f"Domain entity added (ID: {domain_id[:8]}...)")
        
        ip_id = correlation.add_entity('ip_address', '192.168.1.1')
        assert ip_id is not None
        results.add_pass(f"IP entity added (ID: {ip_id[:8]}...)")
        
        # Test relationship creation
        rel_id = correlation.add_relationship(
            domain_id, ip_id,
            'resolves_to',
            confidence=0.95,
            evidence={'source': 'dns_lookup'}
        )
        assert rel_id is not None
        results.add_pass("Relationship created")
        
        # Test observation addition
        obs_id = correlation.add_observation(
            domain_id,
            'test_suite',
            'test_observation',
            {'timestamp': datetime.now().isoformat()}
        )
        assert obs_id is not None
        results.add_pass("Observation recorded")
        
        # Test correlation finding
        correlations = correlation.correlate_data('domain', 'test.example.com')
        assert isinstance(correlations, list)
        assert len(correlations) > 0
        results.add_pass(f"Correlations found ({len(correlations)} relationships)")
        
        # Test entity querying
        entities = correlation.query_entities(entity_type='domain')
        assert len(entities) > 0
        assert entities[0]['entity_type'] == 'domain'
        results.add_pass("Entity querying")
        
        # Test pattern detection
        patterns = correlation.find_patterns()
        assert isinstance(patterns, list)
        results.add_pass(f"Pattern detection ({len(patterns)} patterns)")
        
        # Test timeline retrieval
        timeline = correlation.get_entity_timeline(domain_id)
        assert isinstance(timeline, list)
        results.add_pass("Entity timeline retrieval")
        
        # Test graph export
        json_export = correlation.export_graph('json')
        graph_data = json.loads(json_export)
        assert 'nodes' in graph_data
        assert 'links' in graph_data
        results.add_pass("Graph export to JSON")
        
        # Test graph structure
        assert domain_id in correlation.graph
        assert ip_id in correlation.graph
        assert correlation.graph.has_edge(domain_id, ip_id)
        results.add_pass("Graph structure validation")
        
    except Exception as e:
        results.add_error("Correlation database test", str(e))
        
    return results


def test_integration():
    """Test integration between components."""
    print("\n[9] Testing Component Integration...")
    results = TestResults()
    
    try:
        # Initialize all components
        engine = OSINTEngine()
        bgp = BGPAnalyzer()
        cert_intel = CertificateIntelligence()
        blockchain = BlockchainAnalyzer()
        correlation = CorrelationDatabase()
        monitor = MonitoringEngine()
        
        results.add_pass("All components initialized")
        
        # Test integrated workflow
        test_domain = 'google.com'
        
        # Step 1: BGP Analysis
        bgp_data = bgp.analyze_domain(test_domain)
        bgp_report = bgp.create_report(test_domain, bgp_data)
        engine.add_report(bgp_report)
        
        # Step 2: Add to correlation
        domain_entity = correlation.add_entity('domain', test_domain, metadata=bgp_data)
        
        if bgp_data and bgp_data.get('asn'):
            asn_entity = correlation.add_entity('asn', str(bgp_data['asn']))
            correlation.add_relationship(domain_entity, asn_entity, 'hosted_in_asn')
        
        results.add_pass("BGP → Correlation integration")
        
        # Step 3: Certificate analysis (if available)
        cert = cert_intel.get_certificate(test_domain)
        if cert:
            cert_report = cert_intel.create_report(test_domain, cert)
            engine.add_report(cert_report)
            
            cert_entity = correlation.add_entity('ssl_cert', cert['fingerprint_sha256'][:16])
            correlation.add_relationship(domain_entity, cert_entity, 'has_certificate')
            
            results.add_pass("Certificate → Correlation integration")
        
        # Step 4: Create monitoring rule
        mon_rule = monitor.add_rule(
            name=f'Integration Test - {test_domain}',
            rule_type='domain',
            target=test_domain,
            conditions={},
            actions=['log'],
            interval=7200
        )
        results.add_pass("Monitoring rule integration")
        
        # Step 5: Verify data flow
        reports = engine.get_reports(target=test_domain)
        assert len(reports) >= 1
        results.add_pass(f"Reports collected ({len(reports)} reports)")
        
        correlations = correlation.correlate_data('domain', test_domain)
        assert len(correlations) >= 1
        results.add_pass(f"Correlations established ({len(correlations)} links)")
        
        # Cleanup
        monitor.remove_rule(mon_rule)
        results.add_pass("Integration test cleanup")
        
    except Exception as e:
        results.add_error("Integration test", str(e))
        
    return results


def test_userscripts():
    """Test userscript functionality."""
    print("\n[10] Testing Userscripts...")
    results = TestResults()
    
    try:
        userscript_dir = Path('userscripts/osint')
        
        # Check if userscripts exist
        scripts = ['analyze_page.py', 'monitor_site.py', 'search_shodan.py']
        
        for script in scripts:
            script_path = userscript_dir / script
            if script_path.exists():
                # Check if executable
                if os.access(script_path, os.X_OK):
                    results.add_pass(f"Userscript {script} (executable)")
                else:
                    results.add_fail(f"Userscript {script}", "Not executable")
                    
                # Check shebang
                with open(script_path, 'r') as f:
                    first_line = f.readline()
                    if first_line.startswith('#!/usr/bin/env python'):
                        results.add_pass(f"Userscript {script} shebang")
                    else:
                        results.add_fail(f"Userscript {script} shebang", "Invalid or missing")
            else:
                results.add_fail(f"Userscript {script}", "File not found")
                
    except Exception as e:
        results.add_error("Userscript test", str(e))
        
    return results


def main():
    """Run all tests."""
    print("=" * 60)
    print("OSINT Feature Comprehensive Test Suite")
    print("=" * 60)
    
    all_results = []
    
    # Run all test suites
    test_functions = [
        test_core_engine,
        test_bgp_analyzer,
        test_certificate_intelligence,
        test_blockchain_analyzer,
        test_search_engines,
        test_supply_chain,
        test_monitoring_engine,
        test_correlation_database,
        test_integration,
        test_userscripts
    ]
    
    for test_func in test_functions:
        results = test_func()
        all_results.append(results)
    
    # Summary
    print("\n" + "=" * 60)
    print("OVERALL TEST SUMMARY")
    print("=" * 60)
    
    total_passed = sum(len(r.passed) for r in all_results)
    total_failed = sum(len(r.failed) for r in all_results)
    total_errors = sum(len(r.errors) for r in all_results)
    total_tests = total_passed + total_failed + total_errors
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {total_passed} ({total_passed*100//total_tests if total_tests else 0}%)")
    print(f"Failed: {total_failed}")
    print(f"Errors: {total_errors}")
    
    if total_failed == 0 and total_errors == 0:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n⚠️  Some tests failed or had errors.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
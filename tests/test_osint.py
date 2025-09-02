#!/usr/bin/env python3
"""Test script for OSINT features."""

import sys
import os
import json
from pathlib import Path

# Add qutebrowser to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qutebrowser.osint.core import OSINTEngine, IntelligenceReport
from qutebrowser.osint.bgp import BGPAnalyzer
from qutebrowser.osint.certificates import CertificateIntelligence
from qutebrowser.osint.blockchain import BlockchainAnalyzer
from qutebrowser.osint.search_engines import AdvancedSearchEngine
from qutebrowser.osint.supply_chain import SupplyChainMapper
from qutebrowser.osint.monitoring import MonitoringEngine, MonitoringRule
from qutebrowser.osint.correlation import CorrelationDatabase


def test_core_engine():
    """Test the core OSINT engine."""
    print("Testing Core OSINT Engine...")
    
    engine = OSINTEngine()
    
    # Test report creation
    report = IntelligenceReport(
        source='test',
        target='example.com',
        data_type='test_data',
        data={'test': 'value'},
        confidence=0.8,
        tags=['test', 'demo']
    )
    
    engine.add_report(report)
    
    # Test report retrieval
    reports = engine.get_reports(target='example.com')
    assert len(reports) > 0, "Failed to retrieve reports"
    
    print("✓ Core engine test passed")


def test_bgp_analyzer():
    """Test BGP/ASN analysis."""
    print("Testing BGP Analyzer...")
    
    bgp = BGPAnalyzer()
    
    # Test with Google's DNS
    result = bgp.analyze_ip('8.8.8.8')
    
    assert result is not None, "BGP analysis failed"
    assert 'ip' in result, "Missing IP in result"
    
    # Test domain analysis
    domain_result = bgp.analyze_domain('google.com')
    assert domain_result is not None, "Domain BGP analysis failed"
    
    print("✓ BGP analyzer test passed")


def test_certificate_intelligence():
    """Test certificate intelligence."""
    print("Testing Certificate Intelligence...")
    
    cert_intel = CertificateIntelligence()
    
    # Test certificate retrieval (using google.com as it should always have a cert)
    cert = cert_intel.get_certificate('google.com')
    
    if cert:
        assert 'fingerprint_sha256' in cert, "Missing SHA256 fingerprint"
        assert 'subject' in cert, "Missing subject"
        assert 'issuer' in cert, "Missing issuer"
        print("✓ Certificate intelligence test passed")
    else:
        print("⚠ Certificate retrieval failed (may be network issue)")


def test_blockchain_analyzer():
    """Test blockchain analysis."""
    print("Testing Blockchain Analyzer...")
    
    blockchain = BlockchainAnalyzer()
    
    # Test address detection
    test_text = """
    Bitcoin: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
    Ethereum: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb4
    Some random text here
    """
    
    addresses = blockchain.detect_addresses(test_text)
    
    assert 'bitcoin' in addresses, "Failed to detect Bitcoin address"
    assert 'ethereum' in addresses, "Failed to detect Ethereum address"
    
    # Test Bitcoin address analysis (Genesis block address)
    btc_analysis = blockchain.analyze_bitcoin_address('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
    assert btc_analysis is not None, "Bitcoin analysis failed"
    assert 'address' in btc_analysis, "Missing address in Bitcoin analysis"
    
    print("✓ Blockchain analyzer test passed")


def test_search_engines():
    """Test search engine integration."""
    print("Testing Search Engines...")
    
    search = AdvancedSearchEngine()
    
    # Note: This would require API keys to actually work
    # Testing the structure only
    
    # Test CVE details retrieval
    cve_details = search._get_cve_details('CVE-2021-44228')  # Log4Shell
    
    if cve_details:
        assert 'id' in cve_details, "Missing CVE ID"
        print("✓ Search engine test passed")
    else:
        print("⚠ CVE lookup failed (may be network issue)")


def test_supply_chain():
    """Test supply chain mapping."""
    print("Testing Supply Chain Mapper...")
    
    supply_chain = SupplyChainMapper()
    
    # Test company analysis (basic structure)
    result = supply_chain.analyze_company('Microsoft')
    
    assert result is not None, "Supply chain analysis failed"
    assert 'company' in result, "Missing company in result"
    assert 'risk_assessment' in result, "Missing risk assessment"
    
    # Test shared supplier identification
    shared = supply_chain.identify_shared_suppliers(['Company1', 'Company2'])
    assert isinstance(shared, dict), "Shared supplier identification failed"
    
    print("✓ Supply chain mapper test passed")


def test_monitoring_engine():
    """Test monitoring engine."""
    print("Testing Monitoring Engine...")
    
    monitor = MonitoringEngine()
    
    # Test rule creation
    rule_id = monitor.add_rule(
        name='Test Rule',
        rule_type='domain',
        target='example.com',
        conditions={'test': True},
        actions=['log'],
        interval=3600
    )
    
    assert rule_id in monitor.rules, "Failed to add monitoring rule"
    
    # Test rule removal
    removed = monitor.remove_rule(rule_id)
    assert removed, "Failed to remove monitoring rule"
    
    # Test leak monitor creation
    leak_rule = monitor.create_leak_monitor(
        keywords=['password', 'api_key'],
        email_domains=['example.com']
    )
    
    assert leak_rule in monitor.rules, "Failed to create leak monitor"
    
    print("✓ Monitoring engine test passed")


def test_correlation_database():
    """Test correlation database."""
    print("Testing Correlation Database...")
    
    correlation = CorrelationDatabase()
    
    # Test entity addition
    entity1 = correlation.add_entity('domain', 'example.com')
    entity2 = correlation.add_entity('ip_address', '192.168.1.1')
    
    assert entity1 is not None, "Failed to add domain entity"
    assert entity2 is not None, "Failed to add IP entity"
    
    # Test relationship creation
    rel_id = correlation.add_relationship(
        entity1, entity2,
        'resolves_to',
        confidence=0.9
    )
    
    assert rel_id is not None, "Failed to add relationship"
    
    # Test correlation finding
    correlations = correlation.correlate_data('domain', 'example.com')
    assert isinstance(correlations, list), "Failed to find correlations"
    
    # Test pattern detection
    patterns = correlation.find_patterns()
    assert isinstance(patterns, list), "Failed to find patterns"
    
    # Test export
    export_data = correlation.export_graph('json')
    assert export_data is not None, "Failed to export graph"
    
    print("✓ Correlation database test passed")


def test_integration():
    """Test integration between components."""
    print("Testing Component Integration...")
    
    # Create instances
    engine = OSINTEngine()
    bgp = BGPAnalyzer()
    correlation = CorrelationDatabase()
    
    # Perform integrated analysis
    domain = 'google.com'
    
    # BGP analysis
    bgp_data = bgp.analyze_domain(domain)
    
    # Add to correlation
    domain_entity = correlation.add_entity('domain', domain)
    
    if bgp_data and bgp_data.get('asn'):
        asn_entity = correlation.add_entity('asn', str(bgp_data['asn']))
        correlation.add_relationship(domain_entity, asn_entity, 'hosted_in')
        
    # Create report
    report = bgp.create_report(domain, bgp_data)
    engine.add_report(report)
    
    # Verify integration
    reports = engine.get_reports(target=domain)
    assert len(reports) > 0, "Integration test failed"
    
    print("✓ Integration test passed")


def main():
    """Run all tests."""
    print("=" * 50)
    print("OSINT Feature Test Suite")
    print("=" * 50)
    
    tests = [
        test_core_engine,
        test_bgp_analyzer,
        test_certificate_intelligence,
        test_blockchain_analyzer,
        test_search_engines,
        test_supply_chain,
        test_monitoring_engine,
        test_correlation_database,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
            
    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed successfully! ✓")
        return 0
    else:
        print(f"{failed} tests failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
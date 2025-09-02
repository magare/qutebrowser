"""OSINT commands for qutebrowser."""

import json
from typing import Optional
from urllib.parse import urlparse

from qutebrowser.api import cmdutils
from qutebrowser.utils import message, objreg

from qutebrowser.osint.core import OSINTEngine
from qutebrowser.osint.bgp import BGPAnalyzer
from qutebrowser.osint.certificates import CertificateIntelligence
from qutebrowser.osint.blockchain import BlockchainAnalyzer
from qutebrowser.osint.search_engines import AdvancedSearchEngine
from qutebrowser.osint.supply_chain import SupplyChainMapper
from qutebrowser.osint.monitoring import MonitoringEngine
from qutebrowser.osint.correlation import CorrelationDatabase


# Initialize OSINT components as singletons
_osint_engine = None
_bgp_analyzer = None
_cert_intel = None
_blockchain_analyzer = None
_search_engine = None
_supply_chain = None
_monitor = None
_correlation_db = None


def _get_osint_engine():
    """Get or create OSINT engine instance."""
    global _osint_engine
    if _osint_engine is None:
        _osint_engine = OSINTEngine()
    return _osint_engine


def _get_bgp_analyzer():
    """Get or create BGP analyzer instance."""
    global _bgp_analyzer
    if _bgp_analyzer is None:
        _bgp_analyzer = BGPAnalyzer()
    return _bgp_analyzer


def _get_cert_intel():
    """Get or create certificate intelligence instance."""
    global _cert_intel
    if _cert_intel is None:
        _cert_intel = CertificateIntelligence()
    return _cert_intel


def _get_blockchain_analyzer():
    """Get or create blockchain analyzer instance."""
    global _blockchain_analyzer
    if _blockchain_analyzer is None:
        _blockchain_analyzer = BlockchainAnalyzer()
    return _blockchain_analyzer


def _get_search_engine():
    """Get or create search engine instance."""
    global _search_engine
    if _search_engine is None:
        _search_engine = AdvancedSearchEngine()
    return _search_engine


def _get_supply_chain():
    """Get or create supply chain mapper instance."""
    global _supply_chain
    if _supply_chain is None:
        _supply_chain = SupplyChainMapper()
    return _supply_chain


def _get_monitor():
    """Get or create monitoring engine instance."""
    global _monitor
    if _monitor is None:
        _monitor = MonitoringEngine()
    return _monitor


def _get_correlation_db():
    """Get or create correlation database instance."""
    global _correlation_db
    if _correlation_db is None:
        _correlation_db = CorrelationDatabase()
    return _correlation_db


@cmdutils.register()
def osint_analyze():
    """Perform comprehensive OSINT analysis on the current page.
    
    Args:
        tab: The current tab.
    """
    url = tab.url()
    domain = url.host()
    
    if not domain:
        message.error("No domain to analyze")
        return
        
    message.info(f"Starting OSINT analysis for {domain}...")
    
    engine = _get_osint_engine()
    result = engine.analyze_url(url)
    
    # Perform various analyses
    bgp = _get_bgp_analyzer()
    bgp_data = bgp.analyze_domain(domain)
    result['analyses']['bgp'] = bgp_data
    
    cert = _get_cert_intel()
    cert_data = cert.get_certificate(domain)
    if cert_data:
        result['analyses']['certificate'] = cert_data
        
    # Store in correlation database
    correlation = _get_correlation_db()
    domain_entity = correlation.add_entity('domain', domain)
    
    if bgp_data.get('asn'):
        asn_entity = correlation.add_entity('asn', str(bgp_data['asn']))
        correlation.add_relationship(domain_entity, asn_entity, 'hosted_in_asn')
        
    message.info(f"OSINT analysis complete for {domain}")


@cmdutils.register()
def osint_bgp():
    """Analyze BGP and ASN information for the current domain.
    
    Args:
        tab: The current tab.
    """
    domain = tab.url().host()
    
    if not domain:
        message.error("No domain to analyze")
        return
        
    bgp = _get_bgp_analyzer()
    result = bgp.analyze_domain(domain)
    
    if result:
        info = []
        if result.get('asn'):
            info.append(f"ASN: {result['asn']}")
        if result.get('asn_name'):
            info.append(f"Name: {result['asn_name']}")
        if result.get('country'):
            info.append(f"Country: {result['country']}")
        if result.get('prefix'):
            info.append(f"Prefix: {result['prefix']}")
            
        message.info(f"BGP Info for {domain}: " + " | ".join(info))
    else:
        message.warning(f"No BGP information found for {domain}")


@cmdutils.register()
def osint_certificate():
    """Analyze SSL certificate for the current domain.
    
    Args:
        tab: The current tab.
    """
    domain = tab.url().host()
    
    if not domain:
        message.error("No domain to analyze")
        return
        
    cert_intel = _get_cert_intel()
    cert_data = cert_intel.get_certificate(domain)
    
    if cert_data:
        info = []
        info.append(f"Issuer: {cert_data.get('issuer', {}).get('organizationName', 'Unknown')}")
        info.append(f"Valid until: {cert_data.get('not_after', 'Unknown')}")
        info.append(f"SHA256: {cert_data.get('fingerprint_sha256', '')[:16]}...")
        
        san_count = len(cert_data.get('san', []))
        if san_count > 0:
            info.append(f"SANs: {san_count} domains")
            
        message.info(f"Certificate for {domain}: " + " | ".join(info))
        
        # Search CT logs
        ct_results = cert_intel.search_certificate_transparency(domain)
        if ct_results:
            message.info(f"Found {len(ct_results)} certificates in CT logs")
    else:
        message.warning(f"Could not retrieve certificate for {domain}")


@cmdutils.register()
def osint_shodan(query: str):
    """Search Shodan for the given query.
    
    Args:
        query: The Shodan search query.
    """
    search = _get_search_engine()
    message.info(f"Searching Shodan for: {query}")
    
    results = search.search_shodan(query)
    
    if 'error' in results:
        message.error(f"Shodan search failed: {results['error']}")
    else:
        total = results.get('total', 0)
        message.info(f"Shodan found {total} results for '{query}'")
        
        # Show top vulnerabilities if found
        if 'statistics' in results:
            vulns = results['statistics'].get('vulnerabilities', [])
            if vulns:
                top_vulns = ', '.join(vulns[:5])
                message.warning(f"Top vulnerabilities: {top_vulns}")


@cmdutils.register()
def osint_blockchain(address: str):
    """Analyze a cryptocurrency address.
    
    Args:
        address: The cryptocurrency address to analyze.
    """
    blockchain = _get_blockchain_analyzer()
    
    # Detect address type
    if address.startswith(('1', '3', 'bc1')):
        message.info(f"Analyzing Bitcoin address: {address}")
        result = blockchain.analyze_bitcoin_address(address)
    elif address.startswith('0x'):
        message.info(f"Analyzing Ethereum address: {address}")
        result = blockchain.analyze_ethereum_address(address)
    else:
        message.error("Unknown cryptocurrency address format")
        return
        
    if result:
        info = []
        if 'balance' in result:
            info.append(f"Balance: {result['balance']:.8f}")
        if 'transaction_count' in result:
            info.append(f"Transactions: {result['transaction_count']}")
        if 'balance_eth' in result:
            info.append(f"ETH Balance: {result['balance_eth']:.4f}")
            
        message.info(f"Blockchain analysis: " + " | ".join(info))
        
        # Add to correlation database
        correlation = _get_correlation_db()
        correlation.add_entity('crypto_address', address, metadata=result)


@cmdutils.register()
def osint_supply_chain(company: str):
    """Analyze supply chain for a company.
    
    Args:
        company: The company name to analyze.
    """
    supply_chain = _get_supply_chain()
    message.info(f"Analyzing supply chain for: {company}")
    
    result = supply_chain.analyze_company(company)
    
    if result:
        vendor_count = len(result.get('vendors', []))
        customer_count = len(result.get('customers', []))
        tech_count = len(result.get('technologies', []))
        
        message.info(f"Supply chain analysis for {company}:")
        message.info(f"  Vendors: {vendor_count}")
        message.info(f"  Customers: {customer_count}")
        message.info(f"  Technologies: {tech_count}")
        
        risk = result.get('risk_assessment', {})
        if risk.get('overall_risk') in ['high', 'critical']:
            message.warning(f"  Risk Level: {risk['overall_risk'].upper()}")


@cmdutils.register()
def osint_monitor_start():
    """Start monitoring the current domain for changes.
    
    Args:
        tab: The current tab.
    """
    domain = tab.url().host()
    
    if not domain:
        message.error("No domain to monitor")
        return
        
    monitor = _get_monitor()
    
    # Create monitoring rules
    rules = []
    
    # Certificate monitoring
    cert_rule = monitor.add_rule(
        name=f"Cert Monitor - {domain}",
        rule_type='cert',
        target=domain,
        conditions={},
        actions=['notify', 'log'],
        interval=86400  # Daily
    )
    rules.append(cert_rule)
    
    # DNS monitoring
    dns_rule = monitor.add_rule(
        name=f"DNS Monitor - {domain}",
        rule_type='domain',
        target=domain,
        conditions={},
        actions=['notify', 'log'],
        interval=3600  # Hourly
    )
    rules.append(dns_rule)
    
    # Start monitoring
    monitor.start_monitoring()
    
    message.info(f"Monitoring started for {domain} ({len(rules)} rules created)")


@cmdutils.register()
def osint_monitor_stop():
    """Stop all OSINT monitoring."""
    monitor = _get_monitor()
    monitor.stop_monitoring()
    message.info("OSINT monitoring stopped")


@cmdutils.register()
def osint_monitor_status():
    """Show OSINT monitoring status."""
    monitor = _get_monitor()
    
    if monitor.monitoring_active:
        rule_count = len(monitor.rules)
        enabled_count = sum(1 for r in monitor.rules.values() if r.enabled)
        message.info(f"Monitoring active: {enabled_count}/{rule_count} rules enabled")
        
        # Show recent alerts
        alerts = monitor.get_alerts(days=1)
        if alerts:
            message.warning(f"Recent alerts: {len(alerts)} in last 24 hours")
    else:
        message.info("Monitoring is not active")


@cmdutils.register()
@cmdutils.argument('entity_type', choices=['domain', 'ip', 'email', 'crypto_address', 'asn', 'ssl_cert'])
def osint_correlate(entity_type: str, entity_value: str):
    """Find correlations for an entity.
    
    Args:
        entity_type: The type of entity.
        entity_value: The entity value to correlate.
    """
    correlation = _get_correlation_db()
    
    # Add entity to database
    entity_id = correlation.add_entity(entity_type, entity_value)
    
    # Find correlations
    correlations = correlation.correlate_data(entity_type, entity_value)
    
    if correlations:
        message.info(f"Found {len(correlations)} correlations for {entity_value}")
        
        # Show top correlations
        for corr in correlations[:3]:
            rel_type = corr['relationship_type']
            confidence = corr['confidence']
            
            if 'entity' in corr:
                related = corr['entity']['value']
                message.info(f"  → {related} ({rel_type}, confidence: {confidence:.2f})")
    else:
        message.info(f"No correlations found for {entity_value}")


@cmdutils.register()
@cmdutils.argument('format', choices=['json', 'gexf', 'graphml'])
def osint_export(format: str, filepath: str):
    """Export OSINT correlation graph.
    
    Args:
        format: Export format (json, gexf, graphml).
        filepath: Path to save the export file.
    """
    correlation = _get_correlation_db()
    
    if format == 'json':
        data = correlation.export_graph('json')
        with open(filepath, 'w') as f:
            f.write(data)
    else:
        export_path = correlation.export_graph(format)
        import shutil
        shutil.move(export_path, filepath)
        
    message.info(f"OSINT data exported to {filepath}")


@cmdutils.register()
def osint_clear_cache():
    """Clear OSINT cache and temporary data."""
    engine = _get_osint_engine()
    engine.clear_cache()
    
    message.info("OSINT cache cleared")


@cmdutils.register()
def osint_leak_monitor(keywords: str):
    """Monitor paste sites for data leaks.
    
    Args:
        keywords: Comma-separated keywords to monitor.
    """
    monitor = _get_monitor()
    
    keyword_list = [k.strip() for k in keywords.split(',')]
    
    rule_id = monitor.create_leak_monitor(keyword_list)
    monitor.start_monitoring()
    
    message.info(f"Leak monitoring started for keywords: {', '.join(keyword_list)}")


@cmdutils.register()
def osint_detect_crypto():
    """Detect cryptocurrency addresses on the current page.
    
    Args:
        tab: The current tab.
    """
    # This would need integration with tab content
    # For now, show a message
    message.info("Cryptocurrency detection requires page content access via userscript")
    message.info("Use: :spawn --userscript osint/analyze_page.py")
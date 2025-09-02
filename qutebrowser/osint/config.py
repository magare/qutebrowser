"""Configuration options for OSINT features."""

from qutebrowser.config import configtypes, configdata
from qutebrowser.utils import standarddir


# Add OSINT configuration options to qutebrowser's config system
def register_osint_options():
    """Register OSINT configuration options."""
    
    # OSINT General Settings
    configdata.DATA['osint.enabled'] = configdata.Option(
        name='osint.enabled',
        typ=configtypes.Bool(),
        default=True,
        desc="Enable OSINT features in qutebrowser."
    )
    
    configdata.DATA['osint.auto_analyze'] = configdata.Option(
        name='osint.auto_analyze',
        typ=configtypes.Bool(),
        default=False,
        desc="Automatically perform OSINT analysis on visited sites."
    )
    
    configdata.DATA['osint.monitoring.enabled'] = configdata.Option(
        name='osint.monitoring.enabled',
        typ=configtypes.Bool(),
        default=False,
        desc="Enable automated OSINT monitoring."
    )
    
    configdata.DATA['osint.monitoring.interval'] = configdata.Option(
        name='osint.monitoring.interval',
        typ=configtypes.Int(minval=60),
        default=300,
        desc="Default monitoring check interval in seconds."
    )
    
    # API Keys
    configdata.DATA['osint.api.shodan_key'] = configdata.Option(
        name='osint.api.shodan_key',
        typ=configtypes.String(),
        default='',
        desc="Shodan API key for infrastructure searches."
    )
    
    configdata.DATA['osint.api.censys_id'] = configdata.Option(
        name='osint.api.censys_id',
        typ=configtypes.String(),
        default='',
        desc="Censys API ID for asset searches."
    )
    
    configdata.DATA['osint.api.censys_secret'] = configdata.Option(
        name='osint.api.censys_secret',
        typ=configtypes.String(),
        default='',
        desc="Censys API secret for asset searches."
    )
    
    # BGP/ASN Settings
    configdata.DATA['osint.bgp.enabled'] = configdata.Option(
        name='osint.bgp.enabled',
        typ=configtypes.Bool(),
        default=True,
        desc="Enable BGP/ASN analysis features."
    )
    
    configdata.DATA['osint.bgp.check_hijacking'] = configdata.Option(
        name='osint.bgp.check_hijacking',
        typ=configtypes.Bool(),
        default=False,
        desc="Check for potential BGP hijacking."
    )
    
    # Certificate Settings
    configdata.DATA['osint.certificates.enabled'] = configdata.Option(
        name='osint.certificates.enabled',
        typ=configtypes.Bool(),
        default=True,
        desc="Enable certificate intelligence features."
    )
    
    configdata.DATA['osint.certificates.ct_monitoring'] = configdata.Option(
        name='osint.certificates.ct_monitoring',
        typ=configtypes.Bool(),
        default=True,
        desc="Monitor Certificate Transparency logs."
    )
    
    configdata.DATA['osint.certificates.verify'] = configdata.Option(
        name='osint.certificates.verify',
        typ=configtypes.Bool(),
        default=False,
        desc="Verify certificate chains (may slow down analysis)."
    )
    
    # Blockchain Settings
    configdata.DATA['osint.blockchain.enabled'] = configdata.Option(
        name='osint.blockchain.enabled',
        typ=configtypes.Bool(),
        default=True,
        desc="Enable blockchain analysis features."
    )
    
    configdata.DATA['osint.blockchain.auto_detect'] = configdata.Option(
        name='osint.blockchain.auto_detect',
        typ=configtypes.Bool(),
        default=True,
        desc="Automatically detect cryptocurrency addresses on pages."
    )
    
    configdata.DATA['osint.blockchain.cluster_analysis'] = configdata.Option(
        name='osint.blockchain.cluster_analysis',
        typ=configtypes.Bool(),
        default=False,
        desc="Perform address clustering analysis."
    )
    
    # Supply Chain Settings
    configdata.DATA['osint.supply_chain.enabled'] = configdata.Option(
        name='osint.supply_chain.enabled',
        typ=configtypes.Bool(),
        default=True,
        desc="Enable supply chain mapping features."
    )
    
    configdata.DATA['osint.supply_chain.max_depth'] = configdata.Option(
        name='osint.supply_chain.max_depth',
        typ=configtypes.Int(minval=1, maxval=10),
        default=3,
        desc="Maximum depth for supply chain mapping."
    )
    
    # Search Engine Settings
    configdata.DATA['osint.search.max_results'] = configdata.Option(
        name='osint.search.max_results',
        typ=configtypes.Int(minval=10, maxval=1000),
        default=100,
        desc="Maximum number of search results to retrieve."
    )
    
    configdata.DATA['osint.search.check_vulns'] = configdata.Option(
        name='osint.search.check_vulns',
        typ=configtypes.Bool(),
        default=True,
        desc="Check for vulnerabilities in search results."
    )
    
    # Data Leak Monitoring
    configdata.DATA['osint.leaks.monitor_pastes'] = configdata.Option(
        name='osint.leaks.monitor_pastes',
        typ=configtypes.Bool(),
        default=False,
        desc="Monitor paste sites for data leaks."
    )
    
    configdata.DATA['osint.leaks.keywords'] = configdata.Option(
        name='osint.leaks.keywords',
        typ=configtypes.List(),
        default=[],
        desc="Keywords to monitor in data leak searches."
    )
    
    # Correlation Settings
    configdata.DATA['osint.correlation.enabled'] = configdata.Option(
        name='osint.correlation.enabled',
        typ=configtypes.Bool(),
        default=True,
        desc="Enable data correlation engine."
    )
    
    configdata.DATA['osint.correlation.auto_correlate'] = configdata.Option(
        name='osint.correlation.auto_correlate',
        typ=configtypes.Bool(),
        default=True,
        desc="Automatically correlate discovered entities."
    )
    
    configdata.DATA['osint.correlation.max_hops'] = configdata.Option(
        name='osint.correlation.max_hops',
        typ=configtypes.Int(minval=1, maxval=5),
        default=2,
        desc="Maximum hops for correlation graph traversal."
    )
    
    # Privacy Settings
    configdata.DATA['osint.privacy.store_data'] = configdata.Option(
        name='osint.privacy.store_data',
        typ=configtypes.Bool(),
        default=True,
        desc="Store OSINT data locally for correlation."
    )
    
    configdata.DATA['osint.privacy.clear_on_exit'] = configdata.Option(
        name='osint.privacy.clear_on_exit',
        typ=configtypes.Bool(),
        default=False,
        desc="Clear OSINT data when qutebrowser exits."
    )
    
    # Notification Settings
    configdata.DATA['osint.notifications.enabled'] = configdata.Option(
        name='osint.notifications.enabled',
        typ=configtypes.Bool(),
        default=True,
        desc="Show notifications for OSINT alerts."
    )
    
    configdata.DATA['osint.notifications.critical_only'] = configdata.Option(
        name='osint.notifications.critical_only',
        typ=configtypes.Bool(),
        default=False,
        desc="Only show notifications for critical alerts."
    )
    
    # Export Settings
    configdata.DATA['osint.export.format'] = configdata.Option(
        name='osint.export.format',
        typ=configtypes.SelectOne(
            valid_values=configtypes.ValidValues('json', 'csv', 'html')
        ),
        default='json',
        desc="Default export format for OSINT data."
    )
    
    configdata.DATA['osint.export.include_metadata'] = configdata.Option(
        name='osint.export.include_metadata',
        typ=configtypes.Bool(),
        default=True,
        desc="Include metadata in exports."
    )


# Configuration helper functions
def get_osint_config(option: str):
    """Get an OSINT configuration value.
    
    Args:
        option: The configuration option name.
        
    Returns:
        The configuration value.
    """
    from qutebrowser.config import config
    
    try:
        return config.val.get(option)
    except:
        # Return default if option doesn't exist
        if option in configdata.DATA:
            return configdata.DATA[option].default
        return None


def is_osint_enabled() -> bool:
    """Check if OSINT features are enabled.
    
    Returns:
        True if OSINT is enabled, False otherwise.
    """
    return get_osint_config('osint.enabled') or True


def get_api_key(service: str) -> str:
    """Get API key for a service.
    
    Args:
        service: The service name ('shodan', 'censys_id', 'censys_secret').
        
    Returns:
        The API key or empty string if not configured.
    """
    return get_osint_config(f'osint.api.{service}') or ''


def should_auto_analyze() -> bool:
    """Check if auto-analysis is enabled.
    
    Returns:
        True if auto-analysis is enabled, False otherwise.
    """
    return get_osint_config('osint.auto_analyze') or False


def get_monitoring_interval() -> int:
    """Get the monitoring check interval.
    
    Returns:
        Interval in seconds.
    """
    return get_osint_config('osint.monitoring.interval') or 300


def should_store_data() -> bool:
    """Check if OSINT data should be stored.
    
    Returns:
        True if data should be stored, False otherwise.
    """
    return get_osint_config('osint.privacy.store_data') or True


def should_clear_on_exit() -> bool:
    """Check if OSINT data should be cleared on exit.
    
    Returns:
        True if data should be cleared, False otherwise.
    """
    return get_osint_config('osint.privacy.clear_on_exit') or False


# Default configuration template for config.py
CONFIG_TEMPLATE = """
# OSINT Configuration for qutebrowser

# Enable OSINT features
c.osint.enabled = True

# API Keys (obtain from respective services)
# c.osint.api.shodan_key = 'YOUR_SHODAN_API_KEY'
# c.osint.api.censys_id = 'YOUR_CENSYS_API_ID'
# c.osint.api.censys_secret = 'YOUR_CENSYS_API_SECRET'

# Auto-analysis settings
c.osint.auto_analyze = False  # Automatically analyze visited sites
c.osint.monitoring.enabled = False  # Enable automated monitoring
c.osint.monitoring.interval = 300  # Check interval in seconds

# Feature toggles
c.osint.bgp.enabled = True
c.osint.certificates.enabled = True
c.osint.blockchain.enabled = True
c.osint.supply_chain.enabled = True
c.osint.correlation.enabled = True

# Advanced settings
c.osint.bgp.check_hijacking = False
c.osint.certificates.ct_monitoring = True
c.osint.blockchain.auto_detect = True
c.osint.blockchain.cluster_analysis = False
c.osint.supply_chain.max_depth = 3
c.osint.search.max_results = 100
c.osint.correlation.max_hops = 2

# Privacy settings
c.osint.privacy.store_data = True
c.osint.privacy.clear_on_exit = False

# Notification settings
c.osint.notifications.enabled = True
c.osint.notifications.critical_only = False

# Data leak monitoring
c.osint.leaks.monitor_pastes = False
c.osint.leaks.keywords = []  # Add your keywords to monitor

# Export settings
c.osint.export.format = 'json'
c.osint.export.include_metadata = True
"""


def generate_config_template() -> str:
    """Generate a configuration template for OSINT settings.
    
    Returns:
        Configuration template string.
    """
    return CONFIG_TEMPLATE


def validate_config():
    """Validate OSINT configuration settings."""
    errors = []
    
    # Check API keys if features are enabled
    if get_osint_config('osint.search.enabled'):
        if not get_api_key('shodan_key'):
            errors.append("Shodan API key not configured (osint.api.shodan_key)")
            
    # Check monitoring settings
    if get_osint_config('osint.monitoring.enabled'):
        interval = get_monitoring_interval()
        if interval < 60:
            errors.append("Monitoring interval too short (minimum 60 seconds)")
            
    # Check supply chain depth
    depth = get_osint_config('osint.supply_chain.max_depth')
    if depth and depth > 5:
        errors.append("Supply chain depth too large (maximum 5)")
        
    return errors
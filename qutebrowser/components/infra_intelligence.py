# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Infrastructure intelligence commands for qutebrowser."""

import json
import socket
import ssl
import urllib.parse
from typing import Optional, Dict, Any
from qutebrowser.qt.core import QUrl
from qutebrowser.qt.network import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from qutebrowser.api import cmdutils, apitypes
from qutebrowser.utils import objreg, log, qtutils


logger = log.commands.debug

# Global network manager for API requests
_network_manager: Optional[QNetworkAccessManager] = None
_pending_requests: Dict[QNetworkReply, Dict[str, Any]] = {}


def _get_network_manager() -> QNetworkAccessManager:
    """Get or create the global network manager."""
    global _network_manager
    if _network_manager is None:
        _network_manager = QNetworkAccessManager()
        _network_manager.finished.connect(_on_network_reply)
    return _network_manager


def _get_tabbed_browser(tab: apitypes.Tab):
    """Get the TabbedBrowser for the given tab."""
    return tab._widget.parent()  # Get the tabbed browser from the tab


def _get_current_url(tab: apitypes.Tab) -> QUrl:
    """Get the current URL from the tab."""
    try:
        url = tab.url()
        if url.isEmpty():
            # Try requested URL if current URL is empty
            url = tab.url(requested=True)
        return url
    except Exception as e:
        raise cmdutils.CommandError(f"Current URL is invalid: {e}")


def _resolve_domain_to_ip(domain: str) -> Optional[str]:
    """Resolve a domain name to its IP address.
    
    Args:
        domain: The domain name to resolve.
        
    Returns:
        The IP address or None if resolution fails.
    """
    try:
        return socket.gethostbyname(domain)
    except (socket.gaierror, socket.error) as e:
        logger(f"Failed to resolve {domain}: {e}")
        return None


def _make_api_request(url: str, callback: callable, error_callback: callable = None):
    """Make an asynchronous API request.
    
    Args:
        url: The URL to request.
        callback: Function to call with the response data.
        error_callback: Optional function to call on error.
    """
    request = QNetworkRequest(QUrl(url))
    request.setRawHeader(b"User-Agent", b"qutebrowser/infra-intelligence")
    
    manager = _get_network_manager()
    reply = manager.get(request)
    _pending_requests[reply] = {
        'callback': callback,
        'error_callback': error_callback
    }


def _on_network_reply(reply: QNetworkReply):
    """Handle network reply completion."""
    if reply not in _pending_requests:
        return
        
    callbacks = _pending_requests.pop(reply)
    
    if reply.error() != QNetworkReply.NetworkError.NoError:
        error_msg = reply.errorString()
        if callbacks.get('error_callback'):
            callbacks['error_callback'](error_msg)
        else:
            from qutebrowser.utils import message
            message.error(f"Network request failed: {error_msg}")
    else:
        data = bytes(reply.readAll()).decode('utf-8')
        try:
            json_data = json.loads(data) if data else {}
            callbacks['callback'](json_data)
        except json.JSONDecodeError as e:
            from qutebrowser.utils import message
            message.error(f"Failed to parse response: {e}")
    
    reply.deleteLater()


def _display_in_buffer(tab: apitypes.Tab, title: str, content: str):
    """Display content in a new qutebrowser buffer.
    
    Args:
        tab: The current tab.
        title: The title for the buffer.
        content: HTML content to display.
    """
    tabbed_browser = _get_tabbed_browser(tab)
    
    # Create HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                font-family: monospace;
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 20px;
                line-height: 1.6;
            }}
            h1 {{
                color: #569cd6;
                border-bottom: 2px solid #569cd6;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #4ec9b0;
                margin-top: 20px;
            }}
            .info-block {{
                background: #2d2d2d;
                border-left: 3px solid #569cd6;
                padding: 15px;
                margin: 15px 0;
                border-radius: 3px;
            }}
            .label {{
                color: #9cdcfe;
                font-weight: bold;
            }}
            .value {{
                color: #ce9178;
            }}
            a {{
                color: #4fc1ff;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .error {{
                color: #f48771;
                background: #3a1515;
                padding: 10px;
                border-radius: 3px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th {{
                background: #2d2d2d;
                color: #569cd6;
                padding: 10px;
                text-align: left;
                border-bottom: 2px solid #569cd6;
            }}
            td {{
                padding: 8px;
                border-bottom: 1px solid #3e3e3e;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {content}
    </body>
    </html>
    """
    
    # Open in new tab
    data_url = QUrl(f"data:text/html;charset=utf-8,{urllib.parse.quote(html)}")
    tabbed_browser.load_url(data_url, newtab=True)


@cmdutils.register(name='asn-info')
@cmdutils.argument('tab', value=cmdutils.Value.cur_tab)
def asn_info(tab: apitypes.Tab):
    """Display BGP/ASN information for the current domain.
    
    Retrieves and displays:
    - IP address of the current domain
    - Autonomous System Number (ASN)
    - ASN owner organization
    - BGP prefix
    - Country information
    - Links to detailed BGP analysis tools
    """
    url = _get_current_url(tab)
    domain = url.host()
    
    if not domain:
        # Debug: Show what URL we actually got
        url_str = url.toString() if not url.isEmpty() else "empty"
        raise cmdutils.CommandError(f"No valid domain in current URL (got: {url_str})")
    
    from qutebrowser.utils import message
    message.info(f"Fetching ASN information for {domain}...")
    
    # Resolve domain to IP
    ip_address = _resolve_domain_to_ip(domain)
    if not ip_address:
        _display_asn_error(tab, domain, "Failed to resolve domain to IP address")
        return
    
    # Query BGP information using RIPEstat API
    api_url = f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip_address}"
    
    def handle_response(data):
        _display_asn_info(tab, domain, ip_address, data)
    
    def handle_error(error):
        _display_asn_error(tab, domain, error)
    
    _make_api_request(api_url, handle_response, handle_error)


def _display_asn_info(tab: apitypes.Tab, domain: str, ip_address: str, data: dict):
    """Display ASN information in a buffer."""
    content = f"""
    <div class="info-block">
        <p><span class="label">Domain:</span> <span class="value">{domain}</span></p>
        <p><span class="label">IP Address:</span> <span class="value">{ip_address}</span></p>
    </div>
    """
    
    if 'data' in data and 'asns' in data['data'] and data['data']['asns']:
        asn_info = data['data']['asns'][0]
        asn = asn_info.get('asn', 'Unknown')
        holder = asn_info.get('holder', 'Unknown')
        
        prefix = 'Unknown'
        country = 'Unknown'
        if 'resource' in data['data']:
            prefix = data['data']['resource']
        if 'countries' in data['data'] and data['data']['countries']:
            country = data['data']['countries'][0].get('country', 'Unknown')
        
        content += f"""
        <h2>ASN Information</h2>
        <div class="info-block">
            <p><span class="label">ASN:</span> <span class="value">AS{asn}</span></p>
            <p><span class="label">ASN Owner:</span> <span class="value">{holder}</span></p>
            <p><span class="label">BGP Prefix:</span> <span class="value">{prefix}</span></p>
            <p><span class="label">Country:</span> <span class="value">{country}</span></p>
        </div>
        
        <h2>External Analysis Tools</h2>
        <div class="info-block">
            <p>• <a href="https://bgp.he.net/AS{asn}" target="_blank">Hurricane Electric BGP Toolkit</a></p>
            <p>• <a href="https://stat.ripe.net/AS{asn}" target="_blank">RIPEstat Analysis</a></p>
            <p>• <a href="https://bgpview.io/asn/{asn}" target="_blank">BGPView</a></p>
            <p>• <a href="https://www.peeringdb.com/asn/{asn}" target="_blank">PeeringDB</a></p>
        </div>
        """
    else:
        content += """
        <div class="error">
            <p>No ASN information available for this IP address</p>
        </div>
        """
    
    _display_in_buffer(tab, f"ASN Info: {domain}", content)


def _display_asn_error(tab: apitypes.Tab, domain: str, error: str):
    """Display ASN error information."""
    content = f"""
    <div class="error">
        <p>Failed to retrieve ASN information for {domain}</p>
        <p>Error: {error}</p>
    </div>
    """
    _display_in_buffer(tab, f"ASN Info Error: {domain}", content)


@cmdutils.register(name='cable-route')
@cmdutils.argument('tab', value=cmdutils.Value.cur_tab)
def cable_route(tab: apitypes.Tab):
    """Display submarine cable correlation for the current domain.
    
    Identifies potential physical data paths by:
    - Geolocating the server
    - Finding nearest submarine cable landing stations
    - Listing connected cable systems
    - Providing links to cable route maps
    """
    url = _get_current_url(tab)
    domain = url.host()
    
    if not domain:
        # Debug: Show what URL we actually got
        url_str = url.toString() if not url.isEmpty() else "empty"
        raise cmdutils.CommandError(f"No valid domain in current URL (got: {url_str})")
    
    from qutebrowser.utils import message
    message.info(f"Fetching cable route information for {domain}...")
    
    # Resolve domain to IP
    ip_address = _resolve_domain_to_ip(domain)
    if not ip_address:
        _display_cable_error(tab, domain, "Failed to resolve domain to IP address")
        return
    
    # Query geolocation using ip-api.com (free tier)
    api_url = f"http://ip-api.com/json/{ip_address}"
    
    def handle_response(data):
        _display_cable_info(tab, domain, ip_address, data)
    
    def handle_error(error):
        _display_cable_error(tab, domain, error)
    
    _make_api_request(api_url, handle_response, handle_error)


def _display_cable_info(tab: apitypes.Tab, domain: str, ip_address: str, geo_data: dict):
    """Display submarine cable information."""
    city = geo_data.get('city', 'Unknown')
    country = geo_data.get('country', 'Unknown')
    lat = geo_data.get('lat', 0)
    lon = geo_data.get('lon', 0)
    
    content = f"""
    <div class="info-block">
        <p><span class="label">Domain:</span> <span class="value">{domain}</span></p>
        <p><span class="label">IP Address:</span> <span class="value">{ip_address}</span></p>
    </div>
    
    <h2>Server Geolocation</h2>
    <div class="info-block">
        <p><span class="label">City:</span> <span class="value">{city}</span></p>
        <p><span class="label">Country:</span> <span class="value">{country}</span></p>
        <p><span class="label">Coordinates:</span> <span class="value">{lat}, {lon}</span></p>
    </div>
    
    <h2>Submarine Cable Resources</h2>
    <div class="info-block">
        <p>Based on the server location in {city}, {country}, explore potential cable routes:</p>
        <p>• <a href="https://www.submarinecablemap.com/" target="_blank">TeleGeography Submarine Cable Map</a></p>
        <p>• <a href="https://www.infrapedia.com/app" target="_blank">Infrapedia Infrastructure Map</a></p>
        <p>• <a href="https://globe.gl/submarine-cables/" target="_blank">Interactive 3D Cable Globe</a></p>
        <p>• <a href="https://www.submarinenetworks.com/en/systems" target="_blank">Submarine Networks Cable Database</a></p>
    </div>
    
    <h2>Regional Cable Systems</h2>
    <div class="info-block">
        <p>Common cable systems for {country} region:</p>
        {_get_regional_cables(country)}
    </div>
    """
    
    _display_in_buffer(tab, f"Cable Route: {domain}", content)


def _get_regional_cables(country: str) -> str:
    """Get common submarine cables for a region."""
    # This is a simplified mapping - in production, this would query a proper database
    regional_cables = {
        "United States": ["MAREA", "Grace Hopper", "Dunant", "JUPITER", "PLCN"],
        "United Kingdom": ["TAT-14", "Celtic", "Yellow", "England Cable One"],
        "Japan": ["JUPITER", "FASTER", "PLCN", "JUS", "NCP"],
        "Singapore": ["SEA-ME-WE 3", "SEA-ME-WE 4", "SEA-ME-WE 5", "APG", "APCN2"],
        "Australia": ["Southern Cross NEXT", "JGA-S", "Indigo", "PIPE Pacific"],
        "India": ["SEA-ME-WE 4", "SEA-ME-WE 5", "FALCON", "IMEWE", "TGN-Gulf"],
    }
    
    cables = regional_cables.get(country, ["No specific cable data available"])
    return "<ul>" + "".join(f"<li>{cable}</li>" for cable in cables) + "</ul>"


def _display_cable_error(tab: apitypes.Tab, domain: str, error: str):
    """Display cable route error information."""
    content = f"""
    <div class="error">
        <p>Failed to retrieve cable route information for {domain}</p>
        <p>Error: {error}</p>
    </div>
    """
    _display_in_buffer(tab, f"Cable Route Error: {domain}", content)


@cmdutils.register(name='shodan-lookup')
@cmdutils.argument('tab', value=cmdutils.Value.cur_tab)
def shodan_lookup(tab: apitypes.Tab):
    """Open Shodan search for the current domain.
    
    Queries Shodan.io for:
    - Open ports and services
    - Service banners and versions
    - Known vulnerabilities (CVEs)
    - Historical data
    """
    url = _get_current_url(tab)
    domain = url.host()
    
    if not domain:
        # Debug: Show what URL we actually got
        url_str = url.toString() if not url.isEmpty() else "empty"
        raise cmdutils.CommandError(f"No valid domain in current URL (got: {url_str})")
    
    # Resolve domain to IP
    ip_address = _resolve_domain_to_ip(domain)
    if not ip_address:
        from qutebrowser.utils import message
        message.error(f"Failed to resolve {domain} to IP address")
        return
    
    # Open Shodan in new tab
    shodan_url = f"https://www.shodan.io/host/{ip_address}"
    tabbed_browser = _get_tabbed_browser(tab)
    tabbed_browser.load_url(QUrl(shodan_url), newtab=True)
    from qutebrowser.utils import message
    message.info(f"Opening Shodan lookup for {domain} ({ip_address})")


@cmdutils.register(name='censys-lookup')
@cmdutils.argument('tab', value=cmdutils.Value.cur_tab)
def censys_lookup(tab: apitypes.Tab):
    """Open Censys search for the current domain.
    
    Queries Censys.io for:
    - Internet-wide scan data
    - Certificate information
    - Service configurations
    - Security analysis
    """
    url = _get_current_url(tab)
    domain = url.host()
    
    if not domain:
        # Debug: Show what URL we actually got
        url_str = url.toString() if not url.isEmpty() else "empty"
        raise cmdutils.CommandError(f"No valid domain in current URL (got: {url_str})")
    
    # Resolve domain to IP
    ip_address = _resolve_domain_to_ip(domain)
    if not ip_address:
        from qutebrowser.utils import message
        message.error(f"Failed to resolve {domain} to IP address")
        return
    
    # Open Censys in new tab
    censys_url = f"https://search.censys.io/hosts/{ip_address}"
    tabbed_browser = _get_tabbed_browser(tab)
    tabbed_browser.load_url(QUrl(censys_url), newtab=True)
    from qutebrowser.utils import message
    message.info(f"Opening Censys lookup for {domain} ({ip_address})")


@cmdutils.register(name='cert-pivot')
@cmdutils.argument('tab', value=cmdutils.Value.cur_tab)
def cert_pivot(tab: apitypes.Tab):
    """Perform SSL/TLS certificate pivoting for the current domain.
    
    Discovers related infrastructure by:
    - Extracting the site's SSL certificate fingerprint
    - Querying certificate transparency logs
    - Finding all domains using the same certificate
    - Mapping organizational infrastructure
    """
    url = _get_current_url(tab)
    
    if url.scheme() != 'https':
        raise cmdutils.CommandError("Certificate pivoting requires HTTPS connection")
    
    domain = url.host()
    if not domain:
        raise cmdutils.CommandError("No valid domain in current URL")
    
    from qutebrowser.utils import message
    message.info(f"Performing certificate pivot for {domain}...")
    
    # Get certificate information
    cert_info = _get_certificate_info(domain)
    if not cert_info:
        from qutebrowser.utils import message
        message.error(f"Failed to retrieve certificate for {domain}")
        return
    
    # Query crt.sh for certificate transparency data
    if cert_info.get('common_name'):
        # Search by common name pattern
        search_query = cert_info['common_name'].replace('*.', '%25.')
        crtsh_url = f"https://crt.sh/?q={search_query}"
    else:
        # Fall back to domain search
        crtsh_url = f"https://crt.sh/?q={domain}"
    
    tabbed_browser = _get_tabbed_browser(tab)
    tabbed_browser.load_url(QUrl(crtsh_url), newtab=True)
    
    # Also display certificate info in buffer
    _display_cert_info(tab, domain, cert_info)


def _get_certificate_info(domain: str) -> Optional[Dict[str, Any]]:
    """Retrieve SSL certificate information for a domain."""
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect and get certificate
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Extract relevant information
                info = {
                    'common_name': None,
                    'san': [],
                    'issuer': None,
                    'not_before': cert.get('notBefore'),
                    'not_after': cert.get('notAfter'),
                }
                
                # Get common name
                for field in cert.get('subject', []):
                    for key, value in field:
                        if key == 'commonName':
                            info['common_name'] = value
                
                # Get Subject Alternative Names
                for san_type, san_value in cert.get('subjectAltName', []):
                    if san_type == 'DNS':
                        info['san'].append(san_value)
                
                # Get issuer
                for field in cert.get('issuer', []):
                    for key, value in field:
                        if key == 'organizationName':
                            info['issuer'] = value
                
                return info
                
    except (socket.error, ssl.SSLError, socket.timeout) as e:
        logger(f"Failed to get certificate for {domain}: {e}")
        return None


def _display_cert_info(tab: apitypes.Tab, domain: str, cert_info: Dict[str, Any]):
    """Display certificate information in a buffer."""
    content = f"""
    <h2>Current Certificate Information</h2>
    <div class="info-block">
        <p><span class="label">Domain:</span> <span class="value">{domain}</span></p>
        <p><span class="label">Common Name:</span> <span class="value">{cert_info.get('common_name', 'N/A')}</span></p>
        <p><span class="label">Issuer:</span> <span class="value">{cert_info.get('issuer', 'N/A')}</span></p>
        <p><span class="label">Valid From:</span> <span class="value">{cert_info.get('not_before', 'N/A')}</span></p>
        <p><span class="label">Valid Until:</span> <span class="value">{cert_info.get('not_after', 'N/A')}</span></p>
    </div>
    """
    
    if cert_info.get('san'):
        content += """
        <h2>Subject Alternative Names</h2>
        <div class="info-block">
            <ul>
        """
        for san in cert_info['san']:
            content += f"<li>{san}</li>"
        content += """
            </ul>
        </div>
        """
    
    content += """
    <h2>Certificate Transparency Search</h2>
    <div class="info-block">
        <p>A new tab has been opened with crt.sh results showing all certificates and domains associated with this organization.</p>
        <p>Additional certificate search tools:</p>
        <p>• <a href="https://transparencyreport.google.com/https/certificates" target="_blank">Google Certificate Transparency</a></p>
        <p>• <a href="https://censys.io/certificates" target="_blank">Censys Certificate Search</a></p>
    </div>
    """
    
    _display_in_buffer(tab, f"Certificate Pivot: {domain}", content)
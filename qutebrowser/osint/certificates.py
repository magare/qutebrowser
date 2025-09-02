"""SSL/TLS certificate intelligence gathering module."""

import ssl
import socket
import hashlib
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse

import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from PyQt6.QtCore import QObject, pyqtSignal

from qutebrowser.utils import message, log
from qutebrowser.osint.core import IntelligenceReport

logger = log.osint_cert = logging.getLogger('osint.certificates')


class CertificateIntelligence(QObject):
    """Analyzer for SSL/TLS certificate intelligence."""
    
    certificate_found = pyqtSignal(dict)
    related_domains_found = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cert_cache = {}
        
    def get_certificate(self, hostname: str, port: int = 443) -> Optional[Dict[str, Any]]:
        """Retrieve SSL certificate from a host."""
        cache_key = f"{hostname}:{port}"
        if cache_key in self.cert_cache:
            return self.cert_cache[cache_key]
            
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate in DER format
                    der_cert = ssock.getpeercert(binary_form=True)
                    pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
                    cert = x509.load_pem_x509_certificate(
                        pem_cert.encode(), default_backend()
                    )
                    
                    cert_info = self._parse_certificate(cert, der_cert)
                    cert_info['hostname'] = hostname
                    cert_info['port'] = port
                    
                    self.cert_cache[cache_key] = cert_info
                    self.certificate_found.emit(cert_info)
                    return cert_info
                    
        except Exception as e:
            logger.error(f"Failed to get certificate for {hostname}:{port}: {e}")
            return None
    
    def _parse_certificate(self, cert: x509.Certificate, der_cert: bytes) -> Dict[str, Any]:
        """Parse X.509 certificate details."""
        # Calculate certificate fingerprints
        sha1 = hashlib.sha1(der_cert).hexdigest()
        sha256 = hashlib.sha256(der_cert).hexdigest()
        
        # Extract subject information
        subject_dict = {}
        for attr in cert.subject:
            subject_dict[attr.oid._name] = attr.value
            
        # Extract issuer information
        issuer_dict = {}
        for attr in cert.issuer:
            issuer_dict[attr.oid._name] = attr.value
            
        # Extract SANs (Subject Alternative Names)
        san_list = []
        try:
            san_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            san_list = [san.value for san in san_ext.value]
        except x509.ExtensionNotFound:
            pass
            
        return {
            'fingerprint_sha1': sha1,
            'fingerprint_sha256': sha256,
            'subject': subject_dict,
            'issuer': issuer_dict,
            'serial_number': str(cert.serial_number),
            'not_before': cert.not_valid_before_utc.isoformat(),
            'not_after': cert.not_valid_after_utc.isoformat(),
            'san': san_list,
            'signature_algorithm': cert.signature_algorithm_oid._name,
            'version': cert.version.name,
            'is_ca': self._is_ca_certificate(cert),
            'key_usage': self._get_key_usage(cert),
            'extended_key_usage': self._get_extended_key_usage(cert)
        }
    
    def _is_ca_certificate(self, cert: x509.Certificate) -> bool:
        """Check if certificate is a CA certificate."""
        try:
            basic_constraints = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.BASIC_CONSTRAINTS
            )
            return basic_constraints.value.ca
        except x509.ExtensionNotFound:
            return False
            
    def _get_key_usage(self, cert: x509.Certificate) -> List[str]:
        """Extract key usage from certificate."""
        usage = []
        try:
            key_usage_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.KEY_USAGE
            )
            ku = key_usage_ext.value
            
            usage_mapping = {
                'digital_signature': ku.digital_signature if hasattr(ku, 'digital_signature') else False,
                'key_encipherment': ku.key_encipherment if hasattr(ku, 'key_encipherment') else False,
                'key_agreement': ku.key_agreement if hasattr(ku, 'key_agreement') else False,
                'key_cert_sign': ku.key_cert_sign if hasattr(ku, 'key_cert_sign') else False,
                'crl_sign': ku.crl_sign if hasattr(ku, 'crl_sign') else False,
            }
            
            usage = [key for key, value in usage_mapping.items() if value]
        except x509.ExtensionNotFound:
            pass
        return usage
        
    def _get_extended_key_usage(self, cert: x509.Certificate) -> List[str]:
        """Extract extended key usage from certificate."""
        usage = []
        try:
            eku_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.EXTENDED_KEY_USAGE
            )
            usage = [oid._name for oid in eku_ext.value]
        except x509.ExtensionNotFound:
            pass
        return usage
    
    def search_certificate_transparency(self, domain: str) -> List[Dict[str, Any]]:
        """Search Certificate Transparency logs for related certificates."""
        ct_results = []
        
        try:
            # Query crt.sh API with shorter timeout and better error handling
            url = f"https://crt.sh/?q={domain}&output=json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                certificates = response.json()
                
                for cert in certificates:
                    ct_results.append({
                        'id': cert.get('id'),
                        'logged_at': cert.get('entry_timestamp'),
                        'not_before': cert.get('not_before'),
                        'not_after': cert.get('not_after'),
                        'common_name': cert.get('common_name'),
                        'name_value': cert.get('name_value'),
                        'issuer': cert.get('issuer_name'),
                        'serial': cert.get('serial_number')
                    })
                    
                self.related_domains_found.emit(ct_results)
                
        except Exception as e:
            logger.error(f"CT log search failed for {domain}: {e}")
            
        return ct_results
    
    def find_certificates_by_fingerprint(self, fingerprint: str) -> List[Dict[str, Any]]:
        """Find other hosts using the same certificate fingerprint."""
        hosts = []
        
        try:
            # Use Censys API to search for certificate fingerprint
            # Note: Requires API key in production
            headers = {
                'Accept': 'application/json',
            }
            
            # This would require Censys API credentials
            # For now, return cached results if available
            for cache_key, cert_info in self.cert_cache.items():
                if (cert_info.get('fingerprint_sha256') == fingerprint or 
                    cert_info.get('fingerprint_sha1') == fingerprint):
                    hostname, port = cache_key.split(':')
                    hosts.append({
                        'hostname': hostname,
                        'port': int(port),
                        'certificate': cert_info
                    })
                    
        except Exception as e:
            logger.error(f"Failed to search by fingerprint {fingerprint}: {e}")
            
        return hosts
    
    def analyze_certificate_chain(self, hostname: str, port: int = 443) -> List[Dict[str, Any]]:
        """Analyze the full certificate chain."""
        chain = []
        
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get the peer certificate
                    cert_der = ssock.getpeercert(binary_form=True)
                    # Note: getpeercert_chain is not available in all Python versions
                    cert_chain = [cert_der]  # Just use the main cert for now
                    
                    if cert_chain:
                        for cert_der in cert_chain:
                            pem_cert = ssl.DER_cert_to_PEM_cert(cert_der)
                            cert = x509.load_pem_x509_certificate(
                                pem_cert.encode(), default_backend()
                            )
                            chain.append(self._parse_certificate(cert, cert_der))
                            
        except Exception as e:
            logger.error(f"Failed to analyze certificate chain for {hostname}: {e}")
            
        return chain
    
    def check_certificate_revocation(self, cert_info: Dict[str, Any]) -> Dict[str, bool]:
        """Check if certificate has been revoked."""
        revocation_status = {
            'checked': False,
            'revoked': False,
            'reason': None
        }
        
        # This would typically check OCSP or CRL
        # For now, return basic status
        try:
            not_after = datetime.fromisoformat(cert_info['not_after'])
            if datetime.now() > not_after:
                revocation_status['revoked'] = True
                revocation_status['reason'] = 'expired'
            revocation_status['checked'] = True
        except Exception as e:
            logger.error(f"Failed to check revocation status: {e}")
            
        return revocation_status
    
    def detect_wildcard_abuse(self, domain: str) -> List[Dict[str, Any]]:
        """Detect potential wildcard certificate abuse."""
        abuse_indicators = []
        
        # Skip CT search if it's already a wildcard domain
        if domain.startswith('*.'):
            return abuse_indicators
            
        # Only search CT logs for non-wildcard domains
        try:
            ct_results = self.search_certificate_transparency(f"*.{domain}")
        except:
            # If CT search fails, return empty list
            return abuse_indicators
        
        for cert in ct_results:
            name_value = cert.get('name_value', '')
            if '*' in name_value:
                # Check for overly broad wildcards
                if name_value.count('.') <= 1:  # e.g., *.com
                    abuse_indicators.append({
                        'type': 'overly_broad_wildcard',
                        'certificate': cert,
                        'risk': 'high'
                    })
                    
        return abuse_indicators
    
    def create_report(self, target: str, cert_data: Dict[str, Any]) -> IntelligenceReport:
        """Create an intelligence report from certificate analysis."""
        confidence = 0.9  # High confidence for direct certificate observation
        
        # Adjust confidence based on certificate validity
        if cert_data:
            try:
                not_after = datetime.fromisoformat(cert_data.get('not_after', ''))
                if datetime.now() > not_after:
                    confidence = 0.5  # Lower confidence for expired certs
            except:
                pass
                
        return IntelligenceReport(
            source='certificate_intelligence',
            target=target,
            data_type='ssl_certificate',
            data=cert_data,
            confidence=confidence,
            tags=['certificate', 'ssl', 'tls', 'encryption', 'pki']
        )
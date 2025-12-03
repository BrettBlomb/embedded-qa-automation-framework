# framework/ssl_utils.py

import ssl
import socket
from datetime import datetime
from typing import Dict, Any

def get_cert_info(hostname: str, port: int = 443) -> Dict[str, Any]:
    """Retrieve certificate info for the given hostname and port."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
    return cert

def is_cert_valid_now(cert: dict) -> bool:
    """Return True if cert is currently valid based on notBefore/notAfter."""
    # notBefore and notAfter are like 'Jan  1 00:00:00 2025 GMT'
    def _parse_date(s: str) -> datetime:
        """Parse an OpenSSL-style date string into a datetime."""
        return datetime.strptime(s, "%b %d %H:%M:%S %Y %Z")

    not_before = _parse_date(cert["notBefore"])
    not_after = _parse_date(cert["notAfter"])
    now = datetime.utcnow()
    return not_before <= now <= not_after

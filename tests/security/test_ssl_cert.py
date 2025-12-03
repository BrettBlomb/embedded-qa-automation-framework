# tests/security/test_ssl_cert.py

from framework.ssl_utils import get_cert_info, is_cert_valid_now

def test_ssl_certificate_valid_for_example_com():
    """Verify certificate for example.com is currently valid."""
    cert = get_cert_info("example.com", 443)
    assert is_cert_valid_now(cert)

def test_ssl_certificate_has_subject():
    """Verify certificate for example.com exposes a subject field."""
    cert = get_cert_info("example.com", 443)
    subject = dict(x[0] for x in cert["subject"])
    assert "commonName" in subject

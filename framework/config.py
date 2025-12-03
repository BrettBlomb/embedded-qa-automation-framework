# framework/config.py

import os

def get_api_base_url() -> str:
    """Return the base URL for the REST API under test."""
    # Reads from env so you can switch environments in Jenkins
    return os.getenv("API_BASE_URL", "https://httpbin.org")

def get_coap_host() -> str:
    """Return the hostname for the CoAP device under test."""
    return os.getenv("COAP_HOST", "localhost")

def get_coap_port() -> int:
    """Return the port for the CoAP device under test."""
    return int(os.getenv("COAP_PORT", "5683"))

def get_selenium_base_url() -> str:
    """Return the base URL for UI tests."""
    return os.getenv("UI_BASE_URL", "https://example.com")

def is_ci_environment() -> bool:
    """Return True if running in CI (Jenkins) based on environment variable."""
    return os.getenv("CI", "false").lower() == "true"

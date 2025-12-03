# framework/api_client.py

import requests
from .config import get_api_base_url

class ApiClient:
    """Simple REST API client wrapper around requests."""

    def __init__(self):
        """Initialize ApiClient with a base URL."""
        self.base_url = get_api_base_url()

    def _build_url(self, path: str) -> str:
        """Build a full URL from a relative path."""
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def get_health(self):
        """Send GET request to /health or a similar endpoint."""
        url = self._build_url("/status/200")  # using httpbin style endpoint
        return requests.get(url, timeout=5)

    def get(self, path: str, **kwargs):
        """Send a generic GET request."""
        url = self._build_url(path)
        return requests.get(url, timeout=5, **kwargs)

    def post(self, path: str, json=None, **kwargs):
        """Send a generic POST request with optional JSON body."""
        url = self._build_url(path)
        return requests.post(url, json=json, timeout=5, **kwargs)

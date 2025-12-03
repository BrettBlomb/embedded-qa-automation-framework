# tests/api/test_rest_health.py

from framework.api_client import ApiClient

def test_health_endpoint_returns_200():
    """Verify that the health endpoint responds with 200 OK."""
    client = ApiClient()
    response = client.get_health()
    assert response.status_code == 200

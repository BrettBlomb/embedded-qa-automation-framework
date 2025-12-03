# tests/api/test_coap_device.py

from framework.coap_client import CoapClient

def test_coap_get_resource_status_code():
    """Verify that CoAP GET returns a 2.xx success code for a resource."""
    client = CoapClient()
    response = client.get_resource_sync("status")
    # 2.xx are success codes in CoAP (e.g. 2.05 Content)
    assert str(response.code).startswith("2.")

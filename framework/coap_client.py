# framework/coap_client.py

import asyncio
from typing import Optional
from aiocoap import Context, Message, GET, PUT

class CoapClient:
    """Minimal CoAP client for interacting with a mock device."""

    def __init__(self, host="127.0.0.1", port=5683):
        """
        Initialize CoapClient.

        We force IPv4 and localhost because the CoAP mock server runs inside Docker
        but is exposed to Jenkins via -p 5683:5683/udp. Using 'localhost' can trigger
        IPv6 resolution and cause ECONNREFUSED inside Jenkins.
        """
        self.host = host
        self.port = port

    async def _send_request(self, method, path: str, payload: Optional[bytes] = None):
        """Send a CoAP request with the given method and payload."""
        protocol = await Context.create_client_context()

        # Force IPv4 URI
        uri = f"coap://{self.host}:{self.port}/{path.lstrip('/')}"

        request = Message(code=method, uri=uri, payload=payload or b"")
        response = await protocol.request(request).response
        return response

    async def get_resource(self, path: str):
        """Perform a CoAP GET request on the given path."""
        return await self._send_request(GET, path)

    async def put_resource(self, path: str, payload: bytes):
        """Perform a CoAP PUT request with a payload."""
        return await self._send_request(PUT, path, payload)

    def get_resource_sync(self, path: str):
        """Synchronous wrapper for CoAP GET for use in tests."""
        return asyncio.run(self.get_resource(path))

    def put_resource_sync(self, path: str, payload: bytes):
        """Synchronous wrapper for CoAP PUT."""
        return asyncio.run(self.put_resource(path, payload))

# framework/coap_client.py

import asyncio
from typing import Optional
from aiocoap import Context, Message, GET, PUT
from .config import get_coap_host, get_coap_port

class CoapClient:
    """Minimal CoAP client for interacting with a mock device."""

    def __init__(self):
        """Initialize CoapClient with host and port."""
        self.host = get_coap_host()
        self.port = get_coap_port()

    async def _send_request(self, method, path: str, payload: Optional[bytes] = None):
        """Send a CoAP request with the given method and payload."""
        protocol = await Context.create_client_context()
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
        """Synchronous wrapper for CoAP PUT for use in tests."""
        return asyncio.run(self.put_resource(path, payload))

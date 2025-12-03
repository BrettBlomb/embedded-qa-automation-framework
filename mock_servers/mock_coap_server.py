# mock_servers/mock_coap_server.py

import asyncio
import os

import aiocoap.resource as resource
from aiocoap import Message, Context
from aiocoap.numbers.codes import Code

# Default CoAP port; can be overridden via env if needed
COAP_PORT = int(os.getenv("COAP_PORT", "5683"))


class StatusResource(resource.Resource):
    """CoAP resource that returns a simple 'ok' payload on GET."""

    async def render_get(self, request):
        payload = b'{"status":"ok"}'
        return Message(code=Code.CONTENT, payload=payload)


async def main():
    # Build resource tree
    root = resource.Site()
    root.add_resource(('.well-known', 'core'),
                      resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('status',), StatusResource())

    # Bind to :: (IPv6) which also serves IPv4 on most stacks
    await Context.create_server_context(root, bind=('::', COAP_PORT))

    # Keep running forever
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())

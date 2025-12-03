# mock_coap_server.py
import asyncio
from aiocoap import Message, Context, resource

class StatusResource(resource.Resource):
    async def render_get(self, request):
        payload = b'{"status": "ok"}'
        return Message(payload=payload)

def main():
    root = resource.Site()
    root.add_resource(['status'], StatusResource())

    asyncio.Task(Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()

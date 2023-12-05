import asyncio
import websockets


class WSServerProtocol(websockets.WebSocketServerProtocol):
    async def handle_message(self, msg):
        # Handle messages here
        pass

    async def process_messages(self):
        # Process messages here
        pass

    async def on_connect(self, request):
        print(':: [Client Connected]')
        await self.process_messages()

    async def on_disconnect(self, close_status):
        print(f':: [Client Disconnected]: {close_status}')


async def main():
    host = 'localhost'
    port = 8080

    server = await websockets.serve(
        WSServerProtocol.on_connect,
        host=host,
        port=port,
        create_protocol=WSServerProtocol
    )

    print('WebSocket Server - running at')
    print(f':: ws://{host}:{port}')
    print(f':: /connect ws://{host}:{port}')
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()

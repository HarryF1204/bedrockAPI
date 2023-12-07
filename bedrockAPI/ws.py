import websockets
import json
import asyncio

from uuid import uuid4


class ConnectContext:
    pass


class BedrockAPI:

    def __init__(self, host='localhost', port=8000):
        self._loop = None
        self._host = host
        self._port = port
        self._ws: websockets.WebSocketServerProtocol | None = None
        self._event_handlers = {}

    def __repr__(self):
        return f"Bedrock API running at {self._host}:{self._port}"

    async def _handleWS(self, ws: websockets.WebSocketServerProtocol) -> None:
        self._ws = ws
        await self._send_event("connect")
        try:
            async for msg in self._ws:
                print(msg)
        except websockets.exceptions.ConnectionClosed as e:
            print(e)

    async def _sendPayload(self, header, body):
        data = json.dumps({
            "header": header,
            "body": body
        })

        return await self._ws.send(data)

    async def run_command(self, command):
        header = {
            "header": {
                "version": 1,
                "requestId": str(uuid4()),
                "messageType": "commandRequest",
                "messagePurpose": "commandRequest"
            }
        }
        body = {
            "version": 1,
            "origin": {"type": "player"},
            "commandLine": command,
            "overworld": "default"
        }
        return await self._sendPayload(header, body)

    async def subscribe_event(self, event):
        header = {
            "header": {
                "version": 1,
                "requestId": str(uuid4()),
                "messageType": "commandRequest",
                "messagePurpose": "subscribe"
            }
        }
        body = {
            "eventName": event
        }
        return await self._sendPayload(header, body)

    def start(self):
        print('WebSocket Server - running at')
        print(f':: ws://localhost:{self._port}')
        print(f':: /connect ws://{self._host}:{self._port}')

        server = websockets.serve(self._handleWS, self._host, self._port)
        self._loop = asyncio.get_event_loop()
        self._loop.run_until_complete(server)
        # run ready event
        self._loop.run_forever()

    async def _send_event(self, event):
        if event in self._event_handlers:
            await self._event_handlers[event]({})

    def server_event(self, event_name):
        def decorator(func):
            self._event_handlers[event_name] = func
            return func

        return decorator


if __name__ == '__main__':
    bedrock_api = BedrockAPI()


    @bedrock_api.server_event("connect")
    async def connect(context: ConnectContext) -> None:
        print("Connect")


    bedrock_api.start()

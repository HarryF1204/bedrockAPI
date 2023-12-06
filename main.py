import asyncio
import json
import websockets
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class WSServer:
    def __init__(self, host='localhost', port=8080):
        self._host = host
        self._port = port
        self._server: websockets.WebSocketServerProtocol | None = field(init=False, default=None)

    async def handle_websocket(self, ws):
        self._server = ws
        await self.run_command("say a")
        try:
            async for msg in self._server:
                print(msg)
        except websockets.exceptions.ConnectionClosed as e:
            print(e)

    @staticmethod
    def _createPayload(message_type, message_purpose, body):
        return json.dumps({
            "header": {
                "version": 1,
                "requestId": str(uuid4()),
                "messageType": message_type,
                "messagePurpose": message_purpose
            },
            "body": body
        })

    @classmethod
    def _createSubscribePayload(cls, event):
        return cls._createPayload("commandRequest", "subscribe", {
            "eventName": event
        })

    @classmethod
    def _createCommandPayload(cls, command):
        return cls._createPayload("commandRequest", "commandRequest", {
            "version": 1,
            "origin": {"type": "player"},
            "commandLine": command,
            "overworld": "default"
        })

    async def subscribe(self, event):
        payload = self._createSubscribePayload(event)
        await self._server.send(payload)

    async def run_command(self, command):
        payload = self._createCommandPayload(command)
        await self._server.send(payload)

    def run(self):
        print('WebSocket Server - running at')
        print(f':: ws://localhost:{self._port}')
        print(f':: /connect ws://{self._host}:{self._port}')
        server = websockets.serve(self.handle_websocket, self._host, self._port)

        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    server = WSServer()
    server.run()

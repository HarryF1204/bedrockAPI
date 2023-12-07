import asyncio
import json
import websockets
from dataclasses import dataclass, field
from uuid import uuid4

from request import CommandRequest
from response import CommandResponse


class WSServer:
    def __init__(self, host='localhost', port=8080):
        self.loop = None
        self._host = host
        self._port = port
        self._server: websockets.WebSocketServerProtocol | None = field(init=False, default=None)
        self._loop: asyncio.AbstractEventLoop | None = field(init=False, default=None)
        self._requests: list[CommandRequest] = field(init=False, default_factory=list)
        self._command_processing_semaphore: asyncio.BoundedSemaphore = field(
            init=False,
            default_factory=lambda: asyncio.BoundedSemaphore(100)
        )

    async def handle_websocket(self, ws):
        self._server = ws
        self._loop = asyncio.get_event_loop()
        self._command_processing_semaphore = asyncio.Semaphore()
        a = await self.runCommand("testfor @a")
        print(a)
        b = await self.subscribe("CommandResponse")
        print(b)
        try:
            async for msg in self._server:
                print(msg)
        except websockets.exceptions.ConnectionClosed as e:
            print(e)

    async def runCommand(self, command):
        identifier = uuid4()
        header = {
            "version": 1,
            "requestId": str(identifier),
            "messageType": "commandRequest",
            "messagePurpose": "commandRequest"
        }
        body = {
            "version": 1,
            "origin": {"type": "player"},
            "commandLine": command,
            "overworld": "default"
        }

        return await self._sendPayload(header, body, identifier)

    async def subscribe(self, event):
        identifier = uuid4()
        header = {
            "version": 1,
            "requestId": str(identifier),
            "messageType": "commandRequest",
            "messagePurpose": "subscribe"
        }
        body = {
            "eventName": event
        }

        return await self._sendPayload(header, body, identifier)

    async def _sendPayload(self, header, body, identifier) -> CommandResponse:

        data = {
            "header": header,
            "body": body
        }

        request = CommandRequest(identifier=identifier, data=data, response=self._loop.create_future())

        async with self._command_processing_semaphore:
            await self._server.send(json.dumps(data))
        return await request.response

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

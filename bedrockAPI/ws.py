import websockets
import json
import asyncio

from uuid import uuid4

from events import *

import logging


class BedrockAPI:

    def __init__(self, host='localhost', port=8000):
        self._loop = None
        self._host = host
        self._port = port
        self._ws: websockets.WebSocketServerProtocol
        self._serverEvent = ServerEvent()
        self._gameEvent = GameEvent()

    def __repr__(self):
        return f"Bedrock API running at {self._host}:{self._port}"

    async def _handleWS(self, ws: websockets.WebSocketServerProtocol) -> None:
        self._ws = ws
        self._dispatchServerEvent("connect")
        try:
            async for msg in self._ws:
                print(msg)
        except websockets.exceptions.ConnectionClosed as e:
            self._dispatchServerEvent("disconnect")
            print(':: Client Disconnected', e)

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

    async def _subscribeEvent(self, event):
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
        self._dispatchServerEvent("ready")
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            print(':: Server Closed from Keyboard Interrupt')

    def _dispatchServerEvent(self, event):
        assert self._loop
        connectContext = ConnectContext(self._host, self._port)
        self._loop.create_task(self._serverEvent.trigger_event(event, connectContext))

    def server_event(self, func=None):
        def decorator(event):
            self._serverEvent.add_event_handler(event.__name__, event)
            return event

        return decorator(func)

    def game_event(self, func=None):
        def wrapper(event):
            self._gameEvent.add_event_handler(event.__name__, event)
            return event

        return wrapper(func)

    def remove_server_event(self, func=None):
        def wrapper(event):
            self._serverEvent.remove_event_handler(event)

        return wrapper(func)


if __name__ == '__main__':
    api = BedrockAPI()


    @api.server_event
    async def ready(context: ConnectContext) -> None:
        print('ready')


    @api.server_event
    async def connect(context: ConnectContext) -> None:
        print("Connected on {0}:{1}".format(context.host, context.port))

    @api.server_event
    async def disconnect(context: ConnectContext) -> None:
        print('disconnected')


    api.start()

import websockets
import json
import asyncio

from uuid import uuid4

from events import *

import consts
import utils
import context
import logging


class BedrockAPI:

    def __init__(self, host='localhost', port=8000):
        self._host = host
        self._port = port
        self._serverEvent = ServerEvent()
        self._gameEvent = GameEvent()
        self._ws: websockets.WebSocketServerProtocol
        self._loop = asyncio.get_event_loop()

    def __repr__(self):
        return f"Bedrock API running at {self._host}:{self._port}"

    async def _handleWS(self, ws: websockets.WebSocketServerProtocol) -> None:
        self._ws = ws
        self._dispatchServerEvent("connect")

        for item in self._gameEvent.event_handlers.keys():
            await self._subscribeEvent(item)

        try:
            async for msg in self._ws:
                data = json.loads(msg)
                eventName = data["header"]["eventName"]
                body = data["body"]

                gameContext = context.getGameContext(eventName)(body)
                await self._gameEvent.trigger_event(eventName, gameContext)

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

    async def _subscribeEvent(self, event, unsubscribe=False):
        if event not in consts.game_events:
            raise Exception(f"Event: {event} not found in event list")

        subscribeMode = "subscribe" if not unsubscribe else "unsubscribe"

        header = {
            "version": 1,
            "requestId": str(uuid4()),
            "messageType": "commandRequest",
            "messagePurpose": subscribeMode
        }
        body = {
            "eventName": event
        }
        return await self._sendPayload(header, body)

    def start(self):
        assert self._loop

        print('WebSocket Server - running at')
        print(f':: ws://localhost:{self._port}')
        print(f':: /connect ws://{self._host}:{self._port}')

        server = websockets.serve(self._handleWS, self._host, self._port)
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
            event_name = utils.to_pascal_case(event.__name__)
            if event_name not in consts.game_events:
                raise Exception(f"{event_name} not found in events")

            self._gameEvent.add_event_handler(event_name, event)
            return event

        return wrapper(func)

    def remove_server_event(self, event):
        self._serverEvent.remove_event_handler(event)

    def remove_game_event(self, event):
        self._gameEvent.remove_event_handler(event)
        self._loop.create_task(self._subscribeEvent(event, unsubscribe=True))


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

    @api.game_event
    async def PlayerMessage(data) -> None:
        print("Player Message:", data.message)
        api.remove_game_event("PlayerMessage")

    api.start()

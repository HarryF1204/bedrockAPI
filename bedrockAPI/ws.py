import websockets
import json
import asyncio
import sys
import os
import signal

from uuid import uuid4

from bedrockAPI.events import *

import bedrockAPI.consts as consts
import bedrockAPI.utils as utils
import bedrockAPI.context as context
import logging


class BedrockAPI:
    """
    Bedrock API for bridging the gap between python and Minecraft Bedrock Edition
    """
    def __init__(self, host='localhost', port=8000):
        self._host = host
        self._port = port
        self._serverEvent = ServerEvent()
        self._gameEvent = GameEvent()
        self._ws: websockets.WebSocketServerProtocol
        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._commandResponseFutures: Dict[str, asyncio.Future] = {}
        self._server = None

    @property
    def loop(self):
        return self._loop

    def __repr__(self):
        return f"Bedrock API running at {self._host}:{self._port}"
 
    async def _handleWS(self, ws: websockets.WebSocketServerProtocol) -> None:
        self._ws = ws
        self._dispatchServerEvent("connect")

        try:
            async for msg in self._ws:
                data = json.loads(msg)

                header = data["header"]
                body = data["body"]

                if header["messagePurpose"] == "commandResponse":
                    requestId = header["requestId"]
                    if requestId in self._commandResponseFutures:
                        gameContext = context.CommandResponseContext(body)
                        self._commandResponseFutures[requestId].set_result(gameContext)
                        del self._commandResponseFutures[requestId]

                elif header["messagePurpose"] == "event":
                    eventName = header["eventName"]
                    gameContext = context.getGameContext(eventName)(body)
                    self._loop.create_task(self._gameEvent.trigger_event(eventName, gameContext))

                else:
                    print(data)
        except websockets.exceptions.ConnectionClosed as e:
            self._dispatchServerEvent("disconnect")
            print(':: Client Disconnected', e)
        except asyncio.CancelledError:
            raise
        finally:
            if not ws.closed:
                await ws.close()


    async def _sendPayload(self, header, body):
        data = json.dumps({
            "header": header,
            "body": body
        })
        return await self._ws.send(data)

    async def run_command(self, command):
        requestId = str(uuid4())
        header = {
            "version": 1,
            "requestId": requestId,
            "messageType": "commandRequest",
            "messagePurpose": "commandRequest"
        }
        body = {
            "version": 1,
            "origin": {"type": "player"},
            "commandLine": command,
            "overworld": "default"
        }

        response_future = asyncio.Future()
        self._commandResponseFutures[header["requestId"]] = response_future

        await self._sendPayload(header, body)

        future = await response_future
        return future

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
        async def main():
            print('WebSocket Server - running at')
            print(f':: ws://localhost:{self._port}')
            print(f':: /connect ws://{self._host}:{self._port}')
            
            self._server = await websockets.serve(self._handleWS, self._host, self._port)
            self._dispatchServerEvent("ready")
            await self._server.wait_closed()

        if not self._loop.is_running():
            self._server_task = self._loop.create_task(main())
            self._loop.run_forever()
        else:
            asyncio.ensure_future(main(), loop=self._loop)

    def _dispatchServerEvent(self, event):
        assert self._loop
        connectContext = ConnectContext(self._host, self._port)
        self._loop.create_task(self._serverEvent.trigger_event(event, connectContext))

    def server_event(self, func=None):
        def decorator(event):
            self._serverEvent.add_event_handler(event.__name__, event)
            return event

        return decorator(func)

    # @todo: allow specifying the event name in the decorator
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


    def stop(self):
        async def shutdown():
            if self._server is not None:
                # Forcibly close all active WebSocket connections
                for ws in self._server.websockets.copy():
                    ws.transport.close()  # Immediately close the transport (socket)
                
                # Now close the server itself
                self._server.close()
                await self._server.wait_closed()

            await self._loop.shutdown_asyncgens()

        if self._loop.is_running():
            # Schedule the shutdown task and forcibly stop the loop
            asyncio.ensure_future(shutdown(), loop=self._loop)

            print('Terminating the event loop')
            os.kill(os.getpid(), signal.SIGTERM)  # Terminate the process immediately

        else:
            # If the loop is not running, just run the shutdown coroutine directly
            asyncio.run(shutdown())




if __name__ == '__main__':
    api = BedrockAPI()


    @api.game_event
    async def block_placed(ctx) -> None:
        pass


    @api.game_event
    async def block_broken(ctx) -> None:
        print(f'{ctx.block.typeId}\n{ctx.itemStack.typeId}\n{ctx.player.position}')


    @api.server_event
    async def connect(ctx) -> None:
        pass


    api.start()

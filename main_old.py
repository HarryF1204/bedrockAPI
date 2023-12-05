import asyncio
import websockets
import json
from uuid import uuid4
import re


def create_payload(message_type, message_purpose, body):
    return json.dumps({
        "header": {
            "version": 1,
            "requestId": str(uuid4()),
            "messageType": message_type,
            "messagePurpose": message_purpose
        },
        "body": body
    })


def create_subscribe_payload(event):
    return create_payload("commandRequest", "subscribe", {
        "eventName": event
    })


def create_command_payload(command):
    return create_payload("commandRequest", "commandRequest", {
        "version": 1,
        "origin": {"type": "player"},
        "commandLine": command,
        "overworld": "default"
    })


def subscribe(websocket, event):
    payload = create_subscribe_payload(event)
    websocket.send(payload)


def run_command(websocket, command):
    payload = create_command_payload(command)
    websocket.send(payload)


async def wss(websocket, path):
    print(':: [Client Connected]')

    try:
        await websocket.send(create_subscribe_payload("PlayerMessage"))

        async for msg in websocket:
            try:
                msg = json.loads(msg)
                # I have only subscribed messages so this is guaranteed to be in the json data
                if msg["body"]["type"] == "chat":
                    print('is chat')
                    print(msg["body"]["message"])
                    match = re.match(r'^aaa', msg["body"]["message"], re.IGNORECASE)
                    if match:
                        print("AAAAAAA")
            except json.JSONDecodeError as e:
                print(f':: [Error] JSON decoding error: {e}')
            except KeyError as e:
                print(f':: [Error] Missing key in message: {e}')
    except websockets.exceptions.ConnectionClosedError as e:
        print(f':: [Client Disconnected]: {e}')


async def main():
    port = 8080
    async with websockets.serve(wss, host='localhost', port=port):
        print('WebSocket Server - running at')
        print(f':: ws://localhost:{port}')
        print(f':: /connect ws://localhost:{port}')
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()

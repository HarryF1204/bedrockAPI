import websockets
import asyncio
import uuid
import json


async def handle_client(websocket):
    try:

        header = {
            "version": 1,
            "requestId": str(uuid.uuid4),
            "messageType": "commandRequest",
            "messagePurpose": "commandRequest"
        }
        body = {
            "version": 1,
            "origin": {"type": "player"},
            "commandLine": "summon pig",
            "overworld": "default"
        }

        data = {
            "header": header,
            "body": body
        }
        data = json.dumps(data)
        print(await websocket.send(data))
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed.")


start_server = websockets.serve(handle_client, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

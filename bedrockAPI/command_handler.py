import asyncio
from context import CommandResponseContext


class CommandHandler:
    def __init__(self):
        self._command = dict()

    def addCommandRequest(self, data):
        requestID = data["header"]["requestId"]
        self._command[requestID] = asyncio.Future[CommandResponseContext]

    def parseCommandResponse(self, data):
        responseID = data["header"]["requestId"]
        body = data["body"]
        return self._command.get(responseID, None).parseResponse(body)




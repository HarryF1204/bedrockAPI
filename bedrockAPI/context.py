from uuid import UUID
import asyncio

class GameContext:
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data


class PlayerMessageContext(GameContext):
    def __init__(self, data):
        super().__init__(data)

    @property
    def message(self) -> str:
        return self._data["message"]

    @property
    def sender(self) -> str:
        return self._data["sender"]

    @property
    def receiver(self) -> str:
        return None or self._data["receiver"]

    @property
    def msg_type(self) -> str:
        return self._data["type"]


class CommandResponseContext:
    def __init__(self, data):
        self._data = data

    @property
    def message(self) -> str:
        return self._data["message"]

    @property
    def status(self) -> str:
        return self._data["statusCode"]


class CommandRequestContext:
    def __init__(self, identifier, command):
        self._command = command
        self._id: UUID = identifier
        self._response = asyncio.Future[CommandResponseContext]

    @property
    def identifier(self):
        return self._command

    @property
    def id(self):
        return self._id


def getGameContext(name) -> type[GameContext]:
    return {
        "PlayerMessage": PlayerMessageContext
    }.get(name, GameContext)

from uuid import UUID
import asyncio
import math


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


class Location:
    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @staticmethod
    def distance_to(location1, location2):
        if not isinstance(location1, Location) or not isinstance(location2, Location):
            raise ValueError("Can only calculate distance between two Location instances.")
        dx = location1._x - location2.x
        dy = location1._y - location2.y
        dz = location1._z - location2.z
        return math.sqrt(dx**2 + dy**2 + dz**2)

    def __add__(self, other):
        if not isinstance(other, Location):
            raise ValueError("You can only add another Location")
        return Location(self._x + other.x, self._y + other.y, self._z + other.z)

    def __sub__(self, other):
        if not isinstance(other, Location):
            raise ValueError("You can only subtract another Location")
        return Location(self._x - other.x, self._y - other.y, self._z - other.z)

    def __eq__(self, other) -> bool:
        return isinstance(other, Location) and self._x == other.x and self._y == other.y and self._z == other.z


class ItemStack:
    pass


class Player:
    def __init__(self):
        self._dimension = 0
        self._id = 0
        self._name = ""
        self.position = None


class Block:
    pass


def getGameContext(name) -> type[GameContext]:
    return {
        "PlayerMessage": PlayerMessageContext
    }.get(name, GameContext)

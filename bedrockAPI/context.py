from uuid import UUID
import asyncio
import math


class GameContext:
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data


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
        return math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

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

    def __str__(self) -> str:
        return f"Location: {self._x}, {self._y}, {self._z}"


class Enchantment:
    def __init__(self, data):
        self._name = data["name"]
        self._type = data["type"]
        self._level = data["level"]

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def level(self):
        return self._level


class ItemStack:
    def __init__(self, data):
        self._aux = data["aux"]
        self._enchantments = [Enchantment(enchantment) for enchantment in data["enchantments"]]
        self._typeId = f'{data["namespace"]}:{data["id"]}'
        self._stackSize = data["stackSize"]
        self._maxStackSize = data["maxStackSize"]

    @property
    def aux(self):
        return self._aux

    @property
    def enchantments(self):
        return self._enchantments

    @property
    def typeId(self):
        return self._typeId

    @property
    def stackSize(self):
        return self._stackSize

    @property
    def maxStackSize(self):
        return self._maxStackSize


class Block:
    def __init__(self, data):
        self._aux = data["aux"]
        self._typeId = f'{data["namespace"]}:{data["id"]}'

    @property
    def typeId(self) -> str:
        return self._typeId

    @property
    def aux(self) -> int:
        return self._aux


class Player:
    def __init__(self, data):
        self._dimension = data["dimension"]
        self._id = data["id"]
        self._name = data["name"]
        self._position = Location(**data["position"])

    @property
    def dimension(self):
        return self._dimension

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def position(self):
        return self._position


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


class BlockBrokenContext(GameContext):
    def __init__(self, data):
        super().__init__(data)

        self._block = Block(data["block"])
        self._destruction = data["destructionMethod"]
        self._itemStack = ItemStack(data["tool"])
        self._player = Player(data["player"])

    @property
    def block(self):
        return self._block

    @property
    def destruction(self):
        return self._destruction

    @property
    def itemStack(self):
        return self._itemStack

    @property
    def player(self):
        return self._player


def getGameContext(name) -> type[GameContext]:
    return {
        "PlayerMessage": PlayerMessageContext,
        "BlockBroken": BlockBrokenContext
    }.get(name, GameContext)

from uuid import UUID
import asyncio
import math


class GameContext:
    """
    The default class for game context, stores the body of the data returned by the client
    when a subscribed event occurs.

    Attributes:
        _data: private variable holding the json data returned from the event

    Methods:
        data: returns _data as a python object

    Params:
        data: body from the returned subscribe event
    """
    def __init__(self, data: dict):
        self._data = data

    @property
    def data(self) -> dict:
        return self._data


class CommandResponseContext:
    """
    Class for storing the data returned from running a command with run_command (ws.py).

    Attributes:
        _data: the full body section of the returned data

    Methods:
        message: returns the data returned from executing the command
        status: returns the status code
    """
    def __init__(self, data):
        self._data = data

    @property
    def message(self) -> str:
        return self._data["message"]

    @property
    def status(self) -> str:  # to do: raise error on failed command
        return self._data["statusCode"]


class CommandRequestContext:
    """
    Class for storing the request data to be compared to responses in _wsHandler (ws.py)

    Attributes:
        _command: The command sent to the client
        _id: the UUID to be compared to CommandResponses
        _response: The CommandResponseContext object to be obtained later

    Methods:
        command: returns the command
        id: returns the id
    """
    def __init__(self, identifier, command):
        self._command = command
        self._id: UUID = identifier
        self._response = asyncio.Future[CommandResponseContext]

    @property
    def command(self):
        return self._command

    @property
    def id(self):
        return self._id



class Location:
    """
    A class representing a location in 3D space

    Params:
        x, y, z: coordinates

    Attributes:
        x, y, z: coordinates

    Methods:
        x, y, z: returns coordinates

        distance_to:
            @params
                Location1: Location, Location2: Location
            returns the distance between two locations

    """
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
    """
    A class representing game enchantments to be used by context

    Attributes:
        name: The name of the enchant as it appears in game
        type: The int value representing a specific enchantment
        level: The level of the enchant

    Methods:
        name: returns name
        type: returns type
        level: returns level
    """
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
    """
    A class representing in game items

    Attributes:
        aux: the aux identifier of the item -- the item variant
        enchantments: the enchantments on the item returned as an array of Enchantment instances
        typeId: the identifier in the form of namespace:item_name
        stackSize: the amount of the item
        maxStackSize: the max amount of items that this item can have

    Methods:
        aux: returns aux value
        enchantments: returns enchantments list
        typeId: returns the identifier
        stackSize: returns the stack size
        maxStackSize: returns the maxStackSize

    """
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
    """
    A class representing in game blocks

    Attributes:
        aux: the variant of the block type
        typeId: the block type

    Methods:
        aux: returns the aux value
        typeId: returns the block name in the form of namespace:identifier
    """
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
    """
    A class representing player entities

    Attributes:
        dimension -> int: returns the dimension of the player as an integer, e.g., overworld would be 0
        id -> int: the entity identifier
        name -> str: the name tag of the player
        position -> Location: returns the location of the player

    Methods:
        dimension: returns the current dimension of the entity
        id: returns the id
        name: returns the nametag
        position: returns the location of the player as a Location
    """
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

    # to do: set dimension, set position, kill, give item, etc


class PlayerMessageContext(GameContext):
    """
    A class representing the Game Context for Player Messages sent in game.
    This class inherits from Game Context

    Methods:
        message -> str: returns the message that was sent
        sender -> str: returns the sender of the message
        receiver -> str: returns the receiver of the message
        msg_type -> str: returns the type of the message, e.g., tell

    """
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
    """
    A class representing the Game Context for the Block Broken game event.
    This class inherits from Game Context

    Attributes:
        _block: the block that was broken stored as an instance of the Block class
        _destruction: the destruction method
        _itemStack: the item used to break the block
        _player: the player entity that broke the block as a Player instance

    Methods:
        block: returns the block
        destruction: returns the destruction method as an integer
        itemStack: returns the item
        player: returns the player
    """
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

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


def getGameContext(name) -> type[GameContext]:
    return {
        "PlayerMessage": PlayerMessageContext
    }.get(name, GameContext)

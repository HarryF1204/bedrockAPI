from typing import Callable, Dict


class EventManager:
    def __init__(self):
        self._event_handlers: Dict[str, Callable] = {}

    def add_event_handler(self, event, handler):
        self._event_handlers[event] = handler

    def remove_event_handler(self, event):
        self._event_handlers.pop(event)

    async def trigger_event(self, event_name, *args, **kwargs):
        if event_name in self._event_handlers:
            await self._event_handlers[event_name](*args, **kwargs)


class GameEvent(EventManager):
    def __init__(self):
        super().__init__()


class ServerEvent(EventManager):
    def __init__(self):
        super().__init__()


class ConnectContext:
    def __init__(self, host, port):
        self.host = host
        self.port = port

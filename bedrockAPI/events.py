from typing import Callable, Dict


class EventManager:
    def __init__(self):
        self._event_handlers: Dict[str, Callable] = {}

    def add_event_handler(self, event, handler):
        self._event_handlers[event] = handler

    async def trigger_event(self, event_name, *args, **kwargs):
        if event_name in self._event_handlers:
            await self._event_handlers[event_name](*args, **kwargs)


class ConnectContext:
    def __init__(self, host, port):
        self.host = host
        self.port = port

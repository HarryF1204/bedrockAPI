import asyncio
from collections.abc import Mapping
from uuid import UUID
from typing import Any
from dataclasses import dataclass

from response import CommandResponse


@dataclass
class CommandRequest:
    """A command request sent to the server."""

    def __init__(self, identifier, data, response):
        self._identifier: UUID = identifier
        self._data: Mapping[str, Any] = data
        self._response: asyncio.Future[CommandResponse] = response

    @property
    def identifier(self) -> UUID:
        """The unique id of the request."""
        return self._identifier

    @property
    def data(self) -> Mapping[str, Any]:
        """The data of the request."""
        return self._data

    @property
    def response(self) -> asyncio.Future[CommandResponse]:
        """The response of the response wrapped inside a :external+python:class:`asyncio.Future`."""
        return self._response

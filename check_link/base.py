from __future__ import annotations

import abc
import enum

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse


class State(enum.Enum):
    unknown = enum.auto()
    available = enum.auto()
    moved = enum.auto()
    missing = enum.auto()
    protected = enum.auto()
    broken = enum.auto()
    error = enum.auto()


class Option(enum.Flag):
    allow_redirects = enum.auto()
    try_head = enum.auto()
    add_agent = enum.auto()

    default = try_head | add_agent


@dataclass
class Link:
    link: str
    state: State = field(default=State.unknown)
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        url = urlparse(self.link)
        if not url.scheme or not url.hostname:
            raise ValueError("Links without schema or hostname are not allowed")

    def __str__(self):
        return self.link


@dataclass
class BaseChecker(abc.ABC):
    session: Any = field(default=None)
    options: Option = Option.default

    def __post_init__(self):
        if not self.session:
            raise TypeError("Session is not initialized")

    def close(self):
        return self.session.close()

    def _headers(self) -> dict[str, str]:
        headers = {}
        if self.options & Option.add_agent:
            headers.update(
                {
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,"
                        " like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                    )
                }
            )

        return headers

    @staticmethod
    def _state_from_code(code: int):
        if code < 300:
            return State.available

        if 300 <= code < 400:
            return State.moved

        if code == 404:
            return State.missing

        if code in {401, 403}:
            return State.protected

        if code < 500:
            return State.broken

        return State.error

    @abc.abstractmethod
    def check(self, link: Link) -> Any:
        ...

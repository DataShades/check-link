from __future__ import annotations

import abc
import enum

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional
from urllib.parse import urlparse


class State(enum.Enum):
    unknown = enum.auto()
    available = enum.auto()
    moved = enum.auto()
    missing = enum.auto()
    protected = enum.auto()
    broken = enum.auto()
    error = enum.auto()
    exception = enum.auto()

    @classmethod
    def from_code_and_headers(cls, code: int, headers: Mapping[str, Any]):
        if code < 300:
            return cls.available, "Link is available"

        if 300 <= code < 400:
            location = headers.get("Location") or "unknown"
            return cls.moved, f"New location is {location}"

        if code in {404, 410}:
            return cls.missing, "Link is not available"

        if code in {401, 403}:
            return cls.protected, "Link is not accessible"

        if code < 500:
            return cls.broken, "Link is invalid"

        return cls.error, "Link is not available"


class Option(enum.Flag):
    allow_redirects = enum.auto()
    try_head = enum.auto()
    add_agent = enum.auto()

    default = try_head | add_agent | allow_redirects


@dataclass
class Link:
    link: str
    state: State = field(default=State.unknown)
    headers: dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    reason: Optional[str] = None
    code: Optional[int] = None

    def __post_init__(self):
        url = urlparse(self.link)
        if not url.scheme or not url.hostname:
            raise ValueError("Links without schema or hostname are not allowed")

    def __str__(self):
        return self.link

    def state_from_code(
        self, code: int, reason: Optional[str], headers: Mapping[str, Any]
    ):
        self.state, self.details = State.from_code_and_headers(code, headers)
        self.code = code
        self.reason = reason

    def state_from_exception(self, err: Exception):
        self.state = State.exception
        self.details = str(err)


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

    @abc.abstractmethod
    def check(self, link: Link) -> Any:
        ...

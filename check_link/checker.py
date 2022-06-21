from __future__ import annotations

from dataclasses import dataclass, field
import aiohttp
from aiohttp.client import ClientSession

from .base import BaseChecker, Link, Option


@dataclass
class AsyncChecker(BaseChecker):
    session: ClientSession = field(default_factory=ClientSession)

    async def __aenter__(self):
        return self

    async def __aexit__(self, type, value, traceback):
        await self.close()

    async def _ping(
        self, link: Link, headers: dict[str, str]
    ) -> aiohttp.ClientResponse:
        if self.options & Option.try_head:
            resp = await self.session.head(str(link), headers=headers)
            if resp.status != 405:
                return resp

        allow_redirects = bool(self.options & Option.allow_redirects)
        return await self.session.get(
            str(link), allow_redirects=allow_redirects, headers=headers
        )

    async def check(self, link: Link) -> Link:
        if self.session.closed:
            raise RuntimeError("Cannot use closed checker")

        headers = self._headers()
        headers.update(link.headers)

        resp = await self._ping(link, headers)

        link.state = self._state_from_code(resp.status)
        return link

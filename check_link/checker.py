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
        allow_redirects = bool(self.options & Option.allow_redirects)

        if self.options & Option.try_head:
            resp = await self.session.head(
                str(link),
                headers=headers,
                allow_redirects=allow_redirects,
                timeout=link.timeout,
            )
            if resp.status != 405:
                return resp

        return await self.session.get(
            str(link),
            allow_redirects=allow_redirects,
            headers=headers,
            timeout=link.timeout,
        )

    async def check(self, link: Link) -> Link:
        if self.session.closed:
            raise RuntimeError("Cannot use closed checker")

        headers = self._headers()
        headers.update(link.headers)

        try:
            resp = await self._ping(link, headers)
        except aiohttp.ClientConnectionError as e:
            link.state_from_exception(e)
        else:
            link.state_from_code(resp.status, resp.reason, resp.headers)

        return link

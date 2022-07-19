from __future__ import annotations
import asyncio

from dataclasses import dataclass, field
# import aiohttp
# from aiohttp.client import ClientSession
import httpx
# from httpx import AsyncClient

from .base import BaseChecker, Link, Option

def session_factory():
    # return ClientSession()
    return httpx.AsyncClient()

@dataclass
class AsyncChecker(BaseChecker):
    session: httpx.AsyncClient = field(default_factory=session_factory)

    async def __aenter__(self):
        return self

    async def __aexit__(self, type, value, traceback):
        await self.close()

    def close(self):

        return self.session.aclose()


    async def _ping(
        self, link: Link, headers: dict[str, str]
    ) -> httpx.Response:
        allow_redirects = bool(self.options & Option.allow_redirects)

        if self.options & Option.try_head:
            resp = await self.session.head(
                str(link),
                headers=headers,
                follow_redirects=allow_redirects,
                timeout=link.timeout,
            )
            if resp.status_code != 405:
                    return resp

        return await self.session.get(
            str(link),
            follow_redirects=allow_redirects,
            headers=headers,
            timeout=link.timeout,
        )

    async def check(self, link: Link) -> Link:
        if self.session.is_closed:
            raise RuntimeError("Cannot use closed checker")

        headers = self._headers()
        headers.update(link.headers)

        try:
            resp = await self._ping(link, headers)
        # except aiohttp.ClientResponseError as e:
            # link.state_from_code(e.status, e.message, e.headers or {})
        except httpx.RequestError as e:
            link.state_from_exception(e)
        except asyncio.TimeoutError:
            link.state_from_exception(TimeoutError("Timeout reached"))
        else:
            link.state_from_code(resp.status_code, resp.reason_phrase, resp.headers)

        return link

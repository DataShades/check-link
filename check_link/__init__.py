from __future__ import annotations

import asyncio
from typing import Callable, Iterable


from .base import State, Option, Link
from .blocking import BlockingChecker
from .checker import AsyncChecker

__all__ = [
    "State",
    "Option",
    "Link",
    "BlockingChecker",
    "AsyncChecker",
    "check_all_blocking",
]


def check_all_blocking(
    links: Iterable[Link], checker_factory: Callable[[], AsyncChecker] = AsyncChecker
) -> Iterable[Link]:
    result = asyncio.run(_check_all_async(checker_factory, links))

    return result


async def _check_all_async(
    checker_factory: Callable[[], AsyncChecker], links: Iterable[Link]
) -> Iterable[Link]:
    async with checker_factory() as checker:
        results = await asyncio.gather(*map(checker.check, links))

    return results

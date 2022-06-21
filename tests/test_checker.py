import pytest
from aioresponses import aioresponses
from check_link import State, Link, AsyncChecker, Option

URL = "http://example.com"

expected_states = [
    (100, State.available),
    (200, State.available),
    (201, State.available),
    (204, State.available),
    (300, State.moved),
    (301, State.moved),
    (302, State.moved),
    (404, State.missing),
    (401, State.protected),
    (403, State.protected),
    (400, State.broken),
    (402, State.broken),
    # (405, State.broken),
    (410, State.broken),
    (418, State.broken),
    (500, State.error),
    (501, State.error),
    (506, State.error),
]


@pytest.fixture
def rmock():
    with aioresponses() as m:
        yield m


@pytest.mark.parametrize("status,state", expected_states)
async def test_default_head(status, state, rmock: aioresponses):
    rmock.head(URL, status=status)
    link = Link(URL)
    async with AsyncChecker() as checker:
        await checker.check(link)

    assert link.state is state


@pytest.mark.parametrize("status,state", expected_states + [(405, State.broken)])
async def test_disabled_head(status, state, rmock: aioresponses):
    rmock.head(URL, status=405)
    rmock.get(URL, status=status)
    link = Link(URL)
    checker = AsyncChecker(options=Option.default & ~Option.try_head)
    await checker.check(link)
    assert link.state is state

    await checker.close()


async def test_closed_checker():
    async with AsyncChecker() as checker:
        pass

    with pytest.raises(RuntimeError):
        await checker.check(Link(URL))

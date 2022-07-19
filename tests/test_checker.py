import pytest
# from aioresponses import aioresponses
from pytest_httpx import HTTPXMock
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
    (400, State.invalid),
    (402, State.invalid),
    # (405, State.invalid),
    (410, State.missing),
    (418, State.invalid),
    (500, State.invalid),
    (501, State.invalid),
    (506, State.invalid),
]


@pytest.fixture
def rmock(httpx_mock):
    return httpx_mock
    # with aioresponses() as m:
        # yield m


@pytest.mark.parametrize("status,state", expected_states)
async def test_default_head(status, state, rmock: HTTPXMock):
    # rmock.head(URL, status=status)
    rmock.add_response(url=URL, status_code=status, method="HEAD")
    link = Link(URL)
    async with AsyncChecker() as checker:
        await checker.check(link)

    assert link.state is state



@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False

@pytest.mark.parametrize("status,state", expected_states + [(405, State.invalid)])
async def test_disabled_head(status, state, rmock: HTTPXMock):
    # rmock.head(URL, status=405)
    # rmock.get(URL, status=status)
    rmock.add_response(url=URL, status_code=405, method="HEAD")
    rmock.add_response(url=URL, status_code=status, method="GET")

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


# async def test_slow():
#     link = Link("https://www.ellis-brown.com/")
#     link.timeout = 2
#     async with AsyncChecker() as checker:
#         await checker.check(link)

#     from icecream import ic
#     ic(link)

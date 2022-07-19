import pytest
# from aioresponses import aioresponses
from pytest_httpx import HTTPXMock
from check_link import (
    Link,
    State,
    check_all,
)


@pytest.fixture
def rmock(httpx_mock):
    return httpx_mock
    # with aioresponses() as m:
    #     yield m


def test_check_all(faker, rmock: HTTPXMock):
    url1 = faker.url()
    url2 = faker.url()
    # rmock.head(url1, status=200)
    # rmock.head(url2, status=403)
    rmock.add_response(url=url1, status_code=200, method="HEAD")
    rmock.add_response(url=url2, status_code=403, method="HEAD")

    result = check_all(
        [
            Link(url1),
            Link(url2),
        ]
    )

    assert [l.state for l in result] == [State.available, State.protected]




# def test_slow():
#     link = Link("https://www.ellis-brown.com/")
#     link.timeout = 2
#     result = check_all([link])

#     from icecream import ic
#     ic(result)

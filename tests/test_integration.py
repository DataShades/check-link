import pytest
from aioresponses import aioresponses
from check_link import (
    Link,
    State,
    check_all,
)


@pytest.fixture
def rmock():
    with aioresponses() as m:
        yield m


def test_check_all(faker, rmock: aioresponses):
    url1 = faker.url()
    url2 = faker.url()
    rmock.head(url1, status=200)
    rmock.head(url2, status=403)

    result = check_all(
        [
            Link(url1),
            Link(url2),
        ]
    )

    assert [l.state for l in result] == [State.available, State.protected]

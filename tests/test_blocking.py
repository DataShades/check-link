import pytest
import responses
from check_link import State, Link, BlockingChecker, Option

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


@pytest.mark.parametrize("status,state", expected_states)
@responses.activate()
def test_default_head(status, state):
    responses.mock.head(URL, status=status)
    link = Link(URL)
    with BlockingChecker() as checker:
        checker.check(link)

    assert link.state is state


@pytest.mark.parametrize("status,state", expected_states + [(405, State.broken)])
@responses.activate()
def test_disabled_head(status, state):
    responses.mock.head(URL, status=405)
    responses.mock.get(URL, status=status)
    link = Link(URL)
    checker = BlockingChecker(options=Option.default & ~Option.try_head)
    checker.check(link)
    assert link.state is state

    checker.close()


def test_closed_not_raises():
    with BlockingChecker() as checker:
        pass

    checker.check(Link(URL))

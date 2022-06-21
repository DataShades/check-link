import pytest
from check_link import Link


@pytest.mark.parametrize(
    "link",
    [
        "example.com",
        "http:///exmaple.com",
        "http:example.com",
        "/example/com",
        "http://",
    ],
)
def test_invalid(link):
    with pytest.raises(ValueError):
        Link(link)


@pytest.mark.parametrize(
    "link",
    [
        "https://example.com",
        "https://example.com/path",
        "https://example.com/#anchor",
        "https://example.com/?param=1",
        "https://example.com:80",
    ],
)
def test_valid(link):
    Link(link)

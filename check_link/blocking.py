from __future__ import annotations

from dataclasses import dataclass, field
import requests

from .base import BaseChecker, Link, Option


@dataclass
class BlockingChecker(BaseChecker):
    session: requests.Session = field(default_factory=requests.Session)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _ping(self, link: Link, headers: dict[str, str]) -> requests.Response:
        allow_redirects = bool(self.options & Option.allow_redirects)

        if self.options & Option.try_head:
            resp = self.session.head(
                str(link),
                headers=headers,
                allow_redirects=allow_redirects,
                timeout=link.timeout,
            )
            if resp.status_code != 405:
                return resp

        return self.session.get(
            str(link),
            allow_redirects=allow_redirects,
            headers=headers,
            timeout=link.timeout,
        )

    def check(self, link: Link) -> Link:
        headers = self._headers()
        headers.update(link.headers)

        try:
            resp = self._ping(link, headers)
        except requests.RequestException as e:
            link.state_from_exception(e)
        else:
            link.state_from_code(resp.status_code, resp.reason, resp.headers)

        return link

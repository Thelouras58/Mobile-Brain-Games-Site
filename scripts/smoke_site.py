#!/usr/bin/env python3
"""Read-only production smoke checks with bounded retries."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_PATHS = [
    "/",
    "/games/",
    "/games/pattern-lock-brain-games/",
    "/games/simple-memory-game/",
    "/memory-match/",
    "/flame/",
    "/blog/",
    "/sitemap.xml",
    "/robots.txt",
]


class SmokeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.store_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        if tag.lower() == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonicals.append(values.get("href", ""))
        elif tag.lower() == "meta" and values.get("name", "").lower() == "robots":
            self.robots.append(values.get("content", ""))
        elif tag.lower() == "a":
            href = values.get("href", "")
            if urlparse(href).netloc in {"play.google.com", "apps.apple.com"}:
                self.store_links.append(href)


def fetch(url: str, attempts: int, timeout: float) -> tuple[int, str, str]:
    last_error = ""
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": "mbg-site-monitor/1.0"})
            with urlopen(request, timeout=timeout) as response:
                return response.status, response.geturl(), response.read().decode("utf-8", "replace")
        except HTTPError as exc:
            last_error = f"HTTP {exc.code}"
        except URLError as exc:
            last_error = str(exc.reason)
        if attempt + 1 < attempts:
            time.sleep(2**attempt)
    raise RuntimeError(last_error)


def normalized(url: str) -> str:
    return url.rstrip("/") or url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://mobilebraingames.com")
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("paths", nargs="*", default=DEFAULT_PATHS)
    args = parser.parse_args()
    failures: list[str] = []

    for path in args.paths:
        requested = urljoin(args.base_url.rstrip("/") + "/", path.lstrip("/"))
        try:
            status, final_url, body = fetch(requested, args.attempts, args.timeout)
        except RuntimeError as exc:
            failures.append(f"{requested}: request failed after retries: {exc}")
            continue
        if status != 200:
            failures.append(f"{requested}: expected HTTP 200, got {status}")
            continue
        if not final_url.startswith(args.base_url):
            failures.append(f"{requested}: redirected outside site to {final_url}")
        if not path.endswith((".xml", ".txt")):
            parsed = SmokeParser()
            parsed.feed(body)
            if len(parsed.canonicals) != 1:
                failures.append(f"{requested}: expected one canonical")
            elif normalized(parsed.canonicals[0]) != normalized(final_url):
                failures.append(f"{requested}: expected self-canonical {final_url!r}, got {parsed.canonicals[0]!r}")
            if any("noindex" in value.lower() for value in parsed.robots):
                failures.append(f"{requested}: unexpected noindex")
            for href in parsed.store_links:
                target = urlparse(href)
                if target.scheme != "https":
                    failures.append(f"{requested}: non-HTTPS store link {href}")
        print(f"OK {requested}")

    if failures:
        print(f"Production smoke check failed with {len(failures)} error(s):", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Production smoke check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

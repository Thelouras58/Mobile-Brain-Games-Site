#!/usr/bin/env python3
"""Advisory availability check for external store destinations.

This is intentionally separate from release-blocking rendered-site validation.
"""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import sys
from urllib.parse import urljoin, urlparse

from smoke_site import fetch


DEFAULT_PAGES = [
    "/games/pattern-lock-brain-games/",
    "/games/simple-memory-game/",
    "/games/quick-tap/",
    "/games/processing-speed-training/",
    "/memory-match/",
    "/flame/",
]


class StoreLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href") or ""
        if urlparse(href).netloc in {"play.google.com", "apps.apple.com"}:
            self.links.add(href)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://mobilebraingames.com")
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=15)
    args = parser.parse_args()
    links: set[str] = set()
    failures: list[str] = []

    for path in DEFAULT_PAGES:
        url = urljoin(args.base_url.rstrip("/") + "/", path.lstrip("/"))
        try:
            _, _, body = fetch(url, args.attempts, args.timeout)
        except RuntimeError as exc:
            failures.append(f"{url}: could not collect store links: {exc}")
            continue
        parsed = StoreLinkParser()
        parsed.feed(body)
        links.update(parsed.links)

    for link in sorted(links):
        try:
            status, final_url, _ = fetch(link, args.attempts, args.timeout)
        except RuntimeError as exc:
            failures.append(f"{link}: unavailable after retries: {exc}")
            continue
        if status != 200:
            failures.append(f"{link}: expected 200, got {status}")
        elif urlparse(final_url).netloc not in {"play.google.com", "apps.apple.com"}:
            failures.append(f"{link}: redirected to unexpected destination {final_url}")
        else:
            print(f"OK {link}")

    if failures:
        print("Advisory store check found issues:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Advisory store check passed for {len(links)} destination(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

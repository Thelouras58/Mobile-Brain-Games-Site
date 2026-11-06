#!/usr/bin/env python3
"""Validate rendered SEO metadata, links, assets, and sitemap membership."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlparse
import xml.etree.ElementTree as ET


SITE_ORIGIN = "https://mobilebraingames.com"
IGNORED_SCHEMES = {"mailto", "tel", "javascript", "data"}
ALLOWED_STORES = {"google_play", "app_store"}
ALLOWED_STORE_PLACEMENTS = {
    "app_hero", "app_bottom", "smart_banner", "games_directory", "web_game", "content_link"
}


@dataclass
class Page:
    path: Path
    url: str
    titles: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    canonicals: list[str] = field(default_factory=list)
    robots: list[str] = field(default_factory=list)
    refreshes: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    json_ld: list[str] = field(default_factory=list)
    store_controls: list[dict[str, str]] = field(default_factory=list)
    base_href: str | None = None

    @property
    def is_redirect(self) -> bool:
        return bool(self.refreshes)

    @property
    def is_error(self) -> bool:
        return self.path.name == "404.html"

    @property
    def is_noindex(self) -> bool:
        return any("noindex" in value.lower() for value in self.robots)


class PageParser(HTMLParser):
    def __init__(self, page: Page) -> None:
        super().__init__(convert_charrefs=True)
        self.page = page
        self._in_title = False
        self._title_parts: list[str] = []
        self._json_script = False
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
            self._title_parts = []
        elif tag == "meta":
            name = values.get("name", "").lower()
            equiv = values.get("http-equiv", "").lower()
            if name == "description":
                self.page.descriptions.append(values.get("content", "").strip())
            elif name == "robots":
                self.page.robots.append(values.get("content", "").strip())
            elif equiv == "refresh":
                self.page.refreshes.append(values.get("content", "").strip())
        elif tag == "link":
            rel = {part.lower() for part in values.get("rel", "").split()}
            if "canonical" in rel:
                self.page.canonicals.append(values.get("href", "").strip())
        elif tag == "a" and values.get("href"):
            self.page.links.append(values["href"].strip())
            if values.get("data-store-app"):
                self.page.store_controls.append(values)
        elif tag == "img" and values.get("src"):
            self.page.images.append(values["src"].strip())
        elif tag == "base" and values.get("href"):
            self.page.base_href = values["href"].strip()
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._json_script = True
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title" and self._in_title:
            self.page.titles.append("".join(self._title_parts).strip())
            self._in_title = False
        elif tag == "script" and self._json_script:
            self.page.json_ld.append("".join(self._json_parts).strip())
            self._json_script = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        if self._json_script:
            self._json_parts.append(data)


def output_url(root: Path, path: Path) -> str:
    relative = path.relative_to(root).as_posix()
    if relative == "index.html":
        return f"{SITE_ORIGIN}/"
    if relative.endswith("/index.html"):
        return f"{SITE_ORIGIN}/{relative[:-10]}"
    return f"{SITE_ORIGIN}/{relative}"


def parse_page(root: Path, path: Path) -> Page:
    page = Page(path=path.relative_to(root), url=output_url(root, path))
    parser = PageParser(page)
    parser.feed(path.read_text(encoding="utf-8"))
    return page


def local_path_for_url(root: Path, url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc and parsed.netloc != "mobilebraingames.com":
        return None
    path = unquote(parsed.path or "/").lstrip("/")
    candidate = root / path
    if parsed.path.endswith("/") or not candidate.suffix:
        candidate = candidate / "index.html"
    return candidate


def resolve_reference(page: Page, reference: str) -> str:
    base = urljoin(page.url, page.base_href) if page.base_href else page.url
    return urljoin(base, reference)


def refresh_target(page: Page, value: str) -> str | None:
    parts = value.split(";", 1)
    if len(parts) != 2 or "=" not in parts[1]:
        return None
    key, target = parts[1].split("=", 1)
    if key.strip().lower() != "url":
        return None
    return resolve_reference(page, target.strip().strip("'\""))


def sitemap_urls(root: Path, errors: list[str]) -> set[str]:
    path = root / "sitemap.xml"
    if not path.exists():
        errors.append("sitemap.xml: missing rendered sitemap")
        return set()
    try:
        document = ET.parse(path)
    except ET.ParseError as exc:
        errors.append(f"sitemap.xml: invalid XML: {exc}")
        return set()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {
        (element.text or "").strip().rstrip("/") + "/"
        for element in document.findall(".//s:loc", namespace)
        if (element.text or "").strip()
    }


def validate_site(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"{root}: rendered site directory does not exist"]

    pages = [parse_page(root, path) for path in sorted(root.rglob("*.html"))]
    if not pages:
        return [f"{root}: no rendered HTML pages found"]

    sitemap = sitemap_urls(root, errors)
    canonical_pages: set[str] = set()
    canonical_owners: dict[str, list[str]] = {}

    for page in pages:
        label = page.path.as_posix()
        if len(page.titles) != 1 or not page.titles[0]:
            errors.append(f"{label}: expected one non-empty <title>")

        if page.is_error:
            if not page.is_noindex:
                errors.append(f"{label}: error page must include robots noindex")
        elif page.is_redirect:
            if len(page.canonicals) != 1:
                errors.append(f"{label}: redirect page must declare one destination canonical")
            targets = [refresh_target(page, value) for value in page.refreshes]
            if any(target is None for target in targets):
                errors.append(f"{label}: redirect page has an invalid refresh target")
            elif len(set(targets)) != 1:
                errors.append(f"{label}: redirect page has conflicting refresh targets")
            elif len(page.canonicals) == 1 and targets[0].rstrip("/") != page.canonicals[0].rstrip("/"):
                errors.append(f"{label}: redirect canonical must match refresh target")
            if targets and targets[0]:
                target_path = local_path_for_url(root, targets[0])
                if target_path is not None and not target_path.exists():
                    errors.append(f"{label}: redirect target does not exist: {targets[0]}")
        else:
            if len(page.descriptions) != 1 or not page.descriptions[0]:
                errors.append(f"{label}: expected one non-empty meta description")
            if len(page.canonicals) != 1:
                errors.append(f"{label}: expected one canonical URL")
            elif not page.canonicals[0].startswith(f"{SITE_ORIGIN}/"):
                errors.append(f"{label}: canonical must use {SITE_ORIGIN}")
            elif page.canonicals[0].rstrip("/") != page.url.rstrip("/"):
                errors.append(f"{label}: canonical must be self-referential ({page.url})")
            elif not page.is_noindex:
                canonical = page.canonicals[0].rstrip("/") + "/"
                canonical_pages.add(canonical)
                canonical_owners.setdefault(canonical, []).append(label)

        for index, source in enumerate(page.json_ld, start=1):
            try:
                json.loads(source)
            except json.JSONDecodeError as exc:
                errors.append(f"{label}: JSON-LD block {index} is invalid: {exc.msg}")

        for reference in page.links:
            parsed = urlparse(reference)
            if parsed.scheme in IGNORED_SCHEMES or reference.startswith("#"):
                continue
            resolved = resolve_reference(page, reference)
            target = local_path_for_url(root, resolved)
            if target is not None and not target.exists():
                errors.append(f"{label}: broken internal link {reference!r}")

        for reference in page.images:
            parsed = urlparse(reference)
            if parsed.scheme in {"data", "http", "https"} and parsed.netloc != "mobilebraingames.com":
                continue
            resolved = resolve_reference(page, reference)
            target = local_path_for_url(root, resolved)
            if target is not None and not target.exists():
                errors.append(f"{label}: missing image {reference!r}")

        store_links = []
        for href in page.links:
            parsed = urlparse(href)
            if parsed.netloc == "play.google.com" and parsed.path.startswith("/store/apps/"):
                store_links.append(href)
            elif parsed.netloc == "apps.apple.com" and "/app/" in parsed.path:
                store_links.append(href)
        for href in store_links:
            parsed = urlparse(href)
            if parsed.scheme != "https":
                errors.append(f"{label}: store destination must use HTTPS: {href}")
            if parsed.netloc == "play.google.com" and "/store/apps/details" not in parsed.path:
                errors.append(f"{label}: unexpected Google Play destination: {href}")
        for control in page.store_controls:
            if control.get("data-store", "") not in ALLOWED_STORES:
                errors.append(f"{label}: invalid data-store value on {control.get('href')!r}")
            if control.get("data-store-placement", "") not in ALLOWED_STORE_PLACEMENTS:
                errors.append(f"{label}: invalid data-store-placement on {control.get('href')!r}")
        if label.startswith("games/") and label != "games/index.html" and not store_links:
            errors.append(f"{label}: product page has no recognized app-store destination")

    excluded = {
        page.url.rstrip("/") + "/"
        for page in pages
        if page.is_redirect or page.is_error
    }
    for url in sorted(excluded & sitemap):
        errors.append(f"sitemap.xml: redirect/error URL must be excluded: {url}")
    for url in sorted(canonical_pages - sitemap):
        errors.append(f"sitemap.xml: missing indexable canonical: {url}")
    for url in sorted(sitemap - canonical_pages):
        errors.append(f"sitemap.xml: URL is not an indexable rendered canonical: {url}")
    for url, owners in sorted(canonical_owners.items()):
        if len(owners) > 1:
            errors.append(f"duplicate canonical {url}: {', '.join(owners)}")

    required_standalone = [root / "memory-match" / "index.html", root / "flame" / "index.html"]
    for path in required_standalone:
        if not path.exists():
            errors.append(f"{path.relative_to(root)}: standalone browser game page is missing")
        else:
            source = path.read_text(encoding="utf-8")
            for event in ("store_click", "game_load_start", "game_ready", "game_load_error", "page_path"):
                if event not in source:
                    errors.append(f"{path.relative_to(root)}: missing analytics contract token {event!r}")
            if "game_start" in source:
                errors.append(f"{path.relative_to(root)}: must not report game_start from page loading")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, default=Path("_site"))
    args = parser.parse_args()
    errors = validate_site(args.site.resolve())
    if errors:
        print(f"Rendered-site validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Rendered-site validation passed: {args.site}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

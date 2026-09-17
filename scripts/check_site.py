"""Check rendered Jekyll pages for search and navigation regressions."""
from __future__ import annotations

import json
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "_site"
ORIGIN = "https://mobilebraingames.com"


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.h1_count = 0
        self.description = ""
        self.canonical = ""
        self.lang = ""
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.images: list[dict[str, str]] = []
        self.schemas: list[dict] = []
        self.in_title = False
        self.in_script = False
        self.script = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang") or ""
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content") or ""
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href") or ""
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_script = True
            self.script = ""

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
        if self.in_script:
            self.script += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_script:
            self.schemas.append(json.loads(self.script))
            self.in_script = False


def local_file(path: str) -> Path:
    decoded = urllib.parse.unquote(path)
    if decoded.endswith("/"):
        decoded += "index.html"
    return ROOT / decoded.lstrip("/")


def main() -> int:
    sitemap = ET.parse(ROOT / "sitemap.xml")
    urls = [node.text for node in sitemap.iter() if node.tag.endswith("loc") and node.text]
    assert urls, "Sitemap is empty"
    pages: dict[str, Page] = {}
    errors: list[str] = []
    for url in urls:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "mobilebraingames.com":
            errors.append(f"Unexpected sitemap URL: {url}")
            continue
        path = parsed.path
        file = local_file(path)
        if not file.is_file():
            errors.append(f"Missing sitemap page: {file}")
            continue
        page = Page()
        try:
            page.feed(file.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON-LD in {path}: {exc}")
            continue
        pages[path] = page
        if page.title.strip() == "" or page.description.strip() == "":
            errors.append(f"Missing title or description: {path}")
        if page.canonical != url:
            errors.append(f"Canonical mismatch: {path}: {page.canonical}")
        if path != "/memory-match/" and (page.h1_count != 1 or page.lang != "en"):
            errors.append(f"Expected one H1 and English language: {path}")
        if path != "/memory-match/" and not page.schemas:
            errors.append(f"Missing JSON-LD: {path}")
        for img in page.images:
            if "alt" not in img:
                errors.append(f"Image missing alt attribute: {path}: {img.get('src')}")
        if path.startswith("/games/") and path != "/games/":
            nodes = [item for schema in page.schemas for item in schema.get("@graph", [])]
            app = next((item for item in nodes if item.get("@type") == "SoftwareApplication"), None)
            if app is None or app.get("offers", {}).get("price") != 0:
                errors.append(f"Missing free-install app offer: {path}")

    for path, page in pages.items():
        for href in page.links:
            target = urllib.parse.urlparse(urllib.parse.urljoin(ORIGIN + path, href))
            if target.netloc != "mobilebraingames.com":
                continue
            if not local_file(target.path).is_file():
                errors.append(f"Broken internal link on {path}: {href}")
            if target.fragment and target.path in pages:
                if urllib.parse.unquote(target.fragment) not in pages[target.path].ids:
                    errors.append(f"Broken fragment on {path}: {href}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Checked {len(pages)} sitemap pages, JSON-LD, metadata, and internal links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

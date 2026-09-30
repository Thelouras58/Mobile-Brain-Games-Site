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
        self.refresh = ""
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
        if tag == "meta" and (attrs.get("http-equiv") or "").lower() == "refresh":
            self.refresh = attrs.get("content") or ""
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
    seen_titles: dict[str, str] = {}
    seen_descriptions: dict[str, str] = {}
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
        if page.h1_count != 1 or page.lang != "en":
            errors.append(f"Expected one H1 and English language: {path}")
        if not page.schemas:
            errors.append(f"Missing JSON-LD: {path}")
        title = page.title.strip()
        description = page.description.strip()
        if title in seen_titles:
            errors.append(f"Duplicate title on {path} and {seen_titles[title]}: {title}")
        else:
            seen_titles[title] = path
        if description in seen_descriptions:
            errors.append(
                f"Duplicate description on {path} and {seen_descriptions[description]}: {description}"
            )
        else:
            seen_descriptions[description] = path
        for img in page.images:
            if "alt" not in img:
                errors.append(f"Image missing alt attribute: {path}: {img.get('src')}")
            src = img.get("src", "")
            parsed_src = urllib.parse.urlparse(src)
            if src and not parsed_src.netloc and not local_file(parsed_src.path).is_file():
                errors.append(f"Missing local image on {path}: {src}")

        nodes = [item for schema in page.schemas for item in schema.get("@graph", [])]
        if path == "/blog/":
            collection = next((item for item in nodes if item.get("@type") == "CollectionPage"), None)
            breadcrumbs = next((item for item in nodes if item.get("@type") == "BreadcrumbList"), None)
            crumbs = breadcrumbs.get("itemListElement", []) if breadcrumbs else []
            if collection is None or len(crumbs) != 2:
                errors.append("Blog index must use CollectionPage and Home > Blog breadcrumbs")
        elif path.startswith("/blog/"):
            article = next((item for item in nodes if item.get("@type") == "BlogPosting"), None)
            if article is None or not article.get("datePublished") or not article.get("dateModified"):
                errors.append(f"Blog article missing dated BlogPosting schema: {path}")
        if path == "/memory-match/":
            web_app = next((item for item in nodes if item.get("@type") == "WebApplication"), None)
            if web_app is None or web_app.get("offers", {}).get("price") != 0:
                errors.append("Memory Match must expose a free WebApplication schema")
        if path.startswith("/games/") and path != "/games/":
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

    incoming = {path: 0 for path in pages}
    for path, page in pages.items():
        for href in page.links:
            target = urllib.parse.urlparse(urllib.parse.urljoin(ORIGIN + path, href))
            if target.netloc == "mobilebraingames.com" and target.path in incoming:
                incoming[target.path] += 1
    for path, count in incoming.items():
        is_discovery_page = (
            (path.startswith("/games/") and path != "/games/")
            or (path.startswith("/blog/") and path != "/blog/")
            or path == "/memory-match/"
        )
        if is_discovery_page and count == 0:
            errors.append(f"Discovery page has no internal links: {path}")

    redirects = {
        "/guides/": "/blog/",
        "/guides/card-matching-games-for-kids/": "/blog/card-matching-games-for-kids/",
        "/guides/pattern-memory-games/": "/blog/pattern-memory-games/",
        "/guides/quick-reaction-games/": "/blog/quick-reaction-games/",
        "/simplememorygameforkids/": "/memory-match/",
        "/numbergameforkids/": "/games/quick-maths/",
        "/about/": "/#about",
    }
    sitemap_paths = set(pages)
    for source, destination in redirects.items():
        if source in sitemap_paths:
            errors.append(f"Redirect alias must not appear in sitemap: {source}")
        file = local_file(source)
        if not file.is_file():
            errors.append(f"Missing generated redirect page: {source}")
            continue
        redirect_page = Page()
        redirect_page.feed(file.read_text())
        destination_url = urllib.parse.urljoin(ORIGIN + source, destination)
        if redirect_page.canonical != destination_url:
            errors.append(
                f"Redirect canonical mismatch: {source}: {redirect_page.canonical} != {destination_url}"
            )
        if not redirect_page.refresh.startswith("0;"):
            errors.append(f"Redirect must use an immediate refresh: {source}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"Checked {len(pages)} sitemap pages, semantic JSON-LD, unique metadata, "
        f"internal discovery, local images, and {len(redirects)} redirects"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

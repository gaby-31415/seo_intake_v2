"""Sitemap ingestion helpers."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List, Tuple
from urllib.parse import urlparse


def _is_malformed_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return True
    if not parsed.netloc:
        return True
    path = parsed.path or ""
    if path.startswith("/http") or "/https/" in path:
        return True
    return False


def parse_sitemap(sitemap_xml: bytes) -> Tuple[List[str], List[str]]:
    """Parse sitemap XML bytes into a list of URLs and excluded URLs."""

    root = ET.fromstring(sitemap_xml)
    urls: List[str] = []
    excluded: List[str] = []
    for url in root.findall(".//{*}url/{*}loc"):
        if url.text:
            loc = url.text.strip()
            if _is_malformed_url(loc):
                excluded.append(loc)
            else:
                urls.append(loc)
    return urls, excluded


def split_item_urls(urls: List[str]) -> Tuple[List[str], List[str]]:
    """Split URLs into item and non-item collections."""

    item_urls = [url for url in urls if "/items/" in url]
    non_item_urls = [url for url in urls if "/items/" not in url]
    return item_urls, non_item_urls

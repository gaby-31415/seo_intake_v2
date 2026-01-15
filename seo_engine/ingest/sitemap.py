"""Sitemap ingestion helpers."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List, Tuple


def parse_sitemap(sitemap_xml: bytes) -> List[str]:
    """Parse sitemap XML bytes into a list of URLs."""

    root = ET.fromstring(sitemap_xml)
    urls: List[str] = []
    for url in root.findall(".//{*}url/{*}loc"):
        if url.text:
            urls.append(url.text.strip())
    return urls


def split_item_urls(urls: List[str]) -> Tuple[List[str], List[str]]:
    """Split URLs into item and non-item collections."""

    item_urls = [url for url in urls if "/items/" in url]
    non_item_urls = [url for url in urls if "/items/" not in url]
    return item_urls, non_item_urls

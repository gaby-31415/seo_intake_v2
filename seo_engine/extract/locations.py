"""Location extraction utilities."""

from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup


def _clean_text(text: str | None) -> str:
    return "" if text is None else " ".join(text.split())


def extract_locations(html_files: List[bytes]) -> List[Dict[str, Any]]:
    """Extract locations from HTML files.

    Expected pattern:
    - span.location-name
    - address spans
    - tel/mailto links
    """

    locations: List[Dict[str, Any]] = []
    for html in html_files:
        soup = BeautifulSoup(html, "lxml")
        for name_span in soup.select("span.location-name"):
            container = name_span.find_parent()
            address_lines = []
            if container:
                address = container.find("address")
                if address:
                    for span in address.find_all("span"):
                        line = _clean_text(span.get_text())
                        if line:
                            address_lines.append(line)
            tel_link = None
            mail_link = None
            if container:
                tel_link = container.find("a", href=lambda href: href and href.startswith("tel:"))
                mail_link = container.find("a", href=lambda href: href and href.startswith("mailto:"))
            phone = _clean_text(tel_link.get_text()) if tel_link else ""
            email = ""
            if mail_link and mail_link.get("href"):
                email = mail_link["href"].replace("mailto:", "")
            locations.append(
                {
                    "name": _clean_text(name_span.get_text()),
                    "address": address_lines,
                    "phone": phone,
                    "email": email,
                }
            )
    return locations

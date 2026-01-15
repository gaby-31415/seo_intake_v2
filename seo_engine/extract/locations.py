"""Location extraction utilities."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from bs4 import BeautifulSoup


def _clean_text(text: str | None) -> str:
    return "" if text is None else " ".join(text.split())


def _parse_city_state_zip(text: str) -> Tuple[str, str, str]:
    cleaned = _clean_text(text)
    match = re.match(
        r"^(?P<city>.*?),\s*(?P<region>[A-Za-z]{2})\s+(?P<postal>\d{5}(?:-\d{4})?)$",
        cleaned,
    )
    if not match:
        return "", "", ""
    return (
        match.group("city").strip(),
        match.group("region").upper(),
        match.group("postal"),
    )


def _find_city_state_zip(address_lines: List[str]) -> Tuple[str, str, str, str]:
    for line in reversed(address_lines):
        city, region, postal = _parse_city_state_zip(line)
        if city and region and postal:
            return line, city, region, postal
    return "", "", "", ""


def _confidence_level(street: str, city: str, region: str, postal: str) -> str:
    has_street = bool(street)
    has_city_region = bool(city and region)
    has_city_postal = bool(city and postal)
    has_full = bool(city and region and postal)
    if has_street and has_full:
        return "high"
    if has_street and (has_city_region or has_city_postal):
        return "medium"
    return "low"


def extract_locations(html_files: List[bytes]) -> List[Dict[str, Any]]:
    """Extract locations from HTML files.

    Expected pattern:
    - span.location-name
    - address spans
    - tel/mailto links
    """

    locations: List[Dict[str, Any]] = []
    for html in html_files:
        soup = BeautifulSoup(html, "html.parser")
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
            street = address_lines[0] if address_lines else ""
            city_state_zip, city, region, postal = _find_city_state_zip(address_lines)
            full_address = ""
            if street and city and region and postal:
                full_address = f"{street}, {city}, {region} {postal}"
            locations.append(
                {
                    "name": _clean_text(name_span.get_text()),
                    "address": address_lines,
                    "city_state_zip": city_state_zip,
                    "city": city,
                    "region": region,
                    "postal": postal,
                    "full_address": full_address,
                    "confidence": _confidence_level(street, city, region, postal),
                    "phone": phone,
                    "email": email,
                }
            )
    return locations

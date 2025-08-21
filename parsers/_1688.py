import json
import re
from typing import Any, Dict

import requests


class ParsingError(Exception):
    """Raised when a product page cannot be parsed."""


def _extract_json(html: str) -> Dict[str, Any]:
    pattern = re.compile(r"window\.__INIT_DATA__\s*=\s*(\{.*?\})\s*;", re.S)
    match = pattern.search(html)
    if not match:
        raise ParsingError("Product data JSON not found")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ParsingError("Invalid product JSON") from exc


def parse_1688_product(url: str) -> Dict[str, Any]:
    """Fetch and parse product information from 1688.

    Parameters
    ----------
    url: str
        Product page URL.

    Returns
    -------
    dict
        Parsed product data containing name, price, images and delivery info.

    Raises
    ------
    ParsingError
        If the page cannot be retrieved or parsed.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ParsingError(f"Could not fetch {url}") from exc

    data = _extract_json(response.text)

    name = data.get("name") or data.get("title")
    price = data.get("sku", {}).get("price") or data.get("price")
    images = data.get("images") or data.get("gallery", [])
    delivery = data.get("delivery", {})

    return {
        "name": name,
        "price": price,
        "images": images,
        "delivery": delivery,
    }

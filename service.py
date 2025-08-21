"""Simple service for building product cards."""
from parsers._1688 import parse_1688_product


def build_product_card(url: str) -> dict:
    """Build a product card by fetching and parsing 1688 product data."""
    data = parse_1688_product(url)
    return {
        "title": data["name"],
        "price": data["price"],
        "images": data["images"],
        "delivery": data["delivery"],
    }

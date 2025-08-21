import pathlib

import requests

from parsers._1688 import parse_1688_product, ParsingError


class DummyResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(self.status_code)


def fake_get_factory(text: str, status_code: int = 200):
    def _get(url, timeout=10):
        return DummyResponse(text, status_code)
    return _get


def test_parse_product_example_1(monkeypatch):
    html = pathlib.Path("tests/data/1688_product1.html").read_text()
    monkeypatch.setattr(requests, "get", fake_get_factory(html))
    data = parse_1688_product("http://example.com/product1")
    assert data["name"] == "Sample Product A"
    assert data["price"] == "10.00"
    assert data["images"] == ["a1.jpg", "a2.jpg"]
    assert data["delivery"]["shipsFrom"] == "China"


def test_parse_product_example_2(monkeypatch):
    html = pathlib.Path("tests/data/1688_product2.html").read_text()
    monkeypatch.setattr(requests, "get", fake_get_factory(html))
    data = parse_1688_product("http://example.com/product2")
    assert data["name"] == "Sample Product B"
    assert data["price"] == "20.00"
    assert data["images"] == ["b1.jpg"]
    assert data["delivery"]["minOrder"] == 5


def test_network_error(monkeypatch):
    def _get(url, timeout=10):
        raise requests.RequestException("boom")
    monkeypatch.setattr(requests, "get", _get)
    try:
        parse_1688_product("http://example.com/error")
    except ParsingError:
        pass
    else:
        assert False, "ParsingError was not raised"


def test_invalid_structure(monkeypatch):
    html = "<html><body></body></html>"
    monkeypatch.setattr(requests, "get", fake_get_factory(html))
    try:
        parse_1688_product("http://example.com/invalid")
    except ParsingError:
        pass
    else:
        assert False, "ParsingError was not raised for invalid HTML"

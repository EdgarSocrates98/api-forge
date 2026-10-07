from pathlib import Path

from apiforge.adapters.fastapi.extractor import extract_fastapi

ROOT = Path("tests/fixtures/fastapi_orders")


def test_resolves_router_and_include_prefixes() -> None:
    inventory = extract_fastapi(ROOT)
    routes = [(f.measures["method"], f.measures["path"]) for f in inventory.facts]
    assert ("get", "/v1/orders/{order_id}") in routes


def test_preserves_duplicate_route_facts() -> None:
    inventory = extract_fastapi(ROOT)
    posts = [f for f in inventory.facts if f.measures == {"method": "post", "path": "/v1/orders"}]
    assert len(posts) == 2
    assert posts[0].fact_id != posts[1].fact_id


def test_dynamic_path_is_named_unresolved() -> None:
    inventory = extract_fastapi(ROOT)
    assert any(d.code == "AF-FASTAPI-DYNAMIC-ROUTE" for d in inventory.diagnostics)


def test_trailing_slash_routes_are_distinct() -> None:
    inventory = extract_fastapi(ROOT)
    paths = [f.measures["path"] for f in inventory.facts]
    assert "/v1/orders/" in paths
    assert "/v1/orders" in paths  # the two post("") handlers


def test_every_python_file_is_hashed() -> None:
    inventory = extract_fastapi(ROOT)
    scanned = {
        "app/__init__.py",
        "app/main.py",
        "app/routes/__init__.py",
        "app/routes/orders.py",
        "app/routes/hidden.py",
        "app/utils.py",
    }
    assert scanned <= set(inventory.input_hashes)
    assert all(len(sha) == 64 for sha in inventory.input_hashes.values())


def test_unreachable_router_is_marked() -> None:
    inventory = extract_fastapi(ROOT)
    secret = [f for f in inventory.facts if f.measures["path"] == "/secret"]
    assert len(secret) == 1
    assert secret[0].attrs["reachable"] is False
    included = [f for f in inventory.facts if f.measures["path"] == "/v1/orders/"]
    assert all(f.attrs["reachable"] is True for f in included)


def test_facts_are_sorted_and_have_source() -> None:
    inventory = extract_fastapi(ROOT)
    keys = [
        (f.measures["path"], f.measures["method"], f.source.path, f.source.line)
        for f in inventory.facts
    ]
    assert keys == sorted(keys)
    for fact in inventory.facts:
        assert fact.source.sha256 == inventory.input_hashes[fact.source.path]
        assert fact.kind == "code.route"


def test_handler_metadata_lives_in_attrs() -> None:
    inventory = extract_fastapi(ROOT)
    get_order = next(f for f in inventory.facts if f.measures["path"] == "/v1/orders/{order_id}")
    assert get_order.attrs["function"] == "get_order"
    assert get_order.attrs["router"] == "router"
    assert get_order.measures == {"method": "get", "path": "/v1/orders/{order_id}"}

from pathlib import Path

import pytest

from apiforge.context.gateway.errors import GatewayError
from apiforge.context.gateway.refs import CtxStore


def test_put_then_get_round_trips_with_verification(tmp_path: Path) -> None:
    store = CtxStore(tmp_path)
    uri = store.put("Order:\r\n  type: object\r\n")
    assert store.exists(uri)
    assert store.get(uri) == "Order:\n  type: object\n"
    assert store.put("Order:\n  type: object\n") == uri


def test_tampered_object_is_refused_without_content(tmp_path: Path) -> None:
    store = CtxStore(tmp_path)
    uri = store.put("original")
    (store.dir / uri.removeprefix("ctx://sha256/")).write_text("tampered", encoding="utf-8")
    with pytest.raises(GatewayError) as error:
        store.get(uri)
    assert error.value.code == "AF-CTX-HASH-MISMATCH"
    assert error.value.field == "uri"
    assert "rebuild" in error.value.unlock


def test_missing_object_is_refused(tmp_path: Path) -> None:
    with pytest.raises(GatewayError) as error:
        CtxStore(tmp_path).get("ctx://sha256/" + "0" * 64)
    assert error.value.code == "AF-CTX-REF-NOT-FOUND"


@pytest.mark.parametrize("uri", ["bad", "ctx://sha256/../../secret", "ctx://sha256/" + "A" * 64])
def test_malformed_uri_never_touches_the_filesystem(tmp_path: Path, uri: str) -> None:
    with pytest.raises(GatewayError) as error:
        CtxStore(tmp_path).get(uri)
    assert error.value.code == "AF-CTX-REF-INVALID"

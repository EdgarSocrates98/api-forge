from apiforge.context.gateway.canonical import digest, dumps, normalize, uri_for


def test_dumps_is_key_order_independent() -> None:
    assert dumps({"b": 1, "a": [2, {"d": 3, "c": 4}]}) == dumps(
        {"a": [2, {"c": 4, "d": 3}], "b": 1}
    )


def test_crlf_and_lf_content_share_one_uri() -> None:
    assert uri_for("line one\r\nline two\r\n") == uri_for("line one\nline two\n")
    assert normalize("a\rb") == "a\nb"


def test_uri_embeds_sha256_of_normalized_text() -> None:
    assert uri_for("x") == "ctx://sha256/" + digest("x")
    assert len(digest("x")) == 64

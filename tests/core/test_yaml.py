from pathlib import Path

import pytest

from apiforge.core.io import text_sha256
from apiforge.core.yaml import (
    StrictYamlError,
    load_yaml_mapping,
    load_yaml_strict,
    split_frontmatter,
)


def test_rejects_alias() -> None:
    with pytest.raises(StrictYamlError, match="AF-YAML-ALIAS"):
        load_yaml_strict("a: &x 1\nb: *x\n", source="inline")


def test_rejects_duplicate_key() -> None:
    with pytest.raises(StrictYamlError, match="AF-YAML-DUPLICATE-KEY"):
        load_yaml_strict("a: 1\na: 2\n", source="inline")


def test_rejects_merge_key() -> None:
    with pytest.raises(StrictYamlError, match="AF-YAML-MERGE-KEY"):
        load_yaml_strict("merged: {<<: {a: 1}}\n", source="inline")


def test_rejects_custom_tag() -> None:
    with pytest.raises(StrictYamlError, match="AF-YAML-CUSTOM-TAG"):
        load_yaml_strict("a: !secret x\n", source="inline")


def test_mapping_helper_rejects_sequence() -> None:
    with pytest.raises(StrictYamlError, match="AF-YAML-NOT-MAPPING"):
        load_yaml_mapping("- a\n- b\n", source="inline")


def test_frontmatter_tolerates_utf8_bom() -> None:
    block, body = split_frontmatter("﻿---\nkey: 1\n---\nbody\n")
    assert block == "key: 1\n"
    assert body == "body\n"


def test_frontmatter_without_fence_returns_none() -> None:
    block, body = split_frontmatter("# just a doc\ncontent\n")
    assert block is None
    assert body == "# just a doc\ncontent\n"


def test_frontmatter_unclosed_returns_none() -> None:
    block, body = split_frontmatter("---\nkey: 1\nno closing fence\n")
    assert block is None
    assert body == "---\nkey: 1\nno closing fence\n"


def test_frontmatter_crlf() -> None:
    block, body = split_frontmatter("---\r\nkey: 1\r\n---\r\nbody\r\n")
    assert block == "key: 1\n"
    assert body == "body\n"


def test_text_sha256_normalizes_crlf(tmp_path: Path) -> None:
    lf = tmp_path / "lf.md"
    crlf = tmp_path / "crlf.md"
    lf.write_bytes(b"a\nb\n")
    crlf.write_bytes(b"a\r\nb\r\n")
    assert text_sha256(lf) == text_sha256(crlf)

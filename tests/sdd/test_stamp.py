from pathlib import Path

import pytest

from apiforge.core.io import text_sha256
from apiforge.sdd.stamp import SddError, stamp

UPSTREAM = """\
---
sdd: 1
feature: X
phase: discover
profile: standard
status: ready
---
# Discover
"""

TARGET = """\
---
sdd: 1
feature: X
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "0"
---
# Intent
"""


def test_stamp_writes_only_upstream_line(tmp_path: Path) -> None:
    upstream = tmp_path / "discover.md"
    target = tmp_path / "intent.md"
    upstream.write_text(UPSTREAM, encoding="utf-8")
    target.write_text(TARGET, encoding="utf-8")
    before_lines = target.read_text(encoding="utf-8").split("\n")

    result = stamp(target, upstream)

    assert result.changed is True
    assert result.sha256 == text_sha256(upstream)
    after_lines = target.read_text(encoding="utf-8").split("\n")
    assert len(after_lines) == len(before_lines)
    changed = [(b, a) for b, a in zip(before_lines, after_lines, strict=True) if b != a]
    assert changed == [('  sha256: "0"', f'  sha256: "{result.sha256}"')]


def test_stamp_without_upstream_block_inserts_before_fence(tmp_path: Path) -> None:
    upstream = tmp_path / "discover.md"
    target = tmp_path / "intent.md"
    upstream.write_text(UPSTREAM, encoding="utf-8")
    target.write_text(
        TARGET.replace('upstream:\n  path: discover.md\n  sha256: "0"\n', ""), encoding="utf-8"
    )
    result = stamp(target, upstream)
    assert result.changed is True
    assert result.previous is None
    text = target.read_text(encoding="utf-8")
    assert "upstream:\n" in text and result.sha256 in text


def test_stamp_unchanged_when_hash_matches(tmp_path: Path) -> None:
    upstream = tmp_path / "discover.md"
    target = tmp_path / "intent.md"
    upstream.write_text(UPSTREAM, encoding="utf-8")
    target.write_text(TARGET, encoding="utf-8")
    stamp(target, upstream)
    result = stamp(target, upstream)
    assert result.changed is False


def test_stamp_refuses_missing_frontmatter(tmp_path: Path) -> None:
    upstream = tmp_path / "discover.md"
    target = tmp_path / "intent.md"
    upstream.write_text(UPSTREAM, encoding="utf-8")
    target.write_text("# bare\n", encoding="utf-8")
    with pytest.raises(SddError, match="AF-SDD-STAMP"):
        stamp(target, upstream)


def test_stamp_refuses_missing_upstream(tmp_path: Path) -> None:
    target = tmp_path / "intent.md"
    target.write_text(TARGET, encoding="utf-8")
    with pytest.raises(SddError, match="AF-SDD-STAMP"):
        stamp(target, tmp_path / "absent.md")

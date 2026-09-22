"""Spec I — knowledge packs: closed schema, source authority, catalog cross-check."""

from __future__ import annotations

from pathlib import Path

import pytest

from apiforge.knowledge.loader import KnowledgeError, check_packs, load_pack, load_packs

ROOT = Path("knowledge")


def _write_pack(base: Path, domain: str, pack: str, auth: str | None) -> Path:
    d = base / domain
    d.mkdir(parents=True)
    (d / "pack.yaml").write_text(pack, encoding="utf-8")
    if auth is not None:
        (d / "source_authority.yaml").write_text(auth, encoding="utf-8")
    return d


_GOOD_AUTH = """sources:
  - name: RFC 9110
    url: https://www.rfc-editor.org/rfc/rfc9110
    authority: ietf-rfc
    verified: "2026-09-21"
"""


def test_shipped_packs_all_validate() -> None:
    result = check_packs(ROOT)
    assert result["ok"], result["problems"]
    assert result["count"] >= 8


def test_pack_domain_must_match_dir(tmp_path: Path) -> None:
    d = _write_pack(
        tmp_path,
        "real-dir",
        'domain: other-name\nversion: 1\nareas: []\nrule_ids: []\n',
        _GOOD_AUTH,
    )
    with pytest.raises(KnowledgeError, match="AF-KNOW-DOMAIN"):
        load_pack(d)


def test_missing_authority_is_refused(tmp_path: Path) -> None:
    d = _write_pack(
        tmp_path,
        "no-auth",
        'domain: no-auth\nversion: 1\nareas: []\nrule_ids: []\n',
        None,
    )
    with pytest.raises(KnowledgeError, match="AF-KNOW-NO-AUTHORITY"):
        load_pack(d)


def test_unknown_authority_class_refused(tmp_path: Path) -> None:
    d = _write_pack(
        tmp_path,
        "bad-auth",
        'domain: bad-auth\nversion: 1\nareas: []\nrule_ids: []\n',
        """sources:
  - name: blog
    url: https://example.com
    authority: random-blog
    verified: "2026-09-21"
""",
    )
    with pytest.raises(KnowledgeError, match="AF-KNOW-AUTHORITY"):
        load_pack(d)


def test_unknown_rule_id_named(tmp_path: Path) -> None:
    _write_pack(
        tmp_path,
        "ghost-rule",
        'domain: ghost-rule\nversion: 1\nareas: [REST]\nrule_ids: [AF-REST-999]\n',
        _GOOD_AUTH,
    )
    result = check_packs(tmp_path)
    assert not result["ok"]
    assert "AF-REST-999" in result["problems"][0]


def test_matrix_and_evals_parsed() -> None:
    pack = load_pack(ROOT / "spring-boot")
    assert pack.matrix and pack.matrix[0]["component"] == "java"
    owasp = load_pack(ROOT / "owasp-api-2023")
    assert len(owasp.evals) == 2
    assert owasp.evals[0]["expect"]["id"] == "AF-SEC-001"


def test_every_pack_source_has_a_date() -> None:
    for pack in load_packs(ROOT).values():
        assert pack.sources, pack.domain
        for source in pack.sources:
            assert source.verified and source.authority


def test_eval_type_outside_closed_set_refused(tmp_path: Path) -> None:
    """AT-006: an eval with type 'vibes' is refused with AF-KNOW-EVAL-TYPE."""
    d = _write_pack(
        tmp_path,
        "bad-eval",
        'domain: bad-eval\nversion: 1\nareas: []\nrule_ids: []\n',
        _GOOD_AUTH,
    )
    (d / "evals.yaml").write_text(
        'evals:\n'
        '  - id: bad-eval/probe\n'
        '    prompt: "x"\n'
        '    type: vibes\n'
        '    expect: {kind: rule, id: AF-REST-001}\n',
        encoding="utf-8",
    )
    with pytest.raises(KnowledgeError, match="AF-KNOW-EVAL-TYPE"):
        load_pack(d)


def test_eval_type_required_and_valid(tmp_path: Path) -> None:
    d = _write_pack(
        tmp_path,
        "typed-eval",
        'domain: typed-eval\nversion: 1\nareas: []\nrule_ids: []\n',
        _GOOD_AUTH,
    )
    (d / "evals.yaml").write_text(
        'evals:\n'
        '  - id: typed-eval/probe\n'
        '    prompt: "x"\n'
        '    type: regression\n'
        '    expect: {kind: rule, id: AF-REST-001}\n',
        encoding="utf-8",
    )
    pack = load_pack(d)
    assert pack.evals[0]["type"] == "regression"
    # missing type is also a refusal
    (d / "evals.yaml").write_text(
        'evals:\n  - id: p\n    prompt: "x"\n    expect: {kind: rule, id: AF-REST-001}\n',
        encoding="utf-8",
    )
    with pytest.raises(KnowledgeError, match="AF-KNOW-SCHEMA"):
        load_pack(d)


def test_shipped_eval_types_all_in_closed_set() -> None:
    from apiforge.knowledge.loader import EVAL_TYPES

    for pack in load_packs(ROOT).values():
        for e in pack.evals:
            assert e["type"] in EVAL_TYPES, (pack.domain, e["id"])

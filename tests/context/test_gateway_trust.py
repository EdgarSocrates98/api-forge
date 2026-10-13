"""Case integrity and source containment for the Context Gateway and evidence refs."""

import json
from pathlib import Path

import pytest

from apiforge.context.gateway.capsule import build_capsule
from apiforge.context.gateway.errors import GatewayError
from apiforge.context.gateway.refs import CtxStore
from apiforge.core.io import sha256_file
from apiforge.evidence.resolve import resolve
from tests.context.gateway_support import analyzed_root


def _facts(root: Path) -> tuple[Path, dict]:
    path = root / ".apiforge" / "case" / "facts.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def _rehash(root: Path) -> None:
    """Simulate a consistent adversarial case: artifacts edited and re-hashed."""
    case_dir = root / ".apiforge" / "case"
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    for ref in manifest["artifacts"].values():
        ref["sha256"] = sha256_file(case_dir / ref["path"])
    (case_dir / "case.json").write_text(json.dumps(manifest), encoding="utf-8")


def _poison_handler_paths(root: Path, value: str) -> str:
    path, data = _facts(root)
    poisoned = ""
    for fact in data["facts"]:
        source = fact.get("source") or {}
        if fact.get("kind") == "code.route" and source.get("path"):
            source["path"] = value
            poisoned = str(fact["fact_id"])
    path.write_text(json.dumps(data), encoding="utf-8")
    return poisoned


def test_facts_edited_after_manifest_refuse_the_capsule(tmp_path: Path) -> None:
    root = analyzed_root(tmp_path)
    path, data = _facts(root)
    path.write_text(json.dumps(data) + " ", encoding="utf-8")
    with pytest.raises(GatewayError) as err:
        build_capsule(root, "POST /payments")
    assert err.value.code == "AF-CASE-HASH-MISMATCH"
    assert err.value.field == "case"


@pytest.mark.parametrize("value", ["../secret.txt", "/etc/passwd", "\\\\host\\share\\x.py"])
def test_poisoned_source_path_is_refused_per_ref_and_never_stored(
    tmp_path: Path, value: str
) -> None:
    root = analyzed_root(tmp_path)
    (root.parent / "secret.txt").write_text("TOP-SECRET-TOKEN\n", encoding="utf-8")
    _poison_handler_paths(root, value)
    _rehash(root)
    capsule = build_capsule(root, "POST /payments")
    assert any(item.startswith("AF-PATH-OUTSIDE-ROOT") for item in capsule.unresolved)
    assert "operation:POST /payments" in {ref.label for ref in capsule.refs}
    store = CtxStore(root)
    for ref in capsule.refs:
        assert "TOP-SECRET-TOKEN" not in (store.get(ref.uri) or "")


def test_poisoned_project_input_is_refused(tmp_path: Path) -> None:
    root = analyzed_root(tmp_path)
    case_json = root / ".apiforge" / "case" / "case.json"
    manifest = json.loads(case_json.read_text(encoding="utf-8"))
    manifest["inputs"]["project"] = "../.."
    case_json.write_text(json.dumps(manifest), encoding="utf-8")
    capsule = build_capsule(root, "POST /payments")
    assert any(item.startswith("AF-PATH-OUTSIDE-ROOT") for item in capsule.unresolved)
    assert not any(ref.label.startswith("handler:") for ref in capsule.refs)


def test_evidence_resolve_refuses_out_of_root_fact_source(tmp_path: Path) -> None:
    root = analyzed_root(tmp_path)
    (root.parent / "secret.txt").write_text("TOP-SECRET-TOKEN\n", encoding="utf-8")
    fact_id = _poison_handler_paths(root, "../secret.txt")
    _rehash(root)
    node = resolve(root, f"evidence://fact/{fact_id}")
    assert node.source_ref is None
    assert any(item.startswith("AF-PATH-OUTSIDE-ROOT") for item in node.unresolved)

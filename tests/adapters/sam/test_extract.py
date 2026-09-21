"""SAM extractor: Serverless resources as facts, intrinsics as named diagnostics."""

from pathlib import Path

from apiforge.adapters.sam.extract import extract_sam

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "sam" / "template.yaml"


def test_function_and_api_facts() -> None:
    inv = extract_sam(FIXTURE)
    kinds = {f.kind for f in inv.facts}
    assert kinds == {"sam.function", "sam.api"}
    fn = next(f for f in inv.facts if f.kind == "sam.function")
    assert fn.attrs["runtime"] == "python3.12"
    assert fn.attrs["memory_mb"] == 256
    assert fn.attrs["api_events"] == ({"event": "CreateOrder", "path": "/orders", "method": "post"},)
    api = next(f for f in inv.facts if f.kind == "sam.api")
    assert api.attrs["stage_name"] == "prod"
    assert api.attrs["has_auth"] is True


def test_intrinsic_is_unresolved_never_resolved() -> None:
    inv = extract_sam(FIXTURE)
    fn = next(f for f in inv.facts if f.kind == "sam.function")
    assert fn.attrs["timeout_s"] is None  # !Ref not inferred
    assert any(
        d.code == "AF-SAM-UNRESOLVED" and "Timeout" in d.message
        for d in inv.diagnostics
    )


def test_no_resources_is_invalid(tmp_path: Path) -> None:
    tpl = tmp_path / "template.yaml"
    tpl.write_text("AWSTemplateFormatVersion: '2010-09-09'\n")
    inv = extract_sam(tpl)
    assert any(d.code == "AF-SAM-INVALID" for d in inv.diagnostics)


def test_malformed_yaml_is_invalid(tmp_path: Path) -> None:
    tpl = tmp_path / "template.yaml"
    tpl.write_text("{{{")
    inv = extract_sam(tpl)
    assert any(d.code == "AF-SAM-INVALID" for d in inv.diagnostics)

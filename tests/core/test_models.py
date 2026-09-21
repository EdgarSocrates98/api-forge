import json
from math import inf, nan
from typing import Any

import pytest
from pydantic import ValidationError

from apiforge.core.ids import stable_id
from apiforge.core.models import (
    Diagnostic,
    Fact,
    Finding,
    FindingStatus,
    Severity,
    SourceRef,
)


def source_ref(**overrides: Any) -> SourceRef:
    values: dict[str, Any] = {"path": "openapi.yaml", "sha256": "a" * 64}
    values.update(overrides)
    return SourceRef(**values)


def test_stable_id_is_order_independent_for_mapping() -> None:
    assert stable_id("fact", {"b": 2, "a": 1}) == stable_id("fact", {"a": 1, "b": 2})


@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_stable_id_rejects_non_finite_numbers(value: float) -> None:
    with pytest.raises(ValueError, match="JSON-compatible"):
        stable_id("fact", {"value": value})


def test_finding_requires_evidence_unless_unresolved() -> None:
    with pytest.raises(ValidationError, match="evidence"):
        Finding(
            finding_id="finding:x",
            rule_id="AF-CONTRACT-001",
            status=FindingStatus.CONFIRMED,
            severity=Severity.HIGH,
            title="Missing implementation",
            evidence=[],
        )

    unresolved = Finding(
        finding_id="finding:y",
        rule_id="AF-CONTRACT-001",
        status=FindingStatus.UNRESOLVED,
        severity=Severity.HIGH,
        title="Implementation could not be determined",
        evidence=[],
    )
    assert unresolved.evidence == ()


def test_models_are_immutable() -> None:
    fact = Fact(
        fact_id="fact:x",
        kind="api.operation",
        source=source_ref(),
        measures={"method": "GET"},
    )
    with pytest.raises(ValidationError):
        fact.kind = "changed"  # type: ignore[misc]


def test_json_payloads_are_deeply_immutable_and_detached_from_callers() -> None:
    measures = {"request": {"required": ["name"]}}
    attrs = {"tags": ["public"]}
    fact = Fact(
        fact_id="fact:x",
        kind="api.operation",
        source=source_ref(),
        measures=measures,
        attrs=attrs,
    )

    measures["request"]["required"].append("email")  # type: ignore[index,union-attr]
    attrs["tags"].append("mutated")  # type: ignore[union-attr]

    assert fact.measures == {"request": {"required": ("name",)}}
    assert fact.attrs == {"tags": ("public",)}
    with pytest.raises(TypeError):
        fact.measures["request"] = {}  # type: ignore[index]
    with pytest.raises(TypeError):
        fact.measures["request"]["required"] += ("email",)  # type: ignore[index,operator]


def test_frozen_payloads_remain_json_serializable() -> None:
    diagnostic = Diagnostic(
        code="AF-OPENAPI-UNSUPPORTED",
        status=FindingStatus.UNRESOLVED,
        message="Unsupported construct",
        source=source_ref(line=2, column=4),
        details={"constructs": ["callback"], "count": 1},
    )

    encoded = diagnostic.model_dump_json()
    assert json.loads(encoded)["details"] == {"constructs": ["callback"], "count": 1}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sha256", "A" * 64),
        ("sha256", "a" * 63),
        ("line", 0),
        ("column", -1),
    ],
)
def test_source_ref_validates_provenance(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        source_ref(**{field: value})


def test_source_ref_has_a_stable_default_extractor_and_forbids_extra_fields() -> None:
    source = source_ref()
    assert source.extractor == "apiforge"

    with pytest.raises(ValidationError):
        SourceRef(path="openapi.yaml", sha256="a" * 64, unexpected=True)  # type: ignore[call-arg]

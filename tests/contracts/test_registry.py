"""Contract registry: every name resolves to a frozen, closed, versioned model."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from apiforge.contracts.base import ContractError
from apiforge.contracts.registry import CONTRACTS, contract_names, contract_schema


def test_registry_is_sorted_and_complete() -> None:
    names = contract_names()
    assert names == sorted(names)
    # the prompt's canonical list, plus ActionStep/GraphExport helpers
    expected = {
        "ArtifactRef/v1", "Fact/v1", "Finding/v1", "Receipt/v1",
        "Decision/v1", "ActionPlan/v1", "Verification/v1",
        "TaskSpec/v1", "TaskRevision/v1", "TaskPlan/v1", "TaskHandoff/v1",
        "AcceptanceRecord/v1", "CapabilityProof/v1", "OutcomeBrief/v1",
        "GraphNode/v1", "GraphEdge/v1",
        "TelemetryEvent/v1", "PerformanceRun/v1", "DataAccessIR/v1",
        "RuntimeMatrix/v1",
    }
    assert expected <= set(names)


def test_every_contract_is_a_pydantic_model() -> None:
    for name, model in CONTRACTS.items():
        assert issubclass(model, BaseModel), name


def test_unknown_name_is_refused() -> None:
    with pytest.raises(ContractError, match="AF-CONTRACTS-UNKNOWN"):
        contract_schema("Nope/v1")


def test_schemas_are_json_schema() -> None:
    schema = contract_schema("TaskSpec/v1")
    assert schema["type"] == "object"
    assert "outcome" in schema["properties"]


def test_versioned_contracts_reject_extra_fields() -> None:
    from apiforge.contracts.core import ArtifactRef

    sha = "a" * 64
    with pytest.raises(ValidationError):
        ArtifactRef(path="x", sha256=sha, bogus=True)


def test_version_rejects_v2() -> None:
    from apiforge.contracts.core import ArtifactRef

    sha = "a" * 64
    with pytest.raises(ValidationError):
        ArtifactRef(version=2, path="x", sha256=sha)

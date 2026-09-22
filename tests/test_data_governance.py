import pytest

from apiforge.contracts.stubs import DataAccessIR
from apiforge.data_governance import assess_data_access


def _ir(**over: object) -> DataAccessIR:
    values: dict[str, object] = {
        "id": "ir-1",
        "database": "dynamo",
        "provider": "aws",
        "access_patterns": ("GetItem", "Query"),
    }
    values.update(over)
    return DataAccessIR.model_validate(values)


def test_read_access_can_be_ready_when_metadata_is_complete() -> None:
    result = assess_data_access(_ir(), credential_configured=True)
    assert result.status == "ready"
    assert result.mutation_patterns == ()
    assert "network_called:false" in result.evidence


def test_mutating_access_is_blocked_without_approval() -> None:
    result = assess_data_access(
        _ir(access_patterns=("GetItem", "PutItem")), credential_configured=True
    )
    assert result.status == "blocked"
    assert result.mutation_patterns == ("putitem",)
    assert "external-mutation-requires-approval" in result.blockers


def test_missing_metadata_is_review_not_approved() -> None:
    result = assess_data_access(_ir(access_patterns=()))
    assert result.status == "review"
    assert "credential-not-declared" in result.blockers


def test_unknown_database_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported database"):
        assess_data_access(_ir(database="postgres"))

from apiforge.grpc.security import inspect_metadata


def test_security_reports_redactable_metadata_names() -> None:
    result = inspect_metadata({"authorization": "secret", "x-request-id": "id"})
    assert result.safe is True
    assert result.redacted_fields == ("authorization",)

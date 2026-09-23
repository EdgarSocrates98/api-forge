from __future__ import annotations

from apiforge.integrations.external import (
    GitHubIssuesReadOnlyAdapter,
    HttpHealthReadOnlyAdapter,
    HttpJsonReadOnlyAdapter,
    verify_external_receipt,
)


class Transport:
    def get_json(self, path: str, *, params=None) -> object:
        if path.endswith("/issues"):
            return [{"number": 7, "title": "read-only evidence"}]
        return {"status": "ready"}


def test_github_issues_adapter_is_get_only_and_emits_receipt() -> None:
    result = GitHubIssuesReadOnlyAdapter(Transport()).read("example/repo")
    assert result.status == "ok"
    assert result.receipt is not None
    assert result.receipt.read_only is True
    assert result.receipt.mutation_allowed is False
    assert "issues" in result.receipt.reference


def test_health_receipt_has_reproducible_freshness_verification() -> None:
    result = HttpHealthReadOnlyAdapter(Transport()).read(
        "https://example.test/readyz", max_age_seconds=300
    )
    assert result.receipt is not None
    checked = verify_external_receipt(
        result.receipt,
        now=result.receipt.observed_at,
    )
    assert checked["ok"] is True


def test_generic_json_adapter_preserves_external_payload_without_inference() -> None:
    result = HttpJsonReadOnlyAdapter(Transport()).read("https://example.test/api/issues")
    assert result.status == "ok"
    assert result.receipt is not None
    assert "does not infer" in result.limitations[0]

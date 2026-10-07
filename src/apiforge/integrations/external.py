"""Explicit read-only adapters for remote issue and health evidence."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from urllib.parse import urlsplit

from apiforge.contracts.integration import (
    ExternalReadReceipt,
    ExternalReadRequest,
    ExternalReadResult,
)
from apiforge.integrations.github import UrllibReadOnlyTransport
from apiforge.integrations.transport import ReadOnlyTransport, TransportError


def _hash(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _receipt(
    request: ExternalReadRequest, payload: object, observed_at: datetime
) -> ExternalReadReceipt:
    fresh_until = observed_at + timedelta(seconds=request.max_age_seconds)
    return ExternalReadReceipt(
        provider=request.provider,
        reference=request.reference,
        observed_at=observed_at.isoformat(),
        fresh_until=fresh_until.isoformat(),
        response_sha256=_hash(payload),
        limitations=(
            "receipt proves the observed response and declared freshness window, not authorship",
            "provider permissions and deployment safety remain outside this read",
        ),
    )


class GitHubIssuesReadOnlyAdapter:
    """List repository issues through a GET-only injected transport."""

    name = "github-issues-read-only"

    def __init__(self, transport: ReadOnlyTransport) -> None:
        self._transport = transport

    def read(
        self,
        repository: str,
        *,
        state: str = "open",
        max_age_seconds: int = 300,
    ) -> ExternalReadResult:
        request = ExternalReadRequest(
            provider="github",
            reference=f"/repos/{repository.strip('/')}/issues?state={state}",
            max_age_seconds=max_age_seconds,
        )
        payload = self._transport.get_json(
            f"/repos/{repository.strip('/')}/issues", params={"state": state, "per_page": "100"}
        )
        if not isinstance(payload, list):
            raise TransportError(
                "AF-GITHUB-PAYLOAD",
                "issues response must be a JSON array",
                field="issues response",
                unlock="inspect the provider response and retry with the read-only adapter",
            )
        observed = datetime.now(UTC)
        return ExternalReadResult.from_payload(
            provider="github",
            reference=request.reference,
            payload=payload,
            receipt=_receipt(request, payload, observed),
            limitations=("issue comments, labels and state are observations only",),
        )


class HttpHealthReadOnlyAdapter:
    """GET one health/readiness endpoint and emit a freshness receipt."""

    name = "http-health-read-only"

    def __init__(self, transport: ReadOnlyTransport) -> None:
        self._transport = transport

    def read(self, url: str, *, max_age_seconds: int = 60) -> ExternalReadResult:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise TransportError(
                "AF-EXTERNAL-URL",
                "health URL must be an absolute HTTP(S) URL",
                field="url",
                unlock="provide an absolute URL for a read-only health endpoint",
            )
        reference = parsed.path or "/"
        if parsed.query:
            reference += f"?{parsed.query}"
        request = ExternalReadRequest(
            provider="http", reference=url, max_age_seconds=max_age_seconds
        )
        payload = self._transport.get_json(reference)
        observed = datetime.now(UTC)
        return ExternalReadResult.from_payload(
            provider="http",
            reference=url,
            payload=payload,
            receipt=_receipt(request, payload, observed),
            limitations=(
                "a healthy endpoint does not prove application correctness, SLO compliance or deployment rollback",
            ),
        )


class HttpJsonReadOnlyAdapter:
    """Read any explicitly supplied JSON endpoint, such as Jira or Linear."""

    name = "http-json-read-only"

    def __init__(self, transport: ReadOnlyTransport) -> None:
        self._transport = transport

    def read(self, url: str, *, max_age_seconds: int = 300) -> ExternalReadResult:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise TransportError(
                "AF-EXTERNAL-URL",
                "JSON URL must be an absolute HTTP(S) URL",
                field="url",
                unlock="provide an absolute URL for a read-only JSON endpoint",
            )
        reference = parsed.path or "/"
        if parsed.query:
            reference += f"?{parsed.query}"
        request = ExternalReadRequest(
            provider="http", reference=url, max_age_seconds=max_age_seconds
        )
        payload = self._transport.get_json(reference)
        observed = datetime.now(UTC)
        return ExternalReadResult.from_payload(
            provider="http",
            reference=url,
            payload=payload,
            receipt=_receipt(request, payload, observed),
            limitations=(
                "the adapter preserves provider JSON but does not infer issue, project or permission semantics",
            ),
        )


def adapter_for_url(url: str, *, token: str | None = None) -> HttpHealthReadOnlyAdapter:
    """Build the explicit network adapter for a health URL."""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("AF-EXTERNAL-URL: URL must be absolute HTTP(S)")
    return HttpHealthReadOnlyAdapter(
        UrllibReadOnlyTransport(
            f"{parsed.scheme}://{parsed.netloc}", token=token, accept="application/json"
        )
    )


def verify_external_receipt(receipt: ExternalReadReceipt, *, now: str) -> dict[str, object]:
    """Verify the declared freshness window without contacting the provider."""
    try:
        observed = datetime.fromisoformat(receipt.observed_at)
        fresh_until = datetime.fromisoformat(receipt.fresh_until)
        checked_at = datetime.fromisoformat(now)
    except ValueError as exc:
        raise TransportError(
            "AF-EXTERNAL-RECEIPT",
            str(exc),
            field="receipt timestamps",
            unlock="emit a receipt with ISO-8601 timestamps and retry verification",
        ) from exc
    return {
        "ok": checked_at <= fresh_until and observed <= checked_at,
        "fresh": checked_at <= fresh_until,
        "observed_at": receipt.observed_at,
        "fresh_until": receipt.fresh_until,
        "checked_at": now,
        "provider": receipt.provider,
        "reference": receipt.reference,
    }

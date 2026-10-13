"""Read-only GitHub adapter with an injected transport and redacted provenance."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from apiforge.contracts.change_control import (
    ChangeBundle,
    ChangeCheck,
    ChangeCollectRequest,
    ChangePolicy,
    ChangeSource,
    CheckConclusion,
)
from apiforge.core.models import JsonValue, freeze_json
from apiforge.integrations.transport import ReadOnlyTransport, TransportError


def _canonical_hash(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _redact(value: object) -> JsonValue:
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]"
            if re.search(r"token|authorization|secret|password", str(key), re.IGNORECASE)
            else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return tuple(_redact(item) for item in value)
    if isinstance(value, str):
        return re.sub(r"(https?://[^\s?]+\?[^\s]+)", "[REDACTED_URL]", value)
    return freeze_json(value)


class UrllibReadOnlyTransport:
    """Minimal GET-only transport; it never sends a mutating HTTP verb."""

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: float = 10.0,
        accept: str = "application/vnd.github+json",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._accept = accept

    def get_json(self, path: str, *, params: Mapping[str, str] | None = None) -> object:
        query = f"?{urlencode(params)}" if params else ""
        request = Request(f"{self._base_url}/{path.lstrip('/')}{query}", method="GET")
        request.add_header("Accept", self._accept)
        if self._token:
            request.add_header("Authorization", f"Bearer {self._token}")
        try:
            with urlopen(request, timeout=self._timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise TransportError(
                "AF-GITHUB-HTTP", f"HTTP {exc.code}", retryable=exc.code >= 500
            ) from exc
        except URLError as exc:
            raise TransportError("AF-GITHUB-NETWORK", str(exc.reason), retryable=True) from exc
        except json.JSONDecodeError as exc:
            raise TransportError("AF-GITHUB-JSON", "provider response is not JSON") from exc


class GitHubReadOnlyAdapter:
    """Collect pull-request, compare and check-run observations only."""

    name = "github-read-only"

    def __init__(self, transport: ReadOnlyTransport) -> None:
        self._transport = transport

    def collect(self, request: ChangeCollectRequest) -> ChangeBundle:
        repository = request.repository.strip("/")
        now = datetime.now(UTC).isoformat()
        compare_path = f"/repos/{repository}/compare/{request.base_sha}...{request.head_sha}"
        compare = self._transport.get_json(compare_path)
        if not isinstance(compare, Mapping):
            raise TransportError("AF-GITHUB-PAYLOAD", "compare response must be a JSON object")
        sources = [
            ChangeSource(
                provider="github",
                kind="compare",
                reference=compare_path,
                sha256=_canonical_hash(_redact(compare)),
                observed_at=now,
            )
        ]
        checks: list[ChangeCheck] = []
        check_path = f"/repos/{repository}/commits/{request.head_sha}/check-runs"
        try:
            check_payload = self._transport.get_json(check_path, params={"per_page": "100"})
        except TransportError as exc:
            check_payload = {"error": exc.code}
        if not isinstance(check_payload, Mapping):
            raise TransportError("AF-GITHUB-PAYLOAD", "check-runs response must be a JSON object")
        if isinstance(check_payload, Mapping):
            raw_checks = check_payload.get("check_runs", ())
            if isinstance(raw_checks, list):
                for raw in raw_checks:
                    if not isinstance(raw, Mapping):
                        continue
                    conclusion = str(raw.get("conclusion") or "unknown")
                    if conclusion not in {
                        "success",
                        "failure",
                        "neutral",
                        "cancelled",
                        "skipped",
                        "timed_out",
                        "action_required",
                        "unknown",
                    }:
                        conclusion = "unknown"
                    details = _redact(raw)
                    checks.append(
                        ChangeCheck(
                            name=str(raw.get("name", "unnamed")),
                            conclusion=cast(CheckConclusion, conclusion),
                            source=ChangeSource(
                                provider="github",
                                kind="check_run",
                                reference=str(raw.get("html_url", check_path)),
                                sha256=_canonical_hash(details),
                                observed_at=now,
                            ),
                            details=details if isinstance(details, Mapping) else {},
                        )
                    )
        pr_source: tuple[ChangeSource, ...] = ()
        if request.pull_number is not None:
            pr_path = f"/repos/{repository}/pulls/{request.pull_number}"
            pr_payload = self._transport.get_json(pr_path)
            pr_source = (
                ChangeSource(
                    provider="github",
                    kind="pull_request",
                    reference=pr_path,
                    sha256=_canonical_hash(_redact(pr_payload)),
                    observed_at=now,
                ),
            )
        return ChangeBundle(
            repository=repository,
            base_sha=request.base_sha,
            head_sha=request.head_sha,
            origin=request.origin,
            provider="github",
            pull_number=request.pull_number,
            contract=request.contract,
            baseline=request.baseline,
            project=request.project,
            sources=tuple(sources) + pr_source,
            checks=tuple(checks),
            policy=ChangePolicy(
                read_only=True,
                mutation_allowed=False,
                untrusted_input=True,
                limitations=("provider payloads are observations, not execution proof",),
            ),
            limitations=("GitHub adapter does not merge, push, dispatch or deploy",),
        )

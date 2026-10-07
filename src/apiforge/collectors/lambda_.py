"""Collect one Lambda function's configuration into an offline dump.

``Code.Location`` is a pre-signed URL — it is stripped, never persisted.
The injected ``client`` keeps boto3 out of tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from apiforge.collectors.manifest import CollectError, CollectManifest, write_artifact


class _LambdaClient(Protocol):
    def get_function(self, *, FunctionName: str) -> dict[str, Any]: ...

    def get_policy(self, *, FunctionName: str) -> dict[str, Any]: ...


def default_client() -> Any:
    """Build the real boto3 client lazily — the only boto3 import site."""
    try:
        import boto3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise CollectError(
            "AF-COLLECT-AWS",
            "boto3 is not installed; install the 'aws' extra (pip install apiforge[aws])",
        ) from exc
    return boto3.client("lambda")


def collect(
    function_name: str,
    out_dir: Path,
    now: str | None = None,
    client: _LambdaClient | None = None,
) -> CollectManifest:
    """Fetch the function's configuration (and resource policy) as a dump."""
    if client is None:
        client = default_client()
    manifest = CollectManifest(
        source="lambda",
        collected_at=now,
        meta={"function_name": function_name},
    )
    try:
        response = client.get_function(FunctionName=function_name)
    except Exception as exc:
        raise CollectError("AF-COLLECT-AWS", f"get_function failed: {exc}") from exc
    configuration = response.get("Configuration", {})
    name, digest = write_artifact(out_dir, "function.json", configuration)
    manifest.record(name, digest)

    try:
        policy = client.get_policy(FunctionName=function_name).get("Policy")
    except Exception:  # noqa: BLE001 - absent resource policy is data, not failure
        policy = None
    if policy is not None:
        name, digest = write_artifact(out_dir, "policy.json", policy)
        manifest.record(name, digest)

    manifest.write(out_dir)
    return manifest

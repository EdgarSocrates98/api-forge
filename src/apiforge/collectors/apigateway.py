"""Collect API Gateway REST API configuration into an offline dump directory.

The injected ``client`` keeps boto3 out of tests: production wires
``boto3.client("apigateway")`` lazily in the CLI; tests pass a stub.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from apiforge.collectors.manifest import CollectError, CollectManifest, write_artifact


class _GatewayClient(Protocol):
    def get_rest_api(self, *, restApiId: str) -> dict[str, Any]: ...

    def get_resources(self, **kwargs: Any) -> dict[str, Any]: ...

    def get_stages(self, *, restApiId: str) -> dict[str, Any]: ...

    def get_authorizers(self, **kwargs: Any) -> dict[str, Any]: ...


def default_client() -> Any:
    """Build the real boto3 client lazily — the only boto3 import site."""
    try:
        import boto3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise CollectError(
            "AF-COLLECT-AWS",
            "boto3 is not installed; install the 'aws' extra (pip install apiforge[aws])",
        ) from exc
    return boto3.client("apigateway")


def _paginate(client: _GatewayClient, method: str, base: dict[str, Any]) -> list[dict[str, Any]]:
    """Follow API Gateway ``position`` pagination; return all ``items``."""
    items: list[dict[str, Any]] = []
    kwargs = dict(base)
    while True:
        call = getattr(client, method)
        try:
            page = call(**kwargs)
        except Exception as exc:  # boto3 ClientError subclasses vary; name them all
            raise CollectError("AF-COLLECT-AWS", f"{method} failed: {exc}") from exc
        items.extend(page.get("items", []))
        position = page.get("position")
        if not position:
            return items
        kwargs["position"] = position


def collect(
    api_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _GatewayClient | None = None,
) -> CollectManifest:
    """Fetch one REST API's config and write the dump + manifest."""
    if client is None:
        client = default_client()
    manifest = CollectManifest(
        source="api-gateway",
        collected_at=now,
        meta={"api_id": api_id},
    )
    try:
        rest_api = client.get_rest_api(restApiId=api_id)
    except Exception as exc:
        raise CollectError("AF-COLLECT-AWS", f"get_rest_api failed: {exc}") from exc
    name, digest = write_artifact(out_dir, "rest-api.json", rest_api)
    manifest.record(name, digest)

    for artifact, items in (
        ("resources.json", _paginate(client, "get_resources", {"restApiId": api_id})),
        ("stages.json", _stages(client, api_id)),
        ("authorizers.json", _paginate(client, "get_authorizers", {"restApiId": api_id})),
    ):
        name, digest = write_artifact(out_dir, artifact, {"items": items})
        manifest.record(name, digest)

    manifest.write(out_dir)
    return manifest


def _stages(client: _GatewayClient, api_id: str) -> list[dict[str, Any]]:
    try:
        response = client.get_stages(restApiId=api_id)
    except Exception as exc:
        raise CollectError("AF-COLLECT-AWS", f"get_stages failed: {exc}") from exc
    items = response.get("item", [])
    return [item for item in items if isinstance(item, dict)]

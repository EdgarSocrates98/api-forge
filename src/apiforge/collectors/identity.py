"""Collectors for identity/edge protection: IAM role, Cognito pool, WAF ACL.

Same contract as the other collectors: offline dump directory, injected
client, canonical artifacts + manifest. ``collect_iam_role`` reads — it never
simulates or mutates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from apiforge.collectors.manifest import CollectError, CollectManifest, write_artifact
from apiforge.collectors.messaging import _boto3, _call


class _IamClient(Protocol):
    def get_role(self, **kwargs: Any) -> dict[str, Any]: ...

    def list_attached_role_policies(self, **kwargs: Any) -> dict[str, Any]: ...

    def list_role_policies(self, **kwargs: Any) -> dict[str, Any]: ...

    def get_role_policy(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_iam_role(
    role_name: str,
    out_dir: Path,
    now: str | None = None,
    client: _IamClient | None = None,
) -> CollectManifest:
    """Fetch the role, its attached managed policies and inline policy docs."""
    if client is None:
        client = _boto3("iam")
    manifest = CollectManifest(source="iam-role", collected_at=now)
    role = _call(client, "get_role", RoleName=role_name)
    name, digest = write_artifact(out_dir, "role.json", role)
    manifest.record(name, digest)

    attached: list[dict[str, Any]] = []
    marker: str | None = None
    while True:
        kwargs: dict[str, Any] = {"RoleName": role_name}
        if marker:
            kwargs["Marker"] = marker
        page = _call(client, "list_attached_role_policies", **kwargs)
        attached.extend(page.get("AttachedPolicies", []))
        if not page.get("IsTruncated"):
            break
        marker = page.get("Marker")
        if not marker:
            break
    name, digest = write_artifact(out_dir, "attached-policies.json", attached)
    manifest.record(name, digest)

    names = _call(client, "list_role_policies", RoleName=role_name).get("PolicyNames", [])
    inline = {
        str(policy): _call(
            client,
            "get_role_policy",
            RoleName=role_name,
            PolicyName=policy,
        ).get("PolicyDocument")
        for policy in names
    }
    name, digest = write_artifact(out_dir, "inline-policies.json", inline)
    manifest.record(name, digest)
    manifest.meta["role_name"] = role_name
    manifest.write(out_dir)
    return manifest


class _CognitoClient(Protocol):
    def describe_user_pool(self, **kwargs: Any) -> dict[str, Any]: ...

    def list_user_pool_clients(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_cognito(
    user_pool_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _CognitoClient | None = None,
) -> CollectManifest:
    """Fetch the user pool description and its app clients."""
    if client is None:
        client = _boto3("cognito-idp")
    manifest = CollectManifest(source="cognito", collected_at=now)
    pool = _call(client, "describe_user_pool", UserPoolId=user_pool_id)
    name, digest = write_artifact(out_dir, "user-pool.json", pool)
    manifest.record(name, digest)
    clients = _call(client, "list_user_pool_clients", UserPoolId=user_pool_id).get(
        "UserPoolClients", []
    )
    name, digest = write_artifact(out_dir, "clients.json", clients)
    manifest.record(name, digest)
    manifest.meta["user_pool_id"] = user_pool_id
    manifest.write(out_dir)
    return manifest


class _WafClient(Protocol):
    def get_web_acl(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_waf(
    web_acl_id: str,
    web_acl_name: str,
    scope: str,
    out_dir: Path,
    now: str | None = None,
    client: _WafClient | None = None,
) -> CollectManifest:
    """Fetch one WebACL (``scope`` is REGIONAL or CLOUDFRONT)."""
    if scope not in ("REGIONAL", "CLOUDFRONT"):
        raise CollectError("AF-COLLECT-ARG", f"scope must be REGIONAL or CLOUDFRONT, got {scope!r}")
    if client is None:
        client = _boto3("wafv2")
    manifest = CollectManifest(source="waf", collected_at=now)
    acl = _call(
        client,
        "get_web_acl",
        Id=web_acl_id,
        Name=web_acl_name,
        Scope=scope,
    )
    name, digest = write_artifact(out_dir, "web-acl.json", acl)
    manifest.record(name, digest)
    manifest.meta["web_acl_id"] = web_acl_id
    manifest.meta["scope"] = scope
    manifest.write(out_dir)
    return manifest

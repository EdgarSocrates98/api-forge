"""API Gateway dump extractor: offline dump directory -> CodeInventory.

Reads the artifacts a `collect api-gateway` run wrote — never AWS, never
the network. Missing or malformed dump files are named diagnostics.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_DUMP_FILES = ("rest-api.json", "resources.json", "stages.json", "authorizers.json")


def _diag(code: str, message: str, rel: str, digest: str | None) -> Diagnostic:
    source = (
        SourceRef(path=rel, sha256=digest, line=None, extractor="apigateway-dump")
        if digest is not None
        else None
    )
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=message,
        source=source,
    )


def _load_dump(
    dump: Path, name: str, input_hashes: dict[str, str], diagnostics: list[Diagnostic]
) -> Any | None:
    path = dump / name
    if not path.is_file():
        diagnostics.append(
            _diag("AF-GW-DUMP-MISSING", f"{name}: dump file missing from {dump}", name, None)
        )
        return None
    raw = path.read_bytes()
    input_hashes[name] = hashlib.sha256(raw).hexdigest()
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        diagnostics.append(
            _diag("AF-GW-DUMP-INVALID", f"{name}: not valid JSON ({exc})", name, input_hashes[name])
        )
        return None


def _fact(
    kind: str, source_file: str, digest: str, measures: dict[str, Any], attrs: dict[str, Any]
) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"kind": kind, "file": source_file, **measures}),
        kind=kind,
        source=SourceRef(path=source_file, sha256=digest, line=None, extractor="apigateway-dump"),
        measures=measures,
        attrs=attrs,
    )


def extract_apigateway(dump_dir: Path) -> CodeInventory:
    """Read a `collect api-gateway` dump directory into facts, offline."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    facts: list[Fact] = []

    manifest_path = dump / "manifest.json"
    if manifest_path.is_file():
        input_hashes["manifest.json"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    loaded = {name: _load_dump(dump, name, input_hashes, diagnostics) for name in _DUMP_FILES}

    rest_api = loaded["rest-api.json"]
    if isinstance(rest_api, dict):
        facts.append(
            _fact(
                "aws.apigateway.api",
                "rest-api.json",
                input_hashes["rest-api.json"],
                {"api_id": rest_api.get("id", ""), "name": rest_api.get("name", "")},
                {
                    "endpoint_types": rest_api.get("endpointConfiguration", {}).get("types", []),
                    "description": rest_api.get("description"),
                },
            )
        )

    resources = loaded["resources.json"]
    if isinstance(resources, dict):
        digest = input_hashes.get("resources.json", "")
        for item in resources.get("items", []):
            if not isinstance(item, dict):
                continue
            path = item.get("path", "")
            methods = {
                verb: {
                    "authorizationType": spec.get("authorizationType"),
                    "authorizerId": spec.get("authorizerId"),
                    "apiKeyRequired": spec.get("apiKeyRequired", False),
                }
                for verb, spec in (item.get("resourceMethods") or {}).items()
                if isinstance(spec, dict)
            }
            facts.append(
                _fact(
                    "aws.apigateway.resource",
                    "resources.json",
                    digest,
                    {"path": path},
                    {"resource_id": item.get("id", ""), "methods": methods},
                )
            )

    stages = loaded["stages.json"]
    if isinstance(stages, dict):
        digest = input_hashes.get("stages.json", "")
        for item in stages.get("items", []):
            if not isinstance(item, dict):
                continue
            facts.append(
                _fact(
                    "aws.apigateway.stage",
                    "stages.json",
                    digest,
                    {"stage": item.get("stageName", "")},
                    {
                        "access_log": bool(item.get("accessLogSettings")),
                        "cache_cluster": bool(item.get("cacheClusterEnabled")),
                        "deployment": item.get("deploymentId"),
                        "method_settings": item.get("methodSettings", {}),
                        "throttling": item.get("throttling", {}),
                        "variables": item.get("variables", {}),
                        "tracing": bool(item.get("tracingEnabled")),
                    },
                )
            )

    authorizers = loaded["authorizers.json"]
    if isinstance(authorizers, dict):
        digest = input_hashes.get("authorizers.json", "")
        for item in authorizers.get("items", []):
            if not isinstance(item, dict):
                continue
            facts.append(
                _fact(
                    "aws.apigateway.authorizer",
                    "authorizers.json",
                    digest,
                    {"authorizer_id": item.get("id", ""), "name": item.get("name", "")},
                    {
                        "type": item.get("type"),
                        "uri": item.get("authorizerUri"),
                        "ttl": item.get("authorizerResultTtlInSeconds"),
                    },
                )
            )

    return CodeInventory(
        framework="apigateway-dump",
        root=str(dump),
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )

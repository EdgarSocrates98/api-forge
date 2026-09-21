"""Terraform extractor: *.tf HCL -> tf.* facts, offline, no terraform binary.

Interpolated values (``${...}``) are never resolved — the attribute becomes
a named ``AF-TF-UNRESOLVED`` diagnostic; literal values become measures.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from hcl2.api import loads as hcl2_loads

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_EXTRACTOR = "terraform-hcl"

_RESOURCE_KINDS = {
    "aws_lambda_function": "tf.lambda.function",
    "aws_lambda_permission": "tf.lambda.permission",
    "aws_api_gateway_rest_api": "tf.apigateway.rest_api",
    "aws_api_gateway_method": "tf.apigateway.method",
    "aws_api_gateway_integration": "tf.apigateway.integration",
    "aws_api_gateway_stage": "tf.apigateway.stage",
    "aws_apigatewayv2_api": "tf.apigateway.v2_api",
    "aws_apigatewayv2_route": "tf.apigateway.v2_route",
    "aws_apigatewayv2_integration": "tf.apigateway.v2_integration",
    "aws_apigatewayv2_stage": "tf.apigateway.v2_stage",
}

_ATTRS = {
    "tf.lambda.function": (
        "function_name",
        "runtime",
        "memory_size",
        "timeout",
        "reserved_concurrent_executions",
        "handler",
        "package_type",
        "tracing_config",
    ),
    "tf.lambda.permission": ("function_name", "principal", "action", "source_arn"),
    "tf.apigateway.rest_api": ("name", "endpoint_configuration"),
    "tf.apigateway.method": ("http_method", "authorization", "api_key_required", "authorizer_id"),
    "tf.apigateway.integration": ("http_method", "type", "integration_http_method", "timeout_milliseconds", "uri"),
    "tf.apigateway.stage": ("stage_name", "access_log_settings", "xray_tracing_enabled", "cache_cluster_enabled"),
    "tf.apigateway.v2_api": ("name", "protocol_type"),
    "tf.apigateway.v2_route": ("route_key", "authorization_type", "authorizer_id", "api_key_required"),
    "tf.apigateway.v2_integration": ("integration_type", "integration_method", "integration_uri", "timeout_milliseconds"),
    "tf.apigateway.v2_stage": ("name", "auto_deploy", "access_log_settings"),
}


def _diag(code: str, message: str, rel: str, digest: str) -> Diagnostic:
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=message,
        source=SourceRef(path=rel, sha256=digest, line=None, extractor=_EXTRACTOR),
    )


def _flatten(blocks: Any) -> list[tuple[str, str, dict[str, Any]]]:
    """hcl2 emits resource blocks as {type: {label: attrs}} dicts in a list."""
    out: list[tuple[str, str, dict[str, Any]]] = []
    if not isinstance(blocks, list):
        return out
    for block in blocks:
        if not isinstance(block, dict):
            continue
        for rtype, labeled in block.items():
            if not isinstance(labeled, dict):
                continue
            for label, attrs in labeled.items():
                if isinstance(attrs, dict):
                    out.append((rtype, label, attrs))
    return out


def _env_keys(attrs: dict[str, Any]) -> list[str]:
    env = attrs.get("environment")
    if isinstance(env, list):
        env = env[0] if env else {}
    if isinstance(env, dict):
        variables = env.get("variables", {})
        if isinstance(variables, dict):
            return sorted(str(k) for k in variables)
    return []


def extract_terraform(root: Path) -> CodeInventory:
    """Facts for API-facing Terraform resources under ``root``."""
    root = Path(root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}

    for tf_file in sorted(root.rglob("*.tf")):
        rel = str(tf_file.relative_to(root))
        raw = tf_file.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        input_hashes[rel] = digest
        try:
            parsed = hcl2_loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - hcl2/lark error classes vary
            diagnostics.append(_diag("AF-TF-PARSE", f"{rel}: {exc}", rel, digest))
            continue
        for rtype, label, attrs in _flatten(parsed.get("resource")):
            kind = _RESOURCE_KINDS.get(rtype)
            if kind is None:
                continue
            measures: dict[str, Any] = {"resource": f"{rtype}.{label}"}
            out_attrs: dict[str, Any] = {}
            for key in _ATTRS.get(kind, ()):
                value = attrs.get(key)
                if isinstance(value, str) and "${" in value:
                    diagnostics.append(
                        _diag(
                            "AF-TF-UNRESOLVED",
                            f"{rel}: {rtype}.{label}.{key} is interpolated ({value})",
                            rel,
                            digest,
                        )
                    )
                    continue
                out_attrs[key] = value
            if kind == "tf.lambda.function":
                out_attrs["env_keys"] = _env_keys(attrs)
            facts.append(
                Fact(
                    fact_id=stable_id("fact", {"kind": kind, "file": rel, **measures}),
                    kind=kind,
                    source=SourceRef(
                        path=rel, sha256=digest, line=None, extractor=_EXTRACTOR
                    ),
                    measures=measures,
                    attrs=out_attrs,
                )
            )
    return CodeInventory(
        framework="terraform",
        root=str(root),
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )

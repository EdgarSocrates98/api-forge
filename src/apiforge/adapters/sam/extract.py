"""SAM extractor: template.yaml -> sam.* facts, offline.

SAM templates are saturated with intrinsic tags (``!Ref``, ``!Sub``,
``!GetAtt``). A ``SafeLoader`` subclass maps any unknown tag to plain data
``{"tag": <name>, "value": <scalar>}`` — never a constructed object — and
every property whose value is a tag is emitted as ``AF-SAM-UNRESOLVED``,
never resolved by inference.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_EXTRACTOR = "sam-template"


class _SamLoader(yaml.SafeLoader):
    """SafeLoader + intrinsics-as-data; still refuses constructed objects."""


def _tag_to_data(loader: yaml.SafeLoader, tag_suffix: str, node: yaml.Node) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return {"tag": tag_suffix, "value": loader.construct_scalar(node)}
    if isinstance(node, yaml.SequenceNode):
        return {"tag": tag_suffix, "value": loader.construct_sequence(node)}
    if isinstance(node, yaml.MappingNode):
        return {"tag": tag_suffix, "value": loader.construct_mapping(node)}
    return {"tag": tag_suffix, "value": None}


_SamLoader.add_multi_constructor("!", _tag_to_data)


def _diag(code: str, message: str, rel: str, digest: str) -> Diagnostic:
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=message,
        source=SourceRef(path=rel, sha256=digest, line=None, extractor=_EXTRACTOR),
    )


def _is_tag(value: Any) -> bool:
    return isinstance(value, dict) and set(value) == {"tag", "value"}


def _plain_or_unresolved(
    value: Any, code: str, where: str, rel: str, digest: str, diagnostics: list[Diagnostic]
) -> Any:
    """Return the literal value, or None + a named diagnostic for tagged values."""
    if _is_tag(value):
        diagnostics.append(
            _diag(code, f"{where}: intrinsic {value['tag']} not resolved", rel, digest)
        )
        return None
    if isinstance(value, (dict, list)):
        return None
    return value


def _api_events(props: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    events = props.get("Events")
    if not isinstance(events, dict):
        return out
    for name, spec in events.items():
        if not isinstance(spec, dict) or spec.get("Type") != "Api":
            continue
        inner = spec.get("Properties") or {}
        out.append({"event": str(name), "path": inner.get("Path"), "method": inner.get("Method")})
    return out


def extract_sam(template_path: Path) -> CodeInventory:
    """Facts for AWS::Serverless::Function/Api resources in one template."""
    template_path = Path(template_path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    rel = template_path.name
    raw = template_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    input_hashes[rel] = digest

    try:
        doc = yaml.load(raw.decode("utf-8"), Loader=_SamLoader)
    except yaml.YAMLError as exc:
        diagnostics.append(_diag("AF-SAM-INVALID", f"{rel}: {exc}", rel, digest))
        return CodeInventory(
            framework="sam",
            root=str(template_path.parent),
            facts=(),
            diagnostics=tuple(diagnostics),
            input_hashes=input_hashes,
        )
    if not isinstance(doc, dict) or not isinstance(doc.get("Resources"), dict):
        diagnostics.append(_diag("AF-SAM-INVALID", f"{rel}: no Resources mapping", rel, digest))
        return CodeInventory(
            framework="sam",
            root=str(template_path.parent),
            facts=(),
            diagnostics=tuple(diagnostics),
            input_hashes=input_hashes,
        )

    for name, resource in sorted(doc["Resources"].items()):
        if not isinstance(resource, dict):
            continue
        rtype = resource.get("Type")
        props = resource.get("Properties") or {}
        if not isinstance(props, dict):
            props = {}
        where = f"Resources.{name}"
        if rtype == "AWS::Serverless::Function":
            attrs: dict[str, Any] = {
                "runtime": _plain_or_unresolved(
                    props.get("Runtime"),
                    "AF-SAM-UNRESOLVED",
                    f"{where}.Runtime",
                    rel,
                    digest,
                    diagnostics,
                ),
                "memory_mb": _plain_or_unresolved(
                    props.get("MemorySize"),
                    "AF-SAM-UNRESOLVED",
                    f"{where}.MemorySize",
                    rel,
                    digest,
                    diagnostics,
                ),
                "timeout_s": _plain_or_unresolved(
                    props.get("Timeout"),
                    "AF-SAM-UNRESOLVED",
                    f"{where}.Timeout",
                    rel,
                    digest,
                    diagnostics,
                ),
                "handler": props.get("Handler") if isinstance(props.get("Handler"), str) else None,
                "api_events": _api_events(props),
            }
            facts.append(
                Fact(
                    fact_id=stable_id(
                        "fact", {"kind": "sam.function", "file": rel, "resource": name}
                    ),
                    kind="sam.function",
                    source=SourceRef(path=rel, sha256=digest, line=None, extractor=_EXTRACTOR),
                    measures={"resource": name},
                    attrs=attrs,
                )
            )
        elif rtype == "AWS::Serverless::Api":
            auth = props.get("Auth")
            facts.append(
                Fact(
                    fact_id=stable_id("fact", {"kind": "sam.api", "file": rel, "resource": name}),
                    kind="sam.api",
                    source=SourceRef(path=rel, sha256=digest, line=None, extractor=_EXTRACTOR),
                    measures={"resource": name},
                    attrs={
                        "stage_name": _plain_or_unresolved(
                            props.get("StageName"),
                            "AF-SAM-UNRESOLVED",
                            f"{where}.StageName",
                            rel,
                            digest,
                            diagnostics,
                        ),
                        "has_auth": isinstance(auth, dict) and bool(auth),
                        "cors": props.get("Cors") is not None,
                    },
                )
            )
    return CodeInventory(
        framework="sam",
        root=str(template_path.parent),
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )

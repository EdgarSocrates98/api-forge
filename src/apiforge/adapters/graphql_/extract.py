"""GraphQL extractor: schema.graphql -> graphql.* facts, offline.

graphql-core parses the SDL — no server, no introspection endpoint. Root
operation fields (Query/Mutation/Subscription) become ``graphql.field``
facts carrying args, return type and deprecation; every named type becomes
a ``graphql.type`` fact. Syntax errors are ``AF-GQL-INVALID`` diagnostics.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from graphql import build_schema
from graphql.error import GraphQLError

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_EXTRACTOR = "graphql-sdl"
_ROOT_TYPES = ("Query", "Mutation", "Subscription")


def _fact(kind: str, rel: str, digest: str, measures: dict[str, Any], attrs: dict[str, Any]) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"kind": kind, "file": rel, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, extractor=_EXTRACTOR),
        measures=measures,
        attrs=attrs,
    )


def _type_ref(t: Any) -> str:
    return str(t)


def extract_graphql(path: Path) -> CodeInventory:
    """GraphQL SDL document -> ``graphql.type`` + ``graphql.field`` facts."""
    path = Path(path)
    rel = path.name
    raw = path.read_bytes()
    hashes = {rel: hashlib.sha256(raw).hexdigest()}
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []

    try:
        schema = build_schema(raw.decode("utf-8"))
    except (GraphQLError, UnicodeDecodeError) as exc:
        diagnostics.append(
            Diagnostic(
                code="AF-GQL-INVALID",
                status=FindingStatus.UNRESOLVED,
                message=str(exc).split("\n")[0],
                source=SourceRef(
                    path=rel, sha256=hashes[rel], line=None, extractor=_EXTRACTOR
                ),
            )
        )
        return CodeInventory(
            framework="graphql",
            root=str(path.parent),
            diagnostics=tuple(diagnostics),
            facts=(),
            input_hashes=hashes,
        )

    roots = {
        "query": schema.query_type,
        "mutation": schema.mutation_type,
        "subscription": schema.subscription_type,
    }
    for name, gql_type in sorted(schema.type_map.items()):
        if name.startswith("__"):
            continue
        kind = (
            type(gql_type)
            .__name__.removeprefix("GraphQL")
            .removesuffix("Type")
            .lower()
        )
        fields = getattr(gql_type, "fields", None)
        field_count = len(fields) if fields else 0
        deprecated = (
            sum(
                1
                for f in fields.values()
                if getattr(f, "deprecation_reason", None) is not None
            )
            if fields
            else 0
        )
        facts.append(
            _fact(
                "graphql.type",
                rel,
                hashes[rel],
                {"type": name},
                {
                    "kind": kind,
                    "fields": field_count,
                    "deprecated_fields": deprecated,
                    "root": any(name == r.name for r in roots.values() if r),
                },
            )
        )
        if name in {r.name for r in roots.values() if r} and fields:
            root_kind = next(k for k, r in roots.items() if r and r.name == name)
            for fname, fdef in fields.items():
                facts.append(
                    _fact(
                        "graphql.field",
                        rel,
                        hashes[rel],
                        {"operation": root_kind, "field": fname},
                        {
                            "returns": _type_ref(fdef.type),
                            "args": tuple(sorted(fdef.args)),
                            "deprecated": fdef.deprecation_reason is not None,
                        },
                    )
                )

    return CodeInventory(
        framework="graphql",
        root=str(path.parent),
        diagnostics=tuple(diagnostics),
        facts=tuple(facts),
        input_hashes=hashes,
    )

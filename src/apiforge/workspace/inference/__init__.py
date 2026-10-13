"""Opt-in cross-repo relation inference from static facts; never runs by default."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apiforge.adapters.http_targets import extract_http_targets
from apiforge.contracts.workspace import WorkspaceManifest, WorkspaceRelation
from apiforge.workspace.graph import repository_node_id
from apiforge.workspace.inference.match import (
    Outbound,
    RepoFacts,
    Served,
    TopicUse,
    match,
)

_BROKERS = ("kafka", "kinesis", "rabbitmq", "nats", "pulsar")


@dataclass(frozen=True)
class InferenceResult:
    relations: tuple[WorkspaceRelation, ...]
    unresolved: tuple[str, ...]


def _route_extractors() -> tuple[Callable[[Path], Any], ...]:
    from apiforge.adapters.fastapi.extractor import extract_fastapi
    from apiforge.adapters.go.extractor import extract_go
    from apiforge.adapters.spring.extractor import extract_spring

    return (extract_fastapi, extract_spring, extract_go)


def _served(root: Path, unresolved: list[str], name: str) -> tuple[Served, ...]:
    served: set[Served] = set()
    for extractor in _route_extractors():
        try:
            inventory = extractor(root)
        except (OSError, ValueError) as exc:
            unresolved.append(f"AF-WORKSPACE-INFER-EXTRACT: {name}: {type(exc).__name__}")
            continue
        for fact in inventory.facts:
            if fact.kind != "code.route":
                continue
            served.add(
                Served(
                    method=str(fact.measures.get("method", "ANY")).upper(),
                    path=str(fact.measures.get("path", "")),
                    ref=f"{name}:{fact.source.path}:{fact.source.line}",
                )
            )
    return tuple(sorted(served, key=lambda item: (item.path, item.method, item.ref)))


def _topics(root: Path, name: str) -> tuple[TopicUse, ...]:
    from apiforge.adapters.streaming import extract_streaming

    uses: set[TopicUse] = set()
    for broker in _BROKERS:
        inventory = extract_streaming(root, broker)
        roles: dict[str, set[str]] = {}
        for fact in inventory.facts:
            if fact.kind == "data.streaming.operation":
                roles.setdefault(fact.source.path, set()).add(str(fact.measures.get("operation")))
        for fact in inventory.facts:
            if fact.kind != "data.streaming.topic":
                continue
            for role in sorted(roles.get(fact.source.path, set()) & {"producer", "consumer"}):
                uses.add(
                    TopicUse(
                        topic=str(fact.measures.get("topic")),
                        role=role,
                        ref=f"{name}:{fact.source.path}:{fact.source.line}",
                    )
                )
    return tuple(sorted(uses, key=lambda item: (item.topic, item.role, item.ref)))


def _outbound(root: Path, name: str) -> tuple[Outbound, ...]:
    return tuple(
        Outbound(
            method=str(fact.measures.get("method", "unknown")),
            path=str(fact.measures.get("path", "")),
            base_hint=str(fact.measures.get("base_hint", "")),
            ref=f"{name}:{fact.source.path}:{fact.source.line}",
        )
        for fact in extract_http_targets(root)
    )


def infer_relations(manifest: WorkspaceManifest) -> InferenceResult:
    unresolved: list[str] = []
    repos: list[RepoFacts] = []
    for repository in sorted(manifest.repositories, key=lambda item: item.repository_id):
        root = Path(repository.root)
        if not root.is_dir():
            continue
        repos.append(
            RepoFacts(
                node_id=repository_node_id(repository.repository_id),
                name=repository.name,
                outbound=_outbound(root, repository.name),
                served=_served(root, unresolved, repository.name),
                topics=_topics(root, repository.name),
            )
        )
    result = match(tuple(repos))
    return InferenceResult(
        relations=tuple(result.relations),
        unresolved=tuple(sorted(set(unresolved) | set(result.unresolved))),
    )


__all__ = ["InferenceResult", "infer_relations"]

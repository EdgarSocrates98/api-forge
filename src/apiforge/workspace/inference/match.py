"""Pure matcher: outbound targets ↔ served routes, producers ↔ consumers by topic."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from apiforge.contracts.evidence import EvidenceRecord
from apiforge.contracts.workspace import WorkspaceRelation

EXACT = 0.9
PATH_ONLY = 0.6
HINT_BONUS = 0.1
CAP = 0.95
AMBIGUOUS_CAP = 0.45
TOPIC = 0.85
_PARAM = re.compile(r"\{[^}]*\}|\$\{[^}]*\}|<[^>]*>|:[A-Za-z_]\w*|%[sdv]")
_SLUG = re.compile(r"[^a-z0-9]")


@dataclass(frozen=True)
class Outbound:
    method: str
    path: str
    base_hint: str
    ref: str


@dataclass(frozen=True)
class Served:
    method: str
    path: str
    ref: str


@dataclass(frozen=True)
class TopicUse:
    topic: str
    role: str
    ref: str


@dataclass(frozen=True)
class RepoFacts:
    node_id: str
    name: str
    outbound: tuple[Outbound, ...] = ()
    served: tuple[Served, ...] = ()
    topics: tuple[TopicUse, ...] = ()


@dataclass
class MatchResult:
    relations: list[WorkspaceRelation] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)


def template(path: str) -> str:
    normalized = _PARAM.sub("{}", path.strip())
    normalized = re.sub(r"/+", "/", normalized)
    return normalized.rstrip("/") or "/"


def _slug(value: str) -> str:
    return _SLUG.sub("", value.lower())


def _hint_matches(hint: str, name: str) -> bool:
    left, right = _slug(hint), _slug(name)
    return bool(left and right) and (left in right or right in left)


def _relation(
    kind: str, source: str, from_id: str, to_id: str, confidence: float, refs: tuple[str, ...]
) -> WorkspaceRelation:
    return WorkspaceRelation(
        relation=kind,  # type: ignore[arg-type]
        source="workspace.inference",
        from_id=from_id,
        to_id=to_id,
        evidence=EvidenceRecord(
            level="inferred",
            source=source,
            confidence=round(confidence, 2),
            refs=tuple(sorted(set(refs))),
        ),
        limitations=("static inference; not runtime proof",),
    )


def _http(repos: tuple[RepoFacts, ...], result: MatchResult) -> None:
    edges: dict[tuple[str, str], tuple[float, set[str]]] = {}
    for caller in repos:
        for call in caller.outbound:
            wanted = template(call.path)
            candidates: list[tuple[RepoFacts, float, frozenset[str]]] = []
            for callee in repos:
                if callee.node_id == caller.node_id:
                    continue
                best = 0.0
                route_refs: set[str] = set()
                for route in callee.served:
                    if template(route.path) != wanted:
                        continue
                    if call.method != "unknown" and route.method.upper() not in (
                        call.method,
                        "ANY",
                    ):
                        continue
                    best = max(best, EXACT if call.method != "unknown" else PATH_ONLY)
                    route_refs.add(route.ref)
                if best:
                    if _hint_matches(call.base_hint, callee.name):
                        best = min(CAP, best + HINT_BONUS)
                    candidates.append((callee, best, frozenset(route_refs)))
            if not candidates:
                continue
            hinted = [item for item in candidates if _hint_matches(call.base_hint, item[0].name)]
            if len(candidates) > 1 and len(hinted) == 1:
                candidates = hinted
            elif len(candidates) > 1:
                names = ", ".join(sorted(item[0].name for item in candidates))
                result.unresolved.append(
                    f"AF-WORKSPACE-INFER-AMBIGUOUS: {call.method} {wanted} from {caller.name} "
                    f"is served by {names}"
                )
                candidates = [
                    (repo, min(score, AMBIGUOUS_CAP), matched)
                    for repo, score, matched in candidates
                ]
            for callee, score, matched in candidates:
                key = (caller.node_id, callee.node_id)
                previous, refs = edges.get(key, (0.0, set()))
                edges[key] = (max(previous, score), refs | {call.ref} | matched)
    for (from_id, to_id), (score, refs) in sorted(edges.items()):
        result.relations.append(
            _relation("calls", "http.outbound", from_id, to_id, score, tuple(refs))
        )


def _topics(repos: tuple[RepoFacts, ...], result: MatchResult) -> None:
    producers: dict[str, dict[str, set[str]]] = {}
    consumers: dict[str, dict[str, set[str]]] = {}
    for repo in repos:
        for use in repo.topics:
            bucket = producers if use.role == "producer" else consumers
            bucket.setdefault(use.topic, {}).setdefault(repo.node_id, set()).add(use.ref)
    edges: dict[tuple[str, str], set[str]] = {}
    for topic in sorted(set(producers) & set(consumers)):
        for producer, prefs in producers[topic].items():
            for consumer, crefs in consumers[topic].items():
                if producer == consumer:
                    continue
                edges.setdefault((producer, consumer), set()).update(
                    {f"topic:{topic}", *prefs, *crefs}
                )
    for (from_id, to_id), refs in sorted(edges.items()):
        result.relations.append(
            _relation(
                "publishes_to_consumer", "data.streaming.topic", from_id, to_id, TOPIC, tuple(refs)
            )
        )


def match(repos: tuple[RepoFacts, ...]) -> MatchResult:
    ordered = tuple(sorted(repos, key=lambda repo: repo.node_id))
    result = MatchResult()
    _http(ordered, result)
    _topics(ordered, result)
    result.relations.sort(key=lambda item: (item.from_id, item.to_id, item.relation))
    result.unresolved = sorted(set(result.unresolved))
    return result


__all__ = ["MatchResult", "Outbound", "RepoFacts", "Served", "TopicUse", "match", "template"]

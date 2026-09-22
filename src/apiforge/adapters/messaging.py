"""Static AWS messaging access extraction; no queue/topic/stream is contacted."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Literal, cast

from apiforge.adapters.inventory import CodeInventory
from apiforge.contracts.stubs import MessagingAccessIR
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_TOKENS = {
    "sqs": ("sqs", "send_message", "receive_message", "boto3.client('sqs'"),
    "sns": ("sns", "publish", "create_topic", "boto3.client('sns'"),
    "eventbridge": ("eventbridge", "put_events", "put_rule", "events_client"),
    "kinesis": ("kinesis", "put_record", "get_records", "subscribe_to_shard"),
}
_DEST_RE = re.compile(r"(?:QueueUrl|TopicArn|EventBusName|StreamName|queue|topic|stream)\s*[=:,]\s*[\"']([^\"']+)", re.IGNORECASE)
_OPS = {
    "produce": re.compile(r"\b(send_message|publish|put_events|put_record|put_records|put_record_batch|SendMessage|Publish|PutEvents)\b", re.IGNORECASE),
    "consume": re.compile(r"\b(receive_message|get_records|SubscribeToShard|ReceiveMessage|GetRecords)\b", re.IGNORECASE),
    "ack": re.compile(r"\b(delete_message|ack|acknowledge|DeleteMessage)\b", re.IGNORECASE),
    "retry": re.compile(r"\b(retry|redrive|visibility_timeout|backoff|attempts)\b", re.IGNORECASE),
    "dlq": re.compile(r"\b(dlq|dead.?letter|redrive_policy)\b", re.IGNORECASE),
    "idempotency": re.compile(r"\b(deduplication|message.?dedup|idempotenc|sequence_number)\b", re.IGNORECASE),
}


def _fact(kind: str, rel: str, digest: str, line: int, **measures: Any) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"k": kind, "p": rel, "l": line, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, line=line, extractor="messaging"),
        measures={key: value for key, value in measures.items() if value is not None},
        attrs={},
    )


def extract_messaging(project_root: Path, service: str = "sqs") -> CodeInventory:
    if service not in _TOKENS:
        raise ValueError(f"unsupported messaging service {service!r}")
    root = Path(project_root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    tokens = _TOKENS[service]
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in {".py", ".java", ".go", ".ts", ".js", ".yaml", ".yml", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            diagnostics.append(Diagnostic(
                code="AF-MESSAGING-READ", status=FindingStatus.UNRESOLVED,
                message=f"{path}: {exc}", source=SourceRef(path=str(path.relative_to(root)), sha256="0" * 64, extractor="messaging"),
            ))
            continue
        if not any(token.lower() in text.lower() for token in tokens):
            continue
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        input_hashes[rel] = digest
        for match in _DEST_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            facts.append(_fact("data.messaging.destination", rel, digest, line, service=service, destination=match.group(1)))
        for operation, pattern in _OPS.items():
            found = pattern.search(text)
            if found:
                line = text.count("\n", 0, found.start()) + 1
                facts.append(_fact("data.messaging.operation", rel, digest, line, service=service, operation=operation))
    return CodeInventory(
        framework=f"{service}-messaging", root=str(root),
        facts=tuple(sorted(facts, key=lambda fact: fact.fact_id)),
        diagnostics=tuple(diagnostics), input_hashes=input_hashes,
    )


def build_messaging_ir(inventory: CodeInventory, *, service: str, provider: str = "aws") -> MessagingAccessIR:
    destinations = tuple(sorted({str(f.measures["destination"]) for f in inventory.facts if f.kind == "data.messaging.destination"}))
    operations = tuple(sorted({str(f.measures["operation"]) for f in inventory.facts if f.kind == "data.messaging.operation"}))
    roles: set[Literal["producer", "consumer", "router"]] = set()
    if "produce" in operations:
        roles.add("producer")
    if "consume" in operations or "ack" in operations:
        roles.add("consumer")
    if service == "eventbridge":
        roles.add("router")
    reliability = tuple(sorted(set(operations) & {"ack", "retry", "dlq", "idempotency"}))
    return MessagingAccessIR(
        id=stable_id("messaging", {"root": inventory.root, "service": service}),
        service=cast(Literal["sqs", "sns", "eventbridge", "kinesis"], service),
        provider=provider, destinations=destinations, roles=tuple(sorted(roles)),
        operations=operations, reliability_signals=reliability,
        unresolved=tuple(sorted(d.code for d in inventory.diagnostics)),
    )


def extract_sqs(project_root: Path) -> CodeInventory:
    return extract_messaging(project_root, "sqs")


def extract_sns(project_root: Path) -> CodeInventory:
    return extract_messaging(project_root, "sns")


def extract_eventbridge(project_root: Path) -> CodeInventory:
    return extract_messaging(project_root, "eventbridge")


def extract_kinesis(project_root: Path) -> CodeInventory:
    return extract_messaging(project_root, "kinesis")

"""Static Kafka/MSK/Kinesis client extraction for Java, Go and Python."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Literal, cast

from apiforge.adapters.inventory import CodeInventory, static_execution
from apiforge.contracts.stubs import StreamingAccessIR
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_KAFKA_TOKENS = (
    "kafka-python",
    "confluent_kafka",
    "org.apache.kafka",
    "sarama",
    "segmentio/kafka-go",
    "kafkaTemplate",
    "KafkaProducer",
    "KafkaConsumer",
)
_BROKER_TOKENS = {
    "kafka": _KAFKA_TOKENS,
    "msk": _KAFKA_TOKENS,
    "kinesis": ("kinesis", "put_record", "get_records"),
    "rabbitmq": ("pika", "rabbitmq", "basic_publish", "basic_consume", "amqp"),
    "nats": ("nats", "nats.go", "subscribe", "publish"),
    "pulsar": ("pulsar", "pulsar-client", "createProducer", "createConsumer"),
}
_TOPIC_RE = re.compile(
    r"(?:topic|TOPIC|subscribe|publish|send|Produce|NewReader)\s*\(?\s*[=:]?\s*[\"']([^\"']+)",
    re.IGNORECASE,
)
_GROUP_RE = re.compile(
    r"(?:group\.id|group_id|groupId|GroupID|group)\s*[=:,]\s*[\"']([^\"']+)", re.IGNORECASE
)
_OPS = {
    "producer": re.compile(
        r"\b(KafkaProducer|Producer|produce|Produce|send|publish|WriteMessages)\b", re.IGNORECASE
    ),
    "consumer": re.compile(
        r"\b(KafkaConsumer|Consumer|consume|Consume|subscribe|ReadMessage|ReadMessages|poll)\b",
        re.IGNORECASE,
    ),
    "commit": re.compile(r"\b(commit|Commit|commitSync|commitAsync)\b"),
    "transaction": re.compile(
        r"\b(beginTransaction|commitTransaction|abortTransaction|transactional\.id)\b"
    ),
    "retry": re.compile(r"\b(retry|retries|retry\.backoff|backoff)\b", re.IGNORECASE),
    "ack": re.compile(r"\b(acks|acknowledge|acknowledg?e|enable\.idempotence)\b", re.IGNORECASE),
}


def _fact(kind: str, rel: str, digest: str, line: int, **measures: Any) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"k": kind, "p": rel, "l": line, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, line=line, extractor="streaming"),
        measures={key: value for key, value in measures.items() if value is not None},
        attrs={},
    )


def extract_streaming(project_root: Path, broker: str = "kafka") -> CodeInventory:
    """Extract declared streaming signals; no broker connection is opened."""

    if broker not in _BROKER_TOKENS:
        raise ValueError(f"unsupported streaming broker {broker!r}")
    root = Path(project_root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or path.is_symlink()
            or path.suffix.lower()
            not in {".py", ".java", ".go", ".ts", ".js", ".yaml", ".yml", ".properties"}
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            diagnostics.append(
                Diagnostic(
                    code="AF-STREAMING-READ",
                    status=FindingStatus.UNRESOLVED,
                    message=f"{path}: {exc}",
                    source=SourceRef(
                        path=str(path.relative_to(root)), sha256="0" * 64, extractor="streaming"
                    ),
                )
            )
            continue
        lowered = text.lower()
        if not any(token.lower() in lowered for token in _BROKER_TOKENS[broker]):
            continue
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        input_hashes[rel] = digest
        for match in _TOPIC_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            facts.append(
                _fact(
                    "data.streaming.topic", rel, digest, line, broker=broker, topic=match.group(1)
                )
            )
        for match in _GROUP_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            facts.append(
                _fact(
                    "data.streaming.consumer_group",
                    rel,
                    digest,
                    line,
                    broker=broker,
                    group=match.group(1),
                )
            )
        for operation, pattern in _OPS.items():
            found = pattern.search(text)
            if found:
                line = text.count("\n", 0, found.start()) + 1
                facts.append(
                    _fact(
                        "data.streaming.operation",
                        rel,
                        digest,
                        line,
                        broker=broker,
                        operation=operation,
                    )
                )
        if not any(
            fact.source.path == rel and fact.kind == "data.streaming.topic" for fact in facts
        ):
            diagnostics.append(
                Diagnostic(
                    code="AF-STREAMING-DYNAMIC-DESTINATION",
                    status=FindingStatus.UNRESOLVED,
                    message=f"{rel}: broker usage found without a statically resolvable topic or destination",
                    source=SourceRef(path=rel, sha256=digest, extractor="streaming"),
                )
            )
    return CodeInventory(
        framework=f"{broker}-streaming",
        root=str(root),
        facts=tuple(sorted(facts, key=lambda fact: fact.fact_id)),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
        execution=static_execution(
            f"streaming.{broker}",
            input_hashes,
            tuple(diagnostics),
            limitations=("does not connect to broker", "does not measure lag or throughput"),
        ),
    )


def extract_kafka(project_root: Path) -> CodeInventory:
    return extract_streaming(project_root, "kafka")


def extract_msk_access(project_root: Path) -> CodeInventory:
    return extract_streaming(project_root, "msk")


def extract_kinesis(project_root: Path) -> CodeInventory:
    return extract_streaming(project_root, "kinesis")


def extract_rabbitmq(project_root: Path) -> CodeInventory:
    return extract_streaming(project_root, "rabbitmq")


def extract_nats(project_root: Path) -> CodeInventory:
    return extract_streaming(project_root, "nats")


def extract_pulsar(project_root: Path) -> CodeInventory:
    return extract_streaming(project_root, "pulsar")


def build_streaming_ir(
    inventory: CodeInventory, *, broker: str = "kafka", provider: str = "kafka|msk"
) -> StreamingAccessIR:
    broker_name = cast(Literal["kafka", "msk", "kinesis", "rabbitmq", "nats", "pulsar"], broker)
    topics = tuple(
        sorted(
            {str(f.measures["topic"]) for f in inventory.facts if f.kind == "data.streaming.topic"}
        )
    )
    groups = tuple(
        sorted(
            {
                str(f.measures["group"])
                for f in inventory.facts
                if f.kind == "data.streaming.consumer_group"
            }
        )
    )
    operations = tuple(
        sorted(
            {
                str(f.measures["operation"])
                for f in inventory.facts
                if f.kind == "data.streaming.operation"
            }
        )
    )
    roles: set[Literal["producer", "consumer", "admin"]] = set()
    if "producer" in operations:
        roles.add("producer")
    if "consumer" in operations:
        roles.add("consumer")
    delivery = tuple(sorted(set(operations) & {"ack", "commit", "retry", "transaction"}))
    return StreamingAccessIR(
        id=stable_id("streaming", {"root": inventory.root, "broker": broker}),
        broker=broker_name,
        provider=provider,
        topics=topics,
        consumer_groups=groups,
        roles=tuple(sorted(roles)),
        operations=operations,
        delivery_signals=delivery,
        unresolved=tuple(sorted(d.code for d in inventory.diagnostics)),
    )

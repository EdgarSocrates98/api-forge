"""Collectors for the messaging services: SQS, SNS, EventBridge.

Each ``collect_*`` writes an offline dump directory (artifacts + manifest)
that a matching ``model`` reader consumes — the collector is the only code
that may touch AWS. Injected ``client`` keeps boto3 out of tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from apiforge.collectors.manifest import CollectError, CollectManifest, write_artifact


def _boto3(service: str) -> Any:
    try:
        import boto3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise CollectError(
            "AF-COLLECT-AWS",
            "boto3 is not installed; install the 'aws' extra (pip install apiforge[aws])",
        ) from exc
    return boto3.client(service)


def _call(client: Any, method: str, **kwargs: Any) -> dict[str, Any]:
    try:
        result: dict[str, Any] = getattr(client, method)(**kwargs)
        return result
    except Exception as exc:  # boto3 ClientError subclasses vary; name them all
        raise CollectError("AF-COLLECT-AWS", f"{method} failed: {exc}") from exc


def _paginate(
    client: Any, method: str, key: str, base: dict[str, Any], token: str = "NextToken"
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    kwargs = dict(base)
    while True:
        page = _call(client, method, **kwargs)
        items.extend(page.get(key, []))
        nxt = page.get(token) or page.get("nextToken")
        if not nxt:
            return items
        kwargs[token] = nxt


class _SqsClient(Protocol):
    def get_queue_attributes(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_sqs(
    queue_url: str,
    out_dir: Path,
    now: str | None = None,
    client: _SqsClient | None = None,
) -> CollectManifest:
    """Fetch the queue's attribute set as an offline dump."""
    if client is None:
        client = _boto3("sqs")
    manifest = CollectManifest(source="sqs", collected_at=now)
    attrs = _call(
        client, "get_queue_attributes", QueueUrl=queue_url, AttributeNames=["All"]
    )
    name, digest = write_artifact(out_dir, "queue.json", attrs)
    manifest.record(name, digest)
    manifest.meta["queue_url"] = queue_url
    manifest.write(out_dir)
    return manifest


class _SnsClient(Protocol):
    def get_topic_attributes(self, **kwargs: Any) -> dict[str, Any]: ...

    def list_subscriptions_by_topic(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_sns(
    topic_arn: str,
    out_dir: Path,
    now: str | None = None,
    client: _SnsClient | None = None,
) -> CollectManifest:
    """Fetch topic attributes plus its subscription list."""
    if client is None:
        client = _boto3("sns")
    manifest = CollectManifest(source="sns", collected_at=now)
    topic = _call(client, "get_topic_attributes", TopicArn=topic_arn)
    name, digest = write_artifact(out_dir, "topic.json", topic)
    manifest.record(name, digest)
    subs = _paginate(
        client,
        "list_subscriptions_by_topic",
        "Subscriptions",
        {"TopicArn": topic_arn},
    )
    name, digest = write_artifact(out_dir, "subscriptions.json", subs)
    manifest.record(name, digest)
    manifest.meta["topic_arn"] = topic_arn
    manifest.write(out_dir)
    return manifest


class _EventBridgeClient(Protocol):
    def describe_event_bus(self, **kwargs: Any) -> dict[str, Any]: ...

    def list_rules(self, **kwargs: Any) -> dict[str, Any]: ...

    def list_targets_by_rule(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_eventbridge(
    bus_name: str,
    out_dir: Path,
    now: str | None = None,
    client: _EventBridgeClient | None = None,
) -> CollectManifest:
    """Fetch the bus, its rules and every rule's targets."""
    if client is None:
        client = _boto3("events")
    manifest = CollectManifest(source="eventbridge", collected_at=now)
    bus = _call(client, "describe_event_bus", Name=bus_name)
    name, digest = write_artifact(out_dir, "event-bus.json", bus)
    manifest.record(name, digest)
    rules = _paginate(
        client, "list_rules", "Rules", {"EventBusName": bus_name}
    )
    name, digest = write_artifact(out_dir, "rules.json", rules)
    manifest.record(name, digest)
    targets = {
        str(rule["Name"]): _paginate(
            client,
            "list_targets_by_rule",
            "Targets",
            {"EventBusName": bus_name, "Rule": rule["Name"]},
        )
        for rule in rules
        if "Name" in rule
    }
    name, digest = write_artifact(out_dir, "targets.json", targets)
    manifest.record(name, digest)
    manifest.meta["event_bus"] = bus_name
    manifest.write(out_dir)
    return manifest

"""Dump readers for the messaging/identity collectors — offline, never AWS.

Each ``extract_*`` reads the directory its ``collect_*`` counterpart wrote
and emits ``aws.<svc>.*`` facts. Boolean measures record the declared
attribute (``has_redrive: false`` is a measured absence, not an inference).
Missing or malformed dump files become diagnostics naming the blind spot.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef


def _load(
    dump: Path,
    name: str,
    hashes: dict[str, str],
    diagnostics: list[Diagnostic],
    code: str,
) -> Any | None:
    path = dump / name
    rel = name
    if not path.is_file():
        diagnostics.append(
            Diagnostic(
                code=code,
                status=FindingStatus.UNRESOLVED,
                message=f"{name}: dump file missing from {dump}",
                source=None,
            )
        )
        return None
    raw = path.read_bytes()
    hashes[rel] = hashlib.sha256(raw).hexdigest()
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        diagnostics.append(
            Diagnostic(
                code=code,
                status=FindingStatus.UNRESOLVED,
                message=f"{name}: not valid JSON ({exc})",
                source=SourceRef(
                    path=rel, sha256=hashes[rel], line=None, extractor="aws-dump"
                ),
            )
        )
        return None


def _fact(
    kind: str,
    source_file: str,
    digest: str,
    measures: dict[str, Any],
    attrs: dict[str, Any],
) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"kind": kind, "file": source_file, **measures}),
        kind=kind,
        source=SourceRef(
            path=source_file, sha256=digest, line=None, extractor="aws-dump"
        ),
        measures=measures,
        attrs=attrs,
    )


def _inventory(
    framework: str,
    dump: Path,
    facts: list[Fact],
    diagnostics: list[Diagnostic],
    hashes: dict[str, str],
) -> CodeInventory:
    return CodeInventory(
        framework=framework,
        root=str(dump),
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes=hashes,
    )


def extract_sqs(dump_dir: Path) -> CodeInventory:
    """Read a `collect sqs` dump — one ``aws.sqs.queue`` fact."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    data = _load(dump, "queue.json", hashes, diagnostics, "AF-SQS-DUMP")
    if isinstance(data, dict):
        attrs = data.get("Attributes", {})
        redrive = attrs.get("RedrivePolicy")
        facts.append(
            _fact(
                "aws.sqs.queue",
                "queue.json",
                hashes["queue.json"],
                {
                    "queue_arn": attrs.get("QueueArn", ""),
                    "visibility_timeout": int(
                        attrs.get("VisibilityTimeout", 0)
                    ),
                    "message_retention": int(
                        attrs.get("MessageRetentionPeriod", 0)
                    ),
                    "has_redrive": redrive is not None,
                    "has_kms": "KmsMasterKeyId" in attrs,
                    "is_fifo": str(attrs.get("FifoQueue")) == "true",
                },
                {"redrive_policy": redrive},
            )
        )
    return _inventory("sqs", dump, facts, diagnostics, hashes)


def extract_sns(dump_dir: Path) -> CodeInventory:
    """Read a `collect sns` dump — ``aws.sns.topic`` + per-subscription facts."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    topic = _load(dump, "topic.json", hashes, diagnostics, "AF-SNS-DUMP")
    subs = _load(dump, "subscriptions.json", hashes, diagnostics, "AF-SNS-DUMP")
    if isinstance(topic, dict):
        attrs = topic.get("Attributes", {})
        facts.append(
            _fact(
                "aws.sns.topic",
                "topic.json",
                hashes["topic.json"],
                {
                    "topic_arn": attrs.get("TopicArn", ""),
                    "has_kms": "KmsMasterKeyId" in attrs,
                    "is_fifo": str(attrs.get("FifoTopic")) == "true",
                    "subscriptions_count": len(subs) if isinstance(subs, list) else 0,
                },
                {},
            )
        )
    if isinstance(subs, list):
        for sub in subs:
            if not isinstance(sub, dict):
                continue
            facts.append(
                _fact(
                    "aws.sns.subscription",
                    "subscriptions.json",
                    hashes["subscriptions.json"],
                    {
                        "protocol": sub.get("Protocol", ""),
                        "endpoint": sub.get("Endpoint", ""),
                        "confirmed": "PendingConfirmation" not in str(
                            sub.get("SubscriptionArn", "")
                        ),
                    },
                    {},
                )
            )
    return _inventory("sns", dump, facts, diagnostics, hashes)


def extract_eventbridge(dump_dir: Path) -> CodeInventory:
    """Read a `collect eventbridge` dump — bus + per-rule facts."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    rules = _load(dump, "rules.json", hashes, diagnostics, "AF-EVB-DUMP")
    targets = _load(dump, "targets.json", hashes, diagnostics, "AF-EVB-DUMP")
    _load(dump, "event-bus.json", hashes, diagnostics, "AF-EVB-DUMP")
    if isinstance(rules, list):
        target_map = targets if isinstance(targets, dict) else {}
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            name = str(rule.get("Name", ""))
            facts.append(
                _fact(
                    "aws.eventbridge.rule",
                    "rules.json",
                    hashes["rules.json"],
                    {
                        "rule": name,
                        "state": rule.get("State", ""),
                        "has_targets": bool(target_map.get(name)),
                        "has_event_pattern": "EventPattern" in rule,
                    },
                    {"schedule": rule.get("ScheduleExpression")},
                )
            )
    return _inventory("eventbridge", dump, facts, diagnostics, hashes)


def _policy_wildcards(doc: Any) -> tuple[bool, bool]:
    """(wildcard_action, wildcard_resource) across all Allow statements."""
    wild_action = wild_resource = False
    if not isinstance(doc, dict):
        return wild_action, wild_resource
    statements = doc.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]
    for st in statements:
        if not isinstance(st, dict) or st.get("Effect") != "Allow":
            continue
        actions = st.get("Action", [])
        resources = st.get("Resource", [])
        for seq, flag in ((actions, "action"), (resources, "resource")):
            values = seq if isinstance(seq, list) else [seq]
            if "*" in values:
                if flag == "action":
                    wild_action = True
                else:
                    wild_resource = True
    return wild_action, wild_resource


def extract_iam_role(dump_dir: Path) -> CodeInventory:
    """Read a `collect iam-role` dump — role fact + per-inline-policy facts."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    role = _load(dump, "role.json", hashes, diagnostics, "AF-IAM-DUMP")
    attached = _load(
        dump, "attached-policies.json", hashes, diagnostics, "AF-IAM-DUMP"
    )
    inline = _load(
        dump, "inline-policies.json", hashes, diagnostics, "AF-IAM-DUMP"
    )
    if isinstance(role, dict):
        body = role.get("Role", {})
        facts.append(
            _fact(
                "aws.iam.role",
                "role.json",
                hashes["role.json"],
                {
                    "role_arn": body.get("Arn", ""),
                    "attached_count": len(attached) if isinstance(attached, list) else 0,
                    "inline_count": len(inline) if isinstance(inline, dict) else 0,
                    "max_session_duration": int(
                        body.get("MaxSessionDuration", 0)
                    ),
                },
                {"assume_policy": body.get("AssumeRolePolicyDocument")},
            )
        )
    if isinstance(inline, dict):
        for policy_name, doc in inline.items():
            wild_action, wild_resource = _policy_wildcards(doc)
            facts.append(
                _fact(
                    "aws.iam.inline_policy",
                    "inline-policies.json",
                    hashes["inline-policies.json"],
                    {
                        "policy": str(policy_name),
                        "wildcard_action": wild_action,
                        "wildcard_resource": wild_resource,
                    },
                    {},
                )
            )
    return _inventory("iam-role", dump, facts, diagnostics, hashes)


def extract_cognito(dump_dir: Path) -> CodeInventory:
    """Read a `collect cognito` dump — pool fact + per-client facts."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    pool = _load(dump, "user-pool.json", hashes, diagnostics, "AF-COG-DUMP")
    clients = _load(dump, "clients.json", hashes, diagnostics, "AF-COG-DUMP")
    if isinstance(pool, dict):
        body = pool.get("UserPool", {})
        facts.append(
            _fact(
                "aws.cognito.user_pool",
                "user-pool.json",
                hashes["user-pool.json"],
                {
                    "pool_id": body.get("Id", ""),
                    "mfa": body.get("MfaConfiguration", ""),
                    "deletion_protection": body.get("DeletionProtection", "")
                    == "ACTIVE",
                    "advanced_security": str(
                        body.get("UserPoolAddOns", {}).get(
                            "AdvancedSecurityMode", ""
                        )
                    ),
                },
                {},
            )
        )
    if isinstance(clients, list):
        for client in clients:
            if not isinstance(client, dict):
                continue
            facts.append(
                _fact(
                    "aws.cognito.client",
                    "clients.json",
                    hashes["clients.json"],
                    {
                        "client_id": client.get("ClientId", ""),
                        "has_secret": bool(client.get("ClientSecret")),
                    },
                    {},
                )
            )
    return _inventory("cognito", dump, facts, diagnostics, hashes)


def extract_waf(dump_dir: Path) -> CodeInventory:
    """Read a `collect waf` dump — ``aws.waf.web_acl`` + per-rule facts."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    data = _load(dump, "web-acl.json", hashes, diagnostics, "AF-WAF-DUMP")
    if isinstance(data, dict):
        acl = data.get("WebACL", {})
        rules = acl.get("Rules", [])
        facts.append(
            _fact(
                "aws.waf.web_acl",
                "web-acl.json",
                hashes["web-acl.json"],
                {
                    "acl_name": acl.get("Name", ""),
                    "scope": acl.get("Scope", ""),
                    "default_action": next(
                        iter(acl.get("DefaultAction", {"none": True}).keys()),
                        "unknown",
                    ),
                    "rules_count": len(rules),
                    "has_managed_rules": any(
                        "ManagedRuleGroupStatement" in (
                            r.get("Statement", {}) if isinstance(r, dict) else {}
                        )
                        for r in rules
                    ),
                },
                {},
            )
        )
    return _inventory("waf", dump, facts, diagnostics, hashes)


def extract_dynamodb(dump_dir: Path) -> CodeInventory:
    """Read a `collect dynamodb` dump — ``aws.dynamodb.table`` fact."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    table = _load(dump, "table.json", hashes, diagnostics, "AF-DDB-DUMP")
    backups = _load(dump, "backups.json", hashes, diagnostics, "AF-DDB-DUMP")
    if isinstance(table, dict):
        body = table.get("Table", {})
        pitr = (
            backups.get("ContinuousBackupsDescription", {})
            .get("PointInTimeRecoveryDescription", {})
            .get("PointInTimeRecoveryStatus", "")
            if isinstance(backups, dict)
            else ""
        )
        facts.append(
            _fact(
                "aws.dynamodb.table",
                "table.json",
                hashes["table.json"],
                {
                    "table": body.get("TableName", ""),
                    "billing_mode": body.get(
                        "BillingModeSummary", {}
                    ).get("BillingMode", "PROVISIONED"),
                    "pitr_enabled": pitr == "ENABLED",
                    "deletion_protection": bool(
                        body.get("DeletionProtectionEnabled")
                    ),
                },
                {},
            )
        )
    return _inventory("dynamodb", dump, facts, diagnostics, hashes)


def _extract_db_cluster(
    dump_dir: Path, service: str, code: str
) -> CodeInventory:
    """Shared DocDB/Neptune reader — `engine` in the dump disambiguates."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    data = _load(dump, "cluster.json", hashes, diagnostics, code)
    if isinstance(data, dict):
        for cluster in data.get("DBClusters", []):
            if not isinstance(cluster, dict):
                continue
            facts.append(
                _fact(
                    f"aws.{service}.cluster",
                    "cluster.json",
                    hashes["cluster.json"],
                    {
                        "cluster": cluster.get("DBClusterIdentifier", ""),
                        "engine": cluster.get("Engine", ""),
                        "storage_encrypted": bool(
                            cluster.get("StorageEncrypted")
                        ),
                        "deletion_protection": bool(
                            cluster.get("DeletionProtection")
                        ),
                        "multi_az": bool(cluster.get("MultiAZ")),
                    },
                    {},
                )
            )
    return _inventory(service, dump, facts, diagnostics, hashes)


def extract_docdb(dump_dir: Path) -> CodeInventory:
    """Read a `collect docdb` dump — ``aws.docdb.cluster`` facts."""
    return _extract_db_cluster(dump_dir, "docdb", "AF-DOCDB-DUMP")


def extract_neptune(dump_dir: Path) -> CodeInventory:
    """Read a `collect neptune` dump — ``aws.neptune.cluster`` facts."""
    return _extract_db_cluster(dump_dir, "neptune", "AF-NEPTUNE-DUMP")


def extract_stepfunctions(dump_dir: Path) -> CodeInventory:
    """Read a `collect stepfunctions` dump — ``aws.sfn.state_machine`` fact."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    data = _load(dump, "state-machine.json", hashes, diagnostics, "AF-SFN-DUMP")
    if isinstance(data, dict):
        logging = data.get("loggingConfiguration", {})
        tracing = data.get("tracingConfiguration", {})
        facts.append(
            _fact(
                "aws.sfn.state_machine",
                "state-machine.json",
                hashes["state-machine.json"],
                {
                    "name": data.get("name", ""),
                    "type": data.get("type", "STANDARD"),
                    "logging_level": logging.get("level", "OFF"),
                    "has_tracing": bool(tracing.get("enabled")),
                },
                {},
            )
        )
    return _inventory("stepfunctions", dump, facts, diagnostics, hashes)


def extract_cloudwatch(dump_dir: Path) -> CodeInventory:
    """Read a `collect cloudwatch` dump — ``aws.cloudwatch.alarm`` facts."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    alarms = _load(dump, "alarms.json", hashes, diagnostics, "AF-CW-DUMP")
    if isinstance(alarms, list):
        for alarm in alarms:
            if not isinstance(alarm, dict):
                continue
            facts.append(
                _fact(
                    "aws.cloudwatch.alarm",
                    "alarms.json",
                    hashes["alarms.json"],
                    {
                        "alarm": alarm.get("AlarmName", ""),
                        "state": alarm.get("StateValue", ""),
                        "actions_enabled": bool(alarm.get("ActionsEnabled")),
                        "has_actions": bool(alarm.get("AlarmActions")),
                    },
                    {},
                )
            )
    return _inventory("cloudwatch", dump, facts, diagnostics, hashes)


def extract_xray(dump_dir: Path) -> CodeInventory:
    """Read a `collect xray` dump — sampling coverage + encryption facts."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    rules = _load(
        dump, "sampling-rules.json", hashes, diagnostics, "AF-XRAY-DUMP"
    )
    enc = _load(
        dump, "encryption-config.json", hashes, diagnostics, "AF-XRAY-DUMP"
    )
    if isinstance(rules, list):
        facts.append(
            _fact(
                "aws.xray.sampling",
                "sampling-rules.json",
                hashes["sampling-rules.json"],
                {"rules_count": len(rules)},
                {},
            )
        )
    if isinstance(enc, dict):
        facts.append(
            _fact(
                "aws.xray.encryption",
                "encryption-config.json",
                hashes["encryption-config.json"],
                {"encryption_type": enc.get("Type", ""), "status": enc.get("Status", "")},
                {},
            )
        )
    return _inventory("xray", dump, facts, diagnostics, hashes)


def extract_kms(dump_dir: Path) -> CodeInventory:
    """Read a `collect kms` dump — ``aws.kms.key`` fact."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    key = _load(dump, "key.json", hashes, diagnostics, "AF-KMS-DUMP")
    rotation = _load(dump, "rotation.json", hashes, diagnostics, "AF-KMS-DUMP")
    if isinstance(key, dict):
        meta = key.get("KeyMetadata", {})
        rot = rotation.get("KeyRotationEnabled") if isinstance(rotation, dict) else None
        facts.append(
            _fact(
                "aws.kms.key",
                "key.json",
                hashes["key.json"],
                {
                    "key_id": meta.get("KeyId", ""),
                    "key_state": meta.get("KeyState", ""),
                    "key_manager": meta.get("KeyManager", ""),
                    "rotation_enabled": rot,
                    # crossed from two declared fields — AWS-managed keys
                    # cannot rotate, so they never trip this measure
                    "customer_key_without_rotation": (
                        meta.get("KeyManager") == "CUSTOMER" and rot is False
                    ),
                },
                {},
            )
        )
    return _inventory("kms", dump, facts, diagnostics, hashes)




def extract_secrets(dump_dir: Path) -> CodeInventory:
    """Read a `collect secrets` dump — metadata only, values never present."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    secret = _load(
        dump, "secret.json", hashes, diagnostics, "AF-SECRETS-DUMP"
    )
    if isinstance(secret, dict):
        facts.append(
            _fact(
                "aws.secrets.secret",
                "secret.json",
                hashes["secret.json"],
                {
                    "name": secret.get("Name", ""),
                    "rotation_enabled": bool(secret.get("RotationEnabled")),
                    "has_kms": "KmsKeyId" in secret,
                },
                {},
            )
        )
    return _inventory("secrets", dump, facts, diagnostics, hashes)


def extract_vpc_endpoints(dump_dir: Path) -> CodeInventory:
    """Read a `collect vpc-endpoints` dump — ``aws.vpc.endpoint`` facts."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    endpoints = _load(
        dump, "endpoints.json", hashes, diagnostics, "AF-VPC-DUMP"
    )
    if isinstance(endpoints, list):
        for ep in endpoints:
            if not isinstance(ep, dict):
                continue
            measures: dict[str, Any] = {
                "endpoint_id": ep.get("VpcEndpointId", ""),
                "type": ep.get("VpcEndpointType", ""),
                "service": ep.get("ServiceName", ""),
            }
            # Gateway endpoints have no private-DNS concept — the measure is
            # emitted only for Interface, where the field is applicable.
            if ep.get("VpcEndpointType") == "Interface":
                measures["private_dns_enabled"] = bool(
                    ep.get("PrivateDnsEnabled")
                )
            facts.append(
                _fact(
                    "aws.vpc.endpoint",
                    "endpoints.json",
                    hashes["endpoints.json"],
                    measures,
                    {},
                )
            )
    return _inventory("vpc-endpoints", dump, facts, diagnostics, hashes)


def extract_s3(dump_dir: Path) -> CodeInventory:
    """Read a `collect s3` dump — ``aws.s3.bucket`` posture fact."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    facts: list[Fact] = []
    enc = _load(dump, "encryption.json", hashes, diagnostics, "AF-S3-DUMP")
    public = _load(dump, "public-access.json", hashes, diagnostics, "AF-S3-DUMP")
    vers = _load(dump, "versioning.json", hashes, diagnostics, "AF-S3-DUMP")
    if any(v is not None for v in (enc, public, vers)):
        pab = (
            public.get("PublicAccessBlockConfiguration", {})
            if isinstance(public, dict) and "absent" not in public
            else {}
        )
        facts.append(
            _fact(
                "aws.s3.bucket",
                "encryption.json",
                hashes.get("encryption.json", ""),
                {
                    "has_encryption": isinstance(enc, dict)
                    and "ServerSideEncryptionConfiguration" in enc,
                    "public_access_blocked": all(
                        pab.get(k) is True
                        for k in (
                            "BlockPublicAcls",
                            "IgnorePublicAcls",
                            "BlockPublicPolicy",
                            "RestrictPublicBuckets",
                        )
                    ),
                    "versioning": (
                        vers.get("Status", "") if isinstance(vers, dict) else ""
                    ),
                },
                {
                    "absent_artifacts": [
                        n
                        for n, v in (
                            ("encryption.json", enc),
                            ("public-access.json", public),
                            ("versioning.json", vers),
                        )
                        if isinstance(v, dict) and "absent" in v
                    ]
                },
            )
        )
    return _inventory("s3", dump, facts, diagnostics, hashes)

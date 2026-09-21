"""Spec H — collectors write canonical dumps; readers turn them into facts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.adapters.awsdumps import (
    extract_cognito,
    extract_eventbridge,
    extract_iam_role,
    extract_sns,
    extract_sqs,
    extract_waf,
)
from apiforge.collectors.identity import (
    collect_cognito,
    collect_iam_role,
    collect_waf,
)
from apiforge.collectors.manifest import CollectError
from apiforge.collectors.messaging import (
    collect_eventbridge,
    collect_sns,
    collect_sqs,
)
from apiforge.rules.fact_judge import judge_facts


def _findings(inv, rule_id: str):
    return [f for f in judge_facts(inv.facts) if f.rule_id == rule_id]


class _SqsStub:
    def get_queue_attributes(self, **kw):
        return {
            "Attributes": {
                "QueueArn": "arn:aws:sqs:us-east-1:1:orders",
                "VisibilityTimeout": "30",
                "MessageRetentionPeriod": "345600",
                "KmsMasterKeyId": "arn:aws:kms:us-east-1:1:key/k",
            }
        }


class _SnsStub:
    def get_topic_attributes(self, **kw):
        return {"Attributes": {"TopicArn": "arn:aws:sns:us-east-1:1:orders"}}

    def list_subscriptions_by_topic(self, **kw):
        return {
            "Subscriptions": [
                {
                    "Protocol": "sqs",
                    "Endpoint": "arn:aws:sqs:us-east-1:1:q",
                    "SubscriptionArn": "arn:aws:sns:us-east-1:1:orders:abc",
                },
                {
                    "Protocol": "lambda",
                    "Endpoint": "arn:aws:lambda:us-east-1:1:function:f",
                    "SubscriptionArn": "PendingConfirmation",
                },
            ]
        }


class _EventsStub:
    def describe_event_bus(self, **kw):
        return {"Name": "default", "Arn": "arn:aws:events:us-east-1:1:event-bus/default"}

    def list_rules(self, **kw):
        return {
            "Rules": [
                {"Name": "r-live", "State": "ENABLED", "EventPattern": "{}"},
                {"Name": "r-dead", "State": "ENABLED", "EventPattern": "{}"},
            ]
        }

    def list_targets_by_rule(self, **kw):
        if kw["Rule"] == "r-live":
            return {"Targets": [{"Id": "t1", "Arn": "arn:aws:lambda:..."}]}
        return {"Targets": []}


class _IamStub:
    def get_role(self, **kw):
        return {
            "Role": {"Arn": "arn:aws:iam::1:role/api", "MaxSessionDuration": 43200}
        }

    def list_attached_role_policies(self, **kw):
        return {
            "AttachedPolicies": [{"PolicyName": "p1", "PolicyArn": "arn:aws:iam::aws:p"}],
            "IsTruncated": False,
        }

    def list_role_policies(self, **kw):
        return {"PolicyNames": ["wild"]}

    def get_role_policy(self, **kw):
        return {
            "PolicyDocument": {
                "Statement": [
                    {"Effect": "Allow", "Action": "*", "Resource": ["*"]}
                ]
            }
        }


class _CognitoStub:
    def describe_user_pool(self, **kw):
        return {
            "UserPool": {
                "Id": "us-east-1_x",
                "MfaConfiguration": "OFF",
                "DeletionProtection": "INACTIVE",
            }
        }

    def list_user_pool_clients(self, **kw):
        return {"UserPoolClients": [{"ClientId": "c1"}]}


class _WafStub:
    def get_web_acl(self, **kw):
        return {
            "WebACL": {
                "Name": "edge",
                "Scope": "REGIONAL",
                "DefaultAction": {"Allow": {}},
                "Rules": [{"Name": "r", "Statement": {}}],
            }
        }


def _kinds(inv):
    return [f.kind for f in inv.facts]


def test_sqs_dump_to_facts(tmp_path: Path) -> None:
    collect_sqs("https://sqs/q", tmp_path, now="2026-09-21T00:00:00Z", client=_SqsStub())
    inv = extract_sqs(tmp_path)
    assert _kinds(inv) == ["aws.sqs.queue"]
    q = inv.facts[0]
    assert q.measures["has_redrive"] is False
    assert q.measures["has_kms"] is True
    assert inv.diagnostics == ()


def test_sns_dump_to_facts(tmp_path: Path) -> None:
    collect_sns("arn:aws:sns:t", tmp_path, client=_SnsStub())
    inv = extract_sns(tmp_path)
    assert _kinds(inv) == ["aws.sns.topic", "aws.sns.subscription", "aws.sns.subscription"]
    pending = [f for f in inv.facts if f.measures.get("confirmed") is False]
    assert len(pending) == 1 and pending[0].measures["protocol"] == "lambda"
    findings = _findings(inv, "AF-MSG-003")
    assert len(findings) == 1


def test_eventbridge_rule_without_targets_fires(tmp_path: Path) -> None:
    collect_eventbridge("default", tmp_path, client=_EventsStub())
    inv = extract_eventbridge(tmp_path)
    by_name = {f.measures["rule"]: f for f in inv.facts}
    assert by_name["r-live"].measures["has_targets"] is True
    assert by_name["r-dead"].measures["has_targets"] is False
    findings = _findings(inv, "AF-MSG-004")
    assert len(findings) == 1


def test_iam_wildcards_measured(tmp_path: Path) -> None:
    collect_iam_role("api", tmp_path, client=_IamStub())
    inv = extract_iam_role(tmp_path)
    inline = next(f for f in inv.facts if f.kind == "aws.iam.inline_policy")
    assert inline.measures["wildcard_action"] is True
    assert inline.measures["wildcard_resource"] is True
    for rid in ("AF-IAM-001", "AF-IAM-002"):
        assert _findings(inv, rid), rid


def test_cognito_posture_facts(tmp_path: Path) -> None:
    collect_cognito("us-east-1_x", tmp_path, client=_CognitoStub())
    inv = extract_cognito(tmp_path)
    pool = next(f for f in inv.facts if f.kind == "aws.cognito.user_pool")
    assert pool.measures["mfa"] == "OFF"
    assert pool.measures["deletion_protection"] is False
    for rid in ("AF-IAM-004", "AF-IAM-005"):
        assert _findings(inv, rid), rid


def test_waf_allow_default_fires(tmp_path: Path) -> None:
    collect_waf("id", "edge", "REGIONAL", tmp_path, client=_WafStub())
    inv = extract_waf(tmp_path)
    acl = inv.facts[0]
    assert acl.measures["default_action"] == "Allow"
    assert acl.measures["has_managed_rules"] is False
    for rid in ("AF-SEC-105", "AF-SEC-106"):
        assert _findings(inv, rid), rid


def test_waf_scope_refused(tmp_path: Path) -> None:
    with pytest.raises(CollectError, match="AF-COLLECT-ARG"):
        collect_waf("id", "edge", "GLOBAL", tmp_path, client=_WafStub())


def test_missing_dump_is_diagnostic(tmp_path: Path) -> None:
    inv = extract_sqs(tmp_path)
    assert inv.facts == ()
    assert inv.diagnostics[0].code == "AF-SQS-DUMP"


def test_manifest_records_hashes(tmp_path: Path) -> None:
    manifest = collect_sqs("https://sqs/q", tmp_path, client=_SqsStub())
    stored = json.loads((tmp_path / "manifest.json").read_text())
    assert stored["source"] == "sqs"
    assert manifest.artifacts["queue.json"] == stored["artifacts"]["queue.json"]

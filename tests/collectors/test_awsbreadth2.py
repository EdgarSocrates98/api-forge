"""Spec H batch 2 — datastore/ops collectors and their offline readers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.adapters.awsdumps import (
    extract_cloudwatch,
    extract_docdb,
    extract_dynamodb,
    extract_kms,
    extract_neptune,
    extract_s3,
    extract_secrets,
    extract_stepfunctions,
    extract_vpc_endpoints,
    extract_xray,
)
from apiforge.collectors.datastores import (
    collect_docdb,
    collect_dynamodb,
    collect_neptune,
)
from apiforge.collectors.manifest import CollectError
from apiforge.collectors.ops import (
    collect_cloudwatch,
    collect_kms,
    collect_s3,
    collect_secrets,
    collect_stepfunctions,
    collect_vpc_endpoints,
    collect_xray,
)
from apiforge.rules.fact_judge import judge_facts


def _findings(inv, rule_id: str):
    return [f for f in judge_facts(inv.facts) if f.rule_id == rule_id]


def _kinds(inv):
    return [f.kind for f in inv.facts]


class _DynamoStub:
    def describe_table(self, **kw):
        return {
            "Table": {
                "TableName": "orders",
                "BillingModeSummary": {"BillingMode": "PAY_PER_REQUEST"},
                "DeletionProtectionEnabled": False,
            }
        }

    def describe_continuous_backups(self, **kw):
        return {
            "ContinuousBackupsDescription": {
                "PointInTimeRecoveryDescription": {
                    "PointInTimeRecoveryStatus": "DISABLED"
                }
            }
        }


class _DocdbStub:
    def describe_db_clusters(self, **kw):
        return {
            "DBClusters": [
                {
                    "DBClusterIdentifier": "docs",
                    "Engine": "docdb",
                    "StorageEncrypted": False,
                    "DeletionProtection": False,
                    "MultiAZ": True,
                }
            ]
        }


class _NeptuneStub:
    def describe_db_clusters(self, **kw):
        return {
            "DBClusters": [
                {
                    "DBClusterIdentifier": "graph",
                    "Engine": "neptune",
                    "StorageEncrypted": True,
                    "DeletionProtection": True,
                    "MultiAZ": False,
                }
            ]
        }


class _SfnStub:
    def describe_state_machine(self, **kw):
        return {
            "name": "order-flow",
            "type": "STANDARD",
            "loggingConfiguration": {"level": "OFF"},
            "tracingConfiguration": {"enabled": False},
        }


class _CloudWatchStub:
    def describe_alarms(self, **kw):
        return {
            "MetricAlarms": [
                {
                    "AlarmName": "api-5xx",
                    "StateValue": "OK",
                    "ActionsEnabled": True,
                    "AlarmActions": ["arn:aws:sns:t"],
                },
                {
                    "AlarmName": "api-latency",
                    "StateValue": "INSUFFICIENT_DATA",
                    "ActionsEnabled": False,
                    "AlarmActions": [],
                },
            ]
        }


class _XrayStub:
    def get_sampling_rules(self, **kw):
        return {"SamplingRuleRecords": [{"SamplingRule": {"RuleName": "d"}}]}

    def get_encryption_config(self, **kw):
        return {"Type": "KMS", "Status": "ACTIVE"}


class _KmsStub:
    _rotation = True
    _manager = "CUSTOMER"

    def describe_key(self, **kw):
        return {
            "KeyMetadata": {
                "KeyId": "k-1",
                "KeyState": "Enabled",
                "KeyManager": self._manager,
            }
        }

    def get_key_rotation_status(self, **kw):
        return {"KeyRotationEnabled": self._rotation}


class _SecretsStub:
    def describe_secret(self, **kw):
        return {
            "ARN": "arn:aws:secretsmanager:us-east-1:1:secret:db",
            "Name": "db",
            "RotationEnabled": False,
            "KmsKeyId": "k-1",
        }


class _Ec2Stub:
    def describe_vpc_endpoints(self, **kw):
        return {
            "VpcEndpoints": [
                {
                    "VpcEndpointId": "vpce-1",
                    "VpcEndpointType": "Interface",
                    "ServiceName": "com.amazonaws.us-east-1.sqs",
                    "PrivateDnsEnabled": False,
                },
                {
                    "VpcEndpointId": "vpce-2",
                    "VpcEndpointType": "Gateway",
                    "ServiceName": "com.amazonaws.us-east-1.s3",
                },
            ]
        }


class _NamedAwsError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


class _S3Stub:
    _encryption_error: Exception | None = None

    def get_bucket_encryption(self, **kw):
        if self._encryption_error is not None:
            raise self._encryption_error
        return {
            "ServerSideEncryptionConfiguration": {
                "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms"}}]
            }
        }

    def get_public_access_block(self, **kw):
        return {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": False,
            }
        }

    def get_bucket_versioning(self, **kw):
        return {"Status": "Enabled"}


NOW = "2026-09-21T00:00:00Z"


def test_dynamodb_posture(tmp_path: Path) -> None:
    collect_dynamodb("orders", tmp_path, now=NOW, client=_DynamoStub())
    inv = extract_dynamodb(tmp_path)
    assert _kinds(inv) == ["aws.dynamodb.table"]
    table = inv.facts[0]
    assert table.measures["pitr_enabled"] is False
    assert table.measures["deletion_protection"] is False
    assert table.measures["billing_mode"] == "PAY_PER_REQUEST"
    for rid in ("AF-STORE-001", "AF-STORE-002"):
        assert _findings(inv, rid), rid


def test_docdb_unencrypted_fires(tmp_path: Path) -> None:
    collect_docdb("docs", tmp_path, client=_DocdbStub())
    inv = extract_docdb(tmp_path)
    cluster = inv.facts[0]
    assert cluster.kind == "aws.docdb.cluster"
    assert cluster.measures["engine"] == "docdb"
    assert cluster.measures["storage_encrypted"] is False
    assert _findings(inv, "AF-STORE-003")


def test_neptune_encrypted_is_clean(tmp_path: Path) -> None:
    collect_neptune("graph", tmp_path, client=_NeptuneStub())
    inv = extract_neptune(tmp_path)
    cluster = inv.facts[0]
    assert cluster.kind == "aws.neptune.cluster"
    assert cluster.measures["storage_encrypted"] is True
    assert not _findings(inv, "AF-STORE-004")


def test_stepfunctions_silent_machine(tmp_path: Path) -> None:
    collect_stepfunctions("arn:aws:states:m", tmp_path, client=_SfnStub())
    inv = extract_stepfunctions(tmp_path)
    machine = inv.facts[0]
    assert machine.kind == "aws.sfn.state_machine"
    assert machine.measures["logging_level"] == "OFF"
    assert machine.measures["has_tracing"] is False
    assert _findings(inv, "AF-STORE-005")
    assert _findings(inv, "AF-OBS-003")


def test_cloudwatch_silent_alarm(tmp_path: Path) -> None:
    collect_cloudwatch("api-", tmp_path, client=_CloudWatchStub())
    inv = extract_cloudwatch(tmp_path)
    by_name = {f.measures["alarm"]: f for f in inv.facts}
    assert by_name["api-5xx"].measures["actions_enabled"] is True
    assert by_name["api-latency"].measures["has_actions"] is False
    assert len(_findings(inv, "AF-OBS-001")) == 1
    assert len(_findings(inv, "AF-OBS-002")) == 1


def test_xray_facts(tmp_path: Path) -> None:
    collect_xray(tmp_path, client=_XrayStub())
    inv = extract_xray(tmp_path)
    assert _kinds(inv) == ["aws.xray.sampling", "aws.xray.encryption"]
    enc = inv.facts[1]
    assert enc.measures["encryption_type"] == "KMS"


def test_kms_customer_key_without_rotation(tmp_path: Path) -> None:
    stub = _KmsStub()
    stub._rotation = False
    collect_kms("k-1", tmp_path, client=stub)
    inv = extract_kms(tmp_path)
    key = inv.facts[0]
    assert key.measures["customer_key_without_rotation"] is True
    assert _findings(inv, "AF-SEC-107")


def test_kms_aws_managed_never_trips_rotation(tmp_path: Path) -> None:
    stub = _KmsStub()
    stub._manager = "AWS"
    stub._rotation = False
    collect_kms("alias/aws/x", tmp_path, client=stub)
    inv = extract_kms(tmp_path)
    key = inv.facts[0]
    assert key.measures["key_manager"] == "AWS"
    assert key.measures["customer_key_without_rotation"] is False
    assert not _findings(inv, "AF-SEC-107")


def test_secrets_metadata_only(tmp_path: Path) -> None:
    collect_secrets("db", tmp_path, client=_SecretsStub())
    stored = json.loads((tmp_path / "secret.json").read_text())
    assert "SecretString" not in stored
    assert "SecretBinary" not in stored
    inv = extract_secrets(tmp_path)
    secret = inv.facts[0]
    assert secret.kind == "aws.secrets.secret"
    assert secret.measures["rotation_enabled"] is False
    assert _findings(inv, "AF-SEC-108")


def test_vpc_endpoint_private_dns(tmp_path: Path) -> None:
    collect_vpc_endpoints("vpc-1", tmp_path, client=_Ec2Stub())
    inv = extract_vpc_endpoints(tmp_path)
    by_id = {f.measures["endpoint_id"]: f for f in inv.facts}
    assert by_id["vpce-1"].measures["private_dns_enabled"] is False
    # gateway endpoints have no private-DNS concept — no measure emitted
    assert "private_dns_enabled" not in by_id["vpce-2"].measures
    assert len(_findings(inv, "AF-GW-008")) == 1


def test_s3_posture_partial_public_block(tmp_path: Path) -> None:
    collect_s3("bkt", tmp_path, client=_S3Stub())
    inv = extract_s3(tmp_path)
    bucket = inv.facts[0]
    assert bucket.kind == "aws.s3.bucket"
    assert bucket.measures["has_encryption"] is True
    assert bucket.measures["public_access_blocked"] is False
    assert bucket.measures["versioning"] == "Enabled"
    assert _findings(inv, "AF-SEC-109")
    assert not _findings(inv, "AF-SEC-110")


def test_s3_absent_encryption_is_measured(tmp_path: Path) -> None:
    stub = _S3Stub()
    stub._encryption_error = _NamedAwsError("ServerSideEncryptionConfigurationNotFoundError")
    collect_s3("bkt", tmp_path, client=stub)
    artifact = json.loads((tmp_path / "encryption.json").read_text())
    assert artifact == {"absent": "ServerSideEncryptionConfigurationNotFoundError"}
    inv = extract_s3(tmp_path)
    bucket = inv.facts[0]
    assert bucket.measures["has_encryption"] is False
    assert "encryption.json" in bucket.attrs["absent_artifacts"]
    assert _findings(inv, "AF-SEC-110")


def test_s3_unknown_error_propagates(tmp_path: Path) -> None:
    class _Broken(_S3Stub):
        def get_bucket_encryption(self, **kw):
            raise RuntimeError("network")

    with pytest.raises(CollectError, match="AF-COLLECT-AWS"):
        collect_s3("bkt", tmp_path, client=_Broken())


def test_missing_dumps_are_diagnostics(tmp_path: Path) -> None:
    for extract, code in (
        (extract_dynamodb, "AF-DDB-DUMP"),
        (extract_docdb, "AF-DOCDB-DUMP"),
        (extract_neptune, "AF-NEPTUNE-DUMP"),
        (extract_stepfunctions, "AF-SFN-DUMP"),
        (extract_cloudwatch, "AF-CW-DUMP"),
        (extract_xray, "AF-XRAY-DUMP"),
        (extract_kms, "AF-KMS-DUMP"),
        (extract_secrets, "AF-SECRETS-DUMP"),
        (extract_vpc_endpoints, "AF-VPC-DUMP"),
        (extract_s3, "AF-S3-DUMP"),
    ):
        inv = extract(tmp_path / "empty")
        assert inv.facts == ()
        assert inv.diagnostics[0].code == code

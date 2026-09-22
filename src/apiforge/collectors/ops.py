"""Ops/posture collectors: Step Functions, CloudWatch alarms, X-Ray config,
KMS key, Secrets Manager metadata, VPC endpoints, S3 bucket posture.

``collect_secrets`` reads *metadata* only — ``GetSecretValue`` is never
called; a secret's value must never appear in a dump.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from apiforge.collectors.manifest import CollectManifest, write_artifact
from apiforge.collectors.messaging import _boto3, _call, _paginate


class _SfnClient(Protocol):
    def describe_state_machine(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_stepfunctions(
    state_machine_arn: str,
    out_dir: Path,
    now: str | None = None,
    client: _SfnClient | None = None,
) -> CollectManifest:
    """Fetch the state machine description (definition included)."""
    if client is None:
        client = _boto3("stepfunctions")
    manifest = CollectManifest(source="stepfunctions", collected_at=now)
    machine = _call(
        client, "describe_state_machine", stateMachineArn=state_machine_arn
    )
    name, digest = write_artifact(out_dir, "state-machine.json", machine)
    manifest.record(name, digest)
    manifest.meta["state_machine_arn"] = state_machine_arn
    manifest.write(out_dir)
    return manifest


class _CloudWatchClient(Protocol):
    def describe_alarms(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_cloudwatch(
    alarm_name_prefix: str,
    out_dir: Path,
    now: str | None = None,
    client: _CloudWatchClient | None = None,
) -> CollectManifest:
    """Fetch all metric alarms matching a name prefix (paginated)."""
    if client is None:
        client = _boto3("cloudwatch")
    manifest = CollectManifest(source="cloudwatch", collected_at=now)
    alarms = _paginate(
        client,
        "describe_alarms",
        "MetricAlarms",
        {"AlarmNamePrefix": alarm_name_prefix},
    )
    name, digest = write_artifact(out_dir, "alarms.json", alarms)
    manifest.record(name, digest)
    manifest.meta["alarm_name_prefix"] = alarm_name_prefix
    manifest.write(out_dir)
    return manifest


class _XrayClient(Protocol):
    def get_sampling_rules(self, **kwargs: Any) -> dict[str, Any]: ...

    def get_encryption_config(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_xray(
    out_dir: Path,
    now: str | None = None,
    client: _XrayClient | None = None,
) -> CollectManifest:
    """Fetch sampling rules and the encryption configuration."""
    if client is None:
        client = _boto3("xray")
    manifest = CollectManifest(source="xray", collected_at=now)
    rules = _paginate(client, "get_sampling_rules", "SamplingRuleRecords", {})
    name, digest = write_artifact(out_dir, "sampling-rules.json", rules)
    manifest.record(name, digest)
    enc = _call(client, "get_encryption_config")
    name, digest = write_artifact(out_dir, "encryption-config.json", enc)
    manifest.record(name, digest)
    manifest.write(out_dir)
    return manifest


class _KmsClient(Protocol):
    def describe_key(self, **kwargs: Any) -> dict[str, Any]: ...

    def get_key_rotation_status(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_kms(
    key_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _KmsClient | None = None,
) -> CollectManifest:
    """Fetch the key's metadata and rotation status."""
    if client is None:
        client = _boto3("kms")
    manifest = CollectManifest(source="kms", collected_at=now)
    key = _call(client, "describe_key", KeyId=key_id)
    name, digest = write_artifact(out_dir, "key.json", key)
    manifest.record(name, digest)
    rotation = _call(client, "get_key_rotation_status", KeyId=key_id)
    name, digest = write_artifact(out_dir, "rotation.json", rotation)
    manifest.record(name, digest)
    manifest.meta["key_id"] = key_id
    manifest.write(out_dir)
    return manifest


class _SecretsClient(Protocol):
    def describe_secret(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_secrets(
    secret_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _SecretsClient | None = None,
) -> CollectManifest:
    """Fetch the secret's *metadata* — ``GetSecretValue`` is never called."""
    if client is None:
        client = _boto3("secretsmanager")
    manifest = CollectManifest(source="secrets", collected_at=now)
    secret = _call(client, "describe_secret", SecretId=secret_id)
    name, digest = write_artifact(out_dir, "secret.json", secret)
    manifest.record(name, digest)
    manifest.meta["secret_id"] = secret_id
    manifest.write(out_dir)
    return manifest


class _Ec2Client(Protocol):
    def describe_vpc_endpoints(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_vpc_endpoints(
    vpc_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _Ec2Client | None = None,
) -> CollectManifest:
    """Fetch the VPC's endpoints (gateway and interface)."""
    if client is None:
        client = _boto3("ec2")
    manifest = CollectManifest(source="vpc-endpoints", collected_at=now)
    endpoints = _paginate(
        client,
        "describe_vpc_endpoints",
        "VpcEndpoints",
        {"Filters": [{"Name": "vpc-id", "Values": [vpc_id]}]},
    )
    name, digest = write_artifact(out_dir, "endpoints.json", endpoints)
    manifest.record(name, digest)
    manifest.meta["vpc_id"] = vpc_id
    manifest.write(out_dir)
    return manifest


class _S3Client(Protocol):
    def get_bucket_encryption(self, **kwargs: Any) -> dict[str, Any]: ...

    def get_public_access_block(self, **kwargs: Any) -> dict[str, Any]: ...

    def get_bucket_versioning(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_s3(
    bucket: str,
    out_dir: Path,
    now: str | None = None,
    client: _S3Client | None = None,
) -> CollectManifest:
    """Fetch the bucket's encryption, public-access-block and versioning.

    A missing encryption configuration answers with a named diagnostic
    marker (``{"absent": "NoSuchBucketEncryption"}``) — the reader records
    the absence as measured, never inferred.
    """
    if client is None:
        client = _boto3("s3")
    manifest = CollectManifest(source="s3", collected_at=now)
    for name, method in (
        ("encryption.json", "get_bucket_encryption"),
        ("public-access.json", "get_public_access_block"),
        ("versioning.json", "get_bucket_versioning"),
    ):
        try:
            payload = getattr(client, method)(Bucket=bucket)
        except Exception as exc:  # ClientError subclasses vary
            # S3 answers unset configuration with a named error — record the
            # error code as the artifact so the reader sees measured absence.
            code = getattr(exc, "response", {}).get("Error", {}).get("Code")
            if code is None:
                from apiforge.collectors.manifest import CollectError

                raise CollectError(
                    "AF-COLLECT-AWS", f"{method} failed: {exc}"
                ) from exc
            payload = {"absent": code}
        artifact, digest = write_artifact(out_dir, name, payload)
        manifest.record(artifact, digest)
    manifest.meta["bucket"] = bucket
    manifest.write(out_dir)
    return manifest

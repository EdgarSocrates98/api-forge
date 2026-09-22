"""Datastore collectors: DynamoDB table, DocDB cluster, Neptune cluster.

Same contract: offline dump directory, injected client, canonical artifacts.
DocDB and Neptune share ``rds:DescribeDBClusters`` — the ``engine`` field in
the dump is what distinguishes them, and the reader records it as measured.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from apiforge.collectors.manifest import CollectManifest, write_artifact
from apiforge.collectors.messaging import _boto3, _call


class _DynamoClient(Protocol):
    def describe_table(self, **kwargs: Any) -> dict[str, Any]: ...

    def describe_continuous_backups(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_dynamodb(
    table_name: str,
    out_dir: Path,
    now: str | None = None,
    client: _DynamoClient | None = None,
) -> CollectManifest:
    """Fetch the table description plus its continuous-backup (PITR) status."""
    if client is None:
        client = _boto3("dynamodb")
    manifest = CollectManifest(source="dynamodb", collected_at=now)
    table = _call(client, "describe_table", TableName=table_name)
    name, digest = write_artifact(out_dir, "table.json", table)
    manifest.record(name, digest)
    backups = _call(
        client, "describe_continuous_backups", TableName=table_name
    )
    name, digest = write_artifact(out_dir, "backups.json", backups)
    manifest.record(name, digest)
    manifest.meta["table_name"] = table_name
    manifest.write(out_dir)
    return manifest


class _DocdbClient(Protocol):
    def describe_db_clusters(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_docdb(
    cluster_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _DocdbClient | None = None,
) -> CollectManifest:
    """Fetch the DocDB cluster description."""
    if client is None:
        client = _boto3("docdb")
    manifest = CollectManifest(source="docdb", collected_at=now)
    clusters = _call(
        client, "describe_db_clusters", DBClusterIdentifier=cluster_id
    )
    name, digest = write_artifact(out_dir, "cluster.json", clusters)
    manifest.record(name, digest)
    manifest.meta["cluster_id"] = cluster_id
    manifest.write(out_dir)
    return manifest


class _NeptuneClient(Protocol):
    def describe_db_clusters(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_neptune(
    cluster_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _NeptuneClient | None = None,
) -> CollectManifest:
    """Fetch the Neptune cluster description."""
    if client is None:
        client = _boto3("neptune")
    manifest = CollectManifest(source="neptune", collected_at=now)
    clusters = _call(
        client, "describe_db_clusters", DBClusterIdentifier=cluster_id
    )
    name, digest = write_artifact(out_dir, "cluster.json", clusters)
    manifest.record(name, digest)
    manifest.meta["cluster_id"] = cluster_id
    manifest.write(out_dir)
    return manifest


class _RdsClient(Protocol):
    def describe_db_instances(self, **kwargs: Any) -> dict[str, Any]: ...
    def describe_db_clusters(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_rds(
    resource_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _RdsClient | None = None,
) -> CollectManifest:
    """Collect RDS/Aurora posture into an offline dump."""
    if client is None:
        client = _boto3("rds")
    manifest = CollectManifest(source="rds", collected_at=now)
    instances = _call(client, "describe_db_instances", DBInstanceIdentifier=resource_id)
    name, digest = write_artifact(out_dir, "instances.json", instances)
    manifest.record(name, digest)
    clusters = _call(client, "describe_db_clusters", DBClusterIdentifier=resource_id)
    name, digest = write_artifact(out_dir, "clusters.json", clusters)
    manifest.record(name, digest)
    manifest.meta["resource_id"] = resource_id
    manifest.write(out_dir)
    return manifest

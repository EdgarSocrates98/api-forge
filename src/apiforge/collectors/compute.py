"""Compute/load-balancer collectors: ALB, ECS, EKS, EC2, MSK, ElastiCache.

Same contract as the other collectors: offline dump directory, injected
client, canonical artifacts. ECS collects posture for every service in a
cluster (the unit of API exposure there); EC2 collects per-instance
posture — describe-only, never user-data or console output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from apiforge.collectors.manifest import (
    CollectError,
    CollectManifest,
    write_artifact,
)
from apiforge.collectors.messaging import _boto3, _call, _paginate


class _ElbClient(Protocol):
    def describe_load_balancers(self, **kwargs: Any) -> dict[str, Any]: ...

    def describe_listeners(self, **kwargs: Any) -> dict[str, Any]: ...

    def describe_target_groups(self, **kwargs: Any) -> dict[str, Any]: ...

    def describe_load_balancer_attributes(
        self, **kwargs: Any
    ) -> dict[str, Any]: ...


def collect_alb(
    lb_arn: str,
    out_dir: Path,
    now: str | None = None,
    client: _ElbClient | None = None,
) -> CollectManifest:
    """Fetch the load balancer, its listeners, target groups, attributes."""
    if client is None:
        client = _boto3("elbv2")
    manifest = CollectManifest(source="alb", collected_at=now)
    lb = _call(client, "describe_load_balancers", LoadBalancerArns=[lb_arn])
    name, digest = write_artifact(out_dir, "load-balancer.json", lb)
    manifest.record(name, digest)
    listeners = _paginate(
        client, "describe_listeners", "Listeners", {"LoadBalancerArn": lb_arn}
    )
    name, digest = write_artifact(out_dir, "listeners.json", listeners)
    manifest.record(name, digest)
    groups = _paginate(
        client,
        "describe_target_groups",
        "TargetGroups",
        {"LoadBalancerArn": lb_arn},
    )
    name, digest = write_artifact(out_dir, "target-groups.json", groups)
    manifest.record(name, digest)
    attrs = _call(
        client, "describe_load_balancer_attributes", LoadBalancerArn=lb_arn
    )
    name, digest = write_artifact(out_dir, "attributes.json", attrs)
    manifest.record(name, digest)
    manifest.meta["load_balancer_arn"] = lb_arn
    manifest.write(out_dir)
    return manifest


class _EcsClient(Protocol):
    def list_services(self, **kwargs: Any) -> dict[str, Any]: ...

    def describe_services(self, **kwargs: Any) -> dict[str, Any]: ...

    def describe_task_definition(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_ecs(
    cluster: str,
    out_dir: Path,
    now: str | None = None,
    client: _EcsClient | None = None,
) -> CollectManifest:
    """Fetch every service in the cluster plus its task definitions."""
    if client is None:
        client = _boto3("ecs")
    manifest = CollectManifest(source="ecs", collected_at=now)
    service_arns = _paginate(
        client, "list_services", "serviceArns", {"cluster": cluster}
    )
    services: dict[str, Any] = {"services": [], "failures": []}
    for i in range(0, len(service_arns), 10):
        batch = _call(
            client,
            "describe_services",
            cluster=cluster,
            services=service_arns[i : i + 10],
        )
        services["services"].extend(batch.get("services", []))
        services["failures"].extend(batch.get("failures", []))
    name, digest = write_artifact(out_dir, "services.json", services)
    manifest.record(name, digest)
    task_defs: dict[str, Any] = {"taskDefinitions": [], "failures": []}
    seen: set[str] = set()
    for svc in services["services"]:
        td = svc.get("taskDefinition")
        if td and td not in seen:
            seen.add(td)
            try:
                body = _call(client, "describe_task_definition", taskDefinition=td)
            except CollectError:
                task_defs["failures"].append({"arn": td, "reason": "describe failed"})
                continue
            if isinstance(body.get("taskDefinition"), dict):
                task_defs["taskDefinitions"].append(body["taskDefinition"])
    name, digest = write_artifact(out_dir, "task-definitions.json", task_defs)
    manifest.record(name, digest)
    manifest.meta["cluster"] = cluster
    manifest.write(out_dir)
    return manifest


class _EksClient(Protocol):
    def describe_cluster(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_eks(
    cluster_name: str,
    out_dir: Path,
    now: str | None = None,
    client: _EksClient | None = None,
) -> CollectManifest:
    """Fetch the EKS cluster description."""
    if client is None:
        client = _boto3("eks")
    manifest = CollectManifest(source="eks", collected_at=now)
    cluster = _call(client, "describe_cluster", name=cluster_name)
    name, digest = write_artifact(out_dir, "cluster.json", cluster)
    manifest.record(name, digest)
    manifest.meta["cluster_name"] = cluster_name
    manifest.write(out_dir)
    return manifest


class _Ec2Client(Protocol):
    def describe_instances(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_ec2(
    instance_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _Ec2Client | None = None,
) -> CollectManifest:
    """Fetch the instance description — posture only, never user-data."""
    if client is None:
        client = _boto3("ec2")
    manifest = CollectManifest(source="ec2", collected_at=now)
    instances = _call(client, "describe_instances", InstanceIds=[instance_id])
    name, digest = write_artifact(out_dir, "instances.json", instances)
    manifest.record(name, digest)
    manifest.meta["instance_id"] = instance_id
    manifest.write(out_dir)
    return manifest


class _MskClient(Protocol):
    def describe_cluster(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_msk(
    cluster_arn: str,
    out_dir: Path,
    now: str | None = None,
    client: _MskClient | None = None,
) -> CollectManifest:
    """Fetch the MSK cluster description (broker/encryption/logging posture)."""
    if client is None:
        client = _boto3("kafka")
    manifest = CollectManifest(source="msk", collected_at=now)
    cluster = _call(client, "describe_cluster", ClusterArn=cluster_arn)
    name, digest = write_artifact(out_dir, "cluster.json", cluster)
    manifest.record(name, digest)
    manifest.meta["cluster_arn"] = cluster_arn
    manifest.write(out_dir)
    return manifest


class _ElastiCacheClient(Protocol):
    def describe_replication_groups(self, **kwargs: Any) -> dict[str, Any]: ...


def collect_elasticache(
    replication_group_id: str,
    out_dir: Path,
    now: str | None = None,
    client: _ElastiCacheClient | None = None,
) -> CollectManifest:
    """Fetch the replication group — encryption/failover posture only."""
    if client is None:
        client = _boto3("elasticache")
    manifest = CollectManifest(source="elasticache", collected_at=now)
    group = _call(
        client,
        "describe_replication_groups",
        ReplicationGroupId=replication_group_id,
    )
    name, digest = write_artifact(out_dir, "replication-group.json", group)
    manifest.record(name, digest)
    manifest.meta["replication_group_id"] = replication_group_id
    manifest.write(out_dir)
    return manifest

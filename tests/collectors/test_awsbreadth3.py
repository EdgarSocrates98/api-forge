"""Spec H batch 3 — compute collectors (ALB/ECS/EKS/EC2/MSK/ElastiCache)."""

from __future__ import annotations

from pathlib import Path

from apiforge.adapters.awsdumps import (
    extract_alb,
    extract_ec2,
    extract_ecs,
    extract_eks,
    extract_elasticache,
    extract_msk,
)
from apiforge.collectors.compute import (
    collect_alb,
    collect_ec2,
    collect_ecs,
    collect_eks,
    collect_elasticache,
    collect_msk,
)
from apiforge.rules.fact_judge import judge_facts


def _findings(inv, rule_id: str):
    return [f for f in judge_facts(inv.facts) if f.rule_id == rule_id]


class _ElbStub:
    def describe_load_balancers(self, **kw):
        return {
            "LoadBalancers": [
                {
                    "LoadBalancerArn": "arn:lb",
                    "Scheme": "internet-facing",
                    "Type": "application",
                    "DNSName": "lb.example.com",
                }
            ]
        }

    def describe_listeners(self, **kw):
        return {
            "Listeners": [
                {"ListenerArn": "arn:l80", "Protocol": "HTTP", "Port": 80},
                {"ListenerArn": "arn:l443", "Protocol": "HTTPS", "Port": 443},
            ]
        }

    def describe_target_groups(self, **kw):
        return {
            "TargetGroups": [
                {
                    "TargetGroupArn": "arn:tg",
                    "Protocol": "HTTP",
                    "HealthCheckEnabled": True,
                }
            ]
        }

    def describe_load_balancer_attributes(self, **kw):
        return {
            "Attributes": [
                {"Key": "access_logs.s3.enabled", "Value": "false"},
                {"Key": "deletion_protection.enabled", "Value": "true"},
            ]
        }


def test_alb_plain_http_on_internet_facing(tmp_path: Path) -> None:
    collect_alb("arn:lb", tmp_path, client=_ElbStub())
    inv = extract_alb(tmp_path)
    assert not inv.diagnostics
    listeners = [f for f in inv.facts if f.kind == "aws.alb.listener"]
    assert len(listeners) == 2
    http = next(f for f in listeners if f.measures["port"] == 80)
    assert http.measures["internet_facing_plain_http"] is True
    https = next(f for f in listeners if f.measures["port"] == 443)
    assert https.measures["internet_facing_plain_http"] is False
    assert _findings(inv, "AF-SEC-111")  # the HTTP listener fires
    assert _findings(inv, "AF-SEC-112")  # access logs disabled


def test_alb_internal_http_no_false_positive(tmp_path: Path) -> None:
    class Internal(_ElbStub):
        def describe_load_balancers(self, **kw):
            return {
                "LoadBalancers": [
                    {
                        "LoadBalancerArn": "arn:lb",
                        "Scheme": "internal",
                        "Type": "application",
                    }
                ]
            }

        def describe_load_balancer_attributes(self, **kw):
            return {
                "Attributes": [
                    {"Key": "access_logs.s3.enabled", "Value": "true"},
                ]
            }

    collect_alb("arn:lb", tmp_path, client=Internal())
    inv = extract_alb(tmp_path)
    assert not _findings(inv, "AF-SEC-111")
    assert not _findings(inv, "AF-SEC-112")


class _EcsStub:
    def list_services(self, **kw):
        return {"serviceArns": ["arn:svc/api", "arn:svc/web"], "nextToken": None}

    def describe_services(self, **kw):
        return {
            "services": [
                {
                    "serviceName": a.split("/")[-1],
                    "serviceArn": a,
                    "desiredCount": 2,
                    "launchType": "FARGATE",
                    "taskDefinition": "arn:td/api:1",
                    "deploymentConfiguration": {
                        "minimumHealthyPercent": 50,
                        "deploymentCircuitBreaker": {
                            "enable": True,
                            "rollback": True,
                        },
                    },
                }
                for a in kw["services"]
            ],
            "failures": [],
        }

    def describe_task_definition(self, **kw):
        return {
            "taskDefinition": {
                "taskDefinitionArn": kw["taskDefinition"],
                "cpu": "512",
                "memory": "1024",
            }
        }


def test_ecs_service_posture(tmp_path: Path) -> None:
    collect_ecs("prod", tmp_path, client=_EcsStub())
    inv = extract_ecs(tmp_path)
    services = [f for f in inv.facts if f.kind == "aws.ecs.service"]
    assert len(services) == 2
    assert all(f.measures["circuit_breaker_enabled"] for f in services)
    assert all(f.measures["launch_type"] == "FARGATE" for f in services)
    # describe_task_definition called once for the shared task def
    td = tmp_path / "task-definitions.json"
    assert td.is_file()


class _EksStub:
    def describe_cluster(self, **kw):
        return {
            "cluster": {
                "name": "api",
                "version": "1.30",
                "resourcesVpcConfig": {
                    "endpointPublicAccess": True,
                    "endpointPrivateAccess": False,
                },
                "logging": {"clusterLogging": [{"types": ["api"], "enabled": True}]},
                "encryptionConfig": [{"provider": {"keyArn": "arn:kms"}}],
            }
        }


def test_eks_public_endpoint_fires(tmp_path: Path) -> None:
    collect_eks("api", tmp_path, client=_EksStub())
    inv = extract_eks(tmp_path)
    assert _findings(inv, "AF-SEC-115")
    assert not _findings(inv, "AF-OBS-004")  # api logging enabled


def test_eks_silent_control_plane(tmp_path: Path) -> None:
    class Silent(_EksStub):
        def describe_cluster(self, **kw):
            return {
                "cluster": {
                    "name": "api",
                    "version": "1.30",
                    "resourcesVpcConfig": {"endpointPublicAccess": False},
                    "logging": {"clusterLogging": [{"types": [], "enabled": False}]},
                }
            }

    collect_eks("api", tmp_path, client=Silent())
    inv = extract_eks(tmp_path)
    assert _findings(inv, "AF-OBS-004")
    assert not _findings(inv, "AF-SEC-115")


class _Ec2Stub:
    def describe_instances(self, **kw):
        return {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1",
                            "InstanceType": "t3.large",
                            "PublicIpAddress": "54.1.2.3",
                            "MetadataOptions": {"HttpTokens": "optional"},
                            "Monitoring": {"State": "enabled"},
                        }
                    ]
                }
            ]
        }


def test_ec2_posture(tmp_path: Path) -> None:
    collect_ec2("i-1", tmp_path, client=_Ec2Stub())
    inv = extract_ec2(tmp_path)
    assert _findings(inv, "AF-SEC-113")  # IMDSv2 optional
    assert _findings(inv, "AF-SEC-114")  # public IP


class _MskStub:
    def describe_cluster(self, **kw):
        return {
            "ClusterInfo": {
                "ClusterName": "events",
                "EncryptionInfo": {"EncryptionInTransit": {"ClientBroker": "TLS_PLAINTEXT"}},
                "BrokerNodeGroupInfo": {
                    "ConnectivityInfo": {"PublicAccess": {"Type": "SERVICE_PROVIDED_EIPS"}}
                },
                "LoggingInfo": {"BrokerLogs": {"CloudWatchLogs": {"Enabled": False}}},
            }
        }


def test_msk_posture(tmp_path: Path) -> None:
    collect_msk("arn:kafka:c", tmp_path, client=_MskStub())
    inv = extract_msk(tmp_path)
    assert _findings(inv, "AF-SEC-116")  # plaintext allowed
    assert _findings(inv, "AF-OBS-005")  # no broker log destination
    msk = inv.facts[0]
    assert msk.measures["public_access"] is True


class _ElastiCacheStub:
    def describe_replication_groups(self, **kw):
        return {
            "ReplicationGroups": [
                {
                    "ReplicationGroupId": "sessions",
                    "TransitEncryptionEnabled": False,
                    "AtRestEncryptionEnabled": False,
                    "AuthTokenEnabled": False,
                    "AutomaticFailover": "disabled",
                    "SnapshotRetentionLimit": 0,
                }
            ]
        }


def test_elasticache_posture(tmp_path: Path) -> None:
    collect_elasticache("sessions", tmp_path, client=_ElastiCacheStub())
    inv = extract_elasticache(tmp_path)
    assert _findings(inv, "AF-STORE-006")
    assert _findings(inv, "AF-STORE-007")


def test_missing_dump_names_the_blind_spot(tmp_path: Path) -> None:
    inv = extract_eks(tmp_path)
    assert not inv.facts
    assert any(d.code == "AF-EKS-DUMP" for d in inv.diagnostics)

from pathlib import Path

from apiforge.collectors.datastores import collect_rds


class FakeRds:
    def describe_db_instances(self, **kwargs: object) -> dict[str, object]:
        return {"DBInstances": [{"DBInstanceIdentifier": kwargs["DBInstanceIdentifier"]}]}

    def describe_db_clusters(self, **kwargs: object) -> dict[str, object]:
        return {"DBClusters": [{"DBClusterIdentifier": kwargs["DBClusterIdentifier"]}]}


def test_collect_rds_writes_instance_and_cluster_posture(tmp_path: Path) -> None:
    manifest = collect_rds("orders-db", tmp_path, now="2026-09-22T00:00:00Z", client=FakeRds())
    assert manifest.source == "rds"
    assert set(manifest.artifacts) == {"instances.json", "clusters.json"}
    assert (tmp_path / "manifest.json").is_file()

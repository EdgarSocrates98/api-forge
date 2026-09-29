import json
from pathlib import Path

from apiforge.adapters.http_targets import extract_http_targets
from apiforge.contracts.workspace import RepositoryRef, WorkspaceManifest
from apiforge.workspace.graph import build_graph, repository_node_id
from apiforge.workspace.inference import infer_relations
from apiforge.workspace.inference.match import template

PAYMENT_API = """from fastapi import FastAPI

app = FastAPI()


@app.post("/authorize")
def authorize() -> dict:
    return {}
"""
PRODUCER = """from kafka import KafkaProducer

producer = KafkaProducer()
producer.send("payment.authorized", b"ok")
"""
CONSUMER = """from kafka import KafkaConsumer

TOPIC = "payment.authorized"
consumer = KafkaConsumer(TOPIC)
for message in consumer.poll():
    print(message)
"""


def _repo(root: Path, name: str, files: dict[str, str]) -> RepositoryRef:
    directory = root / name
    directory.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        (directory / rel).write_text(text, encoding="utf-8")
    return RepositoryRef(repository_id=f"repository:{name}", name=name, root=str(directory))


def _manifest(root: Path, *repos: RepositoryRef) -> WorkspaceManifest:
    return WorkspaceManifest(workspace_id="ws", name="ws", root=str(root), repositories=repos)


def _flow(root: Path) -> WorkspaceManifest:
    return _manifest(
        root,
        _repo(
            root,
            "web",
            {
                "client.py": 'import requests\nrequests.post("http://payment-service:8080/authorize", json={})\n'
            },
        ),
        _repo(root, "payment-service", {"main.py": PAYMENT_API, "events.py": PRODUCER}),
        _repo(root, "order-service", {"worker.py": CONSUMER}),
    )


def test_http_call_infers_edge_with_provenance(tmp_path: Path) -> None:
    result = infer_relations(_flow(tmp_path))
    calls = [edge for edge in result.relations if edge.relation == "calls"]
    assert len(calls) == 1
    edge = calls[0]
    assert edge.from_id == repository_node_id("repository:web")
    assert edge.to_id == repository_node_id("repository:payment-service")
    assert edge.evidence.level == "inferred"
    assert edge.evidence.confidence == 0.95
    assert "web:client.py:2" in edge.evidence.refs
    assert any(ref.startswith("payment-service:") for ref in edge.evidence.refs)


def test_topic_infers_producer_to_consumer_edge(tmp_path: Path) -> None:
    result = infer_relations(_flow(tmp_path))
    events = [edge for edge in result.relations if edge.relation == "publishes_to_consumer"]
    assert len(events) == 1
    edge = events[0]
    assert edge.from_id == repository_node_id("repository:payment-service")
    assert edge.to_id == repository_node_id("repository:order-service")
    assert "topic:payment.authorized" in edge.evidence.refs
    assert edge.evidence.confidence == 0.85


def test_ambiguous_target_is_capped_and_unresolved(tmp_path: Path) -> None:
    manifest = _manifest(
        tmp_path,
        _repo(tmp_path, "gateway", {"c.py": 'import httpx\nhttpx.post(f"{BASE}/authorize")\n'}),
        _repo(tmp_path, "payments-a", {"main.py": PAYMENT_API}),
        _repo(tmp_path, "payments-b", {"main.py": PAYMENT_API}),
    )
    result = infer_relations(manifest)
    calls = [edge for edge in result.relations if edge.relation == "calls"]
    assert len(calls) == 2
    assert all((edge.evidence.confidence or 0) <= 0.45 for edge in calls)
    assert any("AF-WORKSPACE-INFER-AMBIGUOUS" in item for item in result.unresolved)


def test_default_graph_has_no_inferred_edges(tmp_path: Path) -> None:
    manifest = _flow(tmp_path)
    plain = build_graph(manifest)
    assert all(edge.evidence.level != "inferred" for edge in plain.edges)
    assert plain.evidence_level == "declared"
    again = build_graph(manifest, inferred=())
    assert json.dumps(plain.model_dump(mode="json"), sort_keys=True) == json.dumps(
        again.model_dump(mode="json"), sort_keys=True
    )
    result = infer_relations(manifest)
    enriched = build_graph(manifest, inferred=result.relations)
    assert enriched.evidence_level == "inferred"
    assert len(enriched.edges) == len(plain.edges) + len(result.relations)


def test_http_target_extractor_variants(tmp_path: Path) -> None:
    (tmp_path / "a.ts").write_text(
        'await fetch(`${API}/orders/${id}`, { method: "DELETE" });\naxios.get("/customers/42")\n',
        encoding="utf-8",
    )
    (tmp_path / "b.go").write_text(
        'req, _ := http.NewRequestWithContext(ctx, http.MethodPost, "http://inventory/reserve", nil)\n'
        'resp, _ := http.Get("http://catalog/items")\n',
        encoding="utf-8",
    )
    (tmp_path / "C.java").write_text(
        'rest.postForObject("http://fraud-service/check/{id}", body, Result.class);\n',
        encoding="utf-8",
    )
    (tmp_path / "d.py").write_text('requests.get(url)\nrequests.get("health")\n', encoding="utf-8")
    found = {
        (fact.measures["method"], fact.measures["path"], fact.measures["base_hint"])
        for fact in extract_http_targets(tmp_path)
    }
    assert ("DELETE", "/orders/${id}", "API") in found
    assert ("GET", "/customers/42", "") in found
    assert ("POST", "/reserve", "inventory") in found
    assert ("GET", "/items", "catalog") in found
    assert ("POST", "/check/{id}", "fraud-service") in found
    assert not any(item[1] == "health" for item in found)


def test_template_normalization() -> None:
    assert template("/orders/{id}/") == template("/orders/:id") == template("/orders/<int:id>")
    assert template("/a//b") == "/a/b"


def test_infer_cli_is_audited_and_blocks_baseline_record(tmp_path: Path, monkeypatch) -> None:
    import pytest
    from typer.testing import CliRunner

    from apiforge.cli import app
    from apiforge.field.errors import FieldError
    from apiforge.field.record import record
    from apiforge.workspace.service import WorkspaceService
    from tests.field.support import ENDED, STARTED, corpus, runtime_run

    flow = _flow(tmp_path / "repos")
    service = WorkspaceService(tmp_path)
    for repository in flow.repositories:
        service.add(Path(repository.root))
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    plain = runner.invoke(app, ["workspace", "graph", "--root", str(tmp_path)])
    assert plain.exit_code == 0, plain.output
    assert '"inferred"' not in plain.output
    unattributed = runner.invoke(app, ["workspace", "graph", "--infer", "--root", str(tmp_path)])
    assert "AF-WORKSPACE-INFER-UNATTRIBUTED" in unattributed.output
    audited = runner.invoke(
        app, ["workspace", "graph", "--infer", "--run-id", "run-1", "--root", str(tmp_path)]
    )
    assert audited.exit_code == 0, audited.output
    payload = json.loads(audited.output)
    assert payload["evidence_level"] == "inferred"
    assert {edge["relation"] for edge in payload["edges"]} >= {"calls", "publishes_to_consumer"}
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1")
    with pytest.raises(FieldError) as exc:
        record(
            tmp_path,
            task_id="T001",
            run_ids=("run-1",),
            phase="baseline",
            started_at=STARTED,
            ended_at=ENDED,
            executor="agent:api-orchestrator",
        )
    assert exc.value.code == "AF-FIELD-FLAG-CONTAMINATION"

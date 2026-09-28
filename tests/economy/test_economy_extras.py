from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.contracts.agentic import AgentScorecard
from apiforge.contracts.base import ContractError
from apiforge.economy.doctor import diagnose
from apiforge.economy.providers import decide_tier
from apiforge.evidence.resolve import resolve
from apiforge.knowledge.retrieval import expand, search
from apiforge.mcp import tools
from apiforge.runtime.prompting import envelope
from apiforge.verification.selection import plan_verification
from tests.context.gateway_support import analyzed_root

REPO = Path(__file__).resolve().parents[2]
TEST = "proj/tests/test_payments.py"
runner = CliRunner()


@pytest.fixture(scope="module")
def root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return analyzed_root(tmp_path_factory.mktemp("extras"), "fastapi")


def test_verification_ladder_follows_risk_and_selects_impacted_tests(root: Path) -> None:
    low = plan_verification(root, ["proj/app/routes/payments.py"], risk="low")
    assert low.level == "V2" and [t.path for t in low.tests] == [TEST]
    assert any(reason.startswith("mentions:") for reason in low.tests[0].reasons)
    assert low.executes is False and low.commands == (f"pytest {TEST}",)
    assert plan_verification(root, ["proj/app/routes/payments.py"], risk="high").level == "V5"
    assert (
        plan_verification(root, ["proj/app/routes/payments.py"], risk="low", breaking=True).level
        == "V4"
    )
    empty = plan_verification(root, ["proj/app/routes/customers.py"], risk="low")
    assert empty.level == "V5" and any("no-impacted-tests-found" in r for r in empty.reasons)
    with pytest.raises(ContractError) as bad:
        plan_verification(root, [], risk="enormous")
    assert bad.value.code == "AF-VERIFY-RISK-INVALID"


def test_retrieval_expands_ranks_and_tiers(tmp_path: Path) -> None:
    terms, added = expand("breaking endpoint")
    assert "compatibility" in added and "breaking" in terms
    first = search("breaking endpoint", store_root=tmp_path)
    assert len(first.passages) == 3 and first.next_tier == 2
    assert first.passages[0].pack_id == "api-lifecycle"
    assert all(p.ref.startswith("ctx://sha256/") for p in first.passages)
    second = search("breaking endpoint", tier=2, store_root=tmp_path)
    assert [p.ref for p in second.passages[:3]] == [p.ref for p in first.passages]
    nothing = search("zzqx", store_root=tmp_path)
    assert nothing.passages == () and nothing.unresolved == ("no-passage-matched",)


def test_evidence_refs_resolve_one_hop(root: Path) -> None:
    operation = resolve(root, "evidence://operation/POST /payments")
    assert operation.neighbors and all(
        ref.startswith("evidence://fact/") for ref in operation.neighbors
    )
    fact = resolve(root, operation.neighbors[0])
    assert operation.ref in fact.neighbors and fact.source_ref is not None
    for bad, code in (
        ("ctx://x", "AF-EVIDENCE-REF-INVALID"),
        ("evidence://fact/nope", "AF-EVIDENCE-NOT-FOUND"),
    ):
        with pytest.raises(ContractError) as refused:
            resolve(root, bad)
        assert refused.value.code == code


def test_doctor_reports_cache_off_and_deep_default(root: Path, monkeypatch) -> None:
    monkeypatch.setenv("APIFORGE_CACHE", "off")
    (root / ".apiforge" / "project.yaml").write_text(
        "schema: apiforge/project/v1\nproject_id: project:x\nname: x\nroot: .\neconomy_profile: deep\n",
        encoding="utf-8",
    )
    report = diagnose(root)
    codes = {item.code for item in report.findings}
    assert "AF-ECONOMY-DOCTOR-CACHE-OFF" in codes
    assert report.status == "attention"
    assert all(item.unlock for item in report.findings)
    (root / ".apiforge" / "project.yaml").unlink()


def test_tiers_need_evidence_to_go_cheaper() -> None:
    assert decide_tier("contract.compatibility.rest", "high").tier == "T0"
    assert decide_tier("api-security-review", "high").tier == "T3"
    assert decide_tier("api-contract-review", "low").tier == "T2"
    proof = AgentScorecard(
        agent="local",
        profile_id="openapi-review@T1",
        evaluation_count=40,
        passed_count=39,
        quality_score=0.97,
        quality_promoted=True,
        freshness_state="fresh",
    )
    cheap = decide_tier("api-contract-review", "low", family="openapi-review", scorecards=(proof,))
    assert cheap.tier == "T1" and "0.97" in cheap.reason


def test_prompt_prefix_is_stable_per_capability() -> None:
    one = envelope(REPO, "api-contract-review", task="a", expertise=("openapi-31",))
    two = envelope(REPO, "api-contract-review", task="b", expertise=("openapi-31",))
    other = envelope(REPO, "task-review", task="a")
    assert one.prefix_sha256 == two.prefix_sha256 != other.prefix_sha256
    assert one.suffix != two.suffix and "task" not in json.loads(one.prefix)


def test_locality_orders_target_direct_and_defers_transitive(tmp_path: Path) -> None:
    import yaml

    from apiforge.workspace.locality import plan_locality

    names = ["payments", "contracts", "billing", "customers"]
    for name in names:
        (tmp_path / name).mkdir()
    (tmp_path / "workspace.yaml").write_text(
        yaml.safe_dump(
            {
                "schema": "apiforge/workspace/v1",
                "workspace_id": "workspace:t",
                "name": "t",
                "root": ".",
                "repositories": [
                    {"repository_id": f"repository:{n}", "name": n, "root": n} for n in names
                ],
                "relations": [
                    {
                        "relation": "depends_on",
                        "source": "workspace.yaml",
                        "from_id": "repository:payments",
                        "to_id": "repository:contracts",
                    },
                    {
                        "relation": "depends_on",
                        "source": "workspace.yaml",
                        "from_id": "repository:contracts",
                        "to_id": "repository:billing",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    plan = plan_locality(tmp_path, "payments")
    tiers = {tier.tier: tier for tier in plan.tiers}
    assert tiers["direct"].repositories == ("contracts",)
    assert tiers["transitive"].repositories == ("billing",) and not tiers["transitive"].included
    assert plan.excluded == ("billing", "customers")
    assert plan_locality(tmp_path, "payments", transitive=True).excluded == ("customers",)


def test_cli_and_mcp_parity(root: Path) -> None:
    args = [
        "verify",
        "plan",
        "--changed",
        "proj/app/models.py",
        "--risk",
        "medium",
        "--root",
        str(root),
    ]
    cli = json.loads(runner.invoke(app, args).output)
    assert cli == tools.verify_plan(["proj/app/models.py"], risk="medium", root=str(root))
    tier = json.loads(
        runner.invoke(app, ["economy", "tier", "--capability", "api-contract-review"]).output
    )
    assert tier["tier"] == "T2"
    ref = "evidence://operation/POST /payments"
    assert json.loads(
        runner.invoke(app, ["evidence", "resolve", ref, "--root", str(root)]).output
    ) == (tools.evidence_resolve(ref, root=str(root)))
    doctor = runner.invoke(app, ["doctor", "--economy", "--root", str(root)])
    assert (
        doctor.exit_code == 0
        and json.loads(doctor.output)["schema"] == "apiforge/economy-doctor/v1"
    )

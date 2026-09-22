from apiforge.contracts.agentic import AgenticPolicy, AgenticRun, AgenticState
from apiforge.contracts.registry import CONTRACTS


def test_agentic_contracts_are_registered_and_policy_is_bounded() -> None:
    assert {"AgenticRun/v1", "AgenticRuntime/v1", "AgenticPolicy/v1"} <= set(CONTRACTS)
    assert AgenticPolicy(policy_id="local").max_parallel_agents == 4
    run = AgenticRun(run_id="r", task_id="t", revision=1, state=AgenticState.CREATED, policy_id="local", started_at="now")
    assert run.state is AgenticState.CREATED

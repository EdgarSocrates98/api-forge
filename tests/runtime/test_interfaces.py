from apiforge.mcp.tools import runtime_debate, runtime_resume, runtime_run, runtime_status


def test_runtime_interface_exports_are_callable() -> None:
    assert all(callable(item) for item in (runtime_run, runtime_status, runtime_resume, runtime_debate))

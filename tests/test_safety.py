from apiforge.safety import REQUIRED_API_CONTROLS, assess_api_safety


def _controls(value: bool | None = True) -> dict[str, bool | None]:
    return {name: value for name in REQUIRED_API_CONTROLS}


def test_complete_safety_controls_are_ready() -> None:
    result = assess_api_safety("orders-api", _controls())
    assert result.status == "ready"
    assert len(result.passed_controls) == len(REQUIRED_API_CONTROLS)


def test_missing_safety_control_requires_review() -> None:
    controls = _controls()
    controls["circuit_breaker"] = None
    result = assess_api_safety("orders-api", controls)
    assert result.status == "review"
    assert result.missing_controls == ("circuit_breaker",)


def test_failed_safety_control_blocks() -> None:
    controls = _controls()
    controls["authentication"] = False
    controls["retry_policy"] = False
    result = assess_api_safety("orders-api", controls)
    assert result.status == "blocked"
    assert result.failed_controls == ("authentication", "retry_policy")

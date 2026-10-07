from apiforge.distribution.doctor import diagnose


def test_doctor_survives_blocked_network(tmp_path) -> None:
    result = diagnose(tmp_path, env={"APIFORGE_NETWORK": "blocked"})
    network = next(item for item in result.capabilities if item.capability == "network")
    assert network.state == "unavailable"
    assert "network" in " ".join(result.gaps)

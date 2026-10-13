from apiforge.contracts.distribution import DistributionDoctor, ForgePaths


def test_distribution_contracts_are_versioned_and_closed() -> None:
    paths = ForgePaths(
        package_root="/pkg", executable="/bin/python", state_root="/state", cache_root="/cache"
    )
    doctor = DistributionDoctor(paths=paths)
    assert paths.version == 1
    assert doctor.schema == "apiforge/doctor/v1"


def test_distribution_contract_rejects_unknown_fields() -> None:
    try:
        ForgePaths(
            package_root="/pkg",
            executable="/bin/python",
            state_root="/state",
            cache_root="/cache",
            extra=True,
        )
    except ValueError as exc:
        assert "extra" in str(exc)
    else:
        raise AssertionError("unknown contract fields must be rejected")

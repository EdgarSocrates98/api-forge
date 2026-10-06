import pytest

from apiforge.field import readiness
from tests.field.support import NOW


@pytest.fixture(autouse=True)
def _fixed_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(readiness, "utc_now", lambda: NOW)

"""AWS telemetry bridge accepts previously collected dumps only."""

from collections.abc import Iterable, Mapping
from pathlib import Path

from apiforge.observability.adapters.otel_json import read


def read_dump(path: Path) -> Iterable[Mapping[str, object]]:
    return read(path)

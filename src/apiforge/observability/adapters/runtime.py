"""Runtime trajectory adapter using the same canonical normalization boundary."""

from collections.abc import Iterable, Mapping


def read(payload: Mapping[str, object]) -> Iterable[Mapping[str, object]]:
    events = payload.get("events")
    if not isinstance(events, (list, tuple)):
        return ()
    return tuple(item for item in events if isinstance(item, Mapping))

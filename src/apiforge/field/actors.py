"""Executor and verifier identities: anonymized humans or named agents."""

from __future__ import annotations

import re

from apiforge.contracts.field import ActorRef
from apiforge.field.errors import ACTOR_INVALID, FieldError

_HUMAN = re.compile(r"^sha256:[0-9a-f]{64}$")
_AGENT = re.compile(r"^[a-z][a-z0-9-]{1,63}$")


def parse_actor(value: str, *, field: str) -> ActorRef:
    kind, _, ident = value.partition(":")
    pattern = _HUMAN if kind == "human" else _AGENT if kind == "agent" else None
    if pattern is None or not pattern.match(ident):
        raise FieldError(
            ACTOR_INVALID,
            f"{value!r} is not a valid {field}",
            field=field,
            unlock="use human:sha256:<64 hex> (anonymized) or agent:<roster-name>",
        )
    return ActorRef(kind=kind, id=ident)  # type: ignore[arg-type]


def same_actor(left: ActorRef, right: ActorRef) -> bool:
    return left.kind == right.kind and left.id == right.id


__all__ = ["parse_actor", "same_actor"]

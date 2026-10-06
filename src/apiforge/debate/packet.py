"""Referee packet (§31–32, §85): shared capsule id + position deltas, nothing else.

Naive transport ships the capsule content and every submission to each side
and to the referee. The packet counts the capsule content once (shared by
id) and gives the referee one delta per side (the latest submission), the
union of cited evidence and the disagreement set. Evidence ids are never
dropped — the gate checks that.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apiforge.contracts.selective import Disagreement, PositionDelta, RefereePacket
from apiforge.debate.service import _load


def _delta(submission: dict[str, Any]) -> PositionDelta:
    confidence = submission.get("confidence")
    return PositionDelta(
        side=str(submission["side"]),
        position=str(submission["position"]),
        evidence=tuple(str(item) for item in submission.get("evidence") or ()),
        disagreements=tuple(
            Disagreement(point=str(item["point"]), reason=str(item.get("reason", "")))
            for item in submission.get("disagreements") or ()
        ),
        risks=tuple(str(item) for item in submission.get("risks") or ()),
        confidence=float(confidence) if isinstance(confidence, int | float) else None,
    )


def referee_packet(
    case_dir: Path,
    debate_id: str,
    *,
    capsule_id: str | None = None,
    capsule_bytes: int = 0,
) -> RefereePacket:
    debate = _load(Path(case_dir), debate_id)
    latest: dict[str, dict[str, Any]] = {}
    for submission in debate.submissions:
        latest[str(submission["side"])] = submission
    positions = tuple(_delta(latest[side]) for side in sorted(latest))
    evidence = sorted(
        {str(item) for submission in debate.submissions for item in submission["evidence"]}
    )
    disagreements = sorted(
        {item.point for position in positions for item in position.disagreements}
    )
    packet = RefereePacket(
        debate_id=debate.debate_id,
        question=debate.question,
        capsule_id=capsule_id,
        positions=positions,
        disagreements=tuple(disagreements),
        evidence=tuple(evidence),
    )
    everything = len(json.dumps(list(debate.submissions), sort_keys=True).encode("utf-8"))
    # naive: every side and the referee each receive the capsule content and every submission;
    # packet: the capsule content once (shared by id) plus this compact referee input.
    naive = (len(debate.sides) + 1) * (capsule_bytes + everything)
    size = len(packet.model_dump_json().encode("utf-8")) + capsule_bytes
    return packet.model_copy(update={"packet_bytes": size, "naive_bytes": naive})


__all__ = ["referee_packet"]

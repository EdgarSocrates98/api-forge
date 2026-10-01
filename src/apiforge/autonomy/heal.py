"""Self-healing pipeline — the named bounded loop from the v1 spec.

``detect -> explain -> propose -> authorize -> execute -> verify ->
compare -> accept|rollback``

Every stage transition is an explicit ledger entry under
``event: heal.stage`` carrying the stage name, the policy decision (when a
decision exists) and the outcome. ``authorize`` is a real gate: the plan's
declared class goes through ``decide()`` and a ``deny``/``gate`` halts the
pipeline with missing requirements named — nothing executes. ``execute``
only runs verbs present in the dispatch table; anything else is recorded
``not_dispatchable``. ``rollback`` is operational: the snapshot of every
``writable_paths`` file taken before ``execute`` is restored byte-for-byte
and re-hashed; a file changed by something other than the pipeline is
refused and named, never overwritten silently.

``observe`` mode walks every stage recording ``observed``; ``supervised``
halts on the first non-executed transition; ``continuous`` records the
skip and keeps going.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any

from apiforge.autonomy.modes import AutonomyMode, load_mode
from apiforge.autonomy.service import append_ledger
from apiforge.core.models import Finding
from apiforge.dispatch.runner import DispatchContext, dispatch_step
from apiforge.perf.suggest import suggest_fix
from apiforge.policy.decide import ActionRequest, decide
from apiforge.policy.models import Policy

STAGES: tuple[str, ...] = (
    "detect",
    "explain",
    "propose",
    "authorize",
    "execute",
    "verify",
    "compare",
    "accept|rollback",
)


class HealError(ValueError):
    """A refused heal operation; ``str()`` begins with the AF code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _state(path: Path) -> str:
    return _sha(path) if path.is_file() else "absent"


def _load_findings(path: Path | None) -> list[Finding]:
    if path is None:
        raise HealError("AF-HEAL-NO-FINDINGS", "detect requires ctx.findings")
    import json

    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
        payload = doc if isinstance(doc, list) else doc.get("findings", [])
        return [Finding.model_validate(f) for f in payload]
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise HealError("AF-HEAL-FINDINGS-INVALID", f"{path}: {exc}") from exc


def _snapshot(root: Path, run_id: str, paths: tuple[str, ...]) -> dict[str, str]:
    """Copy every writable path under .apiforge/heal/<run>/; map -> sha256."""
    snap_dir = Path(root) / ".apiforge" / "heal" / run_id
    digests: dict[str, str] = {}
    for raw in paths:
        target = Path(raw)
        if not target.is_file():
            digests[raw] = "absent"
            continue
        rel = target.name
        dest = snap_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(target, dest)
        digests[raw] = _sha(target)
    return digests


def _restore(root: Path, run_id: str, paths: tuple[str, ...]) -> dict[str, str]:
    """Restore only when the current state equals the recorded post-state."""
    snap_dir = Path(root) / ".apiforge" / "heal" / run_id
    pre_path = snap_dir / "pre.json"
    import json

    pre = json.loads(pre_path.read_text(encoding="utf-8")) if pre_path.is_file() else {}
    post_path = snap_dir / "post.json"
    post = json.loads(post_path.read_text(encoding="utf-8")) if post_path.is_file() else {}
    result: dict[str, str] = {}
    for raw in paths:
        target = Path(raw)
        snap = snap_dir / target.name
        expected = pre.get(raw)
        expected_post = post.get(raw)
        if expected is None or expected_post is None:
            result[raw] = "version-unknown"
            continue
        current = _state(target)
        if current != expected_post:
            result[raw] = "conflict"
            continue
        if expected == "absent":
            target.unlink(missing_ok=True)
            result[raw] = "restored" if _state(target) == "absent" else "restore-failed"
            continue
        if not snap.is_file():
            result[raw] = "snapshot-missing"
            continue
        temporary = target.with_name(f".{target.name}.heal.tmp")
        temporary.write_bytes(snap.read_bytes())
        temporary.replace(target)
        result[raw] = "restored" if _state(target) == expected else "restore-failed"
    return result


def run_heal(
    root: Path,
    *,
    ctx: DispatchContext,
    policy: Policy,
    detail: dict[str, str],
    action_class: str = "local_reversible",
    writable_paths: tuple[str, ...] = (),
    actor: str = "",
    now: str | None = None,
) -> dict[str, Any]:
    """Walk the 8-stage pipeline under the current autonomy mode."""
    import json

    root = Path(root)
    mode = load_mode(root).mode
    run_id = hashlib.sha256(
        json.dumps(
            {"actor": actor, "at": now, "findings": str(ctx.findings)},
            sort_keys=True,
        ).encode()
    ).hexdigest()[:16]
    stage_log: list[dict[str, Any]] = []

    def record(stage: str, outcome: str, **extra: Any) -> dict[str, Any]:
        entry = {
            "event": "heal.stage",
            "stage": stage,
            "outcome": outcome,
            "mode": mode.value,
            "run": run_id,
            "actor": actor,
            "at": now,
            **extra,
        }
        stage_log.append(entry)
        append_ledger(root, entry)
        return entry

    halted = False

    def haltable(outcome: str) -> bool:
        """Under supervised, a non-clean transition halts the pipeline."""
        nonlocal halted
        if mode is AutonomyMode.SUPERVISED and outcome not in ("ok", "executed"):
            halted = True
        return halted

    # -- detect -------------------------------------------------------------
    if mode is AutonomyMode.OBSERVE:
        record("detect", "observed")
        findings: list[Finding] = []
    else:
        findings = _load_findings(ctx.findings)
        confirmed = [f for f in findings if f.status.value == "confirmed"]
        if not confirmed:
            record("detect", "no_signal", findings=len(findings))
            append_ledger(
                root,
                {
                    "event": "heal",
                    "run": run_id,
                    "resolution": "accepted",
                    "reason": "no confirmed findings — nothing to heal",
                    "actor": actor,
                    "at": now,
                },
            )
            return {
                "pipeline": "self-healing",
                "run": run_id,
                "resolution": "accepted",
                "reason": "no_signal",
                "stages": stage_log,
            }
        record("detect", "ok", findings=len(confirmed))
        findings = confirmed

    # -- explain ------------------------------------------------------------
    if mode is AutonomyMode.OBSERVE:
        record("explain", "observed")
    else:
        explanation = [
            {
                "finding_id": f.finding_id,
                "rule_id": f.rule_id,
                "severity": f.severity.value,
                "evidence": list(f.evidence),
            }
            for f in findings
        ]
        record("explain", "ok", explanation=explanation)

    # -- propose ------------------------------------------------------------
    if mode is AutonomyMode.OBSERVE:
        record("propose", "observed")
        plan: dict[str, Any] = {}
    else:
        plan_obj = suggest_fix(findings)
        plan = plan_obj.model_dump(mode="json")
        record("propose", "ok", plan_id=plan["id"], steps=len(plan["steps"]))

    # -- authorize ----------------------------------------------------------
    if mode is AutonomyMode.OBSERVE:
        record("authorize", "observed")
    else:
        decision = decide(
            policy,
            ActionRequest(
                verb="heal.execute",
                autonomy_class=action_class,
                args=tuple(str(s.get("verb", "")) for s in plan.get("steps", ())),
                target=str(ctx.findings) if ctx.findings is not None else None,
                detail=detail,
            ),
        )
        record(
            "authorize",
            decision.outcome,
            rule=decision.rule,
            missing=list(decision.missing_requirements),
        )
        if decision.outcome == "deny":
            append_ledger(
                root,
                {
                    "event": "heal",
                    "run": run_id,
                    "resolution": "denied",
                    "missing": list(decision.missing_requirements),
                    "actor": actor,
                    "at": now,
                },
            )
            return {
                "pipeline": "self-healing",
                "run": run_id,
                "resolution": "denied",
                "stages": stage_log,
            }
        if decision.outcome == "gate":
            haltable("gate")
            if halted:
                append_ledger(
                    root,
                    {
                        "event": "heal",
                        "run": run_id,
                        "resolution": "pending",
                        "missing": list(decision.missing_requirements),
                        "actor": actor,
                        "at": now,
                    },
                )
                return {
                    "pipeline": "self-healing",
                    "run": run_id,
                    "resolution": "pending",
                    "missing": list(decision.missing_requirements),
                    "stages": stage_log,
                }

    # -- execute ------------------------------------------------------------
    if mode is AutonomyMode.OBSERVE:
        record("execute", "observed")
        pre: dict[str, str] = {}
    else:
        snap_dir = Path(root) / ".apiforge" / "heal" / run_id
        pre = _snapshot(root, run_id, writable_paths)
        snap_dir.mkdir(parents=True, exist_ok=True)
        (snap_dir / "pre.json").write_text(json.dumps(pre, sort_keys=True) + "\n", encoding="utf-8")
        executed: list[dict[str, Any]] = []
        for step in plan.get("steps", ()):
            verb = str(step.get("verb", ""))
            outcome = dispatch_step(verb, ctx)
            executed.append({"verb": verb, "status": outcome["status"]})
        record(
            "execute", "ok" if executed else "no_dispatchable_steps", steps=executed, snapshot=pre
        )
        post_state = {raw: _state(Path(raw)) for raw in writable_paths}
        (snap_dir / "post.json").write_text(
            json.dumps(post_state, sort_keys=True) + "\n", encoding="utf-8"
        )

    # -- verify -------------------------------------------------------------
    if mode is AutonomyMode.OBSERVE:
        record("verify", "observed")
        verified = False
    elif halted:
        record("verify", "not_reached")
        verified = False
    else:
        post_findings = _load_findings(ctx.findings)
        verified = len([f for f in post_findings if f.status.value == "confirmed"]) < len(findings)
        record(
            "verify",
            "ok" if verified else "unchanged",
            post_confirmed=len([f for f in post_findings if f.status.value == "confirmed"]),
        )

    # -- compare ------------------------------------------------------------
    if mode is AutonomyMode.OBSERVE:
        record("compare", "observed")
    elif halted:
        record("compare", "not_reached")
    else:
        drift = {
            raw: _sha(Path(raw))
            for raw, before in pre.items()
            if before != "absent" and Path(raw).is_file() and _sha(Path(raw)) != before
        }
        record("compare", "ok", changed_paths=sorted(drift))

    # -- accept|rollback ----------------------------------------------------
    if mode is AutonomyMode.OBSERVE:
        record("accept", "observed")
        resolution = "observed"
    elif halted:
        record("accept", "not_reached")
        resolution = "halted"
    elif verified:
        record("accept", "accepted")
        resolution = "accepted"
    else:
        restored = _restore(root, run_id, writable_paths)
        conflict = any(value in {"conflict", "version-unknown"} for value in restored.values())
        record(
            "rollback",
            "conflict" if conflict else "rolled_back",
            restored=restored,
            error_code=(
                "AF-HEAL-ROLLBACK-CONFLICT"
                if any(value == "conflict" for value in restored.values())
                else "AF-HEAL-ROLLBACK-VERSION-UNKNOWN"
                if any(value == "version-unknown" for value in restored.values())
                else None
            ),
        )
        resolution = "conflict" if conflict else "rolled_back"

    append_ledger(
        root,
        {
            "event": "heal",
            "run": run_id,
            "resolution": resolution,
            "actor": actor,
            "at": now,
        },
    )
    return {
        "pipeline": "self-healing",
        "run": run_id,
        "resolution": resolution,
        "stages": stage_log,
    }

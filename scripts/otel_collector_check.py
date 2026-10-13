"""Drive the §52 real-collector acceptance test.

Modes:

- ``--endpoint <url> --output-file <path>``: build deterministic spans,
  export an OTLP/JSON payload, POST it to a running collector's OTLP/HTTP
  receiver, then count span ids accepted in the collector's file-exporter
  output. Emits a ``CollectorProbe/v1`` JSON; exit 1 unless ``accepted``.
- ``--otlp-only``: the same build + export, followed by the deterministic
  structural validation (``OtlpValidation``) instead of a network POST.
  Collector acceptance stays ``unresolved`` — never claimed on faith.

Usage in CI::

    python scripts/otel_collector_check.py \
        --endpoint http://127.0.0.1:4318 --output-file .apiforge/otel/out.json
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from apiforge.runtime.agent_telemetry import append_span, build_span
from apiforge.runtime.otel_export import export_otlp, probe_collector, validate_otlp

_DEMO_SPANS = (
    ("task", "ok", None, None),
    ("routing", "ok", None, None),
    ("context_build", "ok", None, None),
    ("retrieval", "ok", None, None),
    ("invoke_model", "ok", None, None),
    ("execute_tool", "ok", "reviewer", "budget_check"),
    ("security_decision", "ok", None, None),
    ("decision", "ok", None, None),
    ("promotion", "unresolved", None, None),
)


def _seed_spans(root: Path) -> int:
    count = 0
    for index, (operation, status, agent, tool) in enumerate(_DEMO_SPANS):
        span = build_span(
            trace_id="otel-collector-check",
            task_id="collector-check",
            run_id="collector-run-1",
            operation=operation,
            started_at=f"2026-10-06T10:00:{index:02d}Z",
            ended_at=f"2026-10-06T10:00:{index:02d}.500Z",
            status=status,
            agent_name=agent,
            tool_name=tool,
            decision_id="dec-1" if operation in {"decision", "promotion"} else None,
        )
        append_span(root, span)
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", help="OTLP/HTTP base URL, e.g. http://127.0.0.1:4318")
    parser.add_argument("--output-file", type=Path, help="Collector file-exporter path")
    parser.add_argument("--otlp-only", action="store_true", help="No collector; structural check")
    parser.add_argument("--timeout-s", type=float, default=30.0)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="af-otel-check-") as tmp:
        root = Path(tmp)
        seeded = _seed_spans(root)
        export = export_otlp(root)
        payload = export.payload if isinstance(export.payload, dict) else {}
        validation = validate_otlp(payload)
        report: dict[str, object] = {
            "seeded_spans": seeded,
            "validation": validation.model_dump(mode="json"),
        }
        if args.otlp_only or not args.endpoint:
            report["collector"] = {
                "status": "unresolved",
                "detail": "no collector endpoint declared — real acceptance deferred",
                "unresolved": ["collector"],
            }
        else:
            probe = probe_collector(
                payload,
                endpoint=args.endpoint,
                output_file=args.output_file,
                timeout_s=args.timeout_s,
            )
            report["collector"] = probe.model_dump(mode="json")
        print(json.dumps(report, indent=2, sort_keys=True))
        if not validation.accepted:
            return 1
        collector = report["collector"]
        if isinstance(collector, dict) and args.endpoint and collector.get("status") != "accepted":
            return 1
        # without an endpoint, unresolved collector is honest: structural
        # validation still passed
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

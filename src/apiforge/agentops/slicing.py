"""Native RTK-style slicing (§43–44): failures and signatures instead of whole logs.

The complete log is stored once in the content-addressed ctx store and
referenced by ``log_ref``; the slice keeps every failing test and every
distinct error signature (with counts, evidence spans, relevant frames and a
little preceding context). Only context lines are bounded — failures never
are. JUnit XML with a DOCTYPE is refused, so no entity is ever expanded.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from apiforge.contracts.base import ContractError
from apiforge.contracts.tool_host import ErrorSignature, ErrorSlice, TestFailure, TestSlice

MAX_INPUT_BYTES = 25 * 1024 * 1024
CONTEXT_LINES = 3
MAX_FRAMES = 6

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_SUMMARY = re.compile(r"(\d+) (passed|failed|errors?|skipped|xfailed|xpassed|deselected)")
_TIMING = re.compile(r"\bin \d+(?:\.\d+)?s\b")
_SHORT = re.compile(r"^(FAILED|ERROR) (\S+?)(?: - (.*))?$")
_LOCATION = re.compile(r"^([\w./\\-]+\.py):(\d+): (\w+)")
_ERROR_LINE = re.compile(
    r"(?:\b(?:ERROR|FATAL|FAIL|FAILED|FAILURE|Exception|Error|Traceback)\b|\bpanic:|AF-[A-Z0-9-]+)"
)
_FRAME = re.compile(
    r"^\s*(?:at [\w$.<>]+\(.*\)|File \".*\", line \d+|[\w./-]+\.go:\d+|goroutine \d+)"
)
_ENV = re.compile(
    r"(?:python \d+\.\d+|platform (?:linux|win32|darwin)|java version|openjdk \d+|go version go\d|node v\d+)",
    re.IGNORECASE,
)


def _error(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def _read(path: Path) -> str:
    path = Path(path)
    if not path.is_file():
        raise _error(
            "AF-SLICE-INPUT-NOT-FOUND",
            f"{path} does not exist",
            "input",
            "pass the path of a saved test or CI log",
        )
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise _error(
            "AF-SLICE-INPUT-INVALID",
            f"{path} exceeds {MAX_INPUT_BYTES} bytes",
            "input",
            "split the log or slice the relevant job only",
        )
    return _ANSI.sub("", path.read_text(encoding="utf-8", errors="replace"))


def _store(root: Path, text: str) -> str:
    from apiforge.context.gateway.refs import CtxStore

    return CtxStore(Path(root)).put(text)


def normalize_signature(line: str) -> str:
    text = line.strip()
    text = re.sub(r"(?:[A-Za-z]:)?[\\/][\w .\\/-]+", "<path>", text)
    text = re.sub(r"0x[0-9a-fA-F]+", "<hex>", text)
    text = re.sub(r"'[^']*'|\"[^\"]*\"", "<str>", text)
    text = re.sub(r"\d+", "<n>", text)
    return re.sub(r"\s+", " ", text)[:200]


def _finish(model: TestSlice) -> TestSlice:
    size = len(model.model_dump_json().encode("utf-8"))
    return model.model_copy(update={"slice_bytes": size})


def slice_pytest(root: Path, path: Path) -> TestSlice:
    text = _read(path)
    lines = text.splitlines()
    counts: dict[str, Any] = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    summary = next(
        (line for line in reversed(lines) if _SUMMARY.search(line) and _TIMING.search(line)), ""
    )
    for number, kind in _SUMMARY.findall(summary):
        key = "errors" if kind.startswith("error") else kind
        if key in counts:
            counts[key] = int(number)
    failures: dict[str, TestFailure] = {}
    for index, line in enumerate(lines):
        match = _SHORT.match(line.strip())
        if not match:
            continue
        outcome, test, message = match.group(1), match.group(2), match.group(3) or ""
        failures[test] = TestFailure(
            test=test,
            outcome="error" if outcome == "ERROR" else "failed",
            assertion=message.strip()[:300],
            signature=normalize_signature(message or test),
            span=(index + 1, index + 1),
        )
    for index, line in enumerate(lines):
        location = _LOCATION.match(line.strip())
        if not location:
            continue
        file, number, kind = location.groups()
        for test, failure in list(failures.items()):
            if test.split("::", 1)[0].replace("\\", "/").endswith(file.replace("\\", "/")) and (
                failure.line is None
            ):
                assertion = failure.assertion or kind
                context = _preceding_e_line(lines, index)
                failures[test] = failure.model_copy(
                    update={
                        "file": file,
                        "line": int(number),
                        "assertion": (context or assertion)[:300],
                        "span": (max(1, index + 1 - CONTEXT_LINES), index + 1),
                    }
                )
                break
    unresolved: tuple[str, ...] = ()
    if counts["failed"] + counts["errors"] > len(failures):
        unresolved = ("some failures have no short test summary; run pytest with -rfE",)
    return _finish(
        TestSlice(
            format="pytest",
            failures=tuple(failures[key] for key in sorted(failures)),
            log_ref=_store(root, text),
            original_bytes=len(text.encode("utf-8")),
            unresolved=unresolved,
            **counts,
        )
    )


def _preceding_e_line(lines: list[str], index: int) -> str:
    for back in range(index - 1, max(-1, index - 40), -1):
        stripped = lines[back].strip()
        if stripped.startswith("E "):
            return stripped[2:].strip()
    return ""


def slice_junit(root: Path, path: Path) -> TestSlice:
    text = _read(path)
    if "<!DOCTYPE" in text.upper():
        raise _error(
            "AF-SLICE-XML-REFUSED",
            f"{path} declares a DOCTYPE; entity expansion is never processed",
            "input",
            "export JUnit XML without a DOCTYPE",
        )
    try:
        tree = ET.fromstring(text)
    except ET.ParseError as exc:
        raise _error(
            "AF-SLICE-INPUT-INVALID", f"{path}: {exc}", "input", "pass a valid JUnit XML report"
        ) from exc
    counts: dict[str, Any] = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    failures: list[TestFailure] = []
    for case in tree.iter("testcase"):
        name = f"{case.get('classname', '')}::{case.get('name', '')}".strip(":")
        failure = case.find("failure")
        error = case.find("error")
        if case.find("skipped") is not None:
            counts["skipped"] += 1
        elif failure is not None or error is not None:
            node = failure if failure is not None else error
            assert node is not None
            counts["failed" if failure is not None else "errors"] += 1
            message = node.get("message") or (node.text or "").strip().splitlines()[0:1] or [""]
            first = message if isinstance(message, str) else message[0]
            failures.append(
                TestFailure(
                    test=name or "unnamed",
                    outcome="failed" if failure is not None else "error",
                    file=case.get("file"),
                    line=int(str(case.get("line"))) if (case.get("line") or "").isdigit() else None,
                    assertion=first[:300],
                    signature=normalize_signature(first or name),
                )
            )
        else:
            counts["passed"] += 1
    return _finish(
        TestSlice(
            format="junit",
            failures=tuple(sorted(failures, key=lambda item: item.test)),
            log_ref=_store(root, text),
            original_bytes=len(text.encode("utf-8")),
            **counts,
        )
    )


def slice_tests(root: Path, path: Path, fmt: str = "auto") -> TestSlice:
    selected = fmt
    if fmt == "auto":
        head = Path(path).read_text(encoding="utf-8", errors="replace")[:512].lstrip()
        selected = "junit" if head.startswith("<") else "pytest"
    if selected == "junit":
        return slice_junit(root, path)
    if selected == "pytest":
        return slice_pytest(root, path)
    raise _error(
        "AF-SLICE-INPUT-INVALID", f"format {fmt!r} is not pytest|junit|auto", "format", "use auto"
    )


def slice_log(root: Path, path: Path) -> ErrorSlice:
    text = _read(path)
    lines = text.splitlines()
    groups: dict[str, dict[str, object]] = {}
    for index, line in enumerate(lines):
        if not _ERROR_LINE.search(line) or _FRAME.match(line):
            continue
        signature = normalize_signature(line)
        frames = []
        for follow in lines[index + 1 : index + 1 + 40]:
            if _FRAME.match(follow):
                frames.append(follow.strip()[:200])
                if len(frames) >= MAX_FRAMES:
                    break
            elif frames:
                break
        group = groups.setdefault(
            signature,
            {
                "first_line": line.strip()[:300],
                "count": 0,
                "spans": [],
                "frames": tuple(frames),
                "context": tuple(
                    item.strip()[:200]
                    for item in lines[max(0, index - CONTEXT_LINES) : index]
                    if item.strip()
                ),
            },
        )
        group["count"] = int(group["count"]) + 1  # type: ignore[call-overload]
        spans = group["spans"]
        assert isinstance(spans, list)
        if len(spans) < 5:
            spans.append((index + 1, index + 1 + len(frames)))
    environment = tuple(
        sorted({match.group(0).lower() for line in lines for match in [_ENV.search(line)] if match})
    )
    signatures = tuple(
        ErrorSignature(
            signature=signature,
            first_line=str(group["first_line"]),
            count=int(group["count"]),  # type: ignore[call-overload]
            spans=tuple(group["spans"]),  # type: ignore[arg-type]
            frames=group["frames"],  # type: ignore[arg-type]
            context=group["context"],  # type: ignore[arg-type]
        )
        for signature, group in groups.items()
    )
    model = ErrorSlice(
        signatures=signatures,
        environment=environment,
        log_ref=_store(root, text),
        original_bytes=len(text.encode("utf-8")),
        original_lines=len(lines),
    )
    return model.model_copy(update={"slice_bytes": len(model.model_dump_json().encode("utf-8"))})


__all__ = ["normalize_signature", "slice_junit", "slice_log", "slice_pytest", "slice_tests"]

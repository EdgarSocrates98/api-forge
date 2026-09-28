"""Targeted verification (§45–46): impacted tests first, the ladder level the risk requires.

The plan never runs anything — it names the ladder level, the selected tests
with the reason each was selected, and the commands a host or CI would run.
Selection evidence: cached capsule selections whose dependencies hold a
changed file (their test refs), test files that mention a symbol defined in
a changed file, test files that import a changed Python module, and changed
test files themselves. An empty selection never means "nothing to run": the
plan escalates to the full suite and says why.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable, Sequence
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_extras import LadderLevel, SelectedTest, VerificationPlan

LADDER: dict[str, LadderLevel] = {"micro": "V1", "low": "V2", "medium": "V4", "high": "V5"}
ORDER: tuple[LadderLevel, ...] = ("V0", "V1", "V2", "V3", "V4", "V5")
TEST_FILE = re.compile(
    r"(^test_.*\.py$|_test\.py$|Test\.java$|Tests\.java$|_test\.go$|Tests?\.kt$)"
)
_SKIP_DIRS = {".git", ".apiforge", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}
_JAVA_DEF = re.compile(r"\b(?:class|interface|record|enum)\s+([A-Z]\w*)")
_GO_DEF = re.compile(r"^func\s+(?:\([^)]*\)\s*)?([A-Z]\w*)|^type\s+([A-Z]\w*)", re.MULTILINE)


def _refusal(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def discover_tests(root: Path) -> list[str]:
    found: list[str] = []
    stack = [Path(root)]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir())
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name not in _SKIP_DIRS and not entry.name.startswith("."):
                    stack.append(entry)
            elif TEST_FILE.search(entry.name):
                found.append(entry.relative_to(root).as_posix())
    return sorted(found)


def defined_symbols(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    if path.suffix == ".py":
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return set()
        return {
            node.name
            for node in tree.body
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
            and not node.name.startswith("_")
        }
    if path.suffix == ".java":
        return set(_JAVA_DEF.findall(text))
    if path.suffix == ".go":
        return {a or b for a, b in _GO_DEF.findall(text)}
    return set()


def _module_names(changed: str) -> set[str]:
    if not changed.endswith(".py"):
        return set()
    parts = Path(changed).with_suffix("").parts
    names = set()
    for start in range(len(parts)):
        name = ".".join(parts[start:])
        if name and not name.startswith("."):
            names.add(name)
    return {name for name in names if "." in name or len(parts) == 1}


def _cached_test_refs(root: Path, changed: set[str]) -> dict[str, list[str]]:
    from apiforge.cache.store import CacheStore

    refs: dict[str, list[str]] = {}
    for _, _, entry in CacheStore(root).entries(("capsule",)):
        if entry is None:
            continue
        deps = {dep.path for dep in entry.deps_files}
        if not deps & changed:
            continue
        for dep in sorted(deps):
            if TEST_FILE.search(Path(dep).name):
                refs.setdefault(dep, []).append(f"capsule-test-ref:{entry.subject}")
    return refs


def plan_verification(
    root: Path,
    changed: Sequence[str],
    *,
    risk: str = "low",
    breaking: bool = False,
) -> VerificationPlan:
    root = Path(root).resolve()
    if risk not in LADDER:
        raise _refusal(
            "AF-VERIFY-RISK-INVALID",
            f"risk {risk!r} is not micro|low|medium|high",
            "risk",
            "pass --risk from `apiforge sdd classify` (micro, low, medium, high)",
        )
    changed_set = {Path(item).as_posix().removeprefix("./") for item in changed}
    level: LadderLevel = LADDER[risk]
    reasons = [f"risk {risk} sets the ladder floor at {level}"]
    if breaking and ORDER.index(level) < ORDER.index("V4"):
        level = "V4"
        reasons.append("breaking contract verdict raises the ladder to V4")
    tests = discover_tests(root)
    selected: dict[str, list[str]] = {}
    for path, why in _cached_test_refs(root, changed_set).items():
        selected.setdefault(path, []).extend(why)
    symbols: dict[str, str] = {}
    modules: dict[str, str] = {}
    for item in sorted(changed_set):
        if TEST_FILE.search(Path(item).name):
            selected.setdefault(item, []).append("changed")
            continue
        for symbol in defined_symbols(root / item):
            symbols.setdefault(symbol, item)
        for module in _module_names(item):
            modules.setdefault(module, item)
    if symbols or modules:
        symbol_re = (
            re.compile("|".join(rf"(?<![\w]){re.escape(name)}(?![\w])" for name in sorted(symbols)))
            if symbols
            else None
        )
        for test in tests:
            try:
                body = (root / test).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if symbol_re is not None:
                hit = symbol_re.search(body)
                if hit:
                    selected.setdefault(test, []).append(f"mentions:{hit.group(0)}")
            for module in sorted(modules):
                if re.search(rf"(?:from|import)\s+{re.escape(module)}\b", body):
                    selected.setdefault(test, []).append(f"imports:{module}")
                    break
    chosen = tuple(
        SelectedTest(path=path, reasons=tuple(sorted(set(why))))
        for path, why in sorted(selected.items())
        if path in tests or (root / path).is_file()
    )
    if level in {"V2", "V4"} and not chosen:
        level = "V5"
        reasons.append("no-impacted-tests-found: escalated to the full suite")
    commands = _commands(level, chosen, changed_set)
    skipped = tuple(item for item in ORDER if ORDER.index(item) > ORDER.index(level))
    return VerificationPlan(
        risk=risk,  # type: ignore[arg-type]
        level=level,
        changed=tuple(sorted(changed_set)),
        tests=chosen,
        total_tests=len(tests),
        commands=commands,
        skipped_levels=skipped,
        reasons=tuple(reasons),
    )


def _commands(
    level: LadderLevel, tests: Iterable[SelectedTest], changed: set[str]
) -> tuple[str, ...]:
    paths = [item.path for item in tests]
    contract = sorted(
        path for path in changed if path.endswith((".yaml", ".yml", ".json", ".proto"))
    )
    base: list[str] = []
    if contract:
        base.append("apiforge diff contract <baseline> " + contract[0])
    if level in {"V0", "V1"}:
        return tuple(base or ["apiforge analyze --contract <contract> --project <project>"])
    if level in {"V2", "V3"}:
        return (*base, "pytest " + " ".join(paths))
    if level == "V4":
        dirs = sorted({str(Path(path).parent.as_posix()) for path in paths})
        return (*base, "pytest " + " ".join(paths), "pytest " + " ".join(dirs))
    return (*base, "pytest")


__all__ = ["LADDER", "defined_symbols", "discover_tests", "plan_verification"]

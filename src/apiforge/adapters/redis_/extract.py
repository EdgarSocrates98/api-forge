"""Static extraction of Redis/Valkey command call sites.

Python files are parsed with ``ast``: a receiver counts as Redis-bound when
it is assigned a ``redis.Redis``/``valkey.Valkey``/``from_url`` constructor
(``binding: constructor``) or uses a conventional name while a redis package
is imported (``binding: name`` — emitted honestly as heuristic). Java and Go
files are scanned by pattern: the fact is emitted only when the file imports
a Redis client package *and* the receiver name is conventional; the binding
is always ``name``.

``data.redis.command`` facts carry ``command``/``key_literal``; mutating
commands additionally emit ``data.redis.write`` with ``ttl_seconds`` (the
literal when visible, absent otherwise — the AF-DATA-002 check fires on
absence, never on a guess).
"""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_REDIS_PACKAGES = ("redis", "valkey", "glide")
_NAME_RECEIVERS = {"redis", "r", "rc", "rdb", "cache", "rcache"}
_CONSTRUCTOR_RE = re.compile(
    r"(redis|valkey)\.?(?:asyncio\.)?(Redis|Valkey|StrictRedis|from_url)\s*\(",
    re.IGNORECASE,
)

_WRITE_COMMANDS = {
    "set", "setnx", "getset", "mset", "hset", "hmset", "sadd", "lpush",
    "rpush", "lset", "zadd", "zincrby", "incr", "incrby", "incrbyfloat",
    "decr", "decrby", "append", "rename", "restore",
}
_TTL_COMMANDS = {"setex", "psetex"}
_COMMANDS = _WRITE_COMMANDS | _TTL_COMMANDS | {
    "get", "mget", "getrange", "hget", "hmget", "hgetall", "smembers",
    "sismember", "zrange", "zscore", "exists", "ttl", "pttl", "scan",
    "sscan", "hscan", "zscan", "keys", "type", "lrange", "lindex",
    "expire", "pexpire", "expireat", "persist", "delete", "unlink",
    "flushall", "flushdb", "config", "debug", "monitor", "shutdown",
    "save", "bgsave", "pipeline", "multi", "exec", "do", "publish",
    "subscribe", "xadd", "xread", "lpop", "rpop", "getdel", "getex",
}

_COMMAND_ALIASES = {
    "config_set": "config",
    "config_get": "config",
    "config_rewrite": "config",
    "config_resetstat": "config",
    "delete": "del",
}

_COMMANDS |= set(_COMMAND_ALIASES)

# First positional is a pattern/cursor/subcommand, not a key — never an entity.
_NO_KEY_ARG = {
    "keys", "scan", "sscan", "hscan", "zscan", "flushall", "flushdb",
    "config", "debug", "monitor", "shutdown", "save", "bgsave",
    "pipeline", "multi", "exec", "do", "subscribe",
}

_JAVA_REDIS_RE = re.compile(
    r"(?:jedis|redisTemplate|stringRedisTemplate|redis|rcache)\s*\."
    r"(?:opsFor\w+\(\)\s*\.)?(\w+)\s*\(",
)
_GO_REDIS_RE = re.compile(
    r"(?:rdb|redisClient|valkey|rcache)\s*\.\s*([A-Z]\w*)\s*\(",
)
_GO_DO_RE = re.compile(
    r"(?:rdb|redisClient|valkey|rcache)\s*\.\s*Do\s*\(\s*\w+\s*,\s*\"(\w+)\"",
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fact(
    kind: str,
    rel: str,
    digest: str,
    line: int,
    extractor: str,
    **kwargs: Any,
) -> Fact:
    measures = {k: v for k, v in kwargs.items() if v is not None}
    return Fact(
        fact_id=stable_id("fact", {"k": kind, "p": rel, "l": line, **measures}),
        kind=kind,
        source=SourceRef(
            path=rel, sha256=digest, line=line, extractor=extractor
        ),
        measures=measures,
        attrs={},
    )


def _fstring_pattern(node: ast.expr) -> str | None:
    """`f"order:{oid}"` -> `order:*`; returns None if no literal anchor."""
    if not isinstance(node, ast.JoinedStr):
        return None
    parts: list[str] = []
    for value in node.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            parts.append(value.value)
        elif isinstance(value, ast.FormattedValue):
            parts.append("*")
    pattern = "".join(parts)
    while "**" in pattern:
        pattern = pattern.replace("**", "*")
    return pattern if pattern.strip("*:") else None


def _command_facts(
    rel: str,
    digest: str,
    line: int,
    extractor: str,
    command: str,
    key_literal: str | None,
    ttl: float | None,
    binding: str,
    key_pattern: str | None = None,
) -> list[Fact]:
    out = [
        _fact(
            "data.redis.command",
            rel,
            digest,
            line,
            extractor,
            command=command,
            key_literal=key_literal,
            key_pattern=key_pattern,
            binding=binding,
        )
    ]
    if command in _WRITE_COMMANDS or command in _TTL_COMMANDS:
        kwargs: dict[str, Any] = {
            "command": command,
            "key_literal": key_literal,
            "key_pattern": key_pattern,
            "binding": binding,
        }
        if ttl is not None:
            kwargs["ttl_seconds"] = ttl
        out.append(_fact("data.redis.write", rel, digest, line, extractor, **kwargs))
    return out


def _py_call_name(node: ast.expr) -> str | None:
    """`redis.Redis`, `Redis`, `redis.from_url` -> normalized ctor name."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        head = _py_call_name(node.value)
        return f"{head}.{node.attr}" if head else node.attr
    return None


def _scan_python(path: Path, rel: str, digest: str) -> tuple[list[Fact], list[Diagnostic]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        return [], [
            Diagnostic(
                code="AF-REDIS-PARSE",
                status=FindingStatus.UNRESOLVED,
                message=f"{rel}: {exc}",
                source=SourceRef(path=rel, sha256=digest, extractor="redis"),
            )
        ]
    imports_redis = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _REDIS_PACKAGES:
                    imports_redis = True
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.split(".")[0] in _REDIS_PACKAGES
        ):
            imports_redis = True
    receivers: dict[str, str] = {}
    _BARE_CTORS = {"Redis", "Valkey", "StrictRedis", "from_url"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            name = _py_call_name(node.value.func)
            ctor = bool(
                name
                and (
                    _CONSTRUCTOR_RE.search(name + "(")
                    or (imports_redis and name in _BARE_CTORS)
                )
            )
            if ctor:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        receivers[target.id] = "constructor"
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    heuristic = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        receiver = node.func.value
        if not isinstance(receiver, ast.Name):
            continue
        binding = receivers.get(receiver.id)
        if binding is None and imports_redis and receiver.id in _NAME_RECEIVERS:
            binding = "name"
            heuristic = True
        if binding is None:
            continue
        command = node.func.attr.lower()
        if command not in _COMMANDS:
            continue
        command = _COMMAND_ALIASES.get(command, command)
        key_literal = None
        key_pattern = None
        if (
            command not in _NO_KEY_ARG
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            key_literal = node.args[0].value
        elif command not in _NO_KEY_ARG and node.args:
            key_pattern = _fstring_pattern(node.args[0])
        ttl: float | None = None
        # setex/psetex(name, time, value) — ttl is the second positional
        if (
            command in _TTL_COMMANDS
            and len(node.args) > 1
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, (int, float))
        ):
            ttl = float(node.args[1].value)
        for kw in node.keywords:
            if (
                kw.arg in ("ex", "px", "exat", "pxat")
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, (int, float))
            ):
                ttl = float(kw.value.value)
        facts.extend(
            _command_facts(
                rel, digest, node.lineno, "redis", command, key_literal, ttl,
                binding, key_pattern,
            )
        )
    if heuristic:
        diagnostics.append(
            Diagnostic(
                code="AF-REDIS-HEURISTIC-BINDING",
                status=FindingStatus.UNRESOLVED,
                message=(
                    f"{rel}: receivers matched by name — binding not proven "
                    "by a constructor"
                ),
                source=SourceRef(path=rel, sha256=digest, extractor="redis"),
            )
        )
    return facts, diagnostics


def _scan_java(path: Path, rel: str, digest: str) -> tuple[list[Fact], list[Diagnostic]]:
    text = path.read_text(encoding="utf-8")
    if not re.search(r"(jedis|lettuce|RedisClient|RedisTemplate)", text):
        return [], []
    facts: list[Fact] = []
    for index, line in enumerate(text.splitlines(), 1):
        for match in _JAVA_REDIS_RE.finditer(line):
            command = _COMMAND_ALIASES.get(match.group(1).lower(), match.group(1).lower())
            if command in _COMMANDS:
                facts.extend(
                    _command_facts(
                        rel, digest, index, "redis", command, None, None, "name"
                    )
                )
    if facts:
        return facts, [_heuristic_diag(rel, digest)]
    return [], []


def _scan_go(path: Path, rel: str, digest: str) -> tuple[list[Fact], list[Diagnostic]]:
    text = path.read_text(encoding="utf-8")
    if not re.search(r"(go-redis|valkey-go|redigo)", text):
        return [], []
    facts: list[Fact] = []
    for index, line in enumerate(text.splitlines(), 1):
        for match in _GO_DO_RE.finditer(line):
            command = match.group(1).lower()
            if command in _COMMANDS:
                facts.extend(
                    _command_facts(
                        rel, digest, index, "redis", command, None, None, "name"
                    )
                )
        for match in _GO_REDIS_RE.finditer(line):
            command = _COMMAND_ALIASES.get(match.group(1).lower(), match.group(1).lower())
            if command in _COMMANDS:
                facts.extend(
                    _command_facts(
                        rel, digest, index, "redis", command, None, None, "name"
                    )
                )
    if facts:
        return facts, [_heuristic_diag(rel, digest)]
    return [], []


def _heuristic_diag(rel: str, digest: str) -> Diagnostic:
    return Diagnostic(
        code="AF-REDIS-HEURISTIC-BINDING",
        status=FindingStatus.UNRESOLVED,
        message=f"{rel}: receivers matched by name — binding not proven",
        source=SourceRef(path=rel, sha256=digest, extractor="redis"),
    )


def extract_redis(project_root: Path) -> CodeInventory:
    """Scan a project tree for Redis/Valkey call sites — no code executes."""
    root = Path(project_root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if path.suffix == ".py":
            digest = _digest(path)
            input_hashes[rel] = digest
            f, d = _scan_python(path, rel, digest)
            facts.extend(f)
            diagnostics.extend(d)
        elif path.suffix == ".java":
            digest = _digest(path)
            f, d = _scan_java(path, rel, digest)
            if f or d:
                input_hashes[rel] = digest
                facts.extend(f)
                diagnostics.extend(d)
        elif path.suffix == ".go":
            digest = _digest(path)
            f, d = _scan_go(path, rel, digest)
            if f or d:
                input_hashes[rel] = digest
                facts.extend(f)
                diagnostics.extend(d)
    return CodeInventory(
        framework="redis",
        root=str(root),
        facts=tuple(sorted(facts, key=lambda f: f.fact_id)),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )

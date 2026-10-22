# apiforge/discovery_ops.py
"""§6.2 conceptual-op map -> real ``apiforge`` verbs (lf-0037).

Single source for the ``forge/context/v1`` manifest ``discovery.ops`` /
``discovery.commands`` and the ``apiforge capabilities`` verb — the table is
never duplicated so it cannot drift silently.
"""

from __future__ import annotations

from typing import Any

CLI = "apiforge"

DOMAINS: tuple[str, ...] = (
    "api-design",
    "api-contract",
    "api-testing",
    "api-performance",
    "api-observability",
    "api-migration",
    "data-access",
    "messaging",
)

# Published domain -> native prefixes (rule areas are REST/CONTRACT/PERF/…,
# knowledge packs are rest-design/data-access-patterns/…). A name not listed
# matches as a literal normalized prefix.
DOMAIN_PREFIXES: dict[str, tuple[str, ...]] = {
    "api-design": ("rest", "http", "api", "idempoten"),
    "api-contract": ("contract", "breaking", "schema"),
    "api-testing": ("testing", "contract-testing", "mock", "test"),
    "api-performance": ("perf", "latency", "throughput", "cache", "resilien"),
    "api-observability": ("observe", "otel", "monitor", "telemetry"),
    "api-migration": ("migration", "migrate", "evolve", "version"),
    "data-access": ("data", "storage", "gdb", "sql", "nosql", "dynamodb", "documentdb"),
    "messaging": ("messaging", "sqs", "sns", "kafka", "eventbridge", "kinesis"),
}


def domain_prefixes(domain: str) -> tuple[str, ...]:
    norm = domain.strip().lower().replace("_", "-")
    return DOMAIN_PREFIXES.get(norm, (norm,))

PROTOCOLS: tuple[dict[str, str], ...] = (
    {"id": "forge/v1", "version": "1"},
    {"id": "forge/context/v1", "version": "1"},
    {"id": "forge/context-registry/v1", "version": "1"},
)

MCP_INTERFACE: dict[str, Any] = {
    "server_name": "apiforge",
    "command": ["apiforge-mcp"],
    "verify_tool": "portable_status",
}

OPS: dict[str, dict[str, Any]] = {
    "capabilities.list": {
        "id": "capabilities",
        "argv": ["capabilities", "installed"],
        "mode": "direct-capability",
        "description": "installed capabilities, protocols and the §6.2 op map",
    },
    "protocol.describe": {
        "id": "capabilities",
        "argv": ["capabilities", "installed"],
        "mode": "direct-capability",
        "description": "protocols + interfaces section of `capabilities`",
    },
    "rules.search": {
        "id": "rules-search",
        "argv": [
            "rules", "search", "--query", "{term}", "--area", "{area}",
            "--severity", "{severity}", "--limit", "{limit}", "--cursor", "{cursor}",
        ],
        "mode": "direct-capability",
        "description": "keyword/area/severity filter over the rule catalog, paginated",
    },
    "rules.get": {
        "id": "rules-get",
        "argv": ["rules", "lookup", "{rule_id}"],
        "mode": "direct-capability",
        "description": "one rule's full guidance by id",
    },
    "knowledge.search": {
        "id": "knowledge-search",
        "argv": [
            "knowledge", "search", "{term}", "--domain", "{domain}",
            "--limit", "{limit}", "--cursor", "{cursor}",
        ],
        "mode": "direct-capability",
        "description": "offline text search over knowledge packs, one hit per doc",
    },
    "knowledge.get": {
        "id": "knowledge-get",
        "argv": ["knowledge", "get", "{file}"],
        "mode": "direct-capability",
        "description": "resolve one document's absolute path + sha256 + provenance",
    },
    "context.build": {
        "id": "context-pack",
        "argv": ["context", "pack", "--domain", "{domain}"],
        "mode": "direct-capability",
        "description": "bounded domain context pack: rules + knowledge metadata + hash",
    },
    "health.check": {
        "id": "doctor",
        "argv": ["doctor"],
        "mode": "diagnostic-only",
        "description": "environment + installation health",
    },
}


def commands() -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for entry in OPS.values():
        if entry["id"] in seen:
            continue
        seen.add(entry["id"])
        out.append(
            {
                "id": entry["id"],
                "argv": [CLI, *entry["argv"]],
                "mode": entry["mode"],
                "read_only": True,
                "description": entry["description"],
            }
        )
    return out


def ops() -> dict[str, str]:
    return {op: entry["id"] for op, entry in OPS.items()}


def ops_expanded() -> dict[str, dict[str, Any]]:
    return {
        op: {"command": entry["id"], "argv": [CLI, *entry["argv"]]}
        for op, entry in OPS.items()
    }

"""SPARQL query text -> declared shape measures (Neptune RDF).

Pure text analysis; literals and IRIs never execute. ``SELECT *`` and
``COUNT(*)`` are stripped before property-path detection so only real
``+``/``*`` path modifiers count.
"""

from __future__ import annotations

import re

_STRING = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"")
_COMMENT = re.compile(r"#[^\n]*")
_LIMIT = re.compile(r"\bLIMIT\s+\d+", re.IGNORECASE)
_ASK = re.compile(r"^\s*(PREFIX[^\n]*\n\s*|BASE[^\n]*\n\s*)*ASK\b", re.IGNORECASE)
_COUNT_ONLY = re.compile(
    r"\bSELECT\s+(DISTINCT\s+)?\(\s*COUNT\s*\([^)]*\)\s+AS\s+\?\w+\s*\)\s*(WHERE|\{)",
    re.IGNORECASE,
)
_UPDATE = re.compile(
    r"\b(INSERT\s+DATA|INSERT\s*\{|DELETE\s+DATA|DELETE\s*\{|DELETE\s+WHERE|LOAD\s|"
    r"CLEAR\s|DROP\s|CREATE\s+(SILENT\s+)?GRAPH|ADD\s|MOVE\s|COPY\s)",
    re.IGNORECASE,
)
_STARS = re.compile(r"\bSELECT\s+(DISTINCT\s+|REDUCED\s+)?\*|\(\s*\*\s*\)", re.IGNORECASE)
_PATH = re.compile(r"(?<![?$\w:])((?:[A-Za-z_][\w-]*)?:[\w-]*|<[^>\s]+>|\))\s*[+*](?=[\s?<(.;])")
_TYPE = re.compile(r"(?:\s|^)a\s+((?:[A-Za-z_][\w-]*)?:[\w-]+|<[^>\s]+>)")


def analyze(query: str) -> dict[str, object]:
    """Measures declared by the SPARQL text."""
    text = _STRING.sub('""', _COMMENT.sub("", query))
    stripped = _STARS.sub(" ", text)
    risks: list[str] = []
    if _PATH.search(stripped):
        risks.append("unbounded-property-path")
    bounded = bool(_LIMIT.search(text) or _ASK.search(text) or _COUNT_ONLY.search(text))
    return {
        "bounded": bounded,
        "mutation": bool(_UPDATE.search(text)),
        "labels_used": tuple(sorted(set(_TYPE.findall(text)))),
        "edge_labels_used": (),
        "shape_risks": tuple(risks),
    }

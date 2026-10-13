"""Trust Plane: unified origin/trust/taint annotation and propagation."""

from apiforge.trust.plane import (
    BASE_TRUST,
    ORIGIN_TAINT,
    REF_ORIGIN_MAP,
    annotate_capsule,
    annotate_ref,
    external_unit,
    trust_unit,
)
from apiforge.trust.propagation import propagate
from apiforge.trust.tools import TOOL_RISK_FILE, authorize, load_tool_risk

__all__ = [
    "BASE_TRUST",
    "ORIGIN_TAINT",
    "REF_ORIGIN_MAP",
    "TOOL_RISK_FILE",
    "annotate_capsule",
    "annotate_ref",
    "authorize",
    "external_unit",
    "load_tool_risk",
    "propagate",
    "trust_unit",
]

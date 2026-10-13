"""Provider-neutral, policy-gated integration boundaries."""

from apiforge.integrations.devin import (
    build_devin_declaration,
    build_devin_payload,
    probe_devin_cli,
)
from apiforge.integrations.external import (
    GitHubIssuesReadOnlyAdapter,
    HttpHealthReadOnlyAdapter,
    HttpJsonReadOnlyAdapter,
)
from apiforge.integrations.gateway import IntegrationAdapter, IntegrationGateway
from apiforge.integrations.github import GitHubReadOnlyAdapter, UrllibReadOnlyTransport
from apiforge.integrations.replay import ReplayAdapter
from apiforge.integrations.transport import ReadOnlyTransport, TransportError

__all__ = [
    "GitHubIssuesReadOnlyAdapter",
    "GitHubReadOnlyAdapter",
    "HttpHealthReadOnlyAdapter",
    "HttpJsonReadOnlyAdapter",
    "IntegrationAdapter",
    "IntegrationGateway",
    "ReadOnlyTransport",
    "ReplayAdapter",
    "TransportError",
    "UrllibReadOnlyTransport",
    "build_devin_declaration",
    "build_devin_payload",
    "probe_devin_cli",
]

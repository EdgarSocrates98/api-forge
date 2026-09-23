"""Provider-neutral, policy-gated integration boundaries."""

from apiforge.integrations.gateway import IntegrationAdapter, IntegrationGateway
from apiforge.integrations.github import GitHubReadOnlyAdapter, UrllibReadOnlyTransport
from apiforge.integrations.replay import ReplayAdapter
from apiforge.integrations.transport import ReadOnlyTransport, TransportError

__all__ = [
    "GitHubReadOnlyAdapter",
    "IntegrationAdapter",
    "IntegrationGateway",
    "ReadOnlyTransport",
    "ReplayAdapter",
    "TransportError",
    "UrllibReadOnlyTransport",
]

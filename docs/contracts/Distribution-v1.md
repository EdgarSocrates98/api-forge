# Distribution-v1

API Forge is an installed Python package. The package, not a consumer
repository mirror, owns the executable, contracts, agents, skills, knowledge
packs, SDD templates and host adapter templates.

## Paths

| Name | Default | Override |
|---|---|---|
| Package root | installed `apiforge` package | reported by `apiforge inspect` |
| User state | `<project>/.apiforge` | `APIFORGE_HOME` |
| User config | absent | `APIFORGE_CONFIG` |
| Cache | `<state>/cache` | `APIFORGE_CACHE` |

Values are normalized to absolute paths. API Forge never writes to the package
root. A user can install into a virtual environment, a user-local prefix, a
mounted volume or another writable location without administrator privileges;
the executable directory can be added to `PATH` or invoked by absolute path.

## Hostless operation

`inspect`, `init`, `status`, `doctor`, `context`, SDD, agents, skills, graph,
evidence and verification do not require a host process, network port,
provider SDK or remote MCP server. `doctor` reports optional capabilities as
`ready`, `unavailable`, `degraded`, `unresolved` or `blocked` and preserves an
actionable `field` and `unlock`.

## Asset provenance

Packaged assets are loaded through `importlib.resources` and expose a SHA-256.
Missing or divergent assets are named failures. Consumer repositories receive
only minimal manifests and explicitly requested, previewable adapters.

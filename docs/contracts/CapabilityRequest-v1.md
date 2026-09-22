# CapabilityRequest/v1

`CapabilityRequest` is the canonical input shared by CLI, MCP, IDE and UI.
It contains a capability id, user intent, surface, action, JSON context,
optional case id and detail level. Actions are `inspect`, `plan`, `apply` and
`verify`; `apply` is still subject to policy and approval gates.

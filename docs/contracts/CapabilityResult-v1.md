# CapabilityResult/v1

`CapabilityResult` is the canonical surface output. It contains capability
state, operation status, payload, evidence, gaps, limitations and an optional
stable error code. A host may format the result for its UI or protocol, but it
must not reinterpret `unresolved`, `unsupported`, `blocked` or `review` as
success.

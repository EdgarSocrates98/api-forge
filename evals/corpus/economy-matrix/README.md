# Economy matrix corpus

Sixteen canonical contract changes (14 OpenAPI edits of `orders-v1.yaml`, 2 gRPC)
run under economy, balanced and deep. Ground truth (`expected`) is set by the
nature of each edit; `holdout` cases are gated separately; `mutants` are
structural edits applied to compatible candidates that must flip the verdict
to breaking. Axes (quality, evidence, cost, context, latency) are never blended.

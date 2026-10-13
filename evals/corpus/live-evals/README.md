# live-eval layer

The layer is declared in `src/apiforge/rules/live_evals.yaml`: the
deterministic tier lists eval ids + corpora executed by `evals live`;
the provider tier stays `deferred_external` until a provider adapter +
human approval exist — it never gates CI.

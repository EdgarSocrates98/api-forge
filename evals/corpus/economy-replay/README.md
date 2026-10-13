# Economy replay corpus

Stored runs (task spec, routing decision, economy plan) captured from the
economy matrix. `apiforge evals replay --corpus evals/corpus/economy-replay`
re-plans each decision under the current policy without calling a provider
and fails if any risk-required role would be removed.

# Runtime Migration Anti-patterns

- Do not install toolchains implicitly.
- Do not infer a successful build from an absent error.
- Do not mutate AWS or databases in the offline MVP.
- Do not let the executor be the independent verifier.

# VerticalCoverage/v1

`VerticalCoverage` links one required engineering vertical to its fixture,
golden case, holdout and verifier. A matrix cell without all four references is
not coverage. Holdouts may conclude `unresolved`, `unsupported` or
`inconclusive`; they must not be converted into a passing golden result.

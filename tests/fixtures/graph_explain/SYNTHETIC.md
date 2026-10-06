# Synthetic graph plan fixtures

Every file here is **synthetic**: shaped after the official documentation, not captured from a
live cluster. They are parser and rule fixtures, never field evidence (`--synthetic` marks the
resulting `GraphPlanIR`). Replace them with redacted real dumps before shipping claims about
real workloads.

| File | Format | Source of the shape |
|---|---|---|
| `gremlin-explain.txt` | neptune-gremlin-explain | https://docs.aws.amazon.com/neptune/latest/userguide/gremlin-explain-api.html (fold/unfold example) |
| `gremlin-profile.txt` | neptune-gremlin-profile | https://docs.aws.amazon.com/neptune/latest/userguide/gremlin-profile-api.html |
| `cypher-static.txt` | neptune-opencypher-static | https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-opencypher-explain.html (static columns assumed: no runtime columns) |
| `cypher-dynamic.txt` | neptune-opencypher-dynamic | same page, `details` example (label 'ALL' scan) |
| `sparql-explain.txt` | neptune-sparql-explain | https://docs.aws.amazon.com/neptune/latest/userguide/sparql-explain-examples.html |
| `neo4j-explain.txt` | neo4j-explain | https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/ (cypher-shell table) |
| `neo4j-profile.txt` | neo4j-profile | same, PROFILE with Rows/DB Hits, supernode-like expansion |

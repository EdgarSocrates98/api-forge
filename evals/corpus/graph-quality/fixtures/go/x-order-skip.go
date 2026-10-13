package q

import (
	"context"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func run(ctx context.Context, driver neo4j.DriverWithContext) {
	neo4j.ExecuteQuery(ctx, driver, "MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN b ORDER BY b.name SKIP 10 LIMIT 10", nil, neo4j.EagerResultTransformer)
}

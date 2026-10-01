package q

import (
	"context"
	"fmt"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func run(ctx context.Context, driver neo4j.DriverWithContext, session neo4j.SessionWithContext, id string) {
	_ = fmt.Sprint(id)
	neo4j.ExecuteQuery(ctx, driver, "MATCH (n) WHERE n.age > 3 RETURN n", nil, neo4j.EagerResultTransformer)
}

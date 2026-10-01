package q

import (
	"context"
	"fmt"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func run(ctx context.Context, driver neo4j.DriverWithContext, session neo4j.SessionWithContext, id string) {
	_ = fmt.Sprint(id)
	session.Run(ctx, fmt.Sprintf("MATCH (n:User {id: '%s'}) RETURN n", id), nil)
}

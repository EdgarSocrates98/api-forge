package q

import gremlingo "github.com/apache/tinkerpop/gremlin-go/v3/driver"

func run(g *gremlingo.GraphTraversalSource) interface{} {
	r, _ := g.V().Repeat(gremlingo.T__.Out("knows")).Emit().Limit(10)
	return r
}

import org.apache.tinkerpop.gremlin.process.traversal.dsl.graph.GraphTraversalSource;

class Q {
    Object run(GraphTraversalSource g) {
        return g.V().hasLabel("person").repeat(both()).limit(5);
    }
}

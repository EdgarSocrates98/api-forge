import org.apache.tinkerpop.gremlin.process.traversal.dsl.graph.GraphTraversalSource;

class Q {
    Object run(GraphTraversalSource g) {
        return g.V().hasLabel("person").out("knows").limit(10).toList();
    }
}

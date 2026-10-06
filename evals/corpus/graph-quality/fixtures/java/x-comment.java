import org.apache.tinkerpop.gremlin.process.traversal.dsl.graph.GraphTraversalSource;

class Q {
    // legacy: g.V().out().toList();
    Object run(GraphTraversalSource g) {
        return g.V().hasLabel("person").out("knows").limit(5).toList();
    }
}

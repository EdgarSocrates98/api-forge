import org.apache.tinkerpop.gremlin.process.traversal.dsl.graph.GraphTraversalSource;

class Q {
    Object run(GraphTraversalSource g) {
        return g.V().repeat(out("knows")).emit().limit(10);
    }
}

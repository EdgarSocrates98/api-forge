import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (a:P {id: $id}), (b:Q) RETURN a, b");
    }
}

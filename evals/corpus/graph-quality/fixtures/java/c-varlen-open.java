import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (a:Person)-[:KNOWS*2..]->(b) RETURN b");
    }
}

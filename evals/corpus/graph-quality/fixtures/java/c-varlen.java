import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (a:Person)-[:KNOWS*]->(b) RETURN b LIMIT 10");
    }
}
